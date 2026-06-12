"""
Main orchestrator — runs the full Information Digest pipeline.

Pipeline:
  1. Ingest: Fetch content from all configured sources (parallel)
  2. Enrich: Analyze and score each inbox file
  3. Synthesize: Combine top-scored briefs into a weekly digest
  4. Publish: Post the digest to Teams

Usage:
  python -m src.orchestrator

Configure sources in sources.json (created on first run if missing).
"""

from __future__ import annotations
import asyncio
import json
import os
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from opentelemetry import trace

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore", category=UserWarning, module="agent_framework")

load_dotenv()

# --- Optional Azure Monitor telemetry ---
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_azure_monitor()
except ImportError:
    pass  # azure-monitor-opentelemetry not installed — telemetry silently disabled

tracer = trace.get_tracer("information-digest")

SOURCES_FILE = Path(__file__).parent.parent / "sources.json"
MAX_SOURCES_PER_RUN = int(os.getenv("MAX_SOURCES_PER_RUN", "3"))

DEFAULT_SOURCES = {
    "rss_feeds": [
        "https://feeds.feedburner.com/oreilly/radar",
        "https://blog.langchain.dev/rss/"
    ],
    "youtube_channels": [],   # Add channel IDs here, e.g. "UCVHZiUmPe6eL8b3-qSANLSQ"
    "github_orgs": [
        "microsoft",
        "openai"
    ]
}


def _load_sources() -> dict:
    if not SOURCES_FILE.exists():
        SOURCES_FILE.write_text(json.dumps(DEFAULT_SOURCES, indent=2), encoding="utf-8")
        print(f"[orchestrator] Created default sources.json — edit to customize your sources.")
    return json.loads(SOURCES_FILE.read_text(encoding="utf-8"))


async def run_pipeline() -> None:
    from src.agents.content_extractor_agent import (
        fetch_rss_source, fetch_youtube_channel, fetch_github_org
    )
    from src.agents.silver_analyzer_agent import analyze_all_inbox
    from src.agents.master_synthesizer_agent import synthesize
    from src.integrations.teams_notifier import post_digest_to_teams

    with tracer.start_as_current_span("information-digest-pipeline"):
        sources = _load_sources()
        week = datetime.now(timezone.utc).strftime("%Y-W%W")
        print(f"[orchestrator] Starting pipeline for {week}")
        print("[reasoning] PLAN fetch -> score -> filter -> synthesize -> notify")

        # --- Stage 1: Fan-Out extraction (sequential to avoid quota flooding) ---
        with tracer.start_as_current_span("stage-1-extraction"):
            all_sources = (
                [("rss", url) for url in sources.get("rss_feeds", [])] +
                [("youtube", ch) for ch in sources.get("youtube_channels", [])] +
                [("github", org) for org in sources.get("github_orgs", [])]
            )
            total_sources = len(all_sources)
            if MAX_SOURCES_PER_RUN >= 0 and len(all_sources) > MAX_SOURCES_PER_RUN:
                all_sources = all_sources[:MAX_SOURCES_PER_RUN]
                print(f"[orchestrator] Cost guard: limited sources to {len(all_sources)}/{total_sources} this run.")

            ok_count = 0
            for kind, value in all_sources:
                try:
                    if kind == "rss":
                        await fetch_rss_source(value)
                    elif kind == "youtube":
                        await fetch_youtube_channel(value)
                    else:
                        await fetch_github_org(value)
                    ok_count += 1
                except Exception as e:
                    print(f"[orchestrator] Extraction error (non-fatal): {e}")
            print(f"[orchestrator] Fetched {ok_count}/{len(all_sources)} sources OK")

        # --- Stage 2: Enrich and score ---
        with tracer.start_as_current_span("stage-2-silver"):
            silver_paths = await analyze_all_inbox()
            print(f"[orchestrator] Analyzed {len(silver_paths)} inbox files -> silver_data/")

        # --- Stage 3: Digest synthesis ---
        with tracer.start_as_current_span("stage-3-gold"):
            digest, gold_path = await synthesize()
            print(f"[orchestrator] Weekly digest written to {gold_path}")

        # --- Stage 4: Publish ---
        with tracer.start_as_current_span("stage-4-publish"):
            print(f"[orchestrator] Finalizing delivery...")
            # Markdown file is our primary sink for the hackathon
            print(f"[orchestrator] Primary output: {gold_path.absolute()}")

            # Optional secondary sink (Teams)
            teams_url = os.getenv("TEAMS_WEBHOOK_URL", "")
            if teams_url and "your-org" not in teams_url and "example" not in teams_url:
                post_digest_to_teams(digest, week)
            else:
                print("[orchestrator] Teams notification skipped (TEAMS_WEBHOOK_URL not configured).")

    print(f"\n[SUCCESS] Pipeline complete. Your weekly digest is ready at:")
    print(f"👉 {gold_path.absolute()}")


def _exception_handler(loop: asyncio.AbstractEventLoop, context: dict) -> None:
    """Suppress known MCP/anyio async-generator cleanup noise on Windows."""
    exc = context.get("exception")
    msg = context.get("message", "")
    if isinstance(exc, RuntimeError) and "cancel scope" in str(exc):
        return
    if "closing of asynchronous generator" in msg and "stdio_client" in str(context.get("asyncgen", "")):
        return
    loop.default_exception_handler(context)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.set_exception_handler(_exception_handler)
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_pipeline())
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()
