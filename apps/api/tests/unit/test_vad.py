import math
import struct
from pathlib import Path
import wave

from singlish_agent_api.infrastructure.audio.vad import (
    build_silence_segments,
    detect_speech_segments,
)


def _write_vad_test_wav(path: Path) -> None:
    sample_rate_hz = 16_000
    sections = [
        (0.3, 0.0),
        (0.4, 0.7),
        (0.3, 0.0),
    ]
    frames: list[bytes] = []
    for duration_seconds, amplitude in sections:
        sample_count = int(sample_rate_hz * duration_seconds)
        for index in range(sample_count):
            value = 0
            if amplitude:
                value = int(
                    math.sin((2 * math.pi * 440 * index) / sample_rate_hz) * amplitude * 32_767
                )
            frames.append(struct.pack("<h", value))

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(b"".join(frames))


def test_build_silence_segments_returns_gaps_between_speech_spans() -> None:
    silence = build_silence_segments(
        duration_seconds=5.0,
        speech_segments=[
            {"start_seconds": 0.5, "end_seconds": 1.5},
            {"start_seconds": 3.0, "end_seconds": 4.0},
        ],
    )

    assert silence == [
        {"start_seconds": 0.0, "end_seconds": 0.5},
        {"start_seconds": 1.5, "end_seconds": 3.0},
        {"start_seconds": 4.0, "end_seconds": 5.0},
    ]


def test_detect_speech_segments_finds_tone_between_silence(tmp_path: Path) -> None:
    audio_path = tmp_path / "speech-gap.wav"
    _write_vad_test_wav(audio_path)

    segments = detect_speech_segments(audio_path, duration_seconds=1.0)

    assert len(segments) == 1
    assert 0.2 <= segments[0]["start_seconds"] <= 0.4
    assert 0.6 <= segments[0]["end_seconds"] <= 0.8
