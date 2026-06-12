import type { TranscriptSegment } from "@singlish-agent/contracts";

type Props = {
  segments: TranscriptSegment[];
};

function formatTimestamp(seconds: number): string {
  const totalMilliseconds = Math.max(0, Math.round(seconds * 1000));
  const minutes = Math.floor(totalMilliseconds / 60000);
  const remainderMilliseconds = totalMilliseconds % 60000;
  const wholeSeconds = Math.floor(remainderMilliseconds / 1000);
  const centiseconds = Math.floor((remainderMilliseconds % 1000) / 10);
  return `${String(minutes).padStart(2, "0")}:${String(wholeSeconds).padStart(2, "0")}.${String(
    centiseconds,
  ).padStart(2, "0")}`;
}

export function JobSegmentList({ segments }: Props) {
  return (
    <section>
      <h3>Transcript Segments</h3>
      {segments.length === 0 ? <p>Segments pending.</p> : null}
      {segments.length > 0 ? (
        <ol>
          {segments.map((segment, index) => (
            <li key={`${segment.start_seconds}-${segment.end_seconds}-${index}`}>
              <p>
                {formatTimestamp(segment.start_seconds)} - {formatTimestamp(segment.end_seconds)}
              </p>
              <p>{segment.text}</p>
              {segment.confidence !== null ? (
                <p>
                  Confidence: {segment.confidence.toFixed(2)}
                  {segment.low_confidence ? " (low confidence)" : ""}
                </p>
              ) : null}
            </li>
          ))}
        </ol>
      ) : null}
    </section>
  );
}
