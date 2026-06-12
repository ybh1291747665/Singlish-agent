# Data Directory

This directory is reserved for local evaluation and experimentation data.

Current state:

- No formal dataset has been committed yet.
- The repo currently does not contain a public Singlish evaluation set.
- Temporary local audio used during development is not stored here by default.

Recommended structure:

- `data/eval/`
  Store local evaluation manifests, annotation files, and private audio references.
- `data/processed/`
  Store generated metrics, tables, or derived artifacts that are safe to keep locally.

Rules:

- Do not commit restricted audio, personal recordings, or third-party data without permission.
- Prefer committing manifests, schemas, and documentation rather than raw audio.
- If a dataset can be published, place a small public sample in `examples/` and document its source.
