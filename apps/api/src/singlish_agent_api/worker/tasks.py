import asyncio
from datetime import datetime, timezone

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.worker.celery_app import celery_app


PIPELINE_STAGES: tuple[JobStatus, ...] = (
    JobStatus.PREPROCESSING,
    JobStatus.TRANSCRIBING,
    JobStatus.NORMALIZING,
    JobStatus.GENERATING_REPORT,
)


async def _process_job(job_id: str) -> None:
    async with AsyncSessionFactory() as session:
        repository = JobRepository(session)
        job = await repository.get(job_id)
        if job is None:
            raise ValueError(f"job not found: {job_id}")
        try:
            for stage in PIPELINE_STAGES:
                job = await repository.transition(job, stage)
            job.result_summary = "Fake transcript completed successfully."
            job.processed_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(job)
            await repository.transition(job, JobStatus.COMPLETED)
        except Exception:
            if JobStatus(job.status) in PIPELINE_STAGES:
                await repository.transition(job, JobStatus.FAILED)
            raise


@celery_app.task(name="singlish_agent.process_job")
def process_job(job_id: str) -> None:
    asyncio.run(_process_job(job_id))
