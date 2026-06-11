import asyncio
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from singlish_agent_api.core.config import settings


@dataclass
class ASRSegmentResult:
    start_seconds: float
    end_seconds: float
    text: str
    confidence: float | None


@dataclass
class ASRTranscriptionResult:
    provider: str
    raw_transcript: str
    segments: list[ASRSegmentResult]


class TranscriptionProvider(Protocol):
    async def transcribe(self, audio_path: Path) -> ASRTranscriptionResult: ...


class FakeTranscriptionProvider:
    async def transcribe(self, audio_path: Path) -> ASRTranscriptionResult:
        return ASRTranscriptionResult(
            provider="fake",
            raw_transcript="wah lau eh this queue quite fast lah",
            segments=[
                ASRSegmentResult(
                    start_seconds=0.0,
                    end_seconds=2.4,
                    text="wah lau eh this queue quite fast lah",
                    confidence=0.94,
                )
            ],
        )


@lru_cache(maxsize=1)
def _load_whisper_model():
    from faster_whisper import WhisperModel

    return WhisperModel(
        settings.asr_model_size,
        device=settings.asr_device,
        compute_type=settings.asr_compute_type,
    )


class FasterWhisperTranscriptionProvider:
    async def transcribe(self, audio_path: Path) -> ASRTranscriptionResult:
        return await asyncio.to_thread(self._transcribe_blocking, audio_path)

    def _transcribe_blocking(self, audio_path: Path) -> ASRTranscriptionResult:
        model = _load_whisper_model()
        segment_iter, _info = model.transcribe(str(audio_path), language="en", vad_filter=True)

        segments = [
            ASRSegmentResult(
                start_seconds=float(segment.start),
                end_seconds=float(segment.end),
                text=segment.text.strip(),
                confidence=None,
            )
            for segment in segment_iter
            if segment.text.strip()
        ]
        raw_transcript = " ".join(segment.text for segment in segments).strip()

        return ASRTranscriptionResult(
            provider="faster_whisper",
            raw_transcript=raw_transcript,
            segments=segments,
        )


class AutoTranscriptionProvider:
    def __init__(self) -> None:
        self._fake = FakeTranscriptionProvider()
        self._real = FasterWhisperTranscriptionProvider()

    async def transcribe(self, audio_path: Path) -> ASRTranscriptionResult:
        try:
            result = await self._real.transcribe(audio_path)
            if result.raw_transcript:
                return result
        except Exception:
            pass
        return await self._fake.transcribe(audio_path)


def get_transcription_provider() -> TranscriptionProvider:
    if settings.asr_backend == "fake":
        return FakeTranscriptionProvider()
    if settings.asr_backend == "faster_whisper":
        return FasterWhisperTranscriptionProvider()
    return AutoTranscriptionProvider()
