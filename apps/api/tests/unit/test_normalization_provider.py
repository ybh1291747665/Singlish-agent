from singlish_agent_api.infrastructure.normalization.provider import normalize_transcript


def test_normalize_transcript_returns_english_and_chinese_outputs() -> None:
    result = normalize_transcript("wah lau eh this queue quite fast lah")

    assert result["standard_english"] == "Wow, this queue is quite fast."
    assert (
        result["simplified_chinese"]
        == "\u54c7\uff0c\u8fd9\u4e2a\u961f\u4f0d\u8d70\u5f97\u5f88\u5feb\u3002"
    )
    assert result["translation_provider"] == "fallback"
    assert result["glossary_hits"] == ["wah lau eh", "lah"]


def test_normalize_transcript_marks_pending_translation_for_unknown_text() -> None:
    result = normalize_transcript("Meeting starts at nine.")

    assert result["standard_english"] == "Meeting starts at nine."
    assert result["simplified_chinese"] == "[translation pending] Meeting starts at nine."
    assert result["translation_provider"] == "fallback"
    assert result["glossary_hits"] == []
