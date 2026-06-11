import { render, screen } from "@testing-library/react";

import { JobExportLinks } from "./JobExportLinks";

test("renders export download links for all supported formats", () => {
  render(<JobExportLinks jobId="job-123" />);

  expect(screen.getByRole("link", { name: "Download Markdown" })).toHaveAttribute(
    "href",
    "http://127.0.0.1:8000/api/v1/jobs/job-123/exports/md",
  );
  expect(screen.getByRole("link", { name: "Download SRT" })).toHaveAttribute(
    "href",
    "http://127.0.0.1:8000/api/v1/jobs/job-123/exports/srt",
  );
});
