"""Run only the Gold synthesis stage for demos.

Use after `python demo/seed_demo_data.py` when you want one Foundry call to
produce the final digest without fetching sources or re-scoring raw content.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from dotenv import load_dotenv


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(ROOT / ".env")

from src.agents.master_synthesizer_agent import synthesize


async def main() -> None:
    digest, out_path = await synthesize()
    print(f"[demo_gold] Wrote digest to {out_path}")
    print()
    print(digest[:1200])


if __name__ == "__main__":
    asyncio.run(main())
