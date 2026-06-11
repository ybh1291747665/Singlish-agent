export type HealthResponse = {
  status: "ok" | "degraded";
  services: Record<string, "ok" | "error">;
};

export type JobCreateResponse = {
  job_id: string;
  file_name: string;
  status: string;
  created_at: string;
};

export type JobDetailResponse = {
  job_id: string;
  file_name: string;
  status: string;
  result_summary: string | null;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
};
