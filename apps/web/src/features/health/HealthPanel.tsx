import type { HealthResponse } from "@singlish-agent/contracts";

type Props = {
  health: HealthResponse | null;
};

export function HealthPanel({ health }: Props) {
  if (!health) {
    return (
      <section>
        <h2>Health</h2>
        <p>Loading...</p>
      </section>
    );
  }

  return (
    <section>
      <h2>Health</h2>
      <p>overall: {health.status}</p>
      <ul>
        {Object.entries(health.services).map(([name, status]) => (
          <li key={name}>
            <strong>{name}</strong>: {status}
          </li>
        ))}
      </ul>
    </section>
  );
}
