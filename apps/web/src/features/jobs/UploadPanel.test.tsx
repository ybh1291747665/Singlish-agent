import { fireEvent, render, screen } from "@testing-library/react";

import { UploadPanel } from "./UploadPanel";

test("submits the selected file", async () => {
  const submitted: File[] = [];

  render(
    <UploadPanel
      onUpload={async (file) => {
        submitted.push(file);
      }}
    />,
  );

  const input = screen.getByLabelText("Audio file");
  const button = screen.getByRole("button", { name: "Upload" });
  const file = new File(["demo"], "sample.wav", { type: "audio/wav" });

  fireEvent.change(input, { target: { files: [file] } });
  fireEvent.click(button);

  expect(submitted).toHaveLength(1);
  expect(submitted[0].name).toBe("sample.wav");
});
