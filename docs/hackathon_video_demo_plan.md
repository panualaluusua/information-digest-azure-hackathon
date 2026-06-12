# Hackathon Video Demo Plan

Target length: 60-90 seconds.

Goal: show a real Microsoft Foundry reasoning pipeline, not a generic chatbot.

## 1. The Problem

Message:

> AI engineers are drowning in updates. The hard part is not finding news. It is deciding what deserves attention.

Visual:

- Noisy feed, GitHub activity, or inbox.
- Quick cut to the project name: Information Digest.

## 2. The Architecture

Message:

> The system uses a Foundry-backed Semantic ETL pipeline: ingest, enrich, rank, synthesize, and publish.

Visual:

- Show the architecture from `docs/ARCHITECTURE.md`.
- Briefly show `docs/PIPELINE_SPEC.md` to make the operator model explicit.
- Highlight Microsoft Agent Framework, Azure AI Foundry, Pydantic validation, and Teams delivery.

Avoid:

- Do not mention obsolete implementation names from early drafts.
- Do not claim managed identity or private networking as implemented runtime behavior.

## 3. The Reasoning Run

Message:

> Each item is scored against an expert profile. Low-value noise is discarded. High-signal findings are routed to synthesis.

Visual:

- Terminal running `python -m src.orchestrator`.
- For repeated recording takes, use `python demo/seed_demo_data.py` followed by `python demo/run_gold_only.py`.
- Capture lines such as:
  - `PLAN fetch -> score -> filter -> synthesize -> notify`
  - `SCORE ... score=1 decision=discarded_as_noise`
  - `SCORE ... score=5 decision=routed_to_gold`
  - `ROUTE gold_candidates=...`
  - `SYNTHESIZE output=...`

## 4. Reliability And Safety

Message:

> The demo is intentionally bounded: schema validation, tests, golden eval cases, and local cost guards keep the agent inspectable and safe to run.

Visual:

- `python -m pytest tests/ -q`
- `docs/CLOUD_SMOKE_TEST.md` showing the real Foundry E2E result.
- `.env.example` showing:
  - `MAX_SOURCES_PER_RUN`
  - `MAX_INBOX_ITEMS_PER_RUN`
  - `MAX_CONTENT_CHARS_PER_ITEM`
  - `FOUNDRY_RETRY_DELAY_SECONDS`
- Optional Azure Cost Management budget screen if configured.

## 5. The Result

Message:

> The output is a short weekly brief delivered where the engineer already works: Teams.

Visual:

- Generated weekly digest in `gold_synthesis/`.
- Teams Adaptive Card if the webhook is configured.

## 6. Closing

Message:

> Information Digest turns AI noise into an actionable engineering signal.

Visual:

- Project name.
- GitHub repository.
- Track: Reasoning Agents.

## Recording Checklist

- Use `AZURE_AI_MODEL_DEPLOYMENT=o4-mini` for repeated demo takes.
- Seed deterministic data with `python demo/seed_demo_data.py` if live feeds are noisy.
- Use `python demo/run_gold_only.py` for low-cost repeated recording takes.
- Mention that the full cloud path has been smoke-tested, but do not repeat full E2E rapidly on the low-capacity deployment.
- Keep browser tabs and notifications clean.
- Do not show secrets from `.env`.
- Do not show obsolete early-draft architecture docs.
- Run tests before recording.
