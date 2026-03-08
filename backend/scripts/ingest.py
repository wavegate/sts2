#!/usr/bin/env python3
"""
Ingest spire-codex JSON data into the database.

Run from backend directory (where .env and database.py live):

  cd backend && python scripts/ingest.py

Uses DATABASE_URL from backend/.env. Data is read from repo data/ directory
(sts2/data). Replaces existing rows in each table (idempotent re-run).

Optional: set DATA_DIR to override the data directory path.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Allow importing backend modules when run as script or as module
_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from sqlalchemy import delete
from sqlmodel import SQLModel

from database import AsyncSessionLocal, engine
from models import (
    Card,
    Character,
    Encounter,
    Enchantment,
    Event,
    Monster,
    Potion,
    Relic,
)

# Data directory: repo root / data (e.g. sts2/data)
DATA_DIR = _backend.parent / "data"

ENTITY_FILES = [
    ("cards.json", Card),
    ("characters.json", Character),
    ("relics.json", Relic),
    ("monsters.json", Monster),
    ("potions.json", Potion),
    ("enchantments.json", Enchantment),
    ("encounters.json", Encounter),
    ("events.json", Event),
]


async def ingest_one(session, model_class: type[SQLModel], path: Path) -> int:
    if not path.exists():
        print(f"  skip (file not found): {path.name}")
        return 0
    with path.open(encoding="utf-8") as f:
        rows = json.load(f)
    if not rows:
        print(f"  skip (empty): {path.name}")
        return 0
    # Clear existing rows
    await session.execute(delete(model_class))
    count = 0
    for row in rows:
        session.add(model_class.model_validate(row))
        count += 1
    print(f"  {path.name}: {count} rows")
    return count


async def run_ingest(data_dir: Path | None = None) -> None:
    data_dir = data_dir or DATA_DIR
    if not data_dir.is_dir():
        raise SystemExit(f"Data directory not found: {data_dir}")

    async with AsyncSessionLocal() as session:
        for filename, model_class in ENTITY_FILES:
            path = data_dir / filename
            await ingest_one(session, model_class, path)
        await session.commit()

    await engine.dispose()
    print("Done.")


def main() -> None:
    import os
    from dotenv import load_dotenv

    # Load .env from backend/ when run as script
    load_dotenv(_backend / ".env")
    load_dotenv()

    data_dir = os.environ.get("DATA_DIR")
    path = Path(data_dir) if data_dir else DATA_DIR

    asyncio.run(run_ingest(path))


if __name__ == "__main__":
    main()
