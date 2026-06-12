# Concept

## One-Line Pitch

Information Digest is a Foundry-backed Semantic ETL agent that converts noisy AI news into a weekly decision brief for senior data and AI engineers.

## Problem

The AI ecosystem produces more updates than a working engineer can responsibly read: model releases, framework changes, Azure updates, GitHub releases, blog posts, and videos. The problem is not access to information. The problem is deciding what deserves attention.

## Solution

Information Digest applies an expert profile as a reasoning lens inside a staged document signal pipeline:

- Ingest new technical signals.
- Normalize them into inspectable text artifacts.
- Enrich every item against the user's interests.
- Rank and discard low-value noise.
- Synthesize the high-signal items into a concise weekly brief.
- Publish the result to a shareable Markdown file (primary) and optionally to Microsoft Teams.

## Why It Is A Reasoning Agent

The agent does not simply summarize a feed. It makes staged decisions:

1. Is this item relevant to the user's profile?
2. Why does it matter now?
3. Is it practical, strategic, or noise?
4. Should it be routed to the final digest?
5. What theme connects the week's important items?

The intermediate scored JSON makes these decisions inspectable. The current schema is named `SilverBrief` for compatibility with the tested demo path, but conceptually it acts as a scored brief contract.

## Target User

Senior data and AI engineers who need to track:

- LLM and agent framework releases.
- Azure AI Foundry and Microsoft Agent Framework updates.
- Data engineering and MLOps changes.
- High-signal open-source releases.

## Demo Story

Before:

- A noisy inbox of feeds, videos, GitHub updates, and announcements.

After:

- A structured weekly decision brief in Markdown with only the items that matter, grouped by urgency and impact. Ready for any channel.

The value is not another chatbot. The value is a repeatable signal-processing workflow that protects attention.
