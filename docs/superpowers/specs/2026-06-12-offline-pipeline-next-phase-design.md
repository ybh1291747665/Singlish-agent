# Offline Pipeline Next Phase Design

## Goal

Advance the offline MVP from a working demo chain into a more realistic processing pipeline by adding:

1. A local evaluation manifest bootstrap script
2. Real VAD and silence-aware segmentation
3. Dual-version normalization output
   - Standard English
   - Simplified Chinese
4. A low-confidence segment reprocess skeleton

This phase stays inside the existing offline job architecture. It does not introduce realtime or agent-side scope.

## Why This Phase

The current system already supports:

- real audio upload
- real preprocessing metadata
- real offline ASR
- timeline segments
- markdown and subtitle export

The next highest-value step is to make the offline pipeline more structurally complete:

- evaluation collection should become easier to start
- segmentation should come from an explicit preprocessing stage
- normalization should support both English and Chinese outputs
- low-confidence handling should have a visible recovery path

## Scope

### In Scope

- Generate `manifest.local.jsonl` skeletons from a local audio directory
- Add a VAD module that detects speech and silence spans from normalized audio
- Feed segment-aware timing into offline transcript outputs
- Extend normalization results with Simplified Chinese output
- Add a lightweight reprocess entrypoint and state model for low-confidence segments
- Update frontend result views and exports to show the new data

### Out Of Scope

- Full realtime VAD or streaming stabilization
- Production-grade multilingual translation quality
- Complex retry orchestration or multi-pass transcript reconciliation
- Separate database tables for transcript segments in this phase
- Full glossary CRUD or agent tool integration

## Execution Order

1. Local manifest bootstrap script
2. Real VAD and silence-aware segmentation
3. Standard English + Simplified Chinese dual output
4. Low-confidence reprocess skeleton

This order minimizes disruption. Later steps build on earlier data structures instead of replacing them.

## Design

### 1. Manifest Bootstrap Script

Add a local utility that scans a directory of audio files and emits a `manifest.local.jsonl` skeleton.

Responsibilities:

- discover supported audio files
- derive stable `clip_id` values
- compute basic duration metadata
- fill placeholder fields for scenario, speaker, transcript, normalization, and notes

Rules:

- the script must never invent transcripts or translations
- the output is a human-completable scaffold, not a labeled dataset
- the generated manifest should match the existing annotation guide

Likely output fields:

- `clip_id`
- `relative_audio_path`
- `duration_seconds`
- `scenario`
- `speaker_id`
- `languages`
- `reference_transcript`
- `reference_standard_english`
- `glossary_terms`
- `contains_code_switching`
- `contains_background_noise`
- `source_type`
- `consent_status`
- `split`
- `notes`

### 2. Real VAD And Silence-Aware Segmentation

Add an offline VAD module after preprocessing and before transcript post-processing.

Input:

- normalized mono 16k wav from preprocessing

Output:

- `speech_segments`
- `silence_segments`
- segment start and end times
- a speech-aware segmentation summary that can be attached to the job payload

First-pass design principles:

- prefer local, deterministic behavior over maximum model sophistication
- keep a fallback path that preserves full-file transcription if VAD fails
- expose VAD summary inside `preprocessing` so the result is inspectable

The existing `/segments` API should continue to work. Its returned segments should become more meaningfully aligned with speech boundaries over time.

### 3. Dual-Version Normalization

Extend normalization from one target form into two outputs:

- `standard_english`
- `simplified_chinese`

Architecture:

- keep a normalization provider boundary
- add a translation provider boundary
- start with a controllable fallback-first implementation

Phase-one behavior:

- rules or glossary mappings can normalize known Singlish forms
- if no rule applies, Standard English may safely fall back to the original transcript
- Simplified Chinese should come from a replaceable provider
- if a true translation provider is unavailable, the response should still be explicit about fallback behavior rather than pretending quality

Result payload additions should stay inside `normalization` rather than introducing a separate top-level translation object.

### 4. Low-Confidence Reprocess Skeleton

Introduce a lightweight recovery path for weak transcript spans.

Phase-one behavior:

- define a low-confidence threshold
- flag low-confidence transcript segments
- store a structured reprocess status block
- provide an API trigger for reprocessing flagged spans

This phase does not require sophisticated merging logic. It is enough to make the pipeline visibly capable of:

- identifying weak spans
- attempting reprocessing
- recording attempts and outcomes

## Data Shape Changes

The existing `result_payload` remains the primary storage shape for this phase.

Planned extensions:

- `preprocessing`
  - `duration_seconds`
  - `sample_rate_hz`
  - `channels`
  - `normalized_format`
  - `speech_segments`
  - `silence_segments`
- `normalization`
  - `normalized_transcript`
  - `standard_english`
  - `simplified_chinese`
  - `glossary_hits`
  - `translation_provider`
- `reprocess`
  - `low_confidence_segments`
  - `reprocess_status`
  - `reprocess_attempts`

The current `/api/v1/jobs/{job_id}` and `/api/v1/jobs/{job_id}/segments` endpoints remain the main retrieval surfaces.

## API Changes

### Keep

- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/jobs/{job_id}/segments`
- export endpoints

### Add

- `POST /api/v1/jobs/{job_id}/reprocess-low-confidence`

Phase-one response behavior should prioritize stable structure over full final semantics.

## Frontend Changes

The web UI should expose:

- richer preprocessing details
- clearer timeline segmentation
- Standard English output
- Simplified Chinese output
- low-confidence markers
- reprocess trigger and visible status

The frontend should consume these via existing job detail and segments APIs, plus the new reprocess endpoint.

## Error Handling

- manifest generation should skip unsupported files with a clear report
- VAD failure must fall back to whole-file behavior rather than failing the job by default
- translation failure should return explicit fallback metadata
- reprocess failure should update status and attempt counters without corrupting the base transcript result

## Testing

### Unit

- manifest bootstrap field generation
- VAD output shaping
- normalization and translation fallback logic
- low-confidence thresholding

### Integration

- jobs detail response with expanded payload
- segments response after VAD-aware processing
- export content including bilingual fields
- reprocess endpoint and status updates

### Real Validation

At least one local audio file should be used to confirm:

- preprocessing still succeeds
- VAD data is populated or falls back safely
- dual-version normalization fields are returned
- segments and exports remain usable

## Acceptance Criteria

This phase is done when:

- a local audio directory can be scaffolded into a valid evaluation manifest
- the offline pipeline exposes explicit speech/silence segmentation data
- job results include Standard English and Simplified Chinese outputs
- low-confidence spans can be identified and reprocess status can be triggered
- existing upload, detail, segment, and export flows still work end-to-end
