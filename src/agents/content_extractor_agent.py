"""Content Extractor Agent: fan-out stage for the raw layer."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from agent_framework import Agent, MCPStdioTool

from src.agents.foundry_client import build_foundry_chat_client, response_text, run_agent_with_retries


INBOX = Path(__file__).parents[2] / "inbox"
INBOX.mkdir(exist_ok=True)


def build_extractor_agent(mcp_server_command: list[str], source_name: str) -> Agent:
    """Builds a content extractor agent wired to a single MCP server."""
    mcp_tool = MCPStdioTool(
        name=f"{source_name}-mcp",
        command=mcp_server_command[0],
        args=mcp_server_command[1:],
    )
    return Agent(
        client=build_foundry_chat_client(),
        name=f"ContentExtractor-{source_name}",
        tools=[mcp_tool],
        instructions=(
            "You are a content extraction agent. "
            "Use the available tools to fetch content from the requested source. "
            "Return the raw fetched content as-is. Do not summarize or editorialize. "
            "If a tool returns an error, return the error JSON so it can be logged."
        ),
    )


def save_to_inbox(content: str, source_label: str) -> Path:
    """Persists raw fetched content to inbox/ with a timestamped filename."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_label = source_label.replace("/", "-").replace(" ", "_")
    out_path = INBOX / f"{ts}_{safe_label}.txt"
    out_path.write_text(content, encoding="utf-8")
    return out_path


async def fetch_rss_source(feed_url: str) -> Path:
    """Fetches a single RSS/Atom feed and saves it to inbox."""
    print(f"[reasoning] FETCH source=rss url={feed_url}")
    agent = build_extractor_agent(
        mcp_server_command=["python", "src/mcp_servers/blog_fetcher.py"],
        source_name="blog",
    )
    result = await run_agent_with_retries(agent, f"Fetch the latest 5 articles from this RSS feed and return the full JSON: {feed_url}")
    label = feed_url.split("//")[-1].split("/")[0]
    return save_to_inbox(response_text(result), label)


async def fetch_youtube_channel(channel_id: str) -> Path:
    """Fetches recent YouTube videos from a channel and saves them to inbox."""
    print(f"[reasoning] FETCH source=youtube channel={channel_id}")
    agent = build_extractor_agent(
        mcp_server_command=["python", "src/mcp_servers/youtube_fetcher.py"],
        source_name="youtube",
    )
    result = await run_agent_with_retries(agent, f"Fetch the latest 5 videos from YouTube channel '{channel_id}' and return the full JSON.")
    return save_to_inbox(response_text(result), f"yt_{channel_id}")


async def fetch_github_org(org: str) -> Path:
    """Fetches recent GitHub activity from an org and saves it to inbox."""
    print(f"[reasoning] FETCH source=github org={org}")
    agent = build_extractor_agent(
        mcp_server_command=["python", "src/mcp_servers/github_fetcher.py"],
        source_name="github",
    )
    result = await run_agent_with_retries(
        agent,
        f"Fetch the most recently updated public repos from GitHub org '{org}' "
        "(last 7 days) and also their latest releases. Return the full JSON."
    )
    return save_to_inbox(response_text(result), f"gh_{org}")
