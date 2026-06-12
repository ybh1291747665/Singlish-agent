from __future__ import annotations

from array import array
import math
from pathlib import Path
import wave


FRAME_DURATION_MS = 30
MIN_SPEECH_DURATION_MS = 150
MIN_SILENCE_DURATION_MS = 240
DEFAULT_ENERGY_THRESHOLD = 700


def detect_speech_segments(
    audio_path: Path,
    *,
    duration_seconds: float,
    frame_duration_ms: int = FRAME_DURATION_MS,
    min_speech_duration_ms: int = MIN_SPEECH_DURATION_MS,
    min_silence_duration_ms: int = MIN_SILENCE_DURATION_MS,
    energy_threshold: int = DEFAULT_ENERGY_THRESHOLD,
) -> list[dict[str, float]]:
    with wave.open(str(audio_path), "rb") as wav_file:
        sample_rate_hz = wav_file.getframerate()
        sample_width = wav_file.getsampwidth()
        frame_size = max(1, int(sample_rate_hz * frame_duration_ms / 1000))
        energy_frames: list[bool] = []

        while True:
            chunk = wav_file.readframes(frame_size)
            if not chunk:
                break
            energy_frames.append(_compute_rms(chunk, sample_width) >= energy_threshold)

    if not energy_frames:
        return []

    smoothed_frames = _bridge_short_silence_runs(
        energy_frames,
        min_silence_frames=max(1, min_silence_duration_ms // frame_duration_ms),
    )
    return _frames_to_speech_segments(
        smoothed_frames,
        frame_duration_ms=frame_duration_ms,
        min_speech_frames=max(1, min_speech_duration_ms // frame_duration_ms),
        duration_seconds=duration_seconds,
    )


def build_silence_segments(
    *,
    duration_seconds: float,
    speech_segments: list[dict[str, float]],
) -> list[dict[str, float]]:
    silence_segments: list[dict[str, float]] = []
    cursor = 0.0
    for segment in speech_segments:
        start_seconds = round(max(0.0, segment["start_seconds"]), 3)
        end_seconds = round(max(start_seconds, segment["end_seconds"]), 3)
        if start_seconds > cursor:
            silence_segments.append(
                {
                    "start_seconds": round(cursor, 3),
                    "end_seconds": start_seconds,
                }
            )
        cursor = max(cursor, end_seconds)
    if cursor < duration_seconds:
        silence_segments.append(
            {
                "start_seconds": round(cursor, 3),
                "end_seconds": round(duration_seconds, 3),
            }
        )
    return silence_segments


def _bridge_short_silence_runs(
    frames: list[bool],
    *,
    min_silence_frames: int,
) -> list[bool]:
    bridged = frames[:]
    index = 0
    while index < len(bridged):
        if bridged[index]:
            index += 1
            continue
        run_start = index
        while index < len(bridged) and not bridged[index]:
            index += 1
        run_end = index
        silence_length = run_end - run_start
        has_speech_before = run_start > 0 and bridged[run_start - 1]
        has_speech_after = run_end < len(bridged) and bridged[run_end]
        if has_speech_before and has_speech_after and silence_length < min_silence_frames:
            for silence_index in range(run_start, run_end):
                bridged[silence_index] = True
    return bridged


def _frames_to_speech_segments(
    frames: list[bool],
    *,
    frame_duration_ms: int,
    min_speech_frames: int,
    duration_seconds: float,
) -> list[dict[str, float]]:
    segments: list[dict[str, float]] = []
    index = 0
    while index < len(frames):
        if not frames[index]:
            index += 1
            continue
        run_start = index
        while index < len(frames) and frames[index]:
            index += 1
        run_end = index
        if run_end - run_start < min_speech_frames:
            continue
        start_seconds = round((run_start * frame_duration_ms) / 1000, 3)
        end_seconds = round(min(duration_seconds, (run_end * frame_duration_ms) / 1000), 3)
        segments.append(
            {
                "start_seconds": start_seconds,
                "end_seconds": max(start_seconds, end_seconds),
            }
        )
    return segments


def _compute_rms(chunk: bytes, sample_width: int) -> int:
    if sample_width != 2 or not chunk:
        return 0
    samples = array("h")
    samples.frombytes(chunk)
    if not samples:
        return 0
    mean_square = sum(sample * sample for sample in samples) / len(samples)
    return int(math.sqrt(mean_square))
