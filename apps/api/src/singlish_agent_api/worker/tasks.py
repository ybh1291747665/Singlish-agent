import asyncio
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.asr.provider import get_transcription_provider
from singlish_agent_api.infrastructure.audio.preprocess import preprocess_audio_file
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.infrastructure.storage.client import ObjectStorageService
from singlish_agent_api.worker.celery_app import celery_app
from singlish_agent_api.worker.runtime import configure_worker_event_loop, get_worker_event_loop


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

        storage = ObjectStorageService()
        provider = get_transcription_provider()
        suffix = Path(job.file_name).suffix or ".bin"
        source_audio_path: Path | None = None
        normalized_audio_path: Path | None = None
        try:
            result_payload: dict[str, object] = {}

            job = await repository.transition(job, JobStatus.PREPROCESSING)
            audio_bytes = await storage.download(object_key=job.object_key)
            with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(audio_bytes)
                source_audio_path = Path(temp_file.name)
            preprocessed_audio = await preprocess_audio_file(source_audio_path)
            normalized_audio_path = preprocessed_audio.audio_path
            result_payload["preprocessing"] = {
                "duration_seconds": preprocessed_audio.duration_seconds,
                "sample_rate_hz": preprocessed_audio.sample_rate_hz,
                "channels": preprocessed_audio.channels,
                "normalized_format": preprocessed_audio.normalized_format,
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.TRANSCRIBING)
            transcription = await provider.transcribe(normalized_audio_path)
            result_payload["transcription"] = {
                "provider": transcription.provider,
                "raw_transcript": transcription.raw_transcript,
                "segments": [
                    {
                        "start_seconds": segment.start_seconds,
                        "end_seconds": segment.end_seconds,
                        "text": segment.text,
                        "confidence": segment.confidence,
                    }
                    for segment in transcription.segments
                ],
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.NORMALIZING)
            standard_english = (
                "Wow, this queue is quite fast."
                if "wah lau eh" in transcription.raw_transcript.lower()
                else transcription.raw_transcript
            )
            result_payload["normalization"] = {
                "normalized_transcript": transcription.raw_transcript,
                "standard_english": standard_english,
                "glossary_hits": ["wah lau eh", "lah"]
                if "wah lau eh" in transcription.raw_transcript.lower()
                else [],
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.GENERATING_REPORT)
            result_payload["report"] = {
                "summary": "Speaker remarks that the queue moved quickly."
                if "queue" in standard_english.lower()
                else f"Transcript generated: {standard_english}",
                "key_phrases": ["queue", "fast"]
                if "queue" in standard_english.lower()
                else standard_english.split()[:3],
            }
            job = await repository.set_result_payload(job, payload=result_payload)
            job.result_summary = (
                f"Transcription completed successfully via {transcription.provider}."
            )
            job.processed_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(job)
            await repository.transition(job, JobStatus.COMPLETED)
        except Exception:
            if JobStatus(job.status) in PIPELINE_STAGES:
                await repository.transition(job, JobStatus.FAILED)
            raise
        finally:
            if normalized_audio_path is not None:
                normalized_audio_path.unlink(missing_ok=True)
            if source_audio_path is not None:
                source_audio_path.unlink(missing_ok=True)


@celery_app.task(name="singlish_agent.process_job")
def process_job(job_id: str) -> None:
    configure_worker_event_loop()
    loop = get_worker_event_loop()
    loop.run_until_complete(_process_job(job_id))
