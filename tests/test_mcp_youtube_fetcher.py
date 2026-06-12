"""
Tests for the youtube_fetcher MCP server stub.
Verifies that the stub behaves correctly and guides users to the real API.
"""

import json
import os
import pytest
from unittest.mock import patch

from src.mcp_servers.youtube_fetcher import (
    fetch_youtube_channel,
    get_youtube_setup_status,
    _youtube_api_stub,
    _fetch_transcript_stub,
)


class TestYoutubeStub:
    def test_stub_returns_empty_list(self):
        """Stub must return empty list — real impl replaces it."""
        result = _youtube_api_stub("UCtest123", max_results=5)
        assert result == []

    def test_transcript_stub_returns_none(self):
        result = _fetch_transcript_stub("dQw4w9WgXcQ")
        assert result is None


class TestFetchYoutubeChannel:
    def test_missing_api_key_returns_error_json(self):
        with patch.dict(os.environ, {}, clear=True):
            # Ensure key is absent
            os.environ.pop("YOUTUBE_API_KEY", None)
            result = fetch_youtube_channel("UCtest")
            data = json.loads(result)
            assert "error" in data
            assert "YOUTUBE_API_KEY" in data["error"]

    def test_missing_api_key_includes_setup_url(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("YOUTUBE_API_KEY", None)
            result = fetch_youtube_channel("UCtest")
            data = json.loads(result)
            assert "setup_url" in data
            assert "console.cloud.google.com" in data["setup_url"]

    def test_with_api_key_but_stub_returns_empty_videos(self):
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake-key"}):
            result = fetch_youtube_channel("UCtest", max_results=5)
            data = json.loads(result)
            assert data["channel_id"] == "UCtest"
            assert data["videos"] == []

    def test_result_is_valid_json(self):
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake-key"}):
            result = fetch_youtube_channel("UCtest")
            json.loads(result)  # must not raise


class TestGetYoutubeSetupStatus:
    def test_not_configured_when_key_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("YOUTUBE_API_KEY", None)
            result = get_youtube_setup_status()
            data = json.loads(result)
            assert data["configured"] is False
            assert data["api_key_set"] is False

    def test_configured_when_key_present(self):
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "some-key"}):
            result = get_youtube_setup_status()
            data = json.loads(result)
            assert data["configured"] is True
            assert data["api_key_set"] is True

    def test_includes_setup_instructions(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("YOUTUBE_API_KEY", None)
            result = get_youtube_setup_status()
            data = json.loads(result)
            assert "instructions" in data
