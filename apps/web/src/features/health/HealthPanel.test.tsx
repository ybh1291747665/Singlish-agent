import { render, screen } from "@testing-library/react";

import { HealthPanel } from "./HealthPanel";

test("renders service health rows", () => {
  render(
    <HealthPanel
      health={{
        status: "ok",
        services: {
          app: "ok",
          database: "ok",
          redis: "ok",
          object_storage: "ok",
        },
      }}
    />,
  );

  expect(screen.getByText("database")).toBeInTheDocument();
  expect(screen.getByText("object_storage")).toBeInTheDocument();
});
