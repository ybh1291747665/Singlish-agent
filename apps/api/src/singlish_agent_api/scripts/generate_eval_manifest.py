from __future__ import annotations

import argparse
import json
from pathlib import Path
import wave


SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac"}


def discover_audio_files(audio_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in audio_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_SUFFIXES
    )


def get_duration_seconds(audio_path: Path) -> float:
    duration_seconds = _get_wave_duration_seconds(audio_path)
    if duration_seconds is None:
        duration_seconds = _get_pyav_duration_seconds(audio_path)
    if duration_seconds is None:
        return 0.0
    return round(duration_seconds, 3)


def _get_wave_duration_seconds(audio_path: Path) -> float | None:
    if audio_path.suffix.lower() != ".wav":
        return None

    try:
        with wave.open(str(audio_path), "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            if frame_rate <= 0:
                return 0.0
            return wav_file.getnframes() / frame_rate
    except (wave.Error, EOFError):
        return None


def _get_pyav_duration_seconds(audio_path: Path) -> float | None:
    try:
        import av
    except ImportError:
        return None

    try:
        with av.open(str(audio_path)) as container:
            if container.duration is not None:
                return container.duration / 1_000_000

            audio_stream = next(
                (stream for stream in container.streams if stream.type == "audio"),
                None,
            )
            if (
                audio_stream is None
                or audio_stream.duration is None
                or audio_stream.time_base is None
            ):
                return None

            return float(audio_stream.duration * audio_stream.time_base)
    except av.FFmpegError:
        return None


def build_manifest_rows(*, audio_dir: Path, dataset_root: Path) -> list[dict[str, object]]:
    return [
        {
            "clip_id": audio_path.stem,
            "relative_audio_path": audio_path.relative_to(dataset_root).as_posix(),
            "duration_seconds": get_duration_seconds(audio_path),
            "scenario": "unknown",
            "speaker_id": "unknown",
            "languages": [],
            "reference_transcript": "",
            "reference_standard_english": "",
            "simplified_chinese": "",
            "glossary_terms": [],
            "contains_code_switching": False,
            "contains_background_noise": False,
            "source_type": "unknown",
            "consent_status": "unknown",
            "split": "unassigned",
            "notes": "",
        }
        for audio_path in discover_audio_files(audio_dir)
    ]


def write_manifest(output_path: Path, rows: list[dict[str, object]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_body = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    output_path.write_text(f"{manifest_body}\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan local evaluation audio clips and scaffold a JSONL manifest.",
    )
    parser.add_argument("--audio-dir", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    rows = build_manifest_rows(audio_dir=args.audio_dir, dataset_root=args.dataset_root)
    write_manifest(args.output, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
