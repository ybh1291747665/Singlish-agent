# Evaluation Guide

This document explains where the evaluation dataset lives and how it is expected to grow.

## Current Status

- The repository does not yet ship a formal Singlish evaluation dataset.
- The current implementation work has focused on the offline processing pipeline.
- Local development has used synthetic or temporary audio for end-to-end checks.

## Where The Dataset Should Live

- Local private evaluation data: `data/eval/`
- Public demo-safe assets: `examples/`
- Future generated metrics and reports: `data/processed/`

## Why There Is No Dataset In Git Yet

- The project plan expects a speaker-disjoint evaluation set with manual labels.
- That dataset should be assembled from licensed public material and consented recordings.
- Until provenance and redistribution are clear, raw audio should stay out of the repository.

## Recommended Next Collection Milestone

Build a first small evaluation slice with at least:

- 10 `clean_read` clips
- 10 `daily_conversation` clips
- 10 `code_switching` clips
- 5 `noisy_environment` clips

Each clip should have:

- A stable `clip_id`
- Audio path
- Duration
- Reference transcript
- Standard English normalization
- Glossary term labels
- Scenario label

## Manifest Format

Use JSONL, one clip per line.

Example location:

- `data/eval/manifest.example.jsonl`

Recommended local file:

- `data/eval/manifest.local.jsonl`

## Publication Rule

Only commit:

- Documentation
- Schemas
- Small public demo clips with clear permission
- Derived evaluation reports that do not expose restricted source audio

Do not commit:

- Private interview recordings
- Unlicensed third-party corpora
- Audio containing personal data without explicit permission
