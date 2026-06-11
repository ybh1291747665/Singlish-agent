import { render, screen } from "@testing-library/react";

import { JobResultDetails } from "./JobResultDetails";

test("renders structured job results", () => {
  render(
    <JobResultDetails
      resultPayload={{
        preprocessing: {
          duration_seconds: 12.4,
          sample_rate_hz: 16000,
          channels: 1,
          normalized_format: "pcm_s16le",
        },
        transcription: {
          raw_transcript: "wah lau eh this queue quite fast lah",
          segments: [
            {
              start_seconds: 0,
              end_seconds: 2.4,
              text: "wah lau eh this queue quite fast lah",
              confidence: 0.94,
            },
          ],
        },
        normalization: {
          normalized_transcript: "wah lau eh, this queue quite fast lah",
          standard_english: "Wow, this queue is quite fast.",
          glossary_hits: ["wah lau eh", "lah"],
        },
        report: {
          summary: "Speaker remarks that the queue moved quickly.",
          key_phrases: ["queue", "fast"],
        },
      }}
    />,
  );

  expect(screen.getByText("Duration: 12.4s")).toBeInTheDocument();
  expect(screen.getByText("Raw transcript: wah lau eh this queue quite fast lah")).toBeInTheDocument();
  expect(screen.getByText("Standard English: Wow, this queue is quite fast.")).toBeInTheDocument();
  expect(screen.getByText("Summary: Speaker remarks that the queue moved quickly.")).toBeInTheDocument();
});
