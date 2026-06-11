# Monorepo Scaffold Design

Date: 2026-06-10
Topic: Demo-first monorepo scaffold for Singlish Speech Intelligence Agent
Status: Drafted after interactive design approval

## Goal

Build the first runnable project foundation for the Singlish Speech Intelligence Agent as a demo-first monorepo. This scaffold should support immediate development of the offline MVP while preserving a clean path toward realtime transcription, RAG, and the bounded agent described in [project-plan.md](/E:/githubitem/Singlish-agent/project-plan.md).

The scaffold must optimize for:

- fast local startup on the user's existing `conda` environment
- visible end-to-end behavior rather than empty directories
- clear backend and frontend boundaries
- a safe upgrade path toward async processing, storage, and later shared contracts

## Chosen Approach

Use a balanced monorepo:

```text
apps/
  api/
  web/
packages/
  contracts/
  config/
infra/
  docker/
docs/
  superpowers/specs/
```

This is intentionally between two extremes:

- not as thin as a two-app repo with no shared package space
- not as heavy as a full workspace with `ui`, `sdk`, and multiple cross-cutting packages on day one

## Why This Approach

This project will eventually need shared API contracts, environment conventions, and cross-service documentation. A pure `apps/api` + `apps/web` layout would start quickly but would likely duplicate schema and configuration conventions almost immediately.

At the same time, a heavier workspace would introduce package maintenance overhead before the project has enough real behavior to justify it. The balanced monorepo leaves room for growth without making the scaffold itself the main thing being maintained.

## Scope Of This Scaffold

This scaffold is limited to the first meaningful runnable slice. It will not implement real ASR, realtime streaming, or Agent orchestration yet.

It will include:

- FastAPI application skeleton
- Celery worker skeleton
- React + Vite frontend skeleton
- local Docker Compose dependencies for PostgreSQL, Redis, and MinIO
- upload-to-job demo flow
- health checks across core infrastructure
- one fake async processing job that proves the queue and status model work

It will not include:

- real audio preprocessing
- faster-whisper integration
- VAD
- realtime WebSocket transcription
- LangGraph Agent flow
- pgvector retrieval
- authentication or multi-user isolation

## Architecture Decision

### Repository Structure

`apps/api` contains the backend runtime, API routes, worker, persistence, and backend tests.

`apps/web` contains the React demo UI.

`packages/contracts` is reserved for minimal shared contracts that the frontend and backend both need. At scaffold stage this should stay intentionally small, for example:

- health response shape
- job creation response shape
- job status enum or status literals

`packages/config` is reserved for shared repo-level conventions only if they become real. In this scaffold it should stay empty or contain only a short README describing its future purpose.

`infra/docker` contains local dependency orchestration only. The API, worker, and web app remain local processes for a better debugging loop.

### Backend Module Shape

The backend should be organized by capability boundary, not by generic utility folders.

Target structure:

```text
apps/api/
  src/singlish_agent_api/
    main.py
    core/
      config.py
      logging.py
    api/
      routes/
        health.py
        jobs.py
    domain/
      jobs/
        models.py
        schemas.py
        service.py
    infrastructure/
      db/
      cache/
      storage/
      queue/
      repositories/
    worker/
      celery_app.py
      tasks.py
  tests/
    unit/
    integration/
```

This keeps domain logic near its own schemas and services, and gives future modules like `audio`, `realtime`, and `agent` a natural place to grow.

### Frontend Module Shape

The frontend should start with a feature-oriented structure:

```text
apps/web/
  src/
    app/
    pages/
    features/health/
    features/jobs/
    shared/api/
    shared/ui/
```

The first page is a simple demo page that:

- checks API health
- uploads a file
- shows created job metadata
- polls or refreshes job status

## Runtime And Tooling Decisions

### Python Runtime

Keep Python aligned with the existing `environment.yml` and the user's existing `conda` environment. Do not introduce Poetry, uv, or another competing Python environment manager in this phase.

The backend should run with plain Python module entry points, for example:

- `python -m singlish_agent_api.main`
- `python -m singlish_agent_api.worker.celery_app` or the equivalent Celery command bound to the module

### Frontend Package Management

Use `npm workspaces` at the repository root. This is enough to support the monorepo without adding extra package-manager complexity.

Do not introduce `pnpm`, Turborepo, or Nx in this scaffold phase.

### Local Infrastructure

Use Docker Compose only for infrastructure dependencies:

- PostgreSQL
- Redis
- MinIO

Do not containerize the API, worker, or frontend for the primary local developer loop yet. That would slow iteration and complicate debugging on Windows.

## First Runnable Slice

The first slice should prove the backbone of the future system, not just the shape of the folders.

### User Flow

