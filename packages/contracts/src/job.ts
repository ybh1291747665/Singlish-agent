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
  created_at: string;
  updated_at: string;
  processed_at: string | null;
};
