from pathlib import Path
from typing import Protocol

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository


class StoragePort(Protocol):
    async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None: ...


class QueuePort(Protocol):
    async def enqueue(self, job_id: str) -> None: ...


async def create_job_from_upload(
    *,
    upload_file: UploadFile,
    session: AsyncSession,
    storage: StoragePort,
    queue: QueuePort,
) -> tuple[str, str, str, object]:
    repository = JobRepository(session)
    safe_name = Path(upload_file.filename or "upload.bin").name
    job = await repository.create(file_name=safe_name, object_key=f"raw/pending/{safe_name}")

    object_key = f"raw/{job.id}/{safe_name}"
    content = await upload_file.read()
    await storage.upload(
        object_key=object_key,
        content=content,
        content_type=upload_file.content_type or "application/octet-stream",
    )

    job.object_key = object_key
    await session.commit()
    await session.refresh(job)

    job = await repository.transition(job, JobStatus.UPLOADED)
    await queue.enqueue(job.id)
    job = await repository.transition(job, JobStatus.QUEUED)
    return job.id, job.file_name, job.status, job.created_at
