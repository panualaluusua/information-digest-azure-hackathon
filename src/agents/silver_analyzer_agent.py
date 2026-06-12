"""Analyzer Agent: enrich and rank stage.

Reads each file in inbox/, calls the Foundry-backed model to produce a
structured SilverBrief, validates it with Pydantic, and writes the result
to silver_data/.
"""

from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from agent_framework import Agent
from pydantic import ValidationError

from src.agents.foundry_client import build_foundry_chat_client, response_text, run_agent_with_retries
from src.models.silver import SilverBrief

INBOX = Path(__file__).parents[2] / "inbox"
SILVER = Path(__file__).parents[2] / "silver_data"
SILVER.mkdir(exist_ok=True)

PROFILE_PATH = Path(__file__).parents[2] / "profile" / "ai_paradigm_lens.md"
MAX_INBOX_ITEMS_PER_RUN = int(os.getenv("MAX_INBOX_ITEMS_PER_RUN", "5"))
MAX_CONTENT_CHARS_PER_ITEM = int(os.getenv("MAX_CONTENT_CHARS_PER_ITEM", "8000"))


def _load_profile() -> str:
    if PROFILE_PATH.exists():
        return PROFILE_PATH.read_text(encoding="utf-8")
    return "Senior Data/AI Engineer. Focus: LLMs, Data Engineering, MLOps, Azure AI."


def build_silver_agent(profile: str) -> Agent:
    return Agent(
        client=build_foundry_chat_client(),
        name="SilverAnalyzer",
        instructions=f"""You are a content analysis agent for a senior Data/AI engineer.

Your job: read raw fetched content (article, video metadata, GitHub activity) and produce
a structured JSON analysis using this JSON schema:

{json.dumps(SilverBrief.model_json_schema(), indent=2)}

USER PROFILE (use this to determine relevance_score):
{profile}

SCORING GUIDE:
5 = Paradigm Shift — fundamentally changes how the user works
4 = Critical Skill — directly applicable, high practical value
3 = Interesting Trend — worth tracking, no immediate action needed
2 = Background Noise — mildly interesting, off-profile
1 = Noise — marketing, generic hype, irrelevant

Return ONLY valid JSON matching the SilverBrief schema. No prose, no markdown fences.""",
    )


def _safe_parse(raw_json: str, source_path: Path) -> SilverBrief | None:
    """Validates LLM output against SilverBrief schema; returns None on failure."""
    try:
        data = json.loads(raw_json)
        return SilverBrief.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        error_path = SILVER / f"_INVALID_{source_path.stem}.json"
        error_path.write_text(
            json.dumps({"error": str(e), "raw_output": raw_json[:500]}, ensure_ascii=False),
            encoding="utf-8"
        )
        return None


async def analyze_inbox_file(inbox_file: Path) -> Path | None:
    """
    Analyzes a single inbox file and writes a validated scored brief to silver_data/.

    Returns the output path, or None if validation failed.
    """
    profile = _load_profile()
    agent = build_silver_agent(profile)
    raw_content = inbox_file.read_text(encoding="utf-8")

    result = await run_agent_with_retries(
        agent,
        f"Analyze the following content and return a SilverBrief JSON.\n\n"
        f"Source file: {inbox_file.name}\n\n"
        f"Content:\n{raw_content[:MAX_CONTENT_CHARS_PER_ITEM]}"
    )

    brief = _safe_parse(response_text(result), inbox_file)
    if brief is None:
        print(f"[reasoning] VALIDATE file={inbox_file.name} decision=invalid_schema")
        return None

    out_path = SILVER / f"{inbox_file.stem}.json"
    out_path.write_text(
        brief.model_dump_json(indent=2),
        encoding="utf-8"
    )
    decision = "routed_to_gold" if brief.relevance_score >= 3 else "discarded_as_noise"
    print(
        f"[reasoning] SCORE file={inbox_file.name} "
        f"score={int(brief.relevance_score)} decision={decision} title={brief.title!r}"
    )
    return out_path


async def analyze_all_inbox() -> list[Path]:
    """Processes all unanalyzed files in inbox/ and returns successful output paths."""
    processed_paths = {p.stem for p in SILVER.glob("*.json") if not p.stem.startswith("_INVALID")}
    inbox_files = [
        f for f in INBOX.glob("*.txt")
        if f.stem not in processed_paths
    ]
    total_files = len(inbox_files)
    if MAX_INBOX_ITEMS_PER_RUN >= 0:
        inbox_files = inbox_files[:MAX_INBOX_ITEMS_PER_RUN]
    if len(inbox_files) < total_files:
        print(
            f"[silver_analyzer] Cost guard: limited inbox analysis "
            f"to {len(inbox_files)}/{total_files} files this run."
        )

    results = []
    for f in inbox_files:
        out = await analyze_inbox_file(f)
        if out:
            results.append(out)
    return results
