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

For real offline ASR, start the worker from the `singlish-agent` conda environment so it can load `faster-whisper` and related audio dependencies.

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
6. Confirm the job reaches `completed` and a transcription provider is shown in the result details.

See [docs/启动停止手册.md](./docs/启动停止手册.md) for a fuller start/stop and troubleshooting runbook.
