import asyncio
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile


TARGET_SAMPLE_RATE_HZ = 16_000
TARGET_CHANNELS = 1
TARGET_NORMALIZED_FORMAT = "pcm_s16le"


@dataclass
class PreprocessedAudioResult:
    audio_path: Path
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    normalized_format: str


async def preprocess_audio_file(input_path: Path) -> PreprocessedAudioResult:
    return await asyncio.to_thread(_preprocess_audio_file_blocking, input_path)


def _preprocess_audio_file_blocking(input_path: Path) -> PreprocessedAudioResult:
    try:
        import av
        from av.audio.resampler import AudioResampler
    except ImportError as exc:
        raise RuntimeError("PyAV is required for audio preprocessing.") from exc

    temp_file = NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()
    output_path = Path(temp_file.name)

    total_samples = 0
    try:
        with av.open(str(input_path)) as input_container:
            audio_stream = next(
                (stream for stream in input_container.streams if stream.type == "audio"),
                None,
            )
            if audio_stream is None:
                raise ValueError("audio file does not contain an audio stream")

            resampler = AudioResampler(
                format="s16",
                layout="mono",
                rate=TARGET_SAMPLE_RATE_HZ,
            )

            with av.open(str(output_path), mode="w", format="wav") as output_container:
                output_stream = output_container.add_stream(
                    TARGET_NORMALIZED_FORMAT,
                    rate=TARGET_SAMPLE_RATE_HZ,
                )
                output_stream.layout = "mono"

                for frame in input_container.decode(audio=audio_stream.index):
                    resampled_frames = resampler.resample(frame)
                    if resampled_frames is None:
                        continue
                    if not isinstance(resampled_frames, list):
                        resampled_frames = [resampled_frames]

                    for resampled_frame in resampled_frames:
                        total_samples += resampled_frame.samples
                        for packet in output_stream.encode(resampled_frame):
                            output_container.mux(packet)

                for packet in output_stream.encode(None):
                    output_container.mux(packet)
    except Exception:
        output_path.unlink(missing_ok=True)
        raise

    if total_samples <= 0:
        output_path.unlink(missing_ok=True)
        raise ValueError("audio preprocessing produced no samples")

    return PreprocessedAudioResult(
        audio_path=output_path,
        duration_seconds=round(total_samples / TARGET_SAMPLE_RATE_HZ, 3),
        sample_rate_hz=TARGET_SAMPLE_RATE_HZ,
        channels=TARGET_CHANNELS,
        normalized_format=TARGET_NORMALIZED_FORMAT,
    )
