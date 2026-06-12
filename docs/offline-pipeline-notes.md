# Offline Pipeline Notes

## Scope Added On 2026-06-12

- local evaluation manifest bootstrap script
- offline VAD and silence-aware segmentation
- Standard English plus Simplified Chinese normalization output
- low-confidence segment marking and reprocess skeleton

## Manifest Bootstrap

Run the manifest generator from the `singlish-agent` conda environment:

```powershell
& "C:\Users\12917\.conda\envs\singlish-agent\python.exe" -m singlish_agent_api.scripts.generate_eval_manifest `
  --audio-dir data/eval/audio `
  --dataset-root data/eval `
  --output data/eval/manifest.local.jsonl
```

This command only scaffolds JSONL rows. It never invents transcripts, translations, or labels.

## Offline Result Payload Additions

Completed jobs now expose these extra blocks in `result_payload`:

- `preprocessing.speech_segments`
- `preprocessing.silence_segments`
- `normalization.standard_english`
- `normalization.simplified_chinese`
- `normalization.translation_provider`
- `reprocess.low_confidence_segments`
- `reprocess.reprocess_status`
- `reprocess.reprocess_attempts`

## Reprocess Skeleton

You can trigger the low-confidence reprocess skeleton manually:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/jobs/<job_id>/reprocess-low-confidence
```

Current behavior:

- marks low-confidence transcript segments during worker processing
- stores a structured reprocess block in `result_payload`
- updates reprocess status and attempts when the endpoint is called
- does not yet run a second ASR pass or merge a new transcript
