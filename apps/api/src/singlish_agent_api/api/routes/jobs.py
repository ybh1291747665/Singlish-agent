from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.schemas import JobCreateResponse, JobDetailResponse
from singlish_agent_api.domain.jobs.service import create_job_from_upload
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class NoopQueue:
    async def enqueue(self, job_id: str) -> None:
        return None


class NoopStorage:
    async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
        return None


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session


def get_storage() -> NoopStorage:
    return NoopStorage()


def get_queue() -> NoopQueue:
    return NoopQueue()


@router.post("", response_model=JobCreateResponse, status_code=201)
async def create_job(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: NoopStorage = Depends(get_storage),
    queue: NoopQueue = Depends(get_queue),
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
        created_at=job.created_at,
        updated_at=job.updated_at,
        processed_at=job.processed_at,
    )
