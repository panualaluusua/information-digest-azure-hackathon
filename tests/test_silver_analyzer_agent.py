"""
Tests for the Silver Analyzer Agent.
Mocks agent_framework so no Azure credentials needed.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Stub out agent_framework before importing the agent module
import sys

_mock_af = MagicMock()
_mock_af.Agent = MagicMock
_mock_af.FoundryChatClient = MagicMock
_mock_af.tools = MagicMock()
_mock_af.tools.structured_output_tool = lambda schema: MagicMock()
sys.modules["agent_framework"] = _mock_af
sys.modules["agent_framework.tools"] = _mock_af.tools

_mock_foundry = MagicMock()
_mock_foundry.FoundryChatClient = MagicMock
sys.modules["agent_framework_foundry"] = _mock_foundry

from src.models.silver import SilverBrief, RelevanceScore

VALID_BRIEF_JSON = json.dumps({
    "source_url": "https://example.com/article",
    "source_type": "rss",
    "title": "GPT-5 Released",
    "published_at": "2026-06-01T10:00:00Z",
    "what": "OpenAI released GPT-5.",
    "why_now": "First native multi-step tool orchestration.",
    "how": "Uses a new planner head.",
    "so_what": "Replaces custom orchestration glue.",
    "relevance_score": 5,
    "relevance_reason": "Direct impact on agentic workflows.",
    "tags": ["LLM", "Agents"],
})

INVALID_JSON = '{"source_url": "https://example.com", "relevance_score": 99}'
MALFORMED_JSON = "not json at all {{"


class TestSafeParse:
    def test_valid_json_returns_silver_brief(self, tmp_path):
        from src.agents.silver_analyzer_agent import _safe_parse
        with patch("src.agents.silver_analyzer_agent.SILVER", tmp_path):
            result = _safe_parse(VALID_BRIEF_JSON, tmp_path / "test.txt")
        assert result is not None
        assert result.title == "GPT-5 Released"
        assert result.relevance_score == RelevanceScore.PARADIGM_SHIFT

    def test_invalid_schema_writes_error_file(self, tmp_path):
        from src.agents.silver_analyzer_agent import _safe_parse
        with patch("src.agents.silver_analyzer_agent.SILVER", tmp_path):
            result = _safe_parse(INVALID_JSON, tmp_path / "bad.txt")
        assert result is None
        error_files = list(tmp_path.glob("_INVALID_*.json"))
        assert len(error_files) == 1

    def test_malformed_json_writes_error_file(self, tmp_path):
        from src.agents.silver_analyzer_agent import _safe_parse
        with patch("src.agents.silver_analyzer_agent.SILVER", tmp_path):
            result = _safe_parse(MALFORMED_JSON, tmp_path / "broken.txt")
        assert result is None
        error_files = list(tmp_path.glob("_INVALID_*.json"))
        assert len(error_files) == 1

    def test_error_file_contains_raw_output_excerpt(self, tmp_path):
        from src.agents.silver_analyzer_agent import _safe_parse
        with patch("src.agents.silver_analyzer_agent.SILVER", tmp_path):
            _safe_parse(MALFORMED_JSON, tmp_path / "broken.txt")
        error_file = list(tmp_path.glob("_INVALID_*.json"))[0]
        content = json.loads(error_file.read_text())
        assert "error" in content
        assert "raw_output" in content


class TestLoadProfile:
    def test_returns_profile_file_content(self, tmp_path):
        profile_dir = tmp_path / "profile"
        profile_dir.mkdir()
        profile_file = profile_dir / "ai_paradigm_lens.md"
        profile_file.write_text("Senior AI Engineer. Focus: LLMs.", encoding="utf-8")

        with patch("src.agents.silver_analyzer_agent.PROFILE_PATH", profile_file):
            from src.agents.silver_analyzer_agent import _load_profile
            result = _load_profile()
        assert "Senior AI Engineer" in result

    def test_returns_default_when_profile_missing(self, tmp_path):
        missing_path = tmp_path / "nonexistent.md"
        with patch("src.agents.silver_analyzer_agent.PROFILE_PATH", missing_path):
            from src.agents.silver_analyzer_agent import _load_profile
            result = _load_profile()
        assert len(result) > 0
        assert "Engineer" in result


class TestAnalyzeInboxFile:
    @pytest.mark.asyncio
    async def test_valid_llm_output_writes_silver_file(self, tmp_path):
        inbox_file = tmp_path / "test_article.txt"
        inbox_file.write_text("Some article content", encoding="utf-8")
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()

        mock_result = MagicMock()
        mock_result.content = VALID_BRIEF_JSON
        mock_agent = AsyncMock()
        mock_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.silver_analyzer_agent.SILVER", silver_dir), \
             patch("src.agents.silver_analyzer_agent.build_silver_agent", return_value=mock_agent), \
             patch("src.agents.silver_analyzer_agent.PROFILE_PATH", tmp_path / "missing.md"):
            from src.agents.silver_analyzer_agent import analyze_inbox_file
            out_path = await analyze_inbox_file(inbox_file)

        assert out_path is not None
        assert out_path.exists()
        brief = SilverBrief.model_validate_json(out_path.read_text())
        assert brief.title == "GPT-5 Released"

    @pytest.mark.asyncio
    async def test_invalid_llm_output_returns_none(self, tmp_path):
        inbox_file = tmp_path / "bad_article.txt"
        inbox_file.write_text("Some article content", encoding="utf-8")
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()

        mock_result = MagicMock()
        mock_result.content = MALFORMED_JSON
        mock_agent = AsyncMock()
        mock_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.silver_analyzer_agent.SILVER", silver_dir), \
             patch("src.agents.silver_analyzer_agent.build_silver_agent", return_value=mock_agent), \
             patch("src.agents.silver_analyzer_agent.PROFILE_PATH", tmp_path / "missing.md"):
            from src.agents.silver_analyzer_agent import analyze_inbox_file
            out_path = await analyze_inbox_file(inbox_file)

        assert out_path is None

    @pytest.mark.asyncio
    async def test_content_truncated_to_8000_chars(self, tmp_path):
        inbox_file = tmp_path / "long_article.txt"
        inbox_file.write_text("x" * 20000, encoding="utf-8")
        silver_dir = tmp_path / "silver_data"
        silver_dir.mkdir()

        mock_result = MagicMock()
        mock_result.content = VALID_BRIEF_JSON
        mock_agent = AsyncMock()
        mock_agent.run = AsyncMock(return_value=mock_result)

        with patch("src.agents.silver_analyzer_agent.SILVER", silver_dir), \
             patch("src.agents.silver_analyzer_agent.build_silver_agent", return_value=mock_agent), \
             patch("src.agents.silver_analyzer_agent.PROFILE_PATH", tmp_path / "missing.md"):
            from src.agents.silver_analyzer_agent import analyze_inbox_file
            await analyze_inbox_file(inbox_file)

        call_args = mock_agent.run.call_args[0][0]
        # The prompt should contain at most 8000 chars of content
        content_start = call_args.index("Content:\n") + len("Content:\n")
        content_in_prompt = call_args[content_start:]
        assert len(content_in_prompt) <= 8000
