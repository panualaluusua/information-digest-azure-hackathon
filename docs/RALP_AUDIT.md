# RALP Audit

This pass used a practical RALP loop:

- Review: inspect repo state, docs, tests, demo flow, and submission risks.
- Adjust: patch the highest-impact inconsistencies and demo blockers.
- Local validation: run tests, syntax checks, and deterministic demo seed.
- Polish: simplify claims, align docs with implemented behavior, and add checklists.

## Round 1

Review findings:

- The project story needed one clear Foundry narrative.
- Old early-draft references could distract from the implemented Microsoft stack.
- Demo runs needed a deterministic path that does not repeatedly spend tokens.
- Cost safety needed to be visible for the Reliability and Safety rubric.

Adjustments:

- Rewrote README, architecture, concept, video plan, and shot list.
- Added local cost guard documentation.
- Added deterministic demo seed and Gold-only demo runner.
- Added visible reasoning logs.

Validation:

- `python -m pytest tests/ -q` passed.
- `python demo/seed_demo_data.py` produced four stable demo briefs.

## Round 2

Review findings:

- Default source example did not match the source cap well.
- Minor unused imports and Teams markdown formatting could be cleaner.
- Submission readiness needed one explicit checklist.

Adjustments:

- Tuned `sources.json.example` for a small mixed demo run.
- Removed unused imports.
- Improved heading conversion for Teams card text.
- Added `HACKATHON_SUBMISSION_CHECKLIST.md`.

Validation:

- `python -m py_compile ...` passed for demo scripts and touched source modules.
- `python -m pytest tests/ -q` passed with 69 tests.
- `python demo/seed_demo_data.py` regenerated the deterministic demo briefs.
- No obsolete early-draft implementation names remain in the main submission docs.
- A tiny real Foundry E2E run succeeded: one item was scored, and digest synthesis completed after the built-in 429 retry.

Remaining deliberate choices:

- `demo/run_gold_only.py` is intentionally manual because it makes a real Foundry model call.
- Azure budget creation is documented but not executed automatically, because the alert amount and notification email should be explicit.
- Production hosting features such as private networking, APIM, persistent storage, managed identity assignment, and CI quality gates are documented as hardening, not claimed as fully deployed.
