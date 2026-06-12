# Cloud Smoke Test

This document records the smallest real Azure AI Foundry test that verifies the project works beyond mocks.

## Last Verified

Date: 2026-06-10

Environment:

- Azure AI Foundry project endpoint configured in `.env`
- `AZURE_AI_MODEL_DEPLOYMENT=o4-mini`
- Azure authentication through `DefaultAzureCredential`, using the local Azure CLI login
- Teams webhook disabled for the test
- Temporary `inbox/`, `silver_data/`, and `gold_synthesis/` folders

## What Was Tested

The smoke test used one small synthetic raw item about Azure AI Foundry evaluation controls.

Flow:

1. Write one tiny raw item to a temporary inbox folder.
2. Run `SilverAnalyzer` against the real Foundry deployment.
3. Validate the model response with `SilverBrief`.
4. Run `MasterSynthesizer` against the validated scored JSON.
5. Write a temporary weekly digest.

## Result

The real E2E path succeeded.

Observed terminal signals:

```text
[reasoning] SCORE file=tiny_foundry_eval_test.txt score=4 decision=routed_to_gold
[reasoning] ROUTE gold_candidates=1 threshold=score>=3
[foundry] Rate limited; retrying in 75s (1/2).
[reasoning] SYNTHESIZE output=2026-W23.md candidates=1
```

Summary:

```json
{
  "silver_file": "tiny_foundry_eval_test.json",
  "silver_title": "Azure AI Foundry Adds Better Agent Evaluation Controls",
  "silver_score": 4,
  "silver_tags": [
    "Azure AI",
    "Agent Evaluation",
    "LLMOps",
    "Azure Foundry",
    "Evaluation Controls"
  ],
  "gold_file": "2026-W23.md",
  "gold_chars": 1023
}
```

## Lessons From The Smoke Test

- Current `agent-framework-foundry` uses `FoundryChatClient(project_endpoint=..., model=..., credential=...)`.
- `FoundryChatClient` is imported from `agent_framework_foundry`, not from the root `agent_framework` package.
- Agent instructions use the `instructions=` argument.
- Agent responses expose text through `.text`; the code keeps a backward-compatible fallback for older `.content`-style mocks.
- `o4-mini` can return 429 when scoring and synthesis run back-to-back on a low-capacity deployment, so the project includes a small retry.

## Reproducing Safely

Use a tiny input, disable Teams, and keep retry enabled:

```env
AZURE_AI_PROJECT_ENDPOINT=https://your-foundry-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT=o4-mini
MAX_SOURCES_PER_RUN=0
MAX_INBOX_ITEMS_PER_RUN=1
MAX_CONTENT_CHARS_PER_ITEM=1800
FOUNDRY_RETRY_DELAY_SECONDS=75
TEAMS_WEBHOOK_URL=
```

For repeated video takes, prefer:

```powershell
python demo/seed_demo_data.py
python demo/run_gold_only.py
```

That path avoids repeated live fetch and scoring calls.
