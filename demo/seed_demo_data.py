"""Seed curated Silver data for hackathon demo recording.

This script writes a small, deterministic set of validated SilverBrief JSON
files into silver_data/. It avoids cloud calls and gives the demo a stable mix
of score 5, 4, 3, and discarded 1-2 items.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from src.models.silver import SilverBrief

SILVER = ROOT / "silver_data"


DEMO_BRIEFS = [
    {
        "source_url": "https://learn.microsoft.com/azure/ai-foundry/",
        "source_type": "rss",
        "title": "Azure AI Foundry Adds Agent Evaluation Workflows",
        "published_at": "2026-06-10T08:00:00Z",
        "what": "Azure AI Foundry expanded support for evaluating agent behavior across repeatable datasets.",
        "why_now": "Teams building agents need measurable quality gates before moving from demos to production.",
        "how": "Developers can run curated test cases against agent outputs and track regressions over time.",
        "so_what": "This directly supports a GenAIOps loop for shipping safer Foundry agents.",
        "relevance_score": 5,
        "relevance_reason": "The user profile prioritizes Azure AI, agent evaluation, and production LLMOps.",
        "tags": ["Azure AI", "Agents", "Evaluation", "GenAIOps"],
    },
    {
        "source_url": "https://github.com/microsoft/agent-framework",
        "source_type": "github",
        "title": "Microsoft Agent Framework Improves Tool-Oriented Agent Patterns",
        "published_at": "2026-06-09T13:30:00Z",
        "what": "Microsoft Agent Framework introduced cleaner patterns for tool-backed reasoning agents.",
        "why_now": "The framework is becoming a central option for Foundry-based agent development.",
        "how": "Agents can compose model calls, tool calls, and structured outputs behind a unified API.",
        "so_what": "This gives the project a stronger Microsoft-native foundation than a custom orchestration layer.",
        "relevance_score": 4,
        "relevance_reason": "The item is directly applicable to the user's Foundry and agent framework focus.",
        "tags": ["Agent Framework", "Microsoft", "Tools"],
    },
    {
        "source_url": "https://example.com/vector-search-cost-controls",
        "source_type": "rss",
        "title": "Practical Cost Controls For RAG And Agent Pipelines",
        "published_at": "2026-06-08T10:15:00Z",
        "what": "The article describes ways to cap retrieval, prompt size, and batch sizes in AI pipelines.",
        "why_now": "Agent demos can accidentally become expensive when every source item triggers model calls.",
        "how": "It recommends source limits, content truncation, budget alerts, and separate dry-run modes.",
        "so_what": "The same controls make Information Digest safer to run during hackathon demos.",
        "relevance_score": 3,
        "relevance_reason": "The item supports the user's MLOps and cost governance interests.",
        "tags": ["Cost", "MLOps", "RAG"],
    },
    {
        "source_url": "https://example.com/css-button-roundup",
        "source_type": "rss",
        "title": "A Roundup Of New CSS Button Styles",
        "published_at": "2026-06-07T09:00:00Z",
        "what": "The post collects visual button styling tricks for frontend projects.",
        "why_now": "It follows recent browser CSS improvements but does not affect AI engineering work.",
        "how": "It shows CSS snippets for hover states and layout polish.",
        "so_what": "This is not relevant enough for a senior data and AI engineering weekly digest.",
        "relevance_score": 1,
        "relevance_reason": "The user profile focuses on AI, data engineering, Azure, and LLMOps rather than UI styling.",
        "tags": ["Frontend", "CSS"],
    },
]


def main() -> None:
    SILVER.mkdir(exist_ok=True)
    for index, payload in enumerate(DEMO_BRIEFS, start=1):
        brief = SilverBrief.model_validate(payload)
        out = SILVER / f"demo_{index:02d}_{brief.relevance_score}.json"
        out.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
        decision = "routed_to_gold" if brief.relevance_score >= 3 else "discarded"
        print(f"[demo_seed] {out.name}: score={int(brief.relevance_score)} decision={decision}")

    print(f"[demo_seed] Wrote {len(DEMO_BRIEFS)} demo briefs to {SILVER}")


if __name__ == "__main__":
    main()
