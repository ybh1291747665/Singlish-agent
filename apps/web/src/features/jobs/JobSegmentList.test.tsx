import { render, screen } from "@testing-library/react";

import { JobSegmentList } from "./JobSegmentList";

test("renders transcript segments with timeline labels", () => {
  render(
    <JobSegmentList
      segments={[
        {
          start_seconds: 0,
          end_seconds: 1.25,
          text: "this queue",
          confidence: 0.91,
          low_confidence: true,
        },
        {
          start_seconds: 1.25,
          end_seconds: 2.5,
          text: "is quite fast",
          confidence: 0.98,
          low_confidence: false,
        },
      ]}
    />,
  );

  expect(screen.getByText("00:00.00 - 00:01.25")).toBeInTheDocument();
  expect(screen.getByText("00:01.25 - 00:02.50")).toBeInTheDocument();
  expect(screen.getByText("is quite fast")).toBeInTheDocument();
  expect(screen.getByText("Confidence: 0.91 (low confidence)")).toBeInTheDocument();
  expect(screen.getByText("Confidence: 0.98")).toBeInTheDocument();
});
