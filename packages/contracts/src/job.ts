export const JOB_PIPELINE_STAGES = [
  "created",
  "uploaded",
  "queued",
  "preprocessing",
  "transcribing",
  "normalizing",
  "generating_report",
  "completed",
] as const;

export const JOB_EXPORT_FORMATS = ["txt", "md", "json", "srt", "vtt"] as const;

export type JobPipelineStage = (typeof JOB_PIPELINE_STAGES)[number];
export type JobStatus = JobPipelineStage | "failed";
export type JobExportFormat = (typeof JOB_EXPORT_FORMATS)[number];

export type TranscriptSegment = {
  start_seconds: number;
  end_seconds: number;
  text: string;
  confidence: number | null;
  low_confidence?: boolean;
};

export type TimeRangeSegment = {
  start_seconds: number;
  end_seconds: number;
};

export type PreprocessingResult = {
  duration_seconds: number;
  sample_rate_hz: number;
  channels: number;
  normalized_format: string;
  speech_segments: TimeRangeSegment[];
  silence_segments: TimeRangeSegment[];
};

export type TranscriptionResult = {
  provider: string;
  raw_transcript: string;
  segments: TranscriptSegment[];
};

export type NormalizationResult = {
  normalized_transcript: string;
  standard_english: string;
  simplified_chinese: string;
  glossary_hits: string[];
  translation_provider: string;
};

export type ReportResult = {
  summary: string;
  key_phrases: string[];
};

export type ReprocessResult = {
  low_confidence_segments: TranscriptSegment[];
  reprocess_status: string;
  reprocess_attempts: number;
};

export type JobResultPayload = {
  preprocessing: PreprocessingResult | null;
  transcription: TranscriptionResult | null;
  normalization: NormalizationResult | null;
  report: ReportResult | null;
  reprocess: ReprocessResult | null;
};

export type HealthResponse = {
  status: "ok" | "degraded";
  services: Record<string, "ok" | "error">;
};

export type JobCreateResponse = {
  job_id: string;
  file_name: string;
  status: JobStatus;
  created_at: string;
};

export type JobDetailResponse = {
  job_id: string;
  file_name: string;
  status: JobStatus;
  result_summary: string | null;
  result_payload: JobResultPayload | null;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
};

export type JobSegmentsResponse = {
  job_id: string;
  status: JobStatus;
  total_segments: number;
  segments: TranscriptSegment[];
};

export type JobReprocessResponse = {
  job_id: string;
  reprocess_status: string;
  reprocess_attempts: number;
};
