# Information Digest

Personal AI signal filter for engineers drowning in AI news.

Information Digest is a Microsoft Foundry-powered Semantic ETL pipeline that fetches technical signals from RSS feeds, YouTube channels, and GitHub organizations, scores each item against an expert profile, filters low-value noise, and synthesizes the important items into a weekly Markdown brief.

Built for the Microsoft Agents League Hackathon, Track 2: Reasoning Agents.

## Why It Matters

AI engineers do not need more feeds. They need a reliable way to decide what is worth reading, what can be ignored, and what should change their work this week.

This project turns noisy technical inputs into a structured decision brief:

1. Fetch raw content from multiple sources.
2. Enrich and score each item with a Foundry-backed analyzer agent.
3. Validate the result with Pydantic schemas.
4. Route only score >= 3 items to digest synthesis.
5. Generate a weekly Markdown digest (primary) and optionally notify via Teams.

## Architecture

```text
Sources: RSS / YouTube / GitHub
        |
        v
MCP fetchers and fan-out extraction
        |
        v
inbox/                         Raw layer
        |
        v
Analyzer Agent                 Microsoft Agent Framework + Azure AI Foundry
        |
        v
silver_data/*.json             Enriched and scored structured briefs
        |
        v
Digest Synthesizer Agent       score >= 3 only
        |
        v
gold_synthesis/YYYY-WW.md      Primary deliverable: Weekly Markdown digest
        |
        v
Microsoft Teams                (Optional) Adaptive Card notification
```

This is intentionally described as Semantic ETL rather than a strict medallion architecture. The current file names still use `silver` and `gold` for the tested demo path, but the conceptual flow is `ingest -> normalize -> enrich -> rank -> synthesize -> publish`. See [docs/PIPELINE_SPEC.md](docs/PIPELINE_SPEC.md).

## Microsoft IQ Integration — Foundry IQ

This project integrates **Foundry IQ** as its intelligence layer, satisfying the hackathon's mandatory Microsoft IQ requirement.

**What Foundry IQ provides here:** Agentic knowledge retrieval — the synthesis agent does not receive raw JSON context. Instead, scored article briefs are indexed into a Foundry-managed vector store and the agent performs semantic search over them, producing cited, grounded output that reduces hallucination.

**Integration point:** `src/agents/foundry_iq.py` + `src/agents/master_synthesizer_agent.py`

```text
silver_data/*.json (scored briefs)
        |
        v
Foundry IQ: upload_and_index_silver()
        |
        v
Foundry Vector Store (managed, expires after 1 day)
        |
        v
MasterSynthesizerIQ Agent  ← FileSearchTool → vector store
        |
        v
Grounded digest with source citations
```

The `FileSearchTool` is attached to the synthesis agent via `azure-ai-agents` SDK. No external Azure AI Search subscription is required — Foundry manages the vector store natively.

## Hackathon Fit

Reasoning Agents:

- Multi-step workflow: fetch, inspect, score, filter, synthesize, publish.
- Profile-aware reasoning: every item is evaluated against `profile/ai_paradigm_lens.md`.
- Structured outputs: `SilverBrief` currently acts as the scored brief contract and keeps the agent accountable.
- GenAIOps basics: unit tests, golden eval dataset, schema validation, and cost guards.
- Practical UX: The final output is a clean, shareable Markdown digest. It can optionally be posted to Teams.
- **Foundry IQ**: synthesis uses semantic retrieval from a Foundry vector store — grounded, cited answers.

## Safety And Cost Guards

The project includes local caps so demo runs stay small:

| Variable | Default | Purpose |
|---|---:|---|
| `MAX_SOURCES_PER_RUN` | `3` | Maximum source fetch tasks per pipeline run |
| `MAX_INBOX_ITEMS_PER_RUN` | `5` | Maximum inbox files analyzed by the LLM per run |
| `MAX_CONTENT_CHARS_PER_ITEM` | `8000` | Maximum raw content sent to the model per item |
| `FOUNDRY_RETRY_DELAY_SECONDS` | `75` | One retry delay for low-quota 429 responses |

For Azure spend protection, create a Cost Management budget before running cloud demos. See [docs/COST_SAFETY.md](docs/COST_SAFETY.md).

## Cloud Smoke Test

The real Foundry path has been smoke-tested with one tiny item:

- Silver Analyzer called `o4-mini` through Azure AI Foundry.
- The item was scored `4` and routed to digest synthesis.
- Digest synthesis completed after the built-in 429 retry.
- Local tests passed afterward: `69 passed`.

See [docs/CLOUD_SMOKE_TEST.md](docs/CLOUD_SMOKE_TEST.md) for the exact result and reproduction notes.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy configuration files:

```powershell
Copy-Item .env.example .env
Copy-Item sources.json.example sources.json
```

Set at least:

```env
AZURE_AI_PROJECT_ENDPOINT=https://your-foundry-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT=o4-mini
MAX_SOURCES_PER_RUN=3
MAX_INBOX_ITEMS_PER_RUN=5
MAX_CONTENT_CHARS_PER_ITEM=8000
FOUNDRY_RETRY_DELAY_SECONDS=75
```

Then run:

```powershell
python -m src.orchestrator
```

## Demo Mode

To seed a predictable hackathon demo dataset without spending tokens on fetching and scoring:

```powershell
python demo/seed_demo_data.py
```

Then run only the digest synthesis stage:

```powershell
python demo/run_gold_only.py
```

This makes one model call for the final digest and avoids repeated fetch and scoring calls during video recording.

## Evaluation

Unit tests do not require Azure credentials:

```powershell
python -m pytest tests/ -q
```

The optional eval runner uses Foundry credentials and runs the analyzer against `eval/golden_dataset.jsonl`:

```powershell
python eval/run_eval.py
```

## Credentials

| Variable | Purpose |
|---|---|
| `AZURE_AI_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint |
| `AZURE_AI_PROJECT_CONNECTION_STRING` | Backward-compatible endpoint URL fallback |
| `AZURE_AI_MODEL_DEPLOYMENT` | Foundry model deployment name, for example `o4-mini` |
| `FOUNDRY_RETRY_DELAY_SECONDS` | Delay before one retry after a low-quota 429 response |
| `YOUTUBE_API_KEY` | Optional YouTube Data API key |
| `GITHUB_TOKEN` | Optional GitHub token for higher REST API rate limits |
| `TEAMS_WEBHOOK_URL` | Optional Teams Incoming Webhook URL |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Optional Azure Monitor telemetry |

## Project Structure

```text
src/
  agents/
    foundry_client.py
    content_extractor_agent.py
    silver_analyzer_agent.py
    master_synthesizer_agent.py
  integrations/
    teams_notifier.py
  mcp_servers/
    blog_fetcher.py
    github_fetcher.py
    youtube_fetcher.py
  models/
    silver.py
  orchestrator.py
demo/
  seed_demo_data.py
docs/
  ARCHITECTURE.md
  CONCEPT.md
  COST_SAFETY.md
  PIPELINE_SPEC.md
eval/
  golden_dataset.jsonl
tests/
```

## License

MIT
