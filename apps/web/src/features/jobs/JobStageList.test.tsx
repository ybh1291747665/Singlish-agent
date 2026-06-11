import { render, screen } from "@testing-library/react";

import { JobStageList } from "./JobStageList";

test("renders the current pipeline stage", () => {
  render(<JobStageList status="generating_report" />);

  expect(screen.getByText("preprocessing: done")).toBeInTheDocument();
  expect(screen.getByText("generating_report: current")).toBeInTheDocument();
  expect(screen.getByText("completed: pending")).toBeInTheDocument();
});


test("renders a failed marker when the job has failed", () => {
  render(<JobStageList status="failed" />);

  expect(screen.getByText("pipeline_status: failed")).toBeInTheDocument();
});
