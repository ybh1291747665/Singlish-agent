import { useEffect, useState } from "react";
import type { HealthResponse } from "@singlish-agent/contracts";

import { fetchHealth } from "../features/health/api";
import { HealthPanel } from "../features/health/HealthPanel";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => {
        setHealth({
          status: "degraded",
          services: {
            app: "error",
            database: "error",
            redis: "error",
            object_storage: "error",
          },
        });
      });
  }, []);

  return (
    <main>
      <h1>Singlish Agent Demo</h1>
      <HealthPanel health={health} />
    </main>
  );
}
