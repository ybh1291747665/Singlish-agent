import asyncio
from datetime import datetime, timezone
import json
from uuid import uuid4

import pytest

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.worker.celery_app import celery_app
from singlish_agent_api.worker.tasks import process_job


class FakeResult:
    def __init__(self, job) -> None:
        self.job = job

    def scalar_one_or_none(self):
        return self.job


class FakeSession:
    def __init__(self) -> None:
        self.jobs: dict[str, object] = {}
        self.status_history: dict[str, list[str]] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def add(self, job) -> None:
        now = datetime.now(timezone.utc)
        if getattr(job, "id", None) is None:
            job.id = str(uuid4())
            job.created_at = now
            job.result_payload = None
        job.updated_at = now
        self.jobs[job.id] = job
        history = self.status_history.setdefault(job.id, [])
        if not history or history[-1] != job.status:
            history.append(job.status)

    async def commit(self) -> None:
        return None

    async def refresh(self, job) -> None:
        self.jobs[job.id] = job
        history = self.status_history.setdefault(job.id, [])
        if history[-1] != job.status:
            history.append(job.status)

    async def execute(self, statement):
        job_id = statement.whereclause.right.value
        return FakeResult(self.jobs.get(job_id))


def test_worker_task_is_registered_with_celery_app() -> None:
    assert "singlish_agent.process_job" in celery_app.tasks


def test_process_job_configures_worker_event_loop(monkeypatch) -> None:
    from singlish_agent_api.worker import tasks as tasks_module

    configured: list[bool] = []
    processed: list[str] = []

    monkeypatch.setattr(
        tasks_module,
        "configure_worker_event_loop",
        lambda: configured.append(True),
    )
    monkeypatch.setattr(
        tasks_module.asyncio,
        "run",
        lambda coroutine: (processed.append("job-123"), coroutine.close()),
    )

    process_job("job-123")

    assert configured == [True]
    assert processed == ["job-123"]


def test_process_job_runs_full_pipeline_and_marks_job_completed(monkeypatch) -> None:
    from singlish_agent_api.worker import tasks as tasks_module

    session = FakeSession()

    class FakeTranscriptionProvider:
        async def transcribe(self, audio_path) -> object:
            from singlish_agent_api.infrastructure.asr.provider import (
                ASRSegmentResult,
                ASRTranscriptionResult,
            )

            return ASRTranscriptionResult(
                provider="fake",
                raw_transcript="wah lau eh this queue quite fast lah",
                segments=[
                    ASRSegmentResult(
                        start_seconds=0.0,
                        end_seconds=2.4,
                        text="wah lau eh this queue quite fast lah",
                        confidence=0.94,
                    )
                ],
            )

    class FakeStorage:
        async def download(self, *, object_key: str) -> bytes:
            return b"fake-audio"

    class FakeSessionFactory:
        def __call__(self):
            return session

    monkeypatch.setattr(tasks_module, "AsyncSessionFactory", FakeSessionFactory())
    monkeypatch.setattr(tasks_module, "ObjectStorageService", FakeStorage)
    monkeypatch.setattr(tasks_module, "get_transcription_provider", lambda: FakeTranscriptionProvider())

    async def create_job() -> str:
        repository = JobRepository(session)
        job = await repository.create(file_name="sample.wav", object_key="raw/sample.wav")
        job = await repository.transition(job, JobStatus.UPLOADED)
        job = await repository.transition(job, JobStatus.QUEUED)
        return job.id

    async def fetch_job(job_id: str):
        repository = JobRepository(session)
        return await repository.get(job_id)

    job_id = asyncio.run(create_job())

    process_job(job_id)

    refreshed = asyncio.run(fetch_job(job_id))
    assert refreshed is not None
    assert session.status_history[job_id] == [
        JobStatus.CREATED.value,
        JobStatus.UPLOADED.value,
        JobStatus.QUEUED.value,
        JobStatus.PREPROCESSING.value,
        JobStatus.TRANSCRIBING.value,
        JobStatus.NORMALIZING.value,
        JobStatus.GENERATING_REPORT.value,
        JobStatus.COMPLETED.value,
    ]
    assert refreshed.status == JobStatus.COMPLETED.value
    assert refreshed.result_summary == "Transcription completed successfully via fake."
    assert refreshed.processed_at is not None
    payload = json.loads(refreshed.result_payload)
    assert payload["preprocessing"]["duration_seconds"] == 12.4
    assert payload["transcription"]["provider"] == "fake"
    assert payload["transcription"]["raw_transcript"] == "wah lau eh this queue quite fast lah"
    assert payload["normalization"]["standard_english"] == "Wow, this queue is quite fast."
    assert payload["report"]["summary"] == "Speaker remarks that the queue moved quickly."


def test_process_job_marks_job_failed_when_processing_errors(monkeypatch) -> None:
    from singlish_agent_api.worker import tasks as tasks_module

    class FailingSession(FakeSession):
        def __init__(self) -> None:
            super().__init__()
            self.should_fail = True

        async def commit(self) -> None:
            if self.should_fail and any(
                job.status == JobStatus.GENERATING_REPORT.value
                and job.result_summary == "Transcription completed successfully via fake."
                for job in self.jobs.values()
            ):
                self.should_fail = False
                raise RuntimeError("processing persist failed")
            return None

    session = FailingSession()

    class FakeTranscriptionProvider:
        async def transcribe(self, audio_path) -> object:
            from singlish_agent_api.infrastructure.asr.provider import (
                ASRSegmentResult,
                ASRTranscriptionResult,
            )

            return ASRTranscriptionResult(
                provider="fake",
                raw_transcript="wah lau eh this queue quite fast lah",
                segments=[
                    ASRSegmentResult(
                        start_seconds=0.0,
                        end_seconds=2.4,
                        text="wah lau eh this queue quite fast lah",
                        confidence=0.94,
                    )
                ],
            )

    class FakeStorage:
        async def download(self, *, object_key: str) -> bytes:
            return b"fake-audio"

    class FakeSessionFactory:
        def __call__(self):
            return session

    monkeypatch.setattr(tasks_module, "AsyncSessionFactory", FakeSessionFactory())
    monkeypatch.setattr(tasks_module, "ObjectStorageService", FakeStorage)
    monkeypatch.setattr(tasks_module, "get_transcription_provider", lambda: FakeTranscriptionProvider())

    async def create_job() -> str:
        repository = JobRepository(session)
        job = await repository.create(file_name="sample.wav", object_key="raw/sample.wav")
        job = await repository.transition(job, JobStatus.UPLOADED)
        job = await repository.transition(job, JobStatus.QUEUED)
        return job.id

    async def fetch_job(job_id: str):
        repository = JobRepository(session)
        return await repository.get(job_id)

    job_id = asyncio.run(create_job())

    with pytest.raises(RuntimeError, match="processing persist failed"):
        process_job(job_id)

    refreshed = asyncio.run(fetch_job(job_id))
    assert refreshed is not None
    assert refreshed.status == JobStatus.FAILED.value
