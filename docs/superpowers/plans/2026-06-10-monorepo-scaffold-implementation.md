# Monorepo Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a demo-first monorepo scaffold for the Singlish Speech Intelligence Agent with a runnable FastAPI API, Celery worker, React web app, and local PostgreSQL, Redis, and MinIO dependencies.

**Architecture:** The repo starts as a balanced monorepo with `apps/api` for the Python backend and worker, `apps/web` for the React demo, `packages/contracts` for shared TypeScript API contracts, and `infra/docker` for local dependencies. The first vertical slice is upload a file, create a job, enqueue fake processing, and show the job reach `completed` in the web UI.

**Tech Stack:** Python 3.11, FastAPI, Pydantic Settings, SQLAlchemy asyncio, asyncpg, Celery, Redis, boto3, React, TypeScript, Vite, Vitest, Docker Compose, PostgreSQL, MinIO

---

## File Map

- `/.gitignore`
  Ignore Python caches, node output, local env files, uploaded demo files, and `.superpowers/`.
- `/package.json`
  Root npm workspace definition and convenience scripts for the web app.
- `/.env.example`
  Single source of local environment variables for API, worker, and frontend.
- `/README.md`
  Local setup and verification instructions for the scaffold.
- `/infra/docker/docker-compose.yml`
  Local PostgreSQL, Redis, MinIO, and bucket bootstrap services.
- `/apps/api/pyproject.toml`
  Editable-install metadata for the backend package.
- `/apps/api/src/singlish_agent_api/main.py`
  FastAPI application factory and startup wiring.
- `/apps/api/src/singlish_agent_api/core/config.py`
  Pydantic settings for database, Redis, object storage, and queue options.
- `/apps/api/src/singlish_agent_api/core/logging.py`
  Structured logging bootstrap.
- `/apps/api/src/singlish_agent_api/api/routes/health.py`
  `/health` route and service checks.
- `/apps/api/src/singlish_agent_api/api/routes/jobs.py`
  `POST /api/v1/jobs` and `GET /api/v1/jobs/{job_id}`.
- `/apps/api/src/singlish_agent_api/domain/jobs/models.py`
  Job status enum, transition guard, and ORM model.
