# Hackathon Demo Shot List

Record at 1920x1080 if possible. Hide secrets, browser bookmarks, and desktop notifications.

## Shot 1: The Noise

Length: 10-15 seconds.

Show a noisy feed, GitHub activity page, RSS reader, or AI newsletter inbox.

Purpose: establish the attention problem.

## Shot 2: The Architecture

Length: 10-15 seconds.

Show `docs/ARCHITECTURE.md` and the Mermaid diagram.

Purpose: prove the project is a multi-step Foundry Semantic ETL pipeline:

- Ingest raw source material.
- Enrich and score each item.
- Synthesize the weekly digest.
- Publish to Teams.

Optional close-up: show `docs/PIPELINE_SPEC.md` with `ingest -> normalize -> enrich -> rank -> synthesize -> publish`.

## Shot 3: The Code

Length: 10 seconds.

Show:

- `src/agents/foundry_client.py`
- `src/agents/silver_analyzer_agent.py`
- `src/agents/master_synthesizer_agent.py`
- `src/models/silver.py`

Purpose: show Microsoft Agent Framework usage, Foundry-backed clients, Azure credential flow, retry handling, and Pydantic schema validation.

## Shot 4: Safety And Evals

Length: 10-15 seconds.

Run:

```powershell
python -m pytest tests/ -q
```

Then show `.env.example` cost guard variables.

Also show `docs/CLOUD_SMOKE_TEST.md` briefly.

Purpose: demonstrate reliability, real cloud validation, and cost awareness without overclaiming production infrastructure.

## Shot 5: The Reasoning Run

Length: 20-30 seconds.

Run:

```powershell
python demo/seed_demo_data.py
python demo/run_gold_only.py
```

This path still calls Foundry for digest synthesis, but avoids repeated live fetch and item scoring calls.

Capture terminal lines that show decisions:

- `score=5 decision=routed_to_gold` or equivalent routed-to-digest log
- `score=1 decision=discarded`
- `ROUTE gold_candidates=...`
- `SYNTHESIZE output=...`

Purpose: make the Reasoning Agents track visible.

## Shot 6: The Result

Length: 10 seconds.

Show the generated weekly digest in `gold_synthesis/YYYY-WW.md` and, if configured, the Teams Adaptive Card.

Purpose: end with the user value, not the implementation.
