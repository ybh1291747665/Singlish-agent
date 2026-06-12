import json
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
        job.result_payload = None
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


def test_export_job_returns_markdown_document_for_completed_job() -> None:
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
    job = session.jobs[job_id]
    job.status = JobStatus.COMPLETED.value
    job.result_summary = "Transcription completed successfully via fake."
    job.result_payload = json.dumps(
        {
            "preprocessing": {
                "duration_seconds": 2.4,
                "sample_rate_hz": 16000,
                "channels": 1,
                "normalized_format": "pcm_s16le",
                "speech_segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 2.4,
                    }
                ],
                "silence_segments": [],
            },
            "transcription": {
                "provider": "fake",
                "raw_transcript": "wah lau eh this queue quite fast lah",
                "segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 2.4,
                        "text": "wah lau eh this queue quite fast lah",
                        "confidence": 0.94,
                        "low_confidence": True,
                    }
                ],
            },
            "normalization": {
                "normalized_transcript": "wah lau eh this queue quite fast lah",
                "standard_english": "Wow, this queue is quite fast.",
                "simplified_chinese": "\u54c7\uff0c\u8fd9\u4e2a\u961f\u4f0d\u8d70\u5f97\u5f88\u5feb\u3002",
                "glossary_hits": ["wah lau eh", "lah"],
                "translation_provider": "fallback",
            },
            "report": {
                "summary": "Speaker remarks that the queue moved quickly.",
                "key_phrases": ["queue", "fast"],
            },
            "reprocess": {
                "low_confidence_segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 2.4,
                        "text": "wah lau eh this queue quite fast lah",
                        "confidence": 0.94,
                        "low_confidence": True,
                    }
                ],
                "reprocess_status": "not_requested",
                "reprocess_attempts": 0,
            },
        }
    )

    response = client.get(f"/api/v1/jobs/{job_id}/exports/md")

    assert response.status_code == 200
    assert response.headers["content-disposition"].endswith(f"sample-{job_id}.md\"")
    assert "## Summary" in response.text
    assert "## Simplified Chinese" in response.text
    assert "## Low-confidence Reprocess" in response.text
    assert "Speaker remarks that the queue moved quickly." in response.text
    app.dependency_overrides.clear()


def test_export_job_returns_conflict_when_job_not_completed() -> None:
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

    response = client.get(f"/api/v1/jobs/{job_id}/exports/srt")

    assert response.status_code == 409
    assert response.json()["detail"] == "job export not ready"
    app.dependency_overrides.clear()


def test_get_job_segments_returns_paginated_segments() -> None:
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
    job = session.jobs[job_id]
    job.status = JobStatus.COMPLETED.value
    job.result_payload = json.dumps(
        {
            "transcription": {
                "provider": "fake",
                "raw_transcript": "first second third",
                "segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 1.0,
                        "text": "first",
                        "confidence": 0.91,
                    },
                    {
                        "start_seconds": 1.0,
                        "end_seconds": 2.0,
                        "text": "second",
                        "confidence": 0.92,
                    },
                    {
                        "start_seconds": 2.0,
                        "end_seconds": 3.0,
                        "text": "third",
                        "confidence": 0.93,
                    },
                ],
            }
        }
    )

    response = client.get(f"/api/v1/jobs/{job_id}/segments?offset=1&limit=1")

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
    assert response.json()["status"] == "completed"
    assert response.json()["total_segments"] == 3
    assert response.json()["segments"] == [
        {
            "start_seconds": 1.0,
            "end_seconds": 2.0,
            "text": "second",
            "confidence": 0.92,
            "low_confidence": False,
        }
    ]
    app.dependency_overrides.clear()


def test_reprocess_low_confidence_marks_job_reprocess_status() -> None:
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
    job = session.jobs[job_id]
    job.status = JobStatus.COMPLETED.value
    job.result_payload = json.dumps(
        {
            "transcription": {
                "provider": "fake",
                "raw_transcript": "first second third",
                "segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 1.0,
                        "text": "first",
                        "confidence": 0.91,
                        "low_confidence": True,
                    }
                ],
            },
            "reprocess": {
                "low_confidence_segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 1.0,
                        "text": "first",
                        "confidence": 0.91,
                        "low_confidence": True,
                    }
                ],
                "reprocess_status": "not_requested",
                "reprocess_attempts": 0,
            },
        }
    )

    response = client.post(f"/api/v1/jobs/{job_id}/reprocess-low-confidence")

    assert response.status_code == 202
    assert response.json()["job_id"] == job_id
    assert response.json()["reprocess_status"] == "queued"
    assert response.json()["reprocess_attempts"] == 1
    persisted_payload = json.loads(job.result_payload)
    assert persisted_payload["reprocess"]["reprocess_status"] == "queued"
    assert persisted_payload["reprocess"]["reprocess_attempts"] == 1
    app.dependency_overrides.clear()
