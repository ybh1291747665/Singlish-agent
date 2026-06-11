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
          confidence: null,
        },
        {
          start_seconds: 1.25,
          end_seconds: 2.5,
          text: "is quite fast",
          confidence: null,
        },
      ]}
    />,
  );

  expect(screen.getByText("00:00.00 - 00:01.25")).toBeInTheDocument();
  expect(screen.getByText("00:01.25 - 00:02.50")).toBeInTheDocument();
  expect(screen.getByText("is quite fast")).toBeInTheDocument();
});
