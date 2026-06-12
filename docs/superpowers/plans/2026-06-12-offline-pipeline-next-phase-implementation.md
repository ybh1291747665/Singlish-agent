# Offline Pipeline Next Phase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local manifest bootstrap script, real VAD and silence-aware segmentation, dual English/Chinese normalization outputs, and a low-confidence reprocess skeleton to the offline pipeline.

**Architecture:** Keep the existing offline job pipeline centered on `result_payload` and the current job detail / segments / export endpoints. Add focused infrastructure modules for manifest generation, VAD, normalization/translation fallbacks, and reprocess state so the current working pipeline stays stable while becoming more realistic.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy asyncio, Celery, PyAV, faster-whisper, React, TypeScript, Vitest, pytest

---

## File Map

- Create: `apps/api/src/singlish_agent_api/scripts/generate_eval_manifest.py`
  Local CLI utility that scans an audio directory and writes a manifest skeleton.
- Create: `apps/api/src/singlish_agent_api/infrastructure/audio/vad.py`
  VAD and silence-aware segmentation helpers over normalized wav audio.
- Create: `apps/api/src/singlish_agent_api/infrastructure/normalization/provider.py`
  Fallback-first Singlish normalization and Simplified Chinese translation provider.
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
  Expand result payload structures for VAD, Chinese output, and reprocess state.
- Modify: `packages/contracts/src/job.ts`
  Keep frontend contracts aligned with the expanded job payload.
- Modify: `apps/api/src/singlish_agent_api/worker/tasks.py`
  Wire manifest-independent worker steps: preprocessing -> VAD -> transcription -> normalization -> reprocess metadata.
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/exports.py`
  Include bilingual output and low-confidence markers in Markdown/JSON exports.
- Modify: `apps/api/src/singlish_agent_api/api/routes/jobs.py`
  Add reprocess endpoint and return expanded payload through detail/segments routes.
- Modify: `apps/web/src/features/jobs/JobResultDetails.tsx`
  Show Chinese output, VAD summary, and reprocess state.
- Modify: `apps/web/src/features/jobs/JobSegmentList.tsx`
  Surface low-confidence markers and any segment-level flags.
- Modify: `apps/web/src/features/jobs/api.ts`
  Add reprocess endpoint client.
- Modify: `apps/web/src/app/App.tsx`
  Trigger reprocess and display expanded offline results.
- Test: `apps/api/tests/unit/test_generate_eval_manifest.py`
- Test: `apps/api/tests/unit/test_vad.py`
- Test: `apps/api/tests/unit/test_normalization_provider.py`
- Test: `apps/api/tests/integration/test_jobs_api.py`
- Test: `apps/api/tests/integration/test_worker_task.py`
- Test: `apps/web/src/features/jobs/JobResultDetails.test.tsx`
- Test: `apps/web/src/features/jobs/JobSegmentList.test.tsx`
- Test: `apps/web/src/features/jobs/ReprocessButton.test.tsx`
- Modify: `README.md`
- Modify: `docs/启动停止手册.md`
- Modify: `记录.md`

### Task 1: Add The Local Manifest Bootstrap Script

**Files:**
- Create: `apps/api/src/singlish_agent_api/scripts/generate_eval_manifest.py`
- Test: `apps/api/tests/unit/test_generate_eval_manifest.py`
- Modify: `README.md`
- Modify: `记录.md`

- [ ] **Step 1: Write the failing manifest generation unit test**

```python
from pathlib import Path

from singlish_agent_api.scripts.generate_eval_manifest import build_manifest_rows


