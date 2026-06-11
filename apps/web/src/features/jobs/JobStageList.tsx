import { JOB_PIPELINE_STAGES, type JobStatus } from "@singlish-agent/contracts";

type Props = {
  status: JobStatus;
};

function getStageState(stage: string, status: JobStatus): "done" | "current" | "pending" {
  const currentIndex = JOB_PIPELINE_STAGES.indexOf(status as (typeof JOB_PIPELINE_STAGES)[number]);
  const stageIndex = JOB_PIPELINE_STAGES.indexOf(stage as (typeof JOB_PIPELINE_STAGES)[number]);

  if (currentIndex === -1) {
    return "pending";
  }

  if (stageIndex < currentIndex) {
    return "done";
  }

  if (stageIndex === currentIndex) {
    return "current";
  }

  return "pending";
}

export function JobStageList({ status }: Props) {
  return (
    <section>
      <h3>Pipeline</h3>
      {status === "failed" ? <p>pipeline_status: failed</p> : null}
      <ul>
        {JOB_PIPELINE_STAGES.map((stage) => (
          <li key={stage}>
            {stage}: {status === "failed" ? "pending" : getStageState(stage, status)}
          </li>
        ))}
      </ul>
    </section>
  );
}
