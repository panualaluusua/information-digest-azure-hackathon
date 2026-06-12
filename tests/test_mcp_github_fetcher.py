"""
Tests for the github_fetcher MCP server tool logic.
Mocks requests.get to avoid real GitHub API calls.
"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from src.mcp_servers.github_fetcher import fetch_org_repos, fetch_repo_releases


def _mock_response(data: list | dict, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    if status >= 400:
        resp.raise_for_status.side_effect = __import__("requests").HTTPError(
            response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


def _recent_iso() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat().replace("+00:00", "Z")


def _old_iso() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat().replace("+00:00", "Z")


SAMPLE_REPOS = [
    {
        "name": "semantic-kernel",
        "full_name": "microsoft/semantic-kernel",
        "description": "A framework for building AI agents",
        "html_url": "https://github.com/microsoft/semantic-kernel",
        "stargazers_count": 22000,
        "pushed_at": _recent_iso(),
        "topics": ["ai", "agents", "dotnet"],
    },
    {
        "name": "old-project",
        "full_name": "microsoft/old-project",
        "description": "Old",
        "html_url": "https://github.com/microsoft/old-project",
        "stargazers_count": 5,
        "pushed_at": _old_iso(),
        "topics": [],
    },
]

SAMPLE_RELEASES = [
    {
        "tag_name": "v1.0.0",
        "name": "Version 1.0.0",
        "published_at": _recent_iso(),
        "html_url": "https://github.com/microsoft/semantic-kernel/releases/tag/v1.0.0",
        "body": "Major release with new features.",
    }
]


class TestFetchOrgRepos:
    def test_returns_repos_within_time_window(self):
        with patch("requests.get", return_value=_mock_response(SAMPLE_REPOS)):
            result = fetch_org_repos("microsoft", days_back=7)
            data = json.loads(result)
            assert data["org"] == "microsoft"
            # Only the recent repo should pass the cutoff filter
            assert len(data["repos"]) == 1
            assert data["repos"][0]["name"] == "semantic-kernel"

    def test_filters_out_old_repos(self):
        with patch("requests.get", return_value=_mock_response(SAMPLE_REPOS)):
            result = fetch_org_repos("microsoft", days_back=1)
            data = json.loads(result)
            names = [r["name"] for r in data["repos"]]
            assert "old-project" not in names

    def test_repo_fields_present(self):
        with patch("requests.get", return_value=_mock_response([SAMPLE_REPOS[0]])):
            result = fetch_org_repos("microsoft")
            data = json.loads(result)
            repo = data["repos"][0]
            assert "name" in repo
            assert "url" in repo
            assert "stars" in repo
            assert "description" in repo

    def test_rate_limit_returns_friendly_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = __import__("requests").HTTPError(
            response=mock_resp
        )
        with patch("requests.get", return_value=mock_resp):
            result = fetch_org_repos("microsoft")
            data = json.loads(result)
            assert "error" in data
            assert "GITHUB_TOKEN" in data["error"]

    def test_network_error_returns_error_json(self):
        with patch("requests.get", side_effect=ConnectionError("timeout")):
            result = fetch_org_repos("microsoft")
            data = json.loads(result)
            assert "error" in data

    def test_empty_org_returns_empty_list(self):
        with patch("requests.get", return_value=_mock_response([])):
            result = fetch_org_repos("emptyorg")
            data = json.loads(result)
            assert data["repos"] == []


class TestFetchRepoReleases:
    def test_returns_release_data(self):
        with patch("requests.get", return_value=_mock_response(SAMPLE_RELEASES)):
            result = fetch_repo_releases("microsoft", "semantic-kernel", max_releases=5)
            data = json.loads(result)
            assert data["repo"] == "microsoft/semantic-kernel"
            assert len(data["releases"]) == 1
            assert data["releases"][0]["tag"] == "v1.0.0"

    def test_release_body_truncated_to_1000_chars(self):
        long_body_release = [{**SAMPLE_RELEASES[0], "body": "x" * 2000}]
        with patch("requests.get", return_value=_mock_response(long_body_release)):
            result = fetch_repo_releases("owner", "repo")
            data = json.loads(result)
            assert len(data["releases"][0]["body"]) == 1000

    def test_no_releases_returns_empty_list(self):
        with patch("requests.get", return_value=_mock_response([])):
            result = fetch_repo_releases("owner", "repo")
            data = json.loads(result)
            assert data["releases"] == []

    def test_network_error_returns_error_json(self):
        with patch("requests.get", side_effect=ConnectionError("timeout")):
            result = fetch_repo_releases("owner", "repo")
            data = json.loads(result)
            assert "error" in data
