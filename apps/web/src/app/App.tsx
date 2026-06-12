import { useEffect, useState } from "react";
import type {
  HealthResponse,
  JobCreateResponse,
  JobDetailResponse,
  JobSegmentsResponse,
} from "@singlish-agent/contracts";

import { fetchHealth } from "../features/health/api";
import { HealthPanel } from "../features/health/HealthPanel";
import { createJob, getJob, getJobSegments, reprocessLowConfidence } from "../features/jobs/api";
import { JobExportLinks } from "../features/jobs/JobExportLinks";
import { ReprocessButton } from "../features/jobs/ReprocessButton";
import { JobResultDetails } from "../features/jobs/JobResultDetails";
import { JobSegmentList } from "../features/jobs/JobSegmentList";
import { JobStageList } from "../features/jobs/JobStageList";
import { UploadPanel } from "../features/jobs/UploadPanel";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [createdJob, setCreatedJob] = useState<JobCreateResponse | null>(null);
  const [jobDetail, setJobDetail] = useState<JobDetailResponse | null>(null);
  const [jobSegments, setJobSegments] = useState<JobSegmentsResponse | null>(null);
  const [isReprocessSubmitting, setIsReprocessSubmitting] = useState(false);

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
      void refreshJob(createdJob.job_id);
    }, 1500);

    return () => window.clearInterval(intervalId);
  }, [createdJob]);

  async function refreshJob(jobId: string) {
    const [detail, segments] = await Promise.all([getJob(jobId), getJobSegments(jobId)]);
    setJobDetail(detail);
    setJobSegments(segments);
  }

  async function handleUpload(file: File) {
    const created = await createJob(file);
    setCreatedJob(created);
    await refreshJob(created.job_id);
  }

  async function handleReprocess() {
    if (!createdJob) {
      return;
    }
    setIsReprocessSubmitting(true);
    try {
      await reprocessLowConfidence(createdJob.job_id);
      await refreshJob(createdJob.job_id);
    } finally {
      setIsReprocessSubmitting(false);
    }
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
          <ReprocessButton
            disabled={isReprocessSubmitting}
            onTrigger={handleReprocess}
            reprocess={jobDetail?.result_payload?.reprocess ?? null}
          />
          <JobSegmentList segments={jobSegments?.segments ?? []} />
          {jobDetail?.status === "completed" ? (
            <JobExportLinks jobId={createdJob.job_id} />
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
