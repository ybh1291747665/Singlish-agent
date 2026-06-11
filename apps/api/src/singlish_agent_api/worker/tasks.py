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
            result_payload: dict[str, object] = {}

            job = await repository.transition(job, JobStatus.PREPROCESSING)
            result_payload["preprocessing"] = {
                "duration_seconds": 12.4,
                "sample_rate_hz": 16000,
                "channels": 1,
                "normalized_format": "pcm_s16le",
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.TRANSCRIBING)
            result_payload["transcription"] = {
                "raw_transcript": "wah lau eh this queue quite fast lah",
                "segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 2.4,
                        "text": "wah lau eh this queue quite fast lah",
                        "confidence": 0.94,
                    }
                ],
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.NORMALIZING)
            result_payload["normalization"] = {
                "normalized_transcript": "wah lau eh, this queue quite fast lah",
                "standard_english": "Wow, this queue is quite fast.",
                "glossary_hits": ["wah lau eh", "lah"],
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.GENERATING_REPORT)
            result_payload["report"] = {
                "summary": "Speaker remarks that the queue moved quickly.",
                "key_phrases": ["queue", "fast"],
            }
            job = await repository.set_result_payload(job, payload=result_payload)
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
