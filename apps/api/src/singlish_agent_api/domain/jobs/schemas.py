from datetime import datetime

from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str
    confidence: float | None


class PreprocessingResult(BaseModel):
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    normalized_format: str


class TranscriptionResult(BaseModel):
    provider: str
    raw_transcript: str
    segments: list[TranscriptSegment]


class NormalizationResult(BaseModel):
    normalized_transcript: str
    standard_english: str
    glossary_hits: list[str]


class ReportResult(BaseModel):
    summary: str
    key_phrases: list[str]


class JobResultPayload(BaseModel):
    preprocessing: PreprocessingResult | None = None
    transcription: TranscriptionResult | None = None
    normalization: NormalizationResult | None = None
    report: ReportResult | None = None


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
    result_payload: JobResultPayload | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
