"""
GitHub MCP Server — fetches recent repository activity from public GitHub organizations.

Uses the official GitHub REST API v3.
Optional GITHUB_TOKEN raises rate limit from 60 to 5000 req/h.
"""

import json
import os
from datetime import datetime, timezone, timedelta
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GitHubFetcher")

GITHUB_API_BASE = "https://api.github.com"


def _headers() -> dict:
    token = os.getenv("GITHUB_TOKEN")
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


@mcp.tool()
def fetch_org_repos(org: str, days_back: int = 7, max_repos: int = 10) -> str:
    """
    Fetches recently updated public repositories from a GitHub organization.

    Args:
        org: GitHub organization name (e.g. 'microsoft', 'openai')
        days_back: Only include repos updated within this many days
        max_repos: Maximum number of repositories to return
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        url = f"{GITHUB_API_BASE}/orgs/{org}/repos"
        params = {"type": "public", "sort": "updated", "direction": "desc", "per_page": max_repos}
        resp = requests.get(url, headers=_headers(), params=params, timeout=15)
        resp.raise_for_status()

        repos = []
        for repo in resp.json():
            pushed = repo.get("pushed_at")
            if pushed:
                pushed_dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
                if pushed_dt < cutoff:
                    continue
            repos.append({
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description"),
                "url": repo["html_url"],
                "stars": repo.get("stargazers_count", 0),
                "pushed_at": pushed,
                "topics": repo.get("topics", [])
            })

        return json.dumps({"org": org, "repos": repos}, ensure_ascii=False)

    except requests.HTTPError as e:
        if e.response.status_code == 403:
            return json.dumps({
                "error": "Rate limited. Set GITHUB_TOKEN in .env to increase limit to 5000 req/h.",
                "docs": "https://github.com/settings/tokens"
            })
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def fetch_repo_releases(owner: str, repo: str, max_releases: int = 5) -> str:
    """
    Fetches the latest releases from a specific GitHub repository.

    Args:
        owner: Repository owner (org or user)
        repo: Repository name
        max_releases: Maximum number of releases to return
    """
    try:
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases"
        resp = requests.get(url, headers=_headers(), params={"per_page": max_releases}, timeout=15)
        resp.raise_for_status()

        releases = [
            {
                "tag": r["tag_name"],
                "name": r["name"],
                "published_at": r["published_at"],
                "url": r["html_url"],
                "body": r.get("body", "")[:1000]
            }
            for r in resp.json()
        ]
        return json.dumps({"repo": f"{owner}/{repo}", "releases": releases}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="stdio")
