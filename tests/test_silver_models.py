"""
Tests for Silver layer Pydantic schemas.
No network or Azure credentials needed.
"""

import json
import pytest
from pydantic import ValidationError

from src.models.silver import SilverBrief, SilverBatch, RelevanceScore


VALID_BRIEF = {
    "source_url": "https://example.com/article",
    "source_type": "rss",
    "title": "GPT-5 Released",
    "published_at": "2026-06-01T10:00:00Z",
    "what": "OpenAI released GPT-5 with native multi-step tool orchestration.",
    "why_now": "It is the first model to autonomously chain API calls without prompting.",
    "how": "Uses a new internal planner head trained on synthetic agentic traces.",
    "so_what": "Data engineers can replace custom orchestration glue with a single model call.",
    "relevance_score": 5,
    "relevance_reason": "Direct impact on agentic AI engineering workflows.",
    "tags": ["LLM", "Agents", "OpenAI"],
}


class TestSilverBrief:
    def test_valid_brief_parses(self):
        brief = SilverBrief.model_validate(VALID_BRIEF)
        assert brief.title == "GPT-5 Released"
        assert brief.relevance_score == RelevanceScore.PARADIGM_SHIFT

    def test_missing_required_field_raises(self):
        bad = {**VALID_BRIEF}
        del bad["what"]
        with pytest.raises(ValidationError) as exc_info:
            SilverBrief.model_validate(bad)
        assert "what" in str(exc_info.value)

    def test_invalid_source_type_raises(self):
        bad = {**VALID_BRIEF, "source_type": "telegram"}
        with pytest.raises(ValidationError):
            SilverBrief.model_validate(bad)

    def test_score_out_of_range_raises(self):
        bad = {**VALID_BRIEF, "relevance_score": 6}
        with pytest.raises(ValidationError):
            SilverBrief.model_validate(bad)

    def test_score_zero_raises(self):
        bad = {**VALID_BRIEF, "relevance_score": 0}
        with pytest.raises(ValidationError):
            SilverBrief.model_validate(bad)

    def test_optional_how_can_be_none(self):
        brief_data = {**VALID_BRIEF, "how": None}
        brief = SilverBrief.model_validate(brief_data)
        assert brief.how is None

    def test_optional_published_at_can_be_none(self):
        brief_data = {**VALID_BRIEF, "published_at": None}
        brief = SilverBrief.model_validate(brief_data)
        assert brief.published_at is None

    def test_tags_default_to_empty_list(self):
        brief_data = {k: v for k, v in VALID_BRIEF.items() if k != "tags"}
        brief = SilverBrief.model_validate(brief_data)
        assert brief.tags == []

    def test_roundtrip_json(self):
        brief = SilverBrief.model_validate(VALID_BRIEF)
        serialized = brief.model_dump_json()
        restored = SilverBrief.model_validate_json(serialized)
        assert restored.title == brief.title
        assert restored.relevance_score == brief.relevance_score


class TestSilverBatch:
    def _make_brief(self, score: int, url: str = "https://example.com") -> dict:
        return {**VALID_BRIEF, "relevance_score": score, "source_url": url}

    def test_gold_candidates_filters_below_3(self):
        batch = SilverBatch(
            week="2026-W23",
            items=[
                SilverBrief.model_validate(self._make_brief(1, "https://a.com")),
                SilverBrief.model_validate(self._make_brief(2, "https://b.com")),
                SilverBrief.model_validate(self._make_brief(3, "https://c.com")),
                SilverBrief.model_validate(self._make_brief(4, "https://d.com")),
                SilverBrief.model_validate(self._make_brief(5, "https://e.com")),
            ]
        )
        candidates = batch.gold_candidates
        assert len(candidates) == 3
        assert all(c.relevance_score >= 3 for c in candidates)

    def test_empty_batch_has_no_candidates(self):
        batch = SilverBatch(week="2026-W23", items=[])
        assert batch.gold_candidates == []

    def test_all_noise_yields_no_candidates(self):
        batch = SilverBatch(
            week="2026-W23",
            items=[
                SilverBrief.model_validate(self._make_brief(1, "https://a.com")),
                SilverBrief.model_validate(self._make_brief(2, "https://b.com")),
            ]
        )
        assert batch.gold_candidates == []


class TestRelevanceScore:
    def test_all_values_valid(self):
        for v in [1, 2, 3, 4, 5]:
            assert RelevanceScore(v) == v

    def test_human_readable_names(self):
        assert RelevanceScore.PARADIGM_SHIFT == 5
        assert RelevanceScore.CRITICAL_SKILL == 4
        assert RelevanceScore.TREND == 3
        assert RelevanceScore.BACKGROUND == 2
        assert RelevanceScore.NOISE == 1
