"""Pydantic schemas for scored briefs (structured AI output per article)."""

from __future__ import annotations
from enum import IntEnum
from typing import Literal
from pydantic import BaseModel, Field


class RelevanceScore(IntEnum):
    NOISE = 1           # Marketing, generic hype, off-profile
    BACKGROUND = 2      # Mildly interesting, no immediate value
    TREND = 3           # Useful trend worth tracking
    CRITICAL_SKILL = 4  # Deep, directly applicable to current work
    PARADIGM_SHIFT = 5  # Changes how you work — must read


class SourceType(str):
    RSS = "rss"
    YOUTUBE = "youtube"
    GITHUB = "github"


class SilverBrief(BaseModel):
    """Structured scored brief for a single content item."""

    # Identity
    source_url: str = Field(description="Original URL of the article or video")
    source_type: Literal["rss", "youtube", "github"] = Field(description="Type of source")
    title: str = Field(description="Original title of the content")
    published_at: str | None = Field(None, description="ISO 8601 publication date if available")

    # AI-generated structure
    what: str = Field(
        description="One sentence: what is this about? (technology, project, concept)"
    )
    why_now: str = Field(
        description="One sentence: why does this matter right now? What changed or was released?"
    )
    how: str | None = Field(
        None,
        description="One sentence: how does it work or how would you use it? (if technical)"
    )
    so_what: str = Field(
        description="One sentence: what is the practical implication for a senior data/AI engineer?"
    )

    # Curation
    relevance_score: RelevanceScore = Field(
        description="1–5 relevance score against the user profile. Only scores ≥3 reach digest synthesis."
    )
    relevance_reason: str = Field(
        description="Short justification for the score referencing the user profile."
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Up to 5 topic tags (e.g. ['LLM', 'Azure', 'Data Engineering'])"
    )


class SilverBatch(BaseModel):
    """A batch of scored briefs produced in one agent run."""
    week: str = Field(description="ISO week string, e.g. '2026-W23'")
    items: list[SilverBrief]

    @property
    def gold_candidates(self) -> list[SilverBrief]:
        return [i for i in self.items if i.relevance_score >= 3]
