import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.worker.tasks import process_job


class FakeResult:
    def __init__(self, job) -> None:
        self.job = job

    def scalar_one_or_none(self):
        return self.job


class FakeSession:
    def __init__(self) -> None:
        self.jobs: dict[str, object] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def add(self, job) -> None:
        now = datetime.now(timezone.utc)
        if getattr(job, "id", None) is None:
            job.id = str(uuid4())
            job.created_at = now
        job.updated_at = now
        self.jobs[job.id] = job

    async def commit(self) -> None:
        return None

    async def refresh(self, job) -> None:
        self.jobs[job.id] = job

    async def execute(self, statement):
        job_id = statement.whereclause.right.value
        return FakeResult(self.jobs.get(job_id))


def test_process_job_marks_job_completed(monkeypatch) -> None:
    from singlish_agent_api.worker import tasks as tasks_module

    session = FakeSession()

    class FakeSessionFactory:
        def __call__(self):
            return session

    monkeypatch.setattr(tasks_module, "AsyncSessionFactory", FakeSessionFactory())

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
    assert refreshed.status == JobStatus.COMPLETED.value
    assert refreshed.result_summary == "Fake transcript completed successfully."
    assert refreshed.processed_at is not None
