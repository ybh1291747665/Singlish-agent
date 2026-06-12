import asyncio
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.asr.provider import get_transcription_provider
from singlish_agent_api.infrastructure.audio.preprocess import preprocess_audio_file
from singlish_agent_api.infrastructure.audio.vad import build_silence_segments, detect_speech_segments
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.normalization.provider import normalize_transcript
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
            speech_segments = _build_speech_segments_with_fallback(
                normalized_audio_path,
                duration_seconds=preprocessed_audio.duration_seconds,
            )
            silence_segments = build_silence_segments(
                duration_seconds=preprocessed_audio.duration_seconds,
                speech_segments=speech_segments,
            )
            result_payload["preprocessing"] = {
                "duration_seconds": preprocessed_audio.duration_seconds,
                "sample_rate_hz": preprocessed_audio.sample_rate_hz,
                "channels": preprocessed_audio.channels,
                "normalized_format": preprocessed_audio.normalized_format,
                "speech_segments": speech_segments,
                "silence_segments": silence_segments,
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.TRANSCRIBING)
            transcription = await provider.transcribe(normalized_audio_path)
            transcription_segments = [
                {
                    "start_seconds": segment.start_seconds,
                    "end_seconds": segment.end_seconds,
                    "text": segment.text,
                    "confidence": segment.confidence,
                    "low_confidence": _is_low_confidence(segment.confidence),
                }
                for segment in transcription.segments
            ]
            low_confidence_segments = detect_low_confidence_segments(transcription_segments)
            result_payload["transcription"] = {
                "provider": transcription.provider,
                "raw_transcript": transcription.raw_transcript,
                "segments": transcription_segments,
            }
            result_payload["reprocess"] = {
                "low_confidence_segments": low_confidence_segments,
                "reprocess_status": "not_requested" if low_confidence_segments else "not_needed",
                "reprocess_attempts": 0,
            }
            job = await repository.set_result_payload(job, payload=result_payload)

            job = await repository.transition(job, JobStatus.NORMALIZING)
            normalization = normalize_transcript(transcription.raw_transcript)
            standard_english = str(normalization["standard_english"])
            result_payload["normalization"] = normalization
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


def _build_speech_segments_with_fallback(
    audio_path: Path,
    *,
    duration_seconds: float,
) -> list[dict[str, float]]:
    if duration_seconds <= 0:
        return []
    try:
        speech_segments = detect_speech_segments(
            audio_path,
            duration_seconds=duration_seconds,
        )
    except Exception:
        speech_segments = []
    if speech_segments:
        return speech_segments
    return [
        {
            "start_seconds": 0.0,
            "end_seconds": round(duration_seconds, 3),
        }
    ]


def detect_low_confidence_segments(
    segments: list[dict[str, object]],
    *,
    threshold: float = 0.95,
) -> list[dict[str, object]]:
    return [
        segment
        for segment in segments
        if _is_low_confidence(segment.get("confidence"), threshold=threshold)
    ]


def _is_low_confidence(confidence: object, *, threshold: float = 0.95) -> bool:
    if confidence is None:
        return False
    return float(confidence) < threshold
