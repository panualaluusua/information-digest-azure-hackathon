# Hackathon Submission Checklist

Use this as the final pre-submit checklist for Microsoft Agents League, Track 2: Reasoning Agents.

## Required Assets

- [ ] Public GitHub repository is available.
- [ ] README explains the problem, solution, architecture, setup, and demo flow.
- [ ] Demo video is 5 minutes or less.
- [ ] Architecture diagram clearly shows Microsoft Foundry usage.
- [ ] Project description names the user problem and why the agent is useful.
- [ ] Team/member details are ready for the submission form.

## Technical Demo

- [ ] `.env` contains `AZURE_AI_PROJECT_ENDPOINT` or a URL-valued `AZURE_AI_PROJECT_CONNECTION_STRING`.
- [ ] `.env` uses a known deployment, for example `AZURE_AI_MODEL_DEPLOYMENT=o4-mini`.
- [ ] Azure Cost Management budget alert is configured.
- [ ] `python -m pytest tests/ -q` passes.
- [ ] `python demo/seed_demo_data.py` creates stable demo scored briefs.
- [ ] `python demo/run_gold_only.py` creates a weekly digest.
- [ ] `docs/CLOUD_SMOKE_TEST.md` reflects the latest real Foundry smoke test.
- [ ] No secrets are visible in the recording.

## Judging Rubric Coverage

- Accuracy and relevance: profile-based scoring and schema validation.
- Reasoning and multi-step thinking: ingest, enrich, rank, synthesize, publish.
- Creativity: personalized signal filter rather than another generic chatbot.
- UX and presentation: Clean, decision-oriented Markdown digest (ready for any channel).
- Reliability and safety: tests, eval data, local cost guards, validation, budget guidance.
- Community vote: concise story: "AI noise into engineering signal."

## Demo Script Skeleton

1. "AI engineers are drowning in updates."
2. "Information Digest uses a Foundry-backed Semantic ETL pipeline."
3. "The analyzer scores each item against my AI engineering profile."
4. "Low-value noise is discarded. High-signal items are routed to digest synthesis."
5. "The result is a structured weekly decision brief in Markdown."
6. "Tests, schema validation, eval data, and cost guards keep the demo safe and repeatable."
