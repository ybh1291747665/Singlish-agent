from pathlib import Path
import wave

from singlish_agent_api.scripts.generate_eval_manifest import build_manifest_rows


def _write_test_wav(path: Path, *, sample_rate_hz: int = 16_000, duration_seconds: float = 0.5) -> None:
    frame_count = int(sample_rate_hz * duration_seconds)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(b"\x00\x00" * frame_count)


def test_build_manifest_rows_scaffolds_expected_fields(tmp_path: Path) -> None:
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    sample = audio_dir / "clip-one.wav"
    _write_test_wav(sample)

    rows = build_manifest_rows(audio_dir=audio_dir, dataset_root=tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row["clip_id"] == "clip-one"
    assert row["relative_audio_path"] == "audio/clip-one.wav"
    assert row["duration_seconds"] == 0.5
    assert row["scenario"] == "unknown"
    assert row["speaker_id"] == "unknown"
    assert row["languages"] == []
    assert row["reference_transcript"] == ""
    assert row["reference_standard_english"] == ""
    assert row["simplified_chinese"] == ""
    assert row["glossary_terms"] == []
    assert row["contains_code_switching"] is False
    assert row["contains_background_noise"] is False
    assert row["source_type"] == "unknown"
    assert row["consent_status"] == "unknown"
    assert row["split"] == "unassigned"
    assert row["notes"] == ""
