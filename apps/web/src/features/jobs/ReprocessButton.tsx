import type { ReprocessResult } from "@singlish-agent/contracts";

type Props = {
  disabled?: boolean;
  onTrigger: () => void | Promise<void>;
  reprocess: ReprocessResult | null;
};

export function ReprocessButton({ disabled = false, onTrigger, reprocess }: Props) {
  if (!reprocess) {
    return null;
  }

  const flaggedCount = reprocess.low_confidence_segments.length;
  const canTrigger = flaggedCount > 0 && reprocess.reprocess_status !== "queued" && !disabled;

  return (
    <section>
      <h3>Low-confidence Reprocess</h3>
      <p>Flagged segments: {flaggedCount}</p>
      <p>Status: {reprocess.reprocess_status}</p>
      <p>Attempts: {reprocess.reprocess_attempts}</p>
      <button type="button" onClick={() => void onTrigger()} disabled={!canTrigger}>
        Reprocess Low-confidence
      </button>
    </section>
  );
}