1. Start PostgreSQL, Redis, and MinIO with Docker Compose.
2. Start the FastAPI app locally.
3. Start the Celery worker locally.
4. Start the React app locally.
5. Open the web page.
6. The page calls `/health` and renders infrastructure status.
7. The user uploads an audio file.
8. The API stores the file locally or in object storage, creates a `job` record, and enqueues a fake processing task.
9. The worker updates the job through a minimal state sequence.
10. The frontend shows the created job and then reflects the final status after polling or refresh.

### Initial Job State Model

The scaffold should use a trimmed version of the real offline lifecycle so it already matches future design intent:

```text
created -> uploaded -> queued -> processing -> completed
```

This is deliberately simpler than the full planned production flow:

```text
created -> uploaded -> queued -> preprocessing -> transcribing
-> normalizing -> generating_report -> completed
```

The scaffold keeps the state machine understandable while preserving a clear upgrade path.

## API Surface For The Scaffold

The scaffold should expose:

- `GET /health`
- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`

Optional if low effort:

- `GET /api/v1/jobs`

### `GET /health`

Returns a small structured health payload with:

- app status
- database status
- redis status
- object storage status

### `POST /api/v1/jobs`

Accepts one uploaded file and returns:

- `job_id`
- `status`
- uploaded file metadata
- created timestamp

The endpoint does not yet run real audio analysis. It only validates the upload enough to support the demo flow and then schedules a fake background task.

### `GET /api/v1/jobs/{job_id}`

Returns:

- job metadata
- current status
- timestamps
- a deterministic fake result payload when completed, such as a fixed summary string and processed timestamp

## Storage Decision For The Scaffold

The scaffold may use either:

- local filesystem for uploaded demo files plus PostgreSQL metadata
- or MinIO immediately for stored uploads if the implementation cost remains small

Recommendation: use MinIO in the API path if it can be wired cleanly in this pass, because object storage is already in the long-term design. If that path becomes too expensive during implementation, local disk is an acceptable temporary fallback as long as the storage access is hidden behind a storage abstraction.

## Testing Strategy For This Phase

Keep testing targeted and high-signal.

### Backend Unit Tests

- settings loading
- job schema validation
- job status transition rules

### Backend Integration Tests

- `/health`
- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`

### Worker Integration Test

- fake async task updates a queued job to completed

### Frontend Testing

Do not spend this phase on deep frontend unit coverage. Preserve a structure that can accept Playwright later. A frontend smoke test for successful job creation is a nice-to-have, not part of the required acceptance criteria for this scaffold.

## Files Expected From This Scaffold

### Repository Root

- `package.json`
- `.gitignore`
- `.env.example`
- `README.md`

### Backend

- FastAPI entrypoint
- config and logging modules
- health and jobs routes
- SQLAlchemy base setup
- repository or persistence layer for jobs
- Celery app and fake task
- pytest configuration

### Frontend

- Vite React app
- simple upload/status page
- API client utilities
- basic styling

### Infrastructure

- `infra/docker/docker-compose.yml`

## Acceptance Criteria

The scaffold is successful when all of the following are true:

- the repo has a working monorepo structure with `apps`, `packages`, and `infra`
- the API, worker, and web app can each start locally on Windows
- Docker Compose starts PostgreSQL, Redis, and MinIO successfully
- the frontend can reach the API health endpoint
- the upload flow creates a job and shows its status
- the background worker transitions a fake job to completed
- the structure leaves a clear path for offline ASR work without major reorganization

## Deferred Follow-Up

Once this scaffold is complete, the next implementation planning step should break follow-up work into at least these areas:

- real offline audio ingestion and persistence
- preprocessing and VAD pipeline
- faster-whisper provider integration
- report export
- realtime session foundation
- glossary and normalization foundation

## Risks And Guardrails

- Do not overbuild shared packages before shared behavior exists.
- Do not introduce multiple environment management systems.
- Do not make Docker mandatory for running app code during local development.
- Do not let the fake processing path drift so far from the real job model that future replacement becomes painful.
- Keep infrastructure access behind abstractions where possible so local disk can be swapped for MinIO or vice versa.

## Open Constraints Noted During Design

- The current workspace is not initialized as a git repository, so this spec cannot be committed yet.
- The user already has a `conda` environment and dependencies installed, so the scaffold should respect that setup instead of replacing it.

## Final Recommendation

Start implementation with a demo-first balanced monorepo scaffold:

- `apps/api`
- `apps/web`
- `packages/contracts`
- `packages/config`
- `infra/docker`

The first delivered behavior should be a visible upload-to-job-to-completed loop backed by FastAPI, Celery, PostgreSQL, Redis, MinIO, and a React demo page. That creates a credible foundation for the offline MVP without prematurely implementing the full speech pipeline.