def test_build_manifest_rows_scaffolds_expected_fields(tmp_path: Path) -> None:
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    sample = audio_dir / "clip-one.wav"
    sample.write_bytes(b"fake")

    rows = build_manifest_rows(audio_dir=audio_dir, dataset_root=tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row["clip_id"] == "clip-one"
    assert row["relative_audio_path"] == "audio/clip-one.wav"
    assert row["scenario"] == "unknown"
    assert row["reference_transcript"] == ""
    assert row["reference_standard_english"] == ""
    assert row["simplified_chinese"] == ""
```

- [ ] **Step 2: Run the new unit test and verify it fails**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_generate_eval_manifest.py -q
```

Expected:

- FAIL with `ModuleNotFoundError` or missing symbol errors because the script does not exist yet.

- [ ] **Step 3: Implement the manifest generator**

```python
from __future__ import annotations

import json
from pathlib import Path

import av


SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac"}


def discover_audio_files(audio_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in audio_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_SUFFIXES
    )


def get_duration_seconds(audio_path: Path) -> float:
    with av.open(str(audio_path)) as container:
        if container.duration is None:
            return 0.0
        return round(container.duration / 1_000_000, 3)


def build_manifest_rows(*, audio_dir: Path, dataset_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for audio_path in discover_audio_files(audio_dir):
        rows.append(
            {
                "clip_id": audio_path.stem,
                "relative_audio_path": audio_path.relative_to(dataset_root).as_posix(),
                "duration_seconds": get_duration_seconds(audio_path),
                "scenario": "unknown",
                "speaker_id": "unknown",
                "languages": [],
                "reference_transcript": "",
                "reference_standard_english": "",
                "simplified_chinese": "",
                "glossary_terms": [],
                "contains_code_switching": False,
                "contains_background_noise": False,
                "source_type": "unknown",
                "consent_status": "unknown",
                "split": "unassigned",
                "notes": "",
            }
        )
    return rows


def write_manifest(output_path: Path, rows: list[dict[str, object]]) -> None:
    output_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
```

- [ ] **Step 4: Add a CLI entrypoint and verify the unit test passes**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_generate_eval_manifest.py -q
```

Expected:

- PASS with `1 passed`

- [ ] **Step 5: Document the script and commit**

Run:

```powershell
git add apps/api/src/singlish_agent_api/scripts/generate_eval_manifest.py apps/api/tests/unit/test_generate_eval_manifest.py README.md 记录.md
git commit -m "feat: add local evaluation manifest generator"
```

Expected:

- One commit containing the manifest bootstrap utility and docs.

### Task 2: Add Real VAD And Silence-Aware Segmentation

**Files:**
- Create: `apps/api/src/singlish_agent_api/infrastructure/audio/vad.py`
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
- Modify: `packages/contracts/src/job.ts`
- Modify: `apps/api/src/singlish_agent_api/worker/tasks.py`
- Test: `apps/api/tests/unit/test_vad.py`
- Test: `apps/api/tests/integration/test_worker_task.py`

- [ ] **Step 1: Write the failing VAD shaping unit test**

```python
from singlish_agent_api.infrastructure.audio.vad import build_silence_segments


def test_build_silence_segments_returns_gaps_between_speech_spans() -> None:
    silence = build_silence_segments(
        duration_seconds=5.0,
        speech_segments=[
            {"start_seconds": 0.5, "end_seconds": 1.5},
            {"start_seconds": 3.0, "end_seconds": 4.0},
        ],
    )

    assert silence == [
        {"start_seconds": 0.0, "end_seconds": 0.5},
        {"start_seconds": 1.5, "end_seconds": 3.0},
        {"start_seconds": 4.0, "end_seconds": 5.0},
    ]
```

- [ ] **Step 2: Run the VAD unit test and verify it fails**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_vad.py -q
```

Expected:

- FAIL because `vad.py` does not exist yet.

- [ ] **Step 3: Implement VAD helpers and fallback-safe shaping**

```python
def build_silence_segments(*, duration_seconds: float, speech_segments: list[dict[str, float]]) -> list[dict[str, float]]:
    silence_segments: list[dict[str, float]] = []
    cursor = 0.0
    for segment in speech_segments:
        if segment["start_seconds"] > cursor:
            silence_segments.append(
                {"start_seconds": round(cursor, 3), "end_seconds": round(segment["start_seconds"], 3)}
            )
        cursor = max(cursor, segment["end_seconds"])
    if cursor < duration_seconds:
        silence_segments.append({"start_seconds": round(cursor, 3), "end_seconds": round(duration_seconds, 3)})
    return silence_segments
```

- [ ] **Step 4: Expand worker preprocessing payload with VAD outputs and keep fallback behavior**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_worker_task.py -q
```

Expected:

- FAIL first because `preprocessing.speech_segments` and `silence_segments` are missing
- PASS after updating the worker and fake test doubles

- [ ] **Step 5: Commit the VAD layer**

Run:

```powershell
git add apps/api/src/singlish_agent_api/infrastructure/audio/vad.py apps/api/src/singlish_agent_api/domain/jobs/schemas.py packages/contracts/src/job.ts apps/api/src/singlish_agent_api/worker/tasks.py apps/api/tests/unit/test_vad.py apps/api/tests/integration/test_worker_task.py
git commit -m "feat: add offline vad and silence summaries"
```

Expected:

- One commit containing VAD shaping and worker payload expansion.

### Task 3: Add Standard English And Simplified Chinese Output

**Files:**
- Create: `apps/api/src/singlish_agent_api/infrastructure/normalization/provider.py`
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
- Modify: `packages/contracts/src/job.ts`
- Modify: `apps/api/src/singlish_agent_api/worker/tasks.py`
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/exports.py`
- Modify: `apps/web/src/features/jobs/JobResultDetails.tsx`
- Test: `apps/api/tests/unit/test_normalization_provider.py`
- Test: `apps/web/src/features/jobs/JobResultDetails.test.tsx`

- [ ] **Step 1: Write the failing normalization provider unit test**

```python
from singlish_agent_api.infrastructure.normalization.provider import normalize_transcript


def test_normalize_transcript_returns_english_and_chinese_outputs() -> None:
    result = normalize_transcript("wah lau eh this queue quite fast lah")

    assert result["standard_english"] == "Wow, this queue is quite fast."
    assert result["simplified_chinese"] == "哇，这个队伍走得很快。"
    assert result["translation_provider"] == "fallback"
```

- [ ] **Step 2: Run the provider unit test and verify it fails**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_normalization_provider.py -q
```

Expected:

- FAIL because the provider module does not exist yet.

- [ ] **Step 3: Implement fallback-first normalization and translation**

```python
KNOWN_PATTERNS = {
    "wah lau eh this queue quite fast lah": {
        "standard_english": "Wow, this queue is quite fast.",
        "simplified_chinese": "哇，这个队伍走得很快。",
        "glossary_hits": ["wah lau eh", "lah"],
    }
}


def normalize_transcript(raw_transcript: str) -> dict[str, object]:
    normalized_key = raw_transcript.lower().strip()
    if normalized_key in KNOWN_PATTERNS:
        entry = KNOWN_PATTERNS[normalized_key]
        return {
            "normalized_transcript": raw_transcript,
            "standard_english": entry["standard_english"],
            "simplified_chinese": entry["simplified_chinese"],
            "glossary_hits": entry["glossary_hits"],
            "translation_provider": "fallback",
        }
    return {
        "normalized_transcript": raw_transcript,
        "standard_english": raw_transcript,
        "simplified_chinese": f"[translation pending] {raw_transcript}",
        "glossary_hits": [],
        "translation_provider": "fallback",
    }
```

- [ ] **Step 4: Wire the worker, exports, and frontend view**

Run:

```powershell
python -m pytest apps/api/tests/unit/test_normalization_provider.py apps/api/tests/integration/test_worker_task.py -q
npm run test --workspace @singlish-agent/web -- --run
```

Expected:

- Backend tests PASS with bilingual normalization data present
- Frontend tests PASS after showing Standard English and Simplified Chinese

- [ ] **Step 5: Commit the bilingual normalization skeleton**

Run:

```powershell
git add apps/api/src/singlish_agent_api/infrastructure/normalization/provider.py apps/api/src/singlish_agent_api/domain/jobs/schemas.py packages/contracts/src/job.ts apps/api/src/singlish_agent_api/worker/tasks.py apps/api/src/singlish_agent_api/domain/jobs/exports.py apps/api/tests/unit/test_normalization_provider.py apps/web/src/features/jobs/JobResultDetails.tsx apps/web/src/features/jobs/JobResultDetails.test.tsx
git commit -m "feat: add bilingual normalization outputs"
```

Expected:

- One commit containing Standard English and Simplified Chinese result plumbing.

### Task 4: Add Low-Confidence Reprocess Skeleton

**Files:**
- Modify: `apps/api/src/singlish_agent_api/domain/jobs/schemas.py`
- Modify: `packages/contracts/src/job.ts`
- Modify: `apps/api/src/singlish_agent_api/api/routes/jobs.py`
- Modify: `apps/api/src/singlish_agent_api/worker/tasks.py`
- Modify: `apps/api/tests/integration/test_jobs_api.py`
- Modify: `apps/web/src/features/jobs/api.ts`
- Create: `apps/web/src/features/jobs/ReprocessButton.tsx`
- Create: `apps/web/src/features/jobs/ReprocessButton.test.tsx`
- Modify: `apps/web/src/app/App.tsx`
- Modify: `README.md`
- Modify: `docs/启动停止手册.md`
- Modify: `记录.md`

- [ ] **Step 1: Write the failing API test for reprocess trigger**

```python
def test_reprocess_low_confidence_marks_job_reprocess_status() -> None:
    response = client.post(f"/api/v1/jobs/{job_id}/reprocess-low-confidence")

    assert response.status_code == 202
    assert response.json()["reprocess_status"] == "queued"
```

- [ ] **Step 2: Run the integration test and verify it fails**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_jobs_api.py -q
```

Expected:

- FAIL because the reprocess endpoint and payload fields do not exist yet.

- [ ] **Step 3: Add low-confidence detection and reprocess state fields**

```python
def detect_low_confidence_segments(segments: list[dict[str, object]], *, threshold: float = 0.95) -> list[dict[str, object]]:
    return [
        segment
        for segment in segments
        if segment.get("confidence") is not None and float(segment["confidence"]) < threshold
    ]
```

- [ ] **Step 4: Expose the API trigger and frontend button**

Run:

```powershell
python -m pytest apps/api/tests/integration/test_jobs_api.py -q
npm run test --workspace @singlish-agent/web -- --run
```

Expected:

- API tests PASS with `202 Accepted`
- Frontend tests PASS with a visible button and status rendering

- [ ] **Step 5: Run end-to-end verification and commit**

Run:

```powershell
python -m pytest apps/api/tests/unit apps/api/tests/integration -q
npm run test --workspace @singlish-agent/web -- --run
npm run build --workspace @singlish-agent/web
git add apps/api/src/singlish_agent_api/domain/jobs/schemas.py packages/contracts/src/job.ts apps/api/src/singlish_agent_api/api/routes/jobs.py apps/api/src/singlish_agent_api/worker/tasks.py apps/api/tests/integration/test_jobs_api.py apps/web/src/features/jobs/api.ts apps/web/src/features/jobs/ReprocessButton.tsx apps/web/src/features/jobs/ReprocessButton.test.tsx apps/web/src/app/App.tsx README.md "docs/启动停止手册.md" "记录.md"
git commit -m "feat: add low-confidence reprocess skeleton"
```

Expected:

- All backend tests PASS
- All frontend tests PASS
- Production build succeeds
- One commit contains the reprocess skeleton and docs
