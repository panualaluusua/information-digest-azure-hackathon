"""
Evaluation script — runs the Silver agent against the golden dataset and scores accuracy.

Usage:
  python eval/run_eval.py

Requires AZURE_AI_PROJECT_CONNECTION_STRING in .env.
"""

from __future__ import annotations
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.agents.silver_analyzer_agent import analyze_inbox_file
from src.models.silver import SilverBrief

GOLDEN = Path(__file__).parent / "golden_dataset.jsonl"
INBOX = Path(__file__).parents[1] / "inbox"


async def evaluate() -> None:
    cases = [json.loads(l) for l in GOLDEN.read_text().splitlines() if l.strip()]
    results = []

    for i, case in enumerate(cases):
        # Write a temp inbox file for this case
        tmp = INBOX / f"_eval_case_{i}.txt"
        tmp.write_text(
            json.dumps(case["input"], ensure_ascii=False),
            encoding="utf-8"
        )
        try:
            out_path = await analyze_inbox_file(tmp)
            if out_path is None:
                results.append({"case": i, "status": "INVALID", "error": "Schema validation failed"})
                continue
            brief = SilverBrief.model_validate_json(out_path.read_text())
            expected = case["expected"]
            score_ok = brief.relevance_score == expected["relevance_score"]
            tags_ok = all(
                t in brief.tags
                for t in expected.get("tags_must_include", [])
            )
            results.append({
                "case": i,
                "title": case["input"]["title"],
                "status": "PASS" if (score_ok and tags_ok) else "FAIL",
                "expected_score": expected["relevance_score"],
                "actual_score": int(brief.relevance_score),
                "tags_ok": tags_ok,
            })
        finally:
            if tmp.exists():
                tmp.unlink()

    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n=== Eval Results: {passed}/{len(results)} passed ===\n")
    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"{icon} Case {r['case']}: {r.get('title', '')} | {r}")

    # Write report
    report_path = Path(__file__).parent / "eval_report.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    asyncio.run(evaluate())
