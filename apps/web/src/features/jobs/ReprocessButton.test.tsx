import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { ReprocessButton } from "./ReprocessButton";

test("triggers low-confidence reprocess when flagged segments exist", () => {
  const onTrigger = vi.fn();

  render(
    <ReprocessButton
      onTrigger={onTrigger}
      reprocess={{
        low_confidence_segments: [
          {
            start_seconds: 0,
            end_seconds: 1.2,
            text: "wah lau eh",
            confidence: 0.91,
            low_confidence: true,
          },
        ],
        reprocess_status: "not_requested",
        reprocess_attempts: 0,
      }}
    />,
  );

  fireEvent.click(screen.getByRole("button", { name: "Reprocess Low-confidence" }));

  expect(screen.getByText("Flagged segments: 1")).toBeInTheDocument();
  expect(screen.getByText("Status: not_requested")).toBeInTheDocument();
  expect(onTrigger).toHaveBeenCalledTimes(1);
});
