import json
import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.exports import JobExportFormat, build_job_export
from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.domain.jobs.schemas import (
    JobCreateResponse,
    JobDetailResponse,
    JobResultPayload,
    JobSegmentsResponse,
)
from singlish_agent_api.domain.jobs.service import create_job_from_upload
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.infrastructure.storage.client import ObjectStorageService
from singlish_agent_api.worker.celery_app import celery_app
from singlish_agent_api.worker.tasks import process_job


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class CeleryQueue:
    async def enqueue(self, job_id: str) -> None:
        if celery_app.conf.task_always_eager:
            await asyncio.to_thread(process_job.delay, job_id)
            return None
        process_job.delay(job_id)
        return None


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session


def get_storage() -> ObjectStorageService:
    return ObjectStorageService()


def get_queue() -> CeleryQueue:
    return CeleryQueue()


def parse_job_result_payload(job_result_payload: str | None) -> JobResultPayload | None:
    if not job_result_payload:
        return None
    return JobResultPayload.model_validate(json.loads(job_result_payload))


@router.post("", response_model=JobCreateResponse, status_code=201)
async def create_job(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorageService = Depends(get_storage),
    queue: CeleryQueue = Depends(get_queue),
) -> JobCreateResponse:
    job_id, file_name, status, created_at = await create_job_from_upload(
        upload_file=file,
        session=session,
        storage=storage,
        queue=queue,
    )
    return JobCreateResponse(
        job_id=job_id,
        file_name=file_name,
        status=status,
        created_at=created_at,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> JobDetailResponse:
    repository = JobRepository(session)
    job = await repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobDetailResponse(
        job_id=job.id,
        file_name=job.file_name,
        status=job.status,
        result_summary=job.result_summary,
        result_payload=parse_job_result_payload(job.result_payload),
        created_at=job.created_at,
        updated_at=job.updated_at,
        processed_at=job.processed_at,
    )


@router.get("/{job_id}/segments", response_model=JobSegmentsResponse)
async def get_job_segments(
    job_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> JobSegmentsResponse:
    repository = JobRepository(session)
    job = await repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")

    payload = parse_job_result_payload(job.result_payload)
    all_segments = payload.transcription.segments if payload and payload.transcription else []
    return JobSegmentsResponse(
        job_id=job.id,
        status=job.status,
        total_segments=len(all_segments),
        segments=all_segments[offset : offset + limit],
    )


@router.get("/{job_id}/exports/{export_format}")
async def export_job(
    job_id: str,
    export_format: JobExportFormat,
    session: AsyncSession = Depends(get_session),
) -> Response:
    repository = JobRepository(session)
    job = await repository.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.COMPLETED.value or not job.result_payload:
        raise HTTPException(status_code=409, detail="job export not ready")

    payload = parse_job_result_payload(job.result_payload)
    if payload is None:
        raise HTTPException(status_code=409, detail="job export not ready")
    document = build_job_export(job=job, payload=payload, export_format=export_format)
    return Response(
        content=document.content,
        media_type=document.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{document.file_name}"',
        },
    )
