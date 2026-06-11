import { useEffect, useState } from "react";
import type {
  HealthResponse,
  JobCreateResponse,
  JobDetailResponse,
} from "@singlish-agent/contracts";

import { fetchHealth } from "../features/health/api";
import { HealthPanel } from "../features/health/HealthPanel";
import { createJob, getJob } from "../features/jobs/api";
import { JobResultDetails } from "../features/jobs/JobResultDetails";
import { JobStageList } from "../features/jobs/JobStageList";
import { UploadPanel } from "../features/jobs/UploadPanel";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [createdJob, setCreatedJob] = useState<JobCreateResponse | null>(null);
  const [jobDetail, setJobDetail] = useState<JobDetailResponse | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => {
        setHealth({
          status: "degraded",
          services: {
            app: "error",
            database: "error",
            redis: "error",
            object_storage: "error",
          },
        });
      });
  }, []);

  useEffect(() => {
    if (!createdJob) {
      return;
    }

    const intervalId = window.setInterval(() => {
      getJob(createdJob.job_id).then(setJobDetail).catch(() => undefined);
    }, 1500);

    return () => window.clearInterval(intervalId);
  }, [createdJob]);

  async function handleUpload(file: File) {
    const created = await createJob(file);
    setCreatedJob(created);
    const detail = await getJob(created.job_id);
    setJobDetail(detail);
  }

  return (
    <main>
      <h1>Singlish Agent Demo</h1>
      <HealthPanel health={health} />
      <UploadPanel onUpload={handleUpload} />

      {createdJob ? (
        <section>
          <h2>Latest Job</h2>
          <p>job_id: {createdJob.job_id}</p>
          <p>status: {jobDetail?.status ?? createdJob.status}</p>
          <p>file_name: {createdJob.file_name}</p>
          <p>result_summary: {jobDetail?.result_summary ?? "pending"}</p>
          <JobStageList status={jobDetail?.status ?? createdJob.status} />
          <JobResultDetails resultPayload={jobDetail?.result_payload ?? null} />
        </section>
      ) : null}
    </main>
  );
}
