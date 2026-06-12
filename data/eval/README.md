# Evaluation Dataset

This folder is the intended home for the local speaker-disjoint evaluation set described in `project-plan.md`.

What belongs here:

- `manifest.example.jsonl`
  Example manifest format for evaluation clips.
- Private manifests such as `manifest.local.jsonl`
  Local-only file listing audio paths and labels.
- Annotation exports
  Reference transcripts, Standard English normalization labels, slang tags, and metadata.

Suggested local files:

- `manifest.local.jsonl`
- `labels.local.jsonl`
- `splits.local.json`

Recommended evaluation clip fields:

- `clip_id`
- `relative_audio_path`
- `duration_seconds`
- `scenario`
- `speaker_id`
- `languages`
- `reference_transcript`
- `reference_standard_english`
- `glossary_terms`
- `notes`

Scenarios from the project plan:

- `clean_read`
- `daily_conversation`
- `code_switching`
- `noisy_environment`

This folder is intentionally documentation-first right now. It tells us where the dataset should live even before the real clips are collected.
