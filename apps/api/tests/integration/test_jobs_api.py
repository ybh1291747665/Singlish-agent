from io import BytesIO
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.main import app


class FakeResult:
    def __init__(self, job) -> None:
        self.job = job

    def scalar_one_or_none(self):
        return self.job


class FakeSession:
    def __init__(self) -> None:
        self.jobs: dict[str, object] = {}

    def add(self, job) -> None:
        now = datetime.now(timezone.utc)
        job.id = str(uuid4())
        job.created_at = now
        job.updated_at = now
        job.processed_at = None
        job.result_summary = None
        self.jobs[job.id] = job

    async def commit(self) -> None:
        return None

    async def refresh(self, job) -> None:
        if getattr(job, "id", None) is not None:
            self.jobs[job.id] = job

    async def execute(self, statement):
        job_id = statement.whereclause.right.value
        return FakeResult(self.jobs.get(job_id))


def test_create_job_returns_created_job(monkeypatch) -> None:
    from singlish_agent_api.api.routes import jobs as jobs_module

    stored_keys: list[str] = []
    queued_job_ids: list[str] = []
    session = FakeSession()

    class FakeStorage:
        async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
            stored_keys.append(object_key)

    class FakeQueue:
        async def enqueue(self, job_id: str) -> None:
            queued_job_ids.append(job_id)

    async def override_session():
        yield session

    app.dependency_overrides[jobs_module.get_session] = override_session
    app.dependency_overrides[jobs_module.get_storage] = lambda: FakeStorage()
    app.dependency_overrides[jobs_module.get_queue] = lambda: FakeQueue()

    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs",
        files={"file": ("sample.wav", BytesIO(b"demo-audio").read(), "audio/wav")},
    )

    body = response.json()

    assert response.status_code == 201
    assert body["status"] == "queued"
    assert body["file_name"] == "sample.wav"
    assert len(stored_keys) == 1
    assert queued_job_ids == [body["job_id"]]
    app.dependency_overrides.clear()


def test_get_job_returns_job_detail() -> None:
    from singlish_agent_api.api.routes import jobs as jobs_module

    session = FakeSession()

    class FakeStorage:
        async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
            return None

    class FakeQueue:
        async def enqueue(self, job_id: str) -> None:
            return None

    async def override_session():
        yield session

    app.dependency_overrides[jobs_module.get_session] = override_session
    app.dependency_overrides[jobs_module.get_storage] = lambda: FakeStorage()
    app.dependency_overrides[jobs_module.get_queue] = lambda: FakeQueue()

    client = TestClient(app)
    create_response = client.post(
        "/api/v1/jobs",
        files={"file": ("sample.wav", b"demo-audio", "audio/wav")},
    )
    job_id = create_response.json()["job_id"]

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
    app.dependency_overrides.clear()


def test_create_job_keeps_created_status_when_upload_fails() -> None:
    from singlish_agent_api.api.routes import jobs as jobs_module

    session = FakeSession()

    class FailingStorage:
        async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
            raise RuntimeError("upload failed")

    class FakeQueue:
        async def enqueue(self, job_id: str) -> None:
            return None

    async def override_session():
        yield session

    app.dependency_overrides[jobs_module.get_session] = override_session
    app.dependency_overrides[jobs_module.get_storage] = lambda: FailingStorage()
    app.dependency_overrides[jobs_module.get_queue] = lambda: FakeQueue()

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/jobs",
        files={"file": ("sample.wav", b"demo-audio", "audio/wav")},
    )

    created_job = next(iter(session.jobs.values()))
    assert response.status_code == 500
    assert created_job.status == JobStatus.CREATED.value
    app.dependency_overrides.clear()


def test_create_job_keeps_uploaded_status_when_enqueue_fails() -> None:
    from singlish_agent_api.api.routes import jobs as jobs_module

    session = FakeSession()

    class FakeStorage:
        async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
            return None

    class FailingQueue:
        async def enqueue(self, job_id: str) -> None:
            raise RuntimeError("queue publish failed")

    async def override_session():
        yield session

    app.dependency_overrides[jobs_module.get_session] = override_session
    app.dependency_overrides[jobs_module.get_storage] = lambda: FakeStorage()
    app.dependency_overrides[jobs_module.get_queue] = lambda: FailingQueue()

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/jobs",
        files={"file": ("sample.wav", b"demo-audio", "audio/wav")},
    )

    created_job = next(iter(session.jobs.values()))
    assert response.status_code == 500
    assert created_job.status == JobStatus.UPLOADED.value
    app.dependency_overrides.clear()
