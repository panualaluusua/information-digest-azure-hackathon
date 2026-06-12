# Pipeline Spec

Information Digest is a Semantic ETL pipeline for technical intelligence.

It runs a file-backed document signal pipeline: source items are ingested, normalized, enriched with profile-aware reasoning, ranked, synthesized, and published. Each stage leaves an inspectable artifact on disk.

## Stage Model

```text
ingest -> normalize -> enrich -> rank -> synthesize -> publish
```

| Stage | Current implementation | Artifact | Purpose |
|---|---|---|---|
| `ingest` | MCP fetchers and content extractor | `inbox/*.txt` | Capture bounded raw source material |
| `normalize` | Source-specific fetcher formatting | `inbox/*.txt` | Keep source records readable and traceable |
| `enrich` | `silver_analyzer_agent.py` | `silver_data/*.json` | Extract what happened, why it matters, and practical impact |
| `rank` | `SilverBrief.relevance_score` | `silver_data/*.json` | Decide whether the item deserves attention |
| `synthesize` | `master_synthesizer_agent.py` | `gold_synthesis/YYYY-WW.md` | Combine relevant items into a weekly decision brief |
| `publish` | `orchestrator.py` | Markdown file | Deliver the brief as a shareable artifact (optional Teams sync) |

## Operator View

DocETL-style systems describe LLM pipelines as composable operators. This is a useful lens for this project:

| Operator | Information Digest equivalent |
|---|---|
| `map` | Analyze each inbox item independently |
| `extract` | Produce the fields in `SilverBrief` |
| `validate` | Pydantic schema validation |
| `filter` | Drop score 1-2 items |
| `rank` | Use `relevance_score` and tags to prioritize |
| `reduce` | Synthesize selected briefs into one weekly digest |
| `publish` | Write to Markdown (primary) and optionally send to Teams |

This keeps the architecture understandable without overclaiming a full external ETL framework.

## Data Contracts

The main intermediate contract is `SilverBrief`:

- `title`
- `source_url`
- `source_type`
- `summary`
- `why_now`
- `how_to_use`
- `so_what`
- `relevance_score`
- `tags`

## Validation And Guardrails

Implemented controls:

- Pydantic validates every structured model output.
- Invalid model output is written to `_INVALID_*.json` for inspection.
- `MAX_SOURCES_PER_RUN` limits source fan-out.
- `MAX_INBOX_ITEMS_PER_RUN` limits model-scored items.
- `MAX_CONTENT_CHARS_PER_ITEM` limits prompt size.
- `FOUNDRY_RETRY_DELAY_SECONDS` handles low-quota 429 responses with one controlled retry.
- Unit tests cover schema handling, scoring behavior, fetchers, synthesis, and Teams notification formatting.

