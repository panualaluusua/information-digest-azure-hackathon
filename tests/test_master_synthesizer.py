"""
Tests for the Master Synthesizer Agent (Gold layer).
Mocks agent_framework and filesystem.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import sys
if "agent_framework" not in sys.modules:
    _mock_af = MagicMock()
    _mock_af.Agent = MagicMock
    sys.modules["agent_framework"] = _mock_af
if "agent_framework_foundry" not in sys.modules:
    _mock_foundry = MagicMock()
    _mock_foundry.FoundryChatClient = MagicMock
    sys.modules["agent_framework_foundry"] = _mock_foundry

from src.models.silver import SilverBrief, RelevanceScore

BRIEF_SCORE_5 = {
    "source_url": "https://example.com/gpt5",
    "source_type": "rss",
    "title": "GPT-5 Released",
    "published_at": "2026-06-01T10:00:00Z",
    "what": "GPT-5 released.",
    "why_now": "Native tool orchestration.",
    "how": "Planner head.",
    "so_what": "Replaces custom glue.",
    "relevance_score": 5,
    "relevance_reason": "Paradigm shift.",
    "tags": ["LLM"],
}
BRIEF_SCORE_3 = {**BRIEF_SCORE_5, "source_url": "https://example.com/trend",
                  "title": "Azure Update", "relevance_score": 3, "tags": ["Azure"]}
BRIEF_SCORE_2 = {**BRIEF_SCORE_5, "source_url": "https://example.com/noise",
                  "title": "CSS Grid update", "relevance_score": 2, "tags": []}


def _write_briefs(silver_dir: Path, briefs: list[dict]) -> None:
    for b in briefs:
        path = silver_dir / f"{b['title'].replace(' ', '_')}.json"
        path.write_text(json.dumps(b), encoding="utf-8")


class TestLoadGoldCandidates:
    def test_only_returns_score_3_and_above(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        _write_briefs(silver_dir, [BRIEF_SCORE_5, BRIEF_SCORE_3, BRIEF_SCORE_2])

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir):
            from src.agents.master_synthesizer_agent import _load_gold_candidates
            candidates = _load_gold_candidates()

        assert len(candidates) == 2
        assert all(c.relevance_score >= 3 for c in candidates)

    def test_sorted_by_score_descending(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        _write_briefs(silver_dir, [BRIEF_SCORE_3, BRIEF_SCORE_5])

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir):
            from src.agents.master_synthesizer_agent import _load_gold_candidates
            candidates = _load_gold_candidates()

        assert candidates[0].relevance_score == 5

    def test_skips_invalid_files(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        (silver_dir / "broken.json").write_text("not json {{", encoding="utf-8")
        _write_briefs(silver_dir, [BRIEF_SCORE_5])

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir):
            from src.agents.master_synthesizer_agent import _load_gold_candidates
            candidates = _load_gold_candidates()

        assert len(candidates) == 1

    def test_skips_invalid_prefix_files(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        (silver_dir / "_INVALID_something.json").write_text(
            json.dumps(BRIEF_SCORE_5), encoding="utf-8"
        )

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir):
            from src.agents.master_synthesizer_agent import _load_gold_candidates
            candidates = _load_gold_candidates()

        assert len(candidates) == 0


class TestSynthesize:
    @pytest.mark.asyncio
    async def test_empty_candidates_writes_empty_digest(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        gold_dir = tmp_path / "gold_synthesis"
        gold_dir.mkdir()

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir), \
             patch("src.agents.master_synthesizer_agent.GOLD", gold_dir):
            from src.agents.master_synthesizer_agent import synthesize
            digest, path = await synthesize()

        assert path.exists()
        assert "No content" in digest

    @pytest.mark.asyncio
    async def test_with_candidates_calls_agent(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        gold_dir = tmp_path / "gold_synthesis"
        gold_dir.mkdir()
        _write_briefs(silver_dir, [BRIEF_SCORE_5])

        mock_result = MagicMock()
        mock_result.content = "# Weekly Digest\n\nGreat week for LLMs."
        mock_agent = AsyncMock()
        mock_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir), \
             patch("src.agents.master_synthesizer_agent.GOLD", gold_dir), \
             patch("src.agents.master_synthesizer_agent.build_synthesizer_agent",
                   return_value=mock_agent), \
             patch("src.agents.master_synthesizer_agent.PROFILE_PATH", tmp_path / "missing.md"):
            from src.agents.master_synthesizer_agent import synthesize
            digest, path = await synthesize()

        assert path.exists()
        assert "Weekly Digest" in digest
        mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_digest_written_to_gold_dir(self, tmp_path):
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()
        gold_dir = tmp_path / "gold_synthesis"
        gold_dir.mkdir()
        _write_briefs(silver_dir, [BRIEF_SCORE_5])

        mock_result = MagicMock()
        mock_result.content = "# Digest"
        mock_agent = AsyncMock()
        mock_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.master_synthesizer_agent.SILVER", silver_dir), \
             patch("src.agents.master_synthesizer_agent.GOLD", gold_dir), \
             patch("src.agents.master_synthesizer_agent.build_synthesizer_agent",
                   return_value=mock_agent), \
             patch("src.agents.master_synthesizer_agent.PROFILE_PATH", tmp_path / "missing.md"):
            from src.agents.master_synthesizer_agent import synthesize
            _, path = await synthesize()

        assert path.parent == gold_dir
        assert path.suffix == ".md"
