"""Azure AI Foundry client construction helpers."""

from __future__ import annotations

import os
import asyncio

from azure.identity import DefaultAzureCredential
from agent_framework_foundry import FoundryChatClient


def _project_endpoint() -> str:
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if endpoint:
        return endpoint

    legacy_value = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
    if legacy_value and legacy_value.startswith(("https://", "http://")):
        return legacy_value

    raise RuntimeError(
        "Set AZURE_AI_PROJECT_ENDPOINT, or set AZURE_AI_PROJECT_CONNECTION_STRING "
        "to a Foundry project endpoint URL."
    )


def build_foundry_chat_client() -> FoundryChatClient:
    """Builds a Foundry chat client for the configured model deployment."""
    return FoundryChatClient(
        project_endpoint=_project_endpoint(),
        model=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "o4-mini"),
        credential=DefaultAzureCredential(),
    )


def response_text(response: object) -> str:
    """Extracts text from current and older Agent Framework response shapes."""
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text

    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content

    value = getattr(response, "value", None)
    if isinstance(value, str):
        return value

    return str(response)


async def run_agent_with_retries(agent: object, prompt: str, *, attempts: int = 2) -> object:
    """Runs an agent call with a small retry for low-quota demo deployments."""
    delay_seconds = int(os.getenv("FOUNDRY_RETRY_DELAY_SECONDS", "75"))
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await agent.run(prompt)
        except Exception as exc:
            last_error = exc
            message = str(exc).lower()
            is_rate_limit = "rate_limit" in message or "429" in message or "too many requests" in message
            if attempt >= attempts or not is_rate_limit:
                raise
            print(f"[foundry] Rate limited; retrying in {delay_seconds}s ({attempt}/{attempts}).")
            await asyncio.sleep(delay_seconds)
    raise RuntimeError("Agent call failed") from last_error
