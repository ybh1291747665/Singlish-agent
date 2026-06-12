import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from singlish_agent_api.domain.jobs.models import Job
from singlish_agent_api.domain.jobs.schemas import JobResultPayload, TranscriptSegment


class JobExportFormat(StrEnum):
    TXT = "txt"
    MARKDOWN = "md"
    JSON = "json"
    SRT = "srt"
    WEBVTT = "vtt"


@dataclass
class JobExportDocument:
    content: str
    media_type: str
    file_name: str


def build_job_export(
    *,
    job: Job,
    payload: JobResultPayload,
    export_format: JobExportFormat,
) -> JobExportDocument:
    stem = Path(job.file_name).stem or "job"
    file_name = f"{stem}-{job.id}.{export_format.value}"

    if export_format == JobExportFormat.TXT:
        return JobExportDocument(
            content=_render_txt(job=job, payload=payload),
            media_type="text/plain; charset=utf-8",
            file_name=file_name,
        )
    if export_format == JobExportFormat.MARKDOWN:
        return JobExportDocument(
            content=_render_markdown(job=job, payload=payload),
            media_type="text/markdown; charset=utf-8",
            file_name=file_name,
        )
    if export_format == JobExportFormat.JSON:
        return JobExportDocument(
            content=_render_json(job=job, payload=payload),
            media_type="application/json",
            file_name=file_name,
        )
    if export_format == JobExportFormat.SRT:
        return JobExportDocument(
            content=_render_srt(payload),
            media_type="application/x-subrip",
            file_name=file_name,
        )
    return JobExportDocument(
        content=_render_webvtt(payload),
        media_type="text/vtt; charset=utf-8",
        file_name=file_name,
    )


def _render_txt(*, job: Job, payload: JobResultPayload) -> str:
    sections = [
        f"Job ID: {job.id}",
        f"Source file: {job.file_name}",
        f"Status: {job.status}",
    ]
    if payload.transcription:
        sections.extend(
            [
                f"Transcription provider: {payload.transcription.provider}",
                "",
                "Raw transcript:",
                payload.transcription.raw_transcript,
            ]
        )
    if payload.normalization:
        sections.extend(
            [
                "",
                "Standard English:",
                payload.normalization.standard_english,
                "",
                "Simplified Chinese:",
                payload.normalization.simplified_chinese,
            ]
        )
        if payload.normalization.glossary_hits:
            sections.extend(
                [
                    "",
                    "Glossary hits:",
                    ", ".join(payload.normalization.glossary_hits),
                ]
            )
    if payload.report:
        sections.extend(
            [
                "",
                "Summary:",
                payload.report.summary,
            ]
        )
    if payload.reprocess:
        sections.extend(
            [
                "",
                "Reprocess status:",
                payload.reprocess.reprocess_status,
                "",
                f"Low-confidence segments: {len(payload.reprocess.low_confidence_segments)}",
                f"Reprocess attempts: {payload.reprocess.reprocess_attempts}",
            ]
        )
    return "\n".join(sections).strip() + "\n"


def _render_markdown(*, job: Job, payload: JobResultPayload) -> str:
    sections = [
        "# Singlish Agent Export",
        "",
        f"- Job ID: `{job.id}`",
        f"- Source file: `{job.file_name}`",
        f"- Status: `{job.status}`",
    ]
    if payload.transcription:
        sections.extend(
            [
                "",
                "## Transcription",
                "",
                f"- Provider: `{payload.transcription.provider}`",
                "",
                payload.transcription.raw_transcript,
            ]
        )
    if payload.normalization:
        sections.extend(
            [
                "",
                "## Standard English",
                "",
                payload.normalization.standard_english,
                "",
                "## Simplified Chinese",
                "",
                payload.normalization.simplified_chinese,
            ]
        )
        if payload.normalization.glossary_hits:
            sections.extend(
                [
                    "",
                    "## Glossary Hits",
                    "",
                    ", ".join(f"`{term}`" for term in payload.normalization.glossary_hits),
                ]
            )
    if payload.report:
        sections.extend(
            [
                "",
                "## Summary",
                "",
                payload.report.summary,
            ]
        )
    if payload.reprocess:
        sections.extend(
            [
                "",
                "## Low-confidence Reprocess",
                "",
                f"- Status: `{payload.reprocess.reprocess_status}`",
                f"- Flagged segments: `{len(payload.reprocess.low_confidence_segments)}`",
                f"- Attempts: `{payload.reprocess.reprocess_attempts}`",
            ]
        )
    return "\n".join(sections).strip() + "\n"


def _render_json(*, job: Job, payload: JobResultPayload) -> str:
    return json.dumps(
        {
            "job_id": job.id,
            "file_name": job.file_name,
            "status": job.status,
            "result_summary": job.result_summary,
            "result_payload": payload.model_dump(mode="json"),
        },
        ensure_ascii=False,
        indent=2,
    )


def _render_srt(payload: JobResultPayload) -> str:
    cues = _render_segment_blocks(payload, decimal_separator=",")
    return "".join(
        [
            f"{index}\n{start} --> {end}\n{text}\n\n"
            for index, (start, end, text) in enumerate(cues, start=1)
        ]
    ).strip() + "\n"


def _render_webvtt(payload: JobResultPayload) -> str:
    cues = _render_segment_blocks(payload, decimal_separator=".")
    body = "".join(
        [
            f"{start} --> {end}\n{text}\n\n"
            for start, end, text in cues
        ]
    ).strip()
    return f"WEBVTT\n\n{body}\n"


def _render_segment_blocks(
    payload: JobResultPayload,
    *,
    decimal_separator: str,
) -> list[tuple[str, str, str]]:
    segments = payload.transcription.segments if payload.transcription else []
    if not segments and payload.transcription and payload.transcription.raw_transcript:
        segments = [
            TranscriptSegment(
                start_seconds=0.0,
                end_seconds=5.0,
                text=payload.transcription.raw_transcript,
                confidence=None,
            )
        ]

    return [
        (
            _format_timestamp(segment.start_seconds, decimal_separator=decimal_separator),
            _format_timestamp(
                max(segment.end_seconds, segment.start_seconds),
                decimal_separator=decimal_separator,
            ),
            segment.text,
        )
        for segment in segments
    ]


def _format_timestamp(seconds: float, *, decimal_separator: str) -> str:
    milliseconds_total = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds_total, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1_000)
    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}"
        f"{decimal_separator}{milliseconds:03d}"
    )
