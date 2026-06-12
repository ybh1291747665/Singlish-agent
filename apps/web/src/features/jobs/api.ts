import type {
  JobCreateResponse,
  JobDetailResponse,
  JobExportFormat,
  JobReprocessResponse,
  JobSegmentsResponse,
} from "@singlish-agent/contracts";

import { API_BASE_URL, apiFetch } from "../../shared/api/client";

export async function createJob(file: File): Promise<JobCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/v1/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`create job failed: ${response.status}`);
  }

  return (await response.json()) as JobCreateResponse;
}

export function getJob(jobId: string): Promise<JobDetailResponse> {
  return apiFetch<JobDetailResponse>(`/api/v1/jobs/${jobId}`);
}

export function getJobSegments(jobId: string): Promise<JobSegmentsResponse> {
  return apiFetch<JobSegmentsResponse>(`/api/v1/jobs/${jobId}/segments`);
}

export function getJobExportUrl(jobId: string, exportFormat: JobExportFormat): string {
  return `${API_BASE_URL}/api/v1/jobs/${jobId}/exports/${exportFormat}`;
}

export function reprocessLowConfidence(jobId: string): Promise<JobReprocessResponse> {
  return apiFetch<JobReprocessResponse>(`/api/v1/jobs/${jobId}/reprocess-low-confidence`, {
    method: "POST",
  });
}
