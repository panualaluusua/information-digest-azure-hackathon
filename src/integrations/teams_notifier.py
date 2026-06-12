"""
Teams Notifier — posts the weekly digest to a Microsoft Teams channel
via an Incoming Webhook (no SDK required, just requests).

Setup:
  Teams channel → ... → Connectors → Incoming Webhook → create → copy URL
  Set TEAMS_WEBHOOK_URL in your .env
"""

from __future__ import annotations
import os
import re
import requests


def _markdown_to_teams_text(markdown: str) -> str:
    """
    Light conversion: Teams Adaptive Cards support a limited subset of Markdown.
    Strip fences and reduce heading levels for readability in the card body.
    """
    text = re.sub(r"^#{1,2} (.+)$", r"**\1**", markdown, flags=re.MULTILINE)
    text = re.sub(r"^#{3,} ", "", text, flags=re.MULTILINE)
    text = text.replace("```json", "").replace("```", "")
    return text.strip()


def _build_adaptive_card(digest_markdown: str, week: str) -> dict:
    """Builds a Teams Adaptive Card payload from the digest Markdown."""
    body_text = _markdown_to_teams_text(digest_markdown)

    # Split into sections to keep the card readable (Teams has a text limit)
    paragraphs = body_text.split("\n\n")
    body_blocks = [
        {"type": "TextBlock", "text": p.strip(), "wrap": True}
        for p in paragraphs if p.strip()
    ]

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"🗞️ Weekly AI & Data Digest — {week}",
                            "weight": "Bolder",
                            "size": "Large",
                            "wrap": True,
                        },
                        *body_blocks,
                    ],
                },
            }
        ],
    }


def post_digest_to_teams(digest_markdown: str, week: str) -> bool:
    """
    Posts the digest to the configured Teams channel.

    Returns True on success, False on failure (logs the error, does not raise).
    """
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("[teams_notifier] TEAMS_WEBHOOK_URL not set — skipping Teams notification.")
        return False

    payload = _build_adaptive_card(digest_markdown, week)
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
        print(f"[teams_notifier] Digest posted to Teams for week {week}.")
        return True
    except requests.HTTPError as e:
        print(f"[teams_notifier] HTTP error posting to Teams: {e}")
        return False
    except Exception as e:
        print(f"[teams_notifier] Unexpected error: {e}")
        return False
