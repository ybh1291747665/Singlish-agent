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
That same environment is also used for real audio preprocessing metadata extraction, VAD, and bilingual normalization.

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
7. Confirm the structured result card shows VAD counts, Standard English, and Simplified Chinese output.
8. Confirm the transcript segments section shows timestamped timeline items and low-confidence markers when applicable.
9. If low-confidence segments are present, trigger `Reprocess Low-confidence` and confirm the visible status changes.
10. Download a Markdown or SRT export from the Exports section.

## Dataset Status

- There is no formal evaluation dataset committed yet.
- Local dataset scaffolding now lives under `data/`.
- Public redistributable demo assets should go under `examples/`.
- See [docs/evaluation.md](./docs/evaluation.md) and [data/eval/README.md](./data/eval/README.md) for the intended structure.
- The local annotation workflow now starts from `data/eval/manifest.local.template.jsonl` and `data/eval/annotation-guide.md`.

## Generate A Local Evaluation Manifest

Use the `singlish-agent` conda environment so PyAV is available for duration probing:

```powershell
& "C:\Users\12917\.conda\envs\singlish-agent\python.exe" -m singlish_agent_api.scripts.generate_eval_manifest `
  --audio-dir data/eval/audio `
  --dataset-root data/eval `
  --output data/eval/manifest.local.jsonl
```

This command only creates a JSONL scaffold. It does not invent transcripts, translations, or labels.

See [docs/offline-pipeline-notes.md](./docs/offline-pipeline-notes.md) for the new offline VAD, bilingual output, and reprocess notes.
See [docs/启动停止手册.md](./docs/启动停止手册.md) for a fuller start/stop and troubleshooting runbook.
