import json
from datetime import datetime, timezone

from singlish_agent_api.domain.jobs.exports import JobExportFormat, build_job_export
from singlish_agent_api.domain.jobs.models import Job, JobStatus
from singlish_agent_api.domain.jobs.schemas import JobResultPayload


def build_job() -> Job:
    return Job(
        id="job-123",
        file_name="sample.wav",
        object_key="raw/job-123/sample.wav",
        status=JobStatus.COMPLETED.value,
        result_summary="Transcription completed successfully via faster_whisper.",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        processed_at=datetime.now(timezone.utc),
    )


def build_payload() -> JobResultPayload:
    return JobResultPayload.model_validate(
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
                "provider": "faster_whisper",
                "raw_transcript": "This queue is quite fast.",
                "segments": [
                    {
                        "start_seconds": 0.0,
                        "end_seconds": 1.2,
                        "text": "This queue",
                        "confidence": None,
                        "low_confidence": False,
                    },
                    {
                        "start_seconds": 1.2,
                        "end_seconds": 2.4,
                        "text": "is quite fast.",
                        "confidence": None,
                        "low_confidence": False,
                    },
                ],
            },
            "normalization": {
                "normalized_transcript": "This queue is quite fast.",
                "standard_english": "This queue is quite fast.",
                "simplified_chinese": "[translation pending] This queue is quite fast.",
                "glossary_hits": ["lah"],
                "translation_provider": "fallback",
            },
            "report": {
                "summary": "Speaker remarks that the queue moved quickly.",
                "key_phrases": ["queue", "fast"],
            },
            "reprocess": {
                "low_confidence_segments": [],
                "reprocess_status": "not_needed",
                "reprocess_attempts": 0,
            },
        }
    )


def test_build_job_export_renders_srt_segments() -> None:
    document = build_job_export(
        job=build_job(),
        payload=build_payload(),
        export_format=JobExportFormat.SRT,
    )

    assert document.file_name == "sample-job-123.srt"
    assert "1\n00:00:00,000 --> 00:00:01,200\nThis queue\n" in document.content
    assert "2\n00:00:01,200 --> 00:00:02,400\nis quite fast.\n" in document.content


def test_build_job_export_renders_markdown_summary() -> None:
    document = build_job_export(
        job=build_job(),
        payload=build_payload(),
        export_format=JobExportFormat.MARKDOWN,
    )

    assert document.media_type == "text/markdown; charset=utf-8"
    assert "# Singlish Agent Export" in document.content
    assert "## Standard English" in document.content
    assert "## Simplified Chinese" in document.content
    assert "## Low-confidence Reprocess" in document.content
    assert "Speaker remarks that the queue moved quickly." in document.content


def test_build_job_export_renders_json_payload() -> None:
    document = build_job_export(
        job=build_job(),
        payload=build_payload(),
        export_format=JobExportFormat.JSON,
    )

    parsed = json.loads(document.content)
    assert parsed["job_id"] == "job-123"
    assert parsed["result_payload"]["transcription"]["provider"] == "faster_whisper"
