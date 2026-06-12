from datetime import datetime

from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str
    confidence: float | None
    low_confidence: bool = False


class TimeRangeSegment(BaseModel):
    start_seconds: float
    end_seconds: float


class PreprocessingResult(BaseModel):
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    normalized_format: str
    speech_segments: list[TimeRangeSegment] = []
    silence_segments: list[TimeRangeSegment] = []


class TranscriptionResult(BaseModel):
    provider: str
    raw_transcript: str
    segments: list[TranscriptSegment]


class NormalizationResult(BaseModel):
    normalized_transcript: str
    standard_english: str
    simplified_chinese: str = ""
    glossary_hits: list[str]
    translation_provider: str = "unknown"


class ReportResult(BaseModel):
    summary: str
    key_phrases: list[str]


class ReprocessResult(BaseModel):
    low_confidence_segments: list[TranscriptSegment] = []
    reprocess_status: str = "not_requested"
    reprocess_attempts: int = 0


class JobResultPayload(BaseModel):
    preprocessing: PreprocessingResult | None = None
    transcription: TranscriptionResult | None = None
    normalization: NormalizationResult | None = None
    report: ReportResult | None = None
    reprocess: ReprocessResult | None = None


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


class JobSegmentsResponse(BaseModel):
    job_id: str
    status: str
    total_segments: int
    segments: list[TranscriptSegment]


class JobReprocessResponse(BaseModel):
    job_id: str
    reprocess_status: str
    reprocess_attempts: int
