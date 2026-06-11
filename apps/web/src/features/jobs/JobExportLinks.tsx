import { JOB_EXPORT_FORMATS } from "@singlish-agent/contracts";

import { getJobExportUrl } from "./api";

type Props = {
  jobId: string;
};

const LABELS: Record<(typeof JOB_EXPORT_FORMATS)[number], string> = {
  txt: "Download TXT",
  md: "Download Markdown",
  json: "Download JSON",
  srt: "Download SRT",
  vtt: "Download WebVTT",
};

export function JobExportLinks({ jobId }: Props) {
  return (
    <section>
      <h3>Exports</h3>
      <ul>
        {JOB_EXPORT_FORMATS.map((format) => (
          <li key={format}>
            <a href={getJobExportUrl(jobId, format)} target="_blank" rel="noreferrer">
              {LABELS[format]}
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
