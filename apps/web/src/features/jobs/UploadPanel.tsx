import { FormEvent, useState } from "react";

type Props = {
  onUpload: (file: File) => Promise<void>;
};

export function UploadPanel({ onUpload }: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      return;
    }
    await onUpload(selectedFile);
  }

  return (
    <section>
      <h2>Create Job</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Audio file
          <input
            aria-label="Audio file"
            type="file"
            accept=".wav,.mp3,.m4a,.flac"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <button type="submit">Upload</button>
      </form>
    </section>
  );
}
