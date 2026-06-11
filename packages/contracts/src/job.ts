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

export type JobPipelineStage = (typeof JOB_PIPELINE_STAGES)[number];
export type JobStatus = JobPipelineStage | "failed";

export type TranscriptSegment = {
  start_seconds: number;
  end_seconds: number;
  text: string;
  confidence: number | null;
};

export type PreprocessingResult = {
  duration_seconds: number;
  sample_rate_hz: number;
  channels: number;
  normalized_format: string;
};

export type TranscriptionResult = {
  provider: string;
  raw_transcript: string;
  segments: TranscriptSegment[];
};

export type NormalizationResult = {
  normalized_transcript: string;
  standard_english: string;
  glossary_hits: string[];
};

export type ReportResult = {
  summary: string;
  key_phrases: string[];
};

export type JobResultPayload = {
  preprocessing: PreprocessingResult | null;
  transcription: TranscriptionResult | null;
  normalization: NormalizationResult | null;
  report: ReportResult | null;
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
