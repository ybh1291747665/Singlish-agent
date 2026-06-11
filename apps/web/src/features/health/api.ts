import type { HealthResponse } from "@singlish-agent/contracts";

import { apiFetch } from "../../shared/api/client";

export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}
