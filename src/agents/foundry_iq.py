"""Foundry IQ — vector store lifecycle for grounded synthesis.

Uploads silver briefs to a Foundry-managed vector store so the
synthesis agent can do semantic retrieval (cited, grounded answers)
rather than receiving all content as raw JSON context.

This is the Microsoft IQ intelligence layer integration for the hackathon:
Foundry IQ = agentic knowledge retrieval with cited, grounded answers.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    FilePurpose,
    VectorStoreExpirationPolicy,
    VectorStoreExpirationPolicyAnchor,
)
from azure.identity import DefaultAzureCredential


def build_agents_client() -> AgentsClient:
    """Builds an async AgentsClient using the configured Foundry project endpoint."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT") or os.environ.get(
        "AZURE_AI_PROJECT_CONNECTION_STRING", ""
    )
    if not endpoint:
        raise RuntimeError(
            "Set AZURE_AI_PROJECT_ENDPOINT to your Foundry project endpoint URL."
        )
    return AgentsClient(endpoint=endpoint, credential=DefaultAzureCredential())


async def upload_and_index_silver(
    client: AgentsClient,
    silver_paths: List[Path],
    store_name: str,
) -> Tuple[str, int]:
    """Upload silver brief files into a new Foundry vector store.

    Returns (vector_store_id, file_count).
    Raises if no files are uploaded (caller should guard on empty silver_paths).
    """
    file_ids: List[str] = []
    for path in silver_paths:
        file_info = await client.files.upload_and_poll(
            file_path=str(path),
            purpose=FilePurpose.AGENTS,
        )
        file_ids.append(file_info.id)

    store = await client.vector_stores.create_and_poll(
        name=store_name,
        file_ids=file_ids,
        expires_after=VectorStoreExpirationPolicy(
            anchor=VectorStoreExpirationPolicyAnchor.LAST_ACTIVE_AT,
            days=1,
        ),
    )
    return store.id, len(file_ids)


async def delete_vector_store(client: AgentsClient, store_id: str) -> None:
    """Best-effort cleanup of the Foundry vector store."""
    try:
        await client.vector_stores.delete(store_id)
    except Exception:
        pass
