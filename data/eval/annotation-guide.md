# Annotation Guide

This guide defines how to fill the local evaluation manifest and how to annotate clips consistently.

## Scope

Use this guide for short evaluation clips that will be used to measure:

- ASR transcript quality
- Standard English normalization quality
- Singlish glossary detection
- Code-switching coverage

## Required Files

Start from these templates:

- `data/eval/manifest.local.template.jsonl`
- `data/eval/splits.local.template.json`

Recommended local working copies:

- `data/eval/manifest.local.jsonl`
- `data/eval/splits.local.json`

## Annotation Workflow

1. Collect a short audio clip with clear ownership or permission.
2. Assign a stable `clip_id`.
3. Save the audio under your local evaluation audio folder.
4. Add one JSON line to `manifest.local.jsonl`.
5. Listen to the clip and write the reference transcript exactly as spoken.
6. Write a Standard English normalization that preserves meaning and tone as closely as possible.
7. Mark glossary terms only when they are actually present and semantically relevant.
8. Mark whether the clip contains code-switching or noticeable background noise.
9. Assign the clip to `dev` or `test`.
10. Update `splits.local.json` so the split file matches the manifest.

## Field Definitions

### `clip_id`

- Required
- Stable unique identifier
- Recommended pattern: `<slice>-<scenario>-<index>`
- Example: `pilot-clean-001`

### `relative_audio_path`

- Required
- Relative path from the local evaluation root
- Keep it stable once referenced in the manifest

### `duration_seconds`

- Required
- Rounded clip duration in seconds
- Use the real duration, not an estimate when possible

### `scenario`

- Required
- Allowed values:
  - `clean_read`
  - `daily_conversation`
  - `code_switching`
  - `noisy_environment`

### `speaker_id`

- Required
- Stable per speaker
- Do not encode personal names if privacy is a concern

### `languages`

- Required
- Ordered list of languages clearly present in the clip
- Examples:
  - `["en"]`
  - `["en", "zh"]`
  - `["en", "ms"]`

### `reference_transcript`

- Required
- The best manual transcript of what was actually said
- Keep Singlish wording when that is what the speaker used
- Do not silently convert to Standard English here

### `reference_standard_english`

- Required
- Semantic normalization of the transcript into natural Standard English
- Preserve meaning, emphasis, and uncertainty
- If the original wording is already Standard English, this field may match the transcript

### `glossary_terms`

- Required
- List of detected Singlish or local glossary items
- Keep to canonical forms where possible
- Example:
  - `["lah", "wah lau eh"]`

### `contains_code_switching`

- Required
- `true` when more than one language is meaningfully present

### `contains_background_noise`

- Required
- `true` when noise is significant enough to matter for evaluation

### `source_type`

- Required
- Suggested values:
  - `self_recorded`
  - `licensed_public`
  - `consented_internal`

### `consent_status`

- Required
- Suggested values:
  - `confirmed`
  - `not_required`
  - `restricted`

### `split`

- Required
- Allowed values:
  - `dev`
  - `test`

### `notes`

- Optional but recommended
- Use for pronunciation quirks, hard-to-hear spans, or provenance reminders

## Transcript Rules

- Keep filler or discourse markers if they were spoken and matter for the utterance.
- Keep obvious Singlish particles such as `lah`, `leh`, `lor`, `meh` when present.
- Preserve code-switched spans instead of forcing them into English.
- If a word is uncertain, use your best judgment and note uncertainty in `notes`.

## Standard English Rules

- Normalize meaning, not accent.
- Preserve politeness, attitude, and uncertainty where possible.
- Do not add facts that were not present in the original clip.
- If a phrase is genuinely ambiguous, choose the most likely interpretation and note the ambiguity in `notes`.

## Split Rules

- Keep speakers disjoint across `dev` and `test`.
- Do not put clips from the same speaker into both splits.
- Prefer balanced scenario coverage in `test`.

## Minimum Pilot Target

Before claiming the evaluation setup is usable, collect at least:

- 5 `clean_read` clips
- 5 `daily_conversation` clips
- 5 `code_switching` clips
- 3 `noisy_environment` clips

This is smaller than the full project target, but enough to validate the workflow.
