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
          speech_segments: [
            {
              start_seconds: 0,
              end_seconds: 10.2,
            },
          ],
          silence_segments: [
            {
              start_seconds: 10.2,
              end_seconds: 12.4,
            },
          ],
        },
        transcription: {
          provider: "fake",
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
          simplified_chinese: "\u54c7\uff0c\u8fd9\u4e2a\u961f\u4f0d\u8d70\u5f97\u5f88\u5feb\u3002",
          glossary_hits: ["wah lau eh", "lah"],
          translation_provider: "fallback",
        },
        report: {
          summary: "Speaker remarks that the queue moved quickly.",
          key_phrases: ["queue", "fast"],
        },
        reprocess: null,
      }}
    />,
  );

  expect(screen.getByText("Duration: 12.4s")).toBeInTheDocument();
  expect(screen.getByText("Channels: 1")).toBeInTheDocument();
  expect(screen.getByText("Normalized format: pcm_s16le")).toBeInTheDocument();
  expect(screen.getByText("Speech segments: 1")).toBeInTheDocument();
  expect(screen.getByText("Silence segments: 1")).toBeInTheDocument();
  expect(screen.getByText("Transcription provider: fake")).toBeInTheDocument();
  expect(screen.getByText("Raw transcript: wah lau eh this queue quite fast lah")).toBeInTheDocument();
  expect(screen.getByText("Standard English: Wow, this queue is quite fast.")).toBeInTheDocument();
  expect(
    screen.getByText(
      "Simplified Chinese: \u54c7\uff0c\u8fd9\u4e2a\u961f\u4f0d\u8d70\u5f97\u5f88\u5feb\u3002",
    ),
  ).toBeInTheDocument();
  expect(screen.getByText("Translation provider: fallback")).toBeInTheDocument();
  expect(screen.getByText("Summary: Speaker remarks that the queue moved quickly.")).toBeInTheDocument();
});
