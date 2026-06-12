import type { JobResultPayload } from "@singlish-agent/contracts";

type Props = {
  resultPayload: JobResultPayload | null;
};

export function JobResultDetails({ resultPayload }: Props) {
  if (!resultPayload) {
    return <p>Structured results pending.</p>;
  }

  return (
    <section>
      <h3>Structured Results</h3>
      {resultPayload.preprocessing ? (
        <div>
          <p>Duration: {resultPayload.preprocessing.duration_seconds}s</p>
          <p>Sample rate: {resultPayload.preprocessing.sample_rate_hz}Hz</p>
          <p>Channels: {resultPayload.preprocessing.channels}</p>
          <p>Normalized format: {resultPayload.preprocessing.normalized_format}</p>
          <p>Speech segments: {resultPayload.preprocessing.speech_segments.length}</p>
          <p>Silence segments: {resultPayload.preprocessing.silence_segments.length}</p>
        </div>
      ) : null}
      {resultPayload.transcription ? (
        <div>
          <p>Transcription provider: {resultPayload.transcription.provider}</p>
          <p>Raw transcript: {resultPayload.transcription.raw_transcript}</p>
        </div>
      ) : null}
      {resultPayload.normalization ? (
        <div>
          <p>Standard English: {resultPayload.normalization.standard_english}</p>
          <p>Simplified Chinese: {resultPayload.normalization.simplified_chinese}</p>
          <p>Translation provider: {resultPayload.normalization.translation_provider}</p>
        </div>
      ) : null}
      {resultPayload.report ? (
        <div>
          <p>Summary: {resultPayload.report.summary}</p>
        </div>
      ) : null}
    </section>
  );
}
