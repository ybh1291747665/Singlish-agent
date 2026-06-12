from __future__ import annotations


KNOWN_PATTERNS = {
    "wah lau eh this queue quite fast lah": {
        "standard_english": "Wow, this queue is quite fast.",
        "simplified_chinese": "\u54c7\uff0c\u8fd9\u4e2a\u961f\u4f0d\u8d70\u5f97\u5f88\u5feb\u3002",
        "glossary_hits": ["wah lau eh", "lah"],
    }
}


def normalize_transcript(raw_transcript: str) -> dict[str, object]:
    normalized_key = " ".join(raw_transcript.lower().strip().split())
    if normalized_key in KNOWN_PATTERNS:
        entry = KNOWN_PATTERNS[normalized_key]
        return {
            "normalized_transcript": raw_transcript,
            "standard_english": entry["standard_english"],
            "simplified_chinese": entry["simplified_chinese"],
            "glossary_hits": entry["glossary_hits"],
            "translation_provider": "fallback",
        }

    return {
        "normalized_transcript": raw_transcript,
        "standard_english": raw_transcript,
        "simplified_chinese": f"[translation pending] {raw_transcript}",
        "glossary_hits": [],
        "translation_provider": "fallback",
    }