- `/apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
  Pydantic request and response models for jobs.
- `/apps/api/src/singlish_agent_api/domain/jobs/service.py`
  Upload orchestration, repository usage, storage usage, and queue dispatch.
- `/apps/api/src/singlish_agent_api/infrastructure/db/base.py`
  Declarative base.
- `/apps/api/src/singlish_agent_api/infrastructure/db/session.py`
  Async engine, session factory, and `init_db`.
- `/apps/api/src/singlish_agent_api/infrastructure/cache/redis.py`
  Redis client helper and ping check.
- `/apps/api/src/singlish_agent_api/infrastructure/storage/client.py`
  MinIO-backed object storage client and health check.
- `/apps/api/src/singlish_agent_api/infrastructure/repositories/jobs.py`
  CRUD access for job records.
- `/apps/api/src/singlish_agent_api/worker/celery_app.py`
  Celery application configuration.
- `/apps/api/src/singlish_agent_api/worker/tasks.py`
  Fake job processor that updates status and fake result payload.
- `/apps/api/src/singlish_agent_api/worker/run_worker.py`
  Python entrypoint for local worker execution after editable install.
- `/apps/api/tests/conftest.py`
  Shared test bootstrapping and source-path setup.
- `/apps/api/tests/integration/test_health.py`
  Health route tests.
- `/apps/api/tests/integration/test_jobs_api.py`
  Jobs API tests.
- `/apps/api/tests/integration/test_worker_task.py`
  Fake Celery task integration test.
- `/apps/api/tests/unit/test_job_status.py`
  Job transition rule tests.
- `/apps/web/package.json`
  Web app dependencies and scripts.
- `/apps/web/tsconfig.json`
  TypeScript config for the web app.
- `/apps/web/vite.config.ts`
  Vite and Vitest configuration.
- `/apps/web/src/main.tsx`
  React bootstrap.
- `/apps/web/src/app/App.tsx`
  Composition of health and jobs features.
- `/apps/web/src/features/health/*`
  Health API client and panel.
- `/apps/web/src/features/jobs/*`
  Upload form, jobs API client, and status poller.
- `/apps/web/src/shared/api/client.ts`
  Shared fetch wrapper.
- `/apps/web/src/test/setup.ts`
  Vitest DOM setup.
- `/packages/contracts/package.json`
  Shared TypeScript contract package metadata.
- `/packages/contracts/src/job.ts`
  Shared frontend-facing job contract types.
- `/packages/config/README.md`
  Reserved package explanation for future shared config.

### Task 1: Initialize The Repository And Root Workspace

**Files:**
- Create: `.gitignore`
- Create: `package.json`
- Create: `.env.example`
- Create: `README.md`
- Create: `packages/contracts/README.md`
- Create: `packages/config/README.md`

- [ ] **Step 1: Confirm the workspace is not yet a git repository**

Run:

```powershell
git status
```

Expected: FAIL with `fatal: not a git repository`.

- [ ] **Step 2: Initialize git**

Run:

```powershell
git init
```

Expected: success output ending with `Initialized empty Git repository`.

- [ ] **Step 3: Add the root workspace files**

Create `.gitignore`:

```gitignore
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
.venv/
node_modules/
dist/
build/
coverage/
*.log
.env
uploads/
.superpowers/
apps/web/.vite/
apps/web/node_modules/
```

Create `package.json`:

```json
{
  "name": "singlish-agent",
  "private": true,
  "workspaces": [
    "apps/web",
    "packages/*"
  ],
  "scripts": {
    "dev:web": "npm run dev --workspace @singlish-agent/web",
    "build:web": "npm run build --workspace @singlish-agent/web",
    "test:web": "npm run test --workspace @singlish-agent/web"
  }
}
```

Create `.env.example`:

```dotenv
APP_ENV=development
API_HOST=127.0.0.1
API_PORT=8000
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/singlish_agent
REDIS_URL=redis://127.0.0.1:6379/0
S3_ENDPOINT_URL=http://127.0.0.1:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=singlish-agent
S3_REGION=us-east-1
CELERY_TASK_ALWAYS_EAGER=0
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Create `README.md`:

```markdown
# Singlish Agent

Demo-first scaffold for the Singlish Speech Intelligence Agent.

## Planned First Slice

- FastAPI API
- Celery worker
- React upload demo
- PostgreSQL, Redis, and MinIO local dependencies

See this implementation plan for the exact setup sequence.
```

Create `packages/contracts/README.md`:

```markdown
# @singlish-agent/contracts

Shared TypeScript contracts used by the web app.

Python Pydantic schemas remain the source of truth for backend validation in the scaffold phase.
```

Create `packages/config/README.md`:

```markdown
# @singlish-agent/config

Reserved for future shared repository configuration.

Do not add files here until at least two packages need the same config.
```

- [ ] **Step 4: Verify the new root workspace state**

Run:

```powershell
git status --short
npm --version
```

Expected:
- `git status --short` shows the new files as untracked.
- `npm --version` prints a version number.

- [ ] **Step 5: Commit the initialized workspace**

Run:

```powershell
git add .gitignore package.json .env.example README.md packages/contracts/README.md packages/config/README.md
git commit -m "chore: initialize repo workspace"
```

Expected: one commit containing the root workspace setup.

### Task 2: Add Local Infrastructure With Docker Compose

**Files:**
- Create: `infra/docker/docker-compose.yml`
- Modify: `README.md`

- [ ] **Step 1: Prove the compose file does not exist yet**

Run:

```powershell
docker compose -f infra/docker/docker-compose.yml config
```

Expected: FAIL because `infra/docker/docker-compose.yml` does not exist yet.

- [ ] **Step 2: Create the Docker Compose stack**

Create `infra/docker/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: singlish-agent-postgres
    environment:
      POSTGRES_DB: singlish_agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d singlish_agent"]
      interval: 5s
      timeout: 5s
      retries: 20
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: singlish-agent-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 20

  minio:
    image: minio/minio:latest
    container_name: singlish-agent-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 5s
      retries: 20
    volumes:
      - minio-data:/data

  createbucket:
    image: minio/mc:latest
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://minio:9000 minioadmin minioadmin &&
      mc mb --ignore-existing local/singlish-agent
      "

volumes:
  postgres-data:
  minio-data:
```

Update `README.md`:

```markdown
# Singlish Agent

Demo-first scaffold for the Singlish Speech Intelligence Agent.

## Planned First Slice

- FastAPI API
- Celery worker
- React upload demo
- PostgreSQL, Redis, and MinIO local dependencies

## Start Local Infrastructure

```powershell
docker compose -f infra/docker/docker-compose.yml up -d
```
```

- [ ] **Step 3: Validate the compose configuration**

Run:

```powershell
docker compose -f infra/docker/docker-compose.yml config
```

Expected: PASS and printed config containing `postgres`, `redis`, `minio`, and `createbucket`.

- [ ] **Step 4: Bring the stack up once**

Run:

```powershell
docker compose -f infra/docker/docker-compose.yml up -d
docker compose -f infra/docker/docker-compose.yml ps
```

Expected:
- all services start
- `postgres`, `redis`, and `minio` report running

- [ ] **Step 5: Commit the local infra stack**

Run:

```powershell
git add infra/docker/docker-compose.yml README.md
git commit -m "chore: add local infrastructure stack"
```

Expected: one commit for local dependency orchestration.

### Task 3: Create The Backend Package And A Smoke-Tested `/health` Route

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/src/singlish_agent_api/__init__.py`
- Create: `apps/api/src/singlish_agent_api/main.py`
- Create: `apps/api/src/singlish_agent_api/core/config.py`
- Create: `apps/api/src/singlish_agent_api/core/logging.py`
- Create: `apps/api/src/singlish_agent_api/api/__init__.py`
- Create: `apps/api/src/singlish_agent_api/api/routes/__init__.py`
- Create: `apps/api/src/singlish_agent_api/api/routes/health.py`
- Create: `apps/api/tests/conftest.py`
- Create: `apps/api/tests/integration/test_health.py`

- [ ] **Step 1: Write the failing `/health` test**

Create `apps/api/tests/conftest.py`:

```python
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
```

Create `apps/api/tests/integration/test_health.py`:

```python
from fastapi.testclient import TestClient

from singlish_agent_api.main import app


def test_health_returns_app_status() -> None:
    client = TestClient(app)

    response = client.get("/health")
    body = response.json()

    assert response.status_code == 200
    assert body["services"]["app"] == "ok"
    assert body["status"] in {"ok", "degraded"}
```

- [ ] **Step 2: Run the health test and watch it fail**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_health.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'singlish_agent_api'`.

- [ ] **Step 3: Create the backend package and minimal application**

Create `apps/api/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "singlish-agent-api"
version = "0.1.0"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "pydantic-settings",
  "python-multipart",
  "sqlalchemy[asyncio]",
  "asyncpg",
  "redis",
  "boto3",
  "celery[redis]",
  "structlog"
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

Create `apps/api/src/singlish_agent_api/main.py`:

```python
from fastapi import FastAPI

from singlish_agent_api.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Singlish Agent API")
    app.include_router(health_router)
    return app


app = create_app()
```

Create `apps/api/src/singlish_agent_api/core/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
```

Create `apps/api/src/singlish_agent_api/core/logging.py`:

```python
import logging

import structlog


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )
```

Create `apps/api/src/singlish_agent_api/api/routes/health.py`:

```python
from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "services": {"app": "ok"},
    }
```

Create empty package marker files:

```python
# apps/api/src/singlish_agent_api/__init__.py
# apps/api/src/singlish_agent_api/api/__init__.py
# apps/api/src/singlish_agent_api/api/routes/__init__.py
```

- [ ] **Step 4: Run the health test again and install the package editable**

Run:

```powershell
python -m pip install -e apps/api
python -m pytest apps/api/tests/integration/test_health.py -q
```

Expected:
- editable install succeeds
- pytest reports `1 passed`

- [ ] **Step 5: Commit the backend smoke-test scaffold**

Run:

```powershell
git add apps/api/pyproject.toml apps/api/src apps/api/tests
git commit -m "feat: scaffold backend health endpoint"
```

Expected: one commit for the backend package and basic health route.

### Task 4: Add Job Domain Models And Database Bootstrapping

**Files:**
- Create: `apps/api/src/singlish_agent_api/infrastructure/db/base.py`
- Create: `apps/api/src/singlish_agent_api/infrastructure/db/session.py`
- Create: `apps/api/src/singlish_agent_api/domain/__init__.py`
- Create: `apps/api/src/singlish_agent_api/domain/jobs/__init__.py`
- Create: `apps/api/src/singlish_agent_api/domain/jobs/models.py`
- Create: `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
- Create: `apps/api/src/singlish_agent_api/infrastructure/repositories/jobs.py`
- Create: `apps/api/tests/unit/test_job_status.py`
- Modify: `apps/api/src/singlish_agent_api/core/config.py`
- Modify: `apps/api/src/singlish_agent_api/main.py`

- [ ] **Step 1: Write the failing job transition test**

Create `apps/api/tests/unit/test_job_status.py`:

```python
from singlish_agent_api.domain.jobs.models import JobStatus, can_transition


def test_job_status_allows_expected_forward_transition() -> None:
    assert can_transition(JobStatus.CREATED, JobStatus.UPLOADED) is True
    assert can_transition(JobStatus.UPLOADED, JobStatus.QUEUED) is True
    assert can_transition(JobStatus.QUEUED, JobStatus.PROCESSING) is True
    assert can_transition(JobStatus.PROCESSING, JobStatus.COMPLETED) is True


def test_job_status_blocks_invalid_transition() -> None:
    assert can_transition(JobStatus.CREATED, JobStatus.COMPLETED) is False
```

- [ ] **Step 2: Run the job transition test and watch it fail**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_job_status.py -q
```

Expected: FAIL because `singlish_agent_api.domain.jobs.models` does not exist yet.

- [ ] **Step 3: Implement the job domain and database bootstrap**

Update `apps/api/src/singlish_agent_api/core/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/singlish_agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
```

Create `apps/api/src/singlish_agent_api/infrastructure/db/base.py`:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

Create `apps/api/src/singlish_agent_api/domain/jobs/models.py`:

```python
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from singlish_agent_api.infrastructure.db.base import Base


class JobStatus(StrEnum):
    CREATED = "created"
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.CREATED: {JobStatus.UPLOADED},
    JobStatus.UPLOADED: {JobStatus.QUEUED, JobStatus.FAILED},
    JobStatus.QUEUED: {JobStatus.PROCESSING, JobStatus.FAILED},
    JobStatus.PROCESSING: {JobStatus.COMPLETED, JobStatus.FAILED},
    JobStatus.COMPLETED: set(),
    JobStatus.FAILED: set(),
}


def can_transition(current: JobStatus, target: JobStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    file_name: Mapped[str] = mapped_column(String(255))
    object_key: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default=JobStatus.CREATED.value)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Create `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`:

```python
from datetime import datetime

from pydantic import BaseModel


class JobDetailResponse(BaseModel):
    job_id: str
    file_name: str
    status: str
    result_summary: str | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
```

Create `apps/api/src/singlish_agent_api/infrastructure/db/session.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from singlish_agent_api.core.config import settings
from singlish_agent_api.infrastructure.db.base import Base


engine = create_async_engine(settings.database_url, future=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
```

Create `apps/api/src/singlish_agent_api/infrastructure/repositories/jobs.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.models import Job, JobStatus, can_transition


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, file_name: str, object_key: str) -> Job:
        job = Job(file_name=file_name, object_key=object_key, status=JobStatus.CREATED.value)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def transition(self, job: Job, target: JobStatus) -> Job:
        current = JobStatus(job.status)
        if not can_transition(current, target):
            raise ValueError(f"invalid transition: {current} -> {target}")
        job.status = target.value
        await self.session.commit()
        await self.session.refresh(job)
        return job
```

Update `apps/api/src/singlish_agent_api/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from singlish_agent_api.api.routes.health import router as health_router
from singlish_agent_api.infrastructure.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Singlish Agent API", lifespan=lifespan)
    app.include_router(health_router)
    return app


app = create_app()
```

Create package marker files:

```python
# apps/api/src/singlish_agent_api/domain/__init__.py
# apps/api/src/singlish_agent_api/domain/jobs/__init__.py
```

- [ ] **Step 4: Run the unit test again**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_job_status.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit the job domain and db bootstrap**

Run:

```powershell
git add apps/api/src/singlish_agent_api apps/api/tests/unit/test_job_status.py
git commit -m "feat: add job domain model and db bootstrap"
```

Expected: one commit for core job state and database setup.

### Task 5: Expand `/health` To Check Database, Redis, And Object Storage

**Files:**
- Create: `apps/api/src/singlish_agent_api/infrastructure/cache/__init__.py`
- Create: `apps/api/src/singlish_agent_api/infrastructure/cache/redis.py`
- Create: `apps/api/src/singlish_agent_api/infrastructure/storage/__init__.py`
- Create: `apps/api/src/singlish_agent_api/infrastructure/storage/client.py`
- Modify: `apps/api/src/singlish_agent_api/core/config.py`
- Modify: `apps/api/src/singlish_agent_api/api/routes/health.py`
- Create: `apps/api/tests/integration/test_health_dependencies.py`

- [ ] **Step 1: Write a failing test for the richer health payload**

Create `apps/api/tests/integration/test_health_dependencies.py`:

```python
from fastapi.testclient import TestClient

import singlish_agent_api.api.routes.health as health_module
from singlish_agent_api.main import app


def test_health_reports_all_service_checks(monkeypatch) -> None:
    async def ok() -> bool:
        return True

    monkeypatch.setattr(health_module, "check_database", ok)
    monkeypatch.setattr(health_module, "check_redis", ok)
    monkeypatch.setattr(health_module, "check_storage", ok)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "services": {
            "app": "ok",
            "database": "ok",
            "redis": "ok",
            "object_storage": "ok",
        },
    }
```

- [ ] **Step 2: Run the richer health test and watch it fail**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_health_dependencies.py -q
```

Expected: FAIL because `check_database`, `check_redis`, and `check_storage` are not defined.

- [ ] **Step 3: Implement health checks for all infrastructure services**

Update `apps/api/src/singlish_agent_api/core/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/singlish_agent"
    redis_url: str = "redis://127.0.0.1:6379/0"
    s3_endpoint_url: str = "http://127.0.0.1:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "singlish-agent"
    s3_region: str = "us-east-1"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
```

Create `apps/api/src/singlish_agent_api/infrastructure/cache/redis.py`:

```python
from redis.asyncio import Redis

from singlish_agent_api.core.config import settings


def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def check_redis() -> bool:
    client = get_redis_client()
    try:
        return bool(await client.ping())
    finally:
        await client.aclose()
```

Create `apps/api/src/singlish_agent_api/infrastructure/storage/client.py`:

```python
import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from singlish_agent_api.core.config import settings


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


async def check_storage() -> bool:
    try:
        get_s3_client().head_bucket(Bucket=settings.s3_bucket)
        return True
    except (BotoCoreError, ClientError):
        return False
```

Update `apps/api/src/singlish_agent_api/api/routes/health.py`:

```python
from fastapi import APIRouter
from sqlalchemy import text

from singlish_agent_api.infrastructure.cache.redis import check_redis
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.storage.client import check_storage


router = APIRouter()


async def check_database() -> bool:
    async with AsyncSessionFactory() as session:
        await session.execute(text("SELECT 1"))
        return True


@router.get("/health")
async def health() -> dict[str, object]:
    database_ok = await check_database()
    redis_ok = await check_redis()
    storage_ok = await check_storage()

    services = {
        "app": "ok",
        "database": "ok" if database_ok else "error",
        "redis": "ok" if redis_ok else "error",
        "object_storage": "ok" if storage_ok else "error",
    }

    overall = "ok" if all(value == "ok" for value in services.values()) else "degraded"

    return {
        "status": overall,
        "services": services,
    }
```

Create package marker files:

```python
# apps/api/src/singlish_agent_api/infrastructure/cache/__init__.py
# apps/api/src/singlish_agent_api/infrastructure/storage/__init__.py
```

- [ ] **Step 4: Run the health test suite**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_health.py apps/api/tests/integration/test_health_dependencies.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit the infrastructure health checks**

Run:

```powershell
git add apps/api/src/singlish_agent_api apps/api/tests/integration/test_health_dependencies.py
git commit -m "feat: add dependency-aware health checks"
```

Expected: one commit for health checks across db, redis, and object storage.

### Task 6: Implement Job Creation And Job Retrieval API Endpoints

**Files:**
- Create: `apps/api/src/singlish_agent_api/api/routes/jobs.py`
- Create: `apps/api/src/singlish_agent_api/domain/jobs/service.py`
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
- Modify: `apps/api/src/singlish_agent_api/infrastructure/repositories/jobs.py`
- Modify: `apps/api/src/singlish_agent_api/main.py`
- Create: `apps/api/tests/integration/test_jobs_api.py`

- [ ] **Step 1: Write failing tests for `POST /api/v1/jobs` and `GET /api/v1/jobs/{job_id}`**

Create `apps/api/tests/integration/test_jobs_api.py`:

```python
from io import BytesIO

from fastapi.testclient import TestClient

from singlish_agent_api.main import app


def test_create_job_returns_created_job(monkeypatch) -> None:
    from singlish_agent_api.api.routes import jobs as jobs_module

    stored_keys: list[str] = []
    queued_job_ids: list[str] = []

    class FakeStorage:
        async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
            stored_keys.append(object_key)

    class FakeQueue:
        async def enqueue(self, job_id: str) -> None:
            queued_job_ids.append(job_id)

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

    class FakeStorage:
        async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
            return None

    class FakeQueue:
        async def enqueue(self, job_id: str) -> None:
            return None

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
```

- [ ] **Step 2: Run the jobs API tests and watch them fail**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_jobs_api.py -q
```

Expected: FAIL because `jobs` route module and schemas do not exist yet.

- [ ] **Step 3: Implement the jobs route, schemas, and service orchestration**

Update `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`:

```python
from datetime import datetime

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: str
    file_name: str
    status: str
    created_at: datetime


class JobDetailResponse(BaseModel):
    job_id: str
    file_name: str
    status: str
    result_summary: str | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
```

Update `apps/api/src/singlish_agent_api/infrastructure/repositories/jobs.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.models import Job, JobStatus, can_transition


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, file_name: str, object_key: str) -> Job:
        job = Job(file_name=file_name, object_key=object_key, status=JobStatus.CREATED.value)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get(self, job_id: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def transition(self, job: Job, target: JobStatus) -> Job:
        current = JobStatus(job.status)
        if not can_transition(current, target):
            raise ValueError(f"invalid transition: {current} -> {target}")
        job.status = target.value
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def set_result(self, job: Job, *, summary: str) -> Job:
        job.result_summary = summary
        await self.session.commit()
        await self.session.refresh(job)
        return job
```

Create `apps/api/src/singlish_agent_api/domain/jobs/service.py`:

```python
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
    job = await repository.transition(job, JobStatus.UPLOADED)

    object_key = f"raw/{job.id}/{safe_name}"
    content = await upload_file.read()
    await storage.upload(object_key=object_key, content=content, content_type=upload_file.content_type or "application/octet-stream")

    job.object_key = object_key
    await session.commit()
    await session.refresh(job)

    job = await repository.transition(job, JobStatus.QUEUED)
    await queue.enqueue(job.id)
    return job.id, job.file_name, job.status, job.created_at
```

Create `apps/api/src/singlish_agent_api/api/routes/jobs.py`:

```python
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
```

Update `apps/api/src/singlish_agent_api/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from singlish_agent_api.api.routes.health import router as health_router
from singlish_agent_api.api.routes.jobs import router as jobs_router
from singlish_agent_api.infrastructure.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Singlish Agent API", lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(jobs_router)
    return app


app = create_app()
```

- [ ] **Step 4: Run the jobs API tests again**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_jobs_api.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit the jobs API slice**

Run:

```powershell
git add apps/api/src/singlish_agent_api apps/api/tests/integration/test_jobs_api.py
git commit -m "feat: add jobs create and detail endpoints"
```

Expected: one commit for upload-driven job creation and retrieval.

### Task 7: Replace Noop Storage And Queue With MinIO And Celery

**Files:**
- Create: `apps/api/src/singlish_agent_api/worker/__init__.py`
- Create: `apps/api/src/singlish_agent_api/worker/celery_app.py`
- Create: `apps/api/src/singlish_agent_api/worker/tasks.py`
- Create: `apps/api/src/singlish_agent_api/worker/run_worker.py`
- Modify: `apps/api/src/singlish_agent_api/core/config.py`
- Modify: `apps/api/src/singlish_agent_api/api/routes/jobs.py`
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/service.py`
- Modify: `apps/api/src/singlish_agent_api/infrastructure/storage/client.py`
- Create: `apps/api/tests/integration/test_worker_task.py`

- [ ] **Step 1: Write the failing worker task integration test**

Create `apps/api/tests/integration/test_worker_task.py`:

```python
import asyncio

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.worker.tasks import process_job


def test_process_job_marks_job_completed() -> None:
    async def scenario() -> str:
        async with AsyncSessionFactory() as session:
            repository = JobRepository(session)
            job = await repository.create(file_name="sample.wav", object_key="raw/sample.wav")
            job = await repository.transition(job, JobStatus.UPLOADED)
            job = await repository.transition(job, JobStatus.QUEUED)
            process_job(job.id)
            refreshed = await repository.get(job.id)
            assert refreshed is not None
            return refreshed.status

    assert asyncio.run(scenario()) == JobStatus.COMPLETED.value
```

- [ ] **Step 2: Run the worker task test and watch it fail**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_worker_task.py -q
```

Expected: FAIL because the worker module does not exist yet.

- [ ] **Step 3: Implement MinIO uploads, Celery wiring, and the fake processor**

Update `apps/api/src/singlish_agent_api/core/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/singlish_agent"
    redis_url: str = "redis://127.0.0.1:6379/0"
    s3_endpoint_url: str = "http://127.0.0.1:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "singlish-agent"
    s3_region: str = "us-east-1"
    celery_task_always_eager: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
```

Update `apps/api/src/singlish_agent_api/infrastructure/storage/client.py`:

```python
import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from singlish_agent_api.core.config import settings


class ObjectStorageService:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )

    async def upload(self, *, object_key: str, content: bytes, content_type: str) -> None:
        self.client.put_object(
            Bucket=settings.s3_bucket,
            Key=object_key,
            Body=content,
            ContentType=content_type,
        )


def get_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


async def check_storage() -> bool:
    try:
        get_s3_client().head_bucket(Bucket=settings.s3_bucket)
        return True
    except (BotoCoreError, ClientError):
        return False
```

Create `apps/api/src/singlish_agent_api/worker/celery_app.py`:

```python
from celery import Celery

from singlish_agent_api.core.config import settings


celery_app = Celery(
    "singlish_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_store_eager_result=True,
)
```

Create `apps/api/src/singlish_agent_api/worker/tasks.py`:

```python
import asyncio
from datetime import datetime, timezone

from singlish_agent_api.domain.jobs.models import JobStatus
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.worker.celery_app import celery_app


@celery_app.task(name="singlish_agent.process_job")
def process_job(job_id: str) -> None:
    async def scenario() -> None:
        async with AsyncSessionFactory() as session:
            repository = JobRepository(session)
            job = await repository.get(job_id)
            if job is None:
                raise ValueError(f"job not found: {job_id}")
            job = await repository.transition(job, JobStatus.PROCESSING)
            job.result_summary = "Fake transcript completed successfully."
            job.processed_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(job)
            await repository.transition(job, JobStatus.COMPLETED)

    asyncio.run(scenario())
```

Create `apps/api/src/singlish_agent_api/worker/run_worker.py`:

```python
from singlish_agent_api.worker.celery_app import celery_app


def main() -> None:
    celery_app.worker_main(["worker", "--loglevel=INFO", "--pool=solo"])


if __name__ == "__main__":
    main()
```

Update `apps/api/src/singlish_agent_api/domain/jobs/service.py`:

```python
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
    job = await repository.transition(job, JobStatus.UPLOADED)

    object_key = f"raw/{job.id}/{safe_name}"
    content = await upload_file.read()
    await storage.upload(object_key=object_key, content=content, content_type=upload_file.content_type or "application/octet-stream")

    job.object_key = object_key
    await session.commit()
    await session.refresh(job)

    job = await repository.transition(job, JobStatus.QUEUED)
    await queue.enqueue(job.id)
    return job.id, job.file_name, job.status, job.created_at
```

Update `apps/api/src/singlish_agent_api/api/routes/jobs.py`:

```python
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from singlish_agent_api.domain.jobs.schemas import JobCreateResponse, JobDetailResponse
from singlish_agent_api.domain.jobs.service import create_job_from_upload
from singlish_agent_api.infrastructure.db.session import AsyncSessionFactory
from singlish_agent_api.infrastructure.repositories.jobs import JobRepository
from singlish_agent_api.infrastructure.storage.client import ObjectStorageService
from singlish_agent_api.worker.tasks import process_job


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class CeleryQueue:
    async def enqueue(self, job_id: str) -> None:
        process_job.delay(job_id)


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session


def get_storage() -> ObjectStorageService:
    return ObjectStorageService()


def get_queue() -> CeleryQueue:
    return CeleryQueue()


@router.post("", response_model=JobCreateResponse, status_code=201)
async def create_job(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorageService = Depends(get_storage),
    queue: CeleryQueue = Depends(get_queue),
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
async def get_job(job_id: str, session: AsyncSession = Depends(get_session)) -> JobDetailResponse:
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
```

Create package marker file:

```python
# apps/api/src/singlish_agent_api/worker/__init__.py
```

- [ ] **Step 4: Run the worker test again**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_worker_task.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the worker and object storage wiring**

Run:

```powershell
git add apps/api/src/singlish_agent_api apps/api/tests/integration/test_worker_task.py
git commit -m "feat: wire celery worker and object storage"
```

Expected: one commit for fake async processing over real infrastructure boundaries.

### Task 8: Create The Web App Workspace And Health Panel

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/vite.config.ts`
- Create: `apps/web/index.html`
- Create: `apps/web/src/main.tsx`
- Create: `apps/web/src/app/App.tsx`
- Create: `apps/web/src/shared/api/client.ts`
- Create: `apps/web/src/features/health/api.ts`
- Create: `apps/web/src/features/health/HealthPanel.tsx`
- Create: `apps/web/src/test/setup.ts`
- Create: `apps/web/src/features/health/HealthPanel.test.tsx`
- Create: `packages/contracts/package.json`
- Create: `packages/contracts/src/job.ts`

- [ ] **Step 1: Write the failing frontend health panel test**

Create `apps/web/src/features/health/HealthPanel.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";

import { HealthPanel } from "./HealthPanel";


test("renders service health rows", () => {
  render(
    <HealthPanel
      health={{
        status: "ok",
        services: {
          app: "ok",
          database: "ok",
          redis: "ok",
          object_storage: "ok",
        },
      }}
    />,
  );

  expect(screen.getByText("database")).toBeInTheDocument();
  expect(screen.getByText("object_storage")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the frontend test and watch it fail**

Run:

```powershell
npm run test --workspace @singlish-agent/web -- --run
```

Expected: FAIL because the web workspace does not exist yet.

- [ ] **Step 3: Create the web workspace, contracts package, and health panel**

Create `packages/contracts/package.json`:

```json
{
  "name": "@singlish-agent/contracts",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./src/job.ts"
  }
}
```

Create `packages/contracts/src/job.ts`:

```ts
export type HealthResponse = {
  status: "ok" | "degraded";
  services: Record<string, "ok" | "error">;
};

export type JobCreateResponse = {
  job_id: string;
  file_name: string;
  status: string;
  created_at: string;
};

export type JobDetailResponse = {
  job_id: string;
  file_name: string;
  status: string;
  result_summary: string | null;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
};
```

Create `apps/web/package.json`:

```json
{
  "name": "@singlish-agent/web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "test": "vitest"
  },
  "dependencies": {
    "@singlish-agent/contracts": "0.1.0",
    "react": "^19.1.0",
    "react-dom": "^19.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.3",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.0.1",
    "@types/react": "^19.0.10",
    "@types/react-dom": "^19.0.4",
    "jsdom": "^25.0.1",
    "typescript": "^5.6.3",
    "vite": "^6.0.0",
    "vitest": "^2.1.3"
  }
}
```

Create `apps/web/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "Bundler",
    "allowImportingTsExtensions": false,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "strict": true,
    "baseUrl": "./src",
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src"]
}
```

Create `apps/web/vite.config.ts`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";


export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
  },
});
```

Create `apps/web/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Singlish Agent Demo</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `apps/web/src/shared/api/client.ts`:

```ts
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";


export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}
```

Create `apps/web/src/features/health/api.ts`:

```ts
import type { HealthResponse } from "@singlish-agent/contracts";

import { apiFetch } from "../../shared/api/client";


export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}
```

Create `apps/web/src/features/health/HealthPanel.tsx`:

```tsx
import type { HealthResponse } from "@singlish-agent/contracts";


type Props = {
  health: HealthResponse | null;
};


export function HealthPanel({ health }: Props) {
  if (!health) {
    return <section><h2>Health</h2><p>Loading...</p></section>;
  }

  return (
    <section>
      <h2>Health</h2>
      <p>overall: {health.status}</p>
      <ul>
        {Object.entries(health.services).map(([name, status]) => (
          <li key={name}>
            <strong>{name}</strong>: {status}
          </li>
        ))}
      </ul>
    </section>
  );
}
```

Create `apps/web/src/app/App.tsx`:

```tsx
import { useEffect, useState } from "react";
import type { HealthResponse } from "@singlish-agent/contracts";

import { fetchHealth } from "../features/health/api";
import { HealthPanel } from "../features/health/HealthPanel";


export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => {
      setHealth({
        status: "degraded",
        services: {
          app: "error",
          database: "error",
          redis: "error",
          object_storage: "error",
        },
      });
    });
  }, []);

  return (
    <main>
      <h1>Singlish Agent Demo</h1>
      <HealthPanel health={health} />
    </main>
  );
}
```

Create `apps/web/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./app/App";


ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

Create `apps/web/src/test/setup.ts`:

```ts
import "@testing-library/jest-dom";
```

- [ ] **Step 4: Install workspace dependencies and run the frontend checks**

Run:

```powershell
npm install
npm run test --workspace @singlish-agent/web -- --run
npm run build --workspace @singlish-agent/web
```

Expected:
- `npm install` completes successfully
- frontend test passes
- Vite build succeeds

- [ ] **Step 5: Commit the web workspace and contracts package**

Run:

```powershell
git add apps/web packages/contracts package.json
git commit -m "feat: scaffold web workspace and health panel"
```

Expected: one commit for the web app and shared TypeScript contracts.

### Task 9: Add Upload UI, Job Polling, And Final Runbook

**Files:**
- Create: `apps/web/src/features/jobs/api.ts`
- Create: `apps/web/src/features/jobs/UploadPanel.tsx`
- Create: `apps/web/src/features/jobs/UploadPanel.test.tsx`
- Modify: `apps/web/src/app/App.tsx`
- Modify: `README.md`

- [ ] **Step 1: Write the failing upload panel test**

Create `apps/web/src/features/jobs/UploadPanel.test.tsx`:

```tsx
import { fireEvent, render, screen } from "@testing-library/react";

import { UploadPanel } from "./UploadPanel";


test("submits the selected file", async () => {
  const submitted: File[] = [];

  render(<UploadPanel onUpload={async (file) => submitted.push(file)} />);

  const input = screen.getByLabelText("Audio file");
  const button = screen.getByRole("button", { name: "Upload" });
  const file = new File(["demo"], "sample.wav", { type: "audio/wav" });

  fireEvent.change(input, { target: { files: [file] } });
  fireEvent.click(button);

  expect(submitted).toHaveLength(1);
  expect(submitted[0].name).toBe("sample.wav");
});
```

- [ ] **Step 2: Run the upload panel test and watch it fail**

Run:

```powershell
npm run test --workspace @singlish-agent/web -- --run
```

Expected: FAIL because `UploadPanel` and the jobs feature do not exist yet.

- [ ] **Step 3: Implement upload and polling in the web app**

Create `apps/web/src/features/jobs/api.ts`:

```ts
import type { JobCreateResponse, JobDetailResponse } from "@singlish-agent/contracts";

import { API_BASE_URL, apiFetch } from "../../shared/api/client";


export async function createJob(file: File): Promise<JobCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/v1/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`create job failed: ${response.status}`);
  }

  return (await response.json()) as JobCreateResponse;
}


export function getJob(jobId: string): Promise<JobDetailResponse> {
  return apiFetch<JobDetailResponse>(`/api/v1/jobs/${jobId}`);
}
```

Create `apps/web/src/features/jobs/UploadPanel.tsx`:

```tsx
import { FormEvent, useState } from "react";


type Props = {
  onUpload: (file: File) => Promise<void>;
};


export function UploadPanel({ onUpload }: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      return;
    }
    await onUpload(selectedFile);
  }

  return (
    <section>
      <h2>Create Job</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Audio file
          <input
            aria-label="Audio file"
            type="file"
            accept=".wav,.mp3,.m4a,.flac"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <button type="submit">Upload</button>
      </form>
    </section>
  );
}
```

Update `apps/web/src/app/App.tsx`:

```tsx
import { useEffect, useState } from "react";
import type { HealthResponse, JobCreateResponse, JobDetailResponse } from "@singlish-agent/contracts";

import { fetchHealth } from "../features/health/api";
import { HealthPanel } from "../features/health/HealthPanel";
import { createJob, getJob } from "../features/jobs/api";
import { UploadPanel } from "../features/jobs/UploadPanel";


export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [createdJob, setCreatedJob] = useState<JobCreateResponse | null>(null);
  const [jobDetail, setJobDetail] = useState<JobDetailResponse | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => {
      setHealth({
        status: "degraded",
        services: {
          app: "error",
          database: "error",
          redis: "error",
          object_storage: "error",
        },
      });
    });
  }, []);

  useEffect(() => {
    if (!createdJob) {
      return;
    }

    const intervalId = window.setInterval(() => {
      getJob(createdJob.job_id).then(setJobDetail).catch(() => undefined);
    }, 1500);

    return () => window.clearInterval(intervalId);
  }, [createdJob]);

  async function handleUpload(file: File) {
    const created = await createJob(file);
    setCreatedJob(created);
    const detail = await getJob(created.job_id);
    setJobDetail(detail);
  }

  return (
    <main>
      <h1>Singlish Agent Demo</h1>
      <HealthPanel health={health} />
      <UploadPanel onUpload={handleUpload} />

      {createdJob ? (
        <section>
          <h2>Latest Job</h2>
          <p>job_id: {createdJob.job_id}</p>
          <p>status: {jobDetail?.status ?? createdJob.status}</p>
          <p>file_name: {createdJob.file_name}</p>
          <p>result_summary: {jobDetail?.result_summary ?? "pending"}</p>
        </section>
      ) : null}
    </main>
  );
}
```

Update `README.md`:

```markdown
# Singlish Agent

Demo-first scaffold for the Singlish Speech Intelligence Agent.

## Planned First Slice

- FastAPI API
- Celery worker
- React upload demo
- PostgreSQL, Redis, and MinIO local dependencies

## One-Time Setup

```powershell
conda activate singlish-agent
python -m pip install -e apps/api
npm install
```

## Start Local Infrastructure

```powershell
docker compose -f infra/docker/docker-compose.yml up -d
```

## Start The Backend API

```powershell
python -m uvicorn singlish_agent_api.main:app --app-dir apps/api/src --reload --host 127.0.0.1 --port 8000
```

## Start The Worker

```powershell
python -m singlish_agent_api.worker.run_worker
```

## Start The Web App

```powershell
npm run dev --workspace @singlish-agent/web
```

## Verification Checklist

1. Open the Vite URL shown in the terminal.
2. Confirm the health panel shows `ok` for app, database, redis, and object storage.
3. Upload a small `.wav` file.
4. Confirm the UI shows the new `job_id`.
5. Wait for polling to refresh the job status to `completed`.
6. Confirm the fake result summary appears.
```

- [ ] **Step 4: Run the final frontend checks and smoke verification**

Run:

```powershell
npm run test --workspace @singlish-agent/web -- --run
npm run build --workspace @singlish-agent/web
python -m pytest apps/api/tests/unit apps/api/tests/integration -q
```

Expected:
- frontend tests pass
- frontend build succeeds
- backend unit and integration tests pass

- [ ] **Step 5: Commit the upload UI and final runbook**

Run:

```powershell
git add apps/web README.md
git commit -m "feat: add upload demo and local runbook"
```

Expected: one commit for the demo UI and full local usage instructions.
