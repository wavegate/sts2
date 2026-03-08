#!/usr/bin/env python3
"""
Ingest .run files into the runs table.

Run from backend directory:

  cd backend && python scripts/ingest_runs.py [path_or_dir ...]

If no path given, uses DATA_DIR (default: repo data/). Paths can be .run files
or directories (all .run files inside are ingested). Uses start_time as run ID;
re-importing the same file replaces the existing run.

Requires DATABASE_URL in backend/.env.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from dotenv import load_dotenv

load_dotenv(_backend / ".env")
load_dotenv()

from database import AsyncSessionLocal, engine
from run_ingest import ingest_run_file

DATA_DIR = _backend.parent / "data"


def collect_run_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        p = Path(p).resolve()
        if not p.exists():
            print(f"Skip (not found): {p}")
            continue
        if p.is_file():
            if p.suffix.lower() == ".run":
                out.append(p)
            else:
                print(f"Skip (not .run): {p}")
        else:
            for f in sorted(p.rglob("*.run")):
                out.append(f)
    return out


async def main() -> None:
    import os

    raw = os.environ.get("DATA_DIR", "")
    default_dir = Path(raw) if raw else DATA_DIR

    if len(sys.argv) > 1:
        paths = [Path(a) for a in sys.argv[1:]]
    else:
        paths = [default_dir]

    files = collect_run_files(paths)
    if not files:
        print("No .run files found.")
        return

    async with AsyncSessionLocal() as session:
        for f in files:
            try:
                run = await ingest_run_file(session, f)
                print(f"  {f.name} -> run {run.start_time}_{run.seed} ({run.character}, win={run.win})")
            except Exception as e:
                print(f"  {f.name}: {e}")
        await session.commit()

    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
