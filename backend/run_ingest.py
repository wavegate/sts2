"""
Ingestion engine for .run files.

Reads a single run JSON file, computes summary stats, and returns a SQLModel Run
instance. Does not persist to DB; caller adds to session and commits.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import Run


def _floor_reached(players: list[dict[str, Any]]) -> int:
    """Max floor_added_to_deck across all deck cards and relics in players."""
    max_floor = 0
    for p in players:
        for card in p.get("deck") or []:
            f = card.get("floor_added_to_deck")
            if f is not None:
                max_floor = max(max_floor, f)
        for rel in p.get("relics") or []:
            f = rel.get("floor_added_to_deck")
            if f is not None:
                max_floor = max(max_floor, f)
    return max_floor


def _map_point_counts(map_point_history: list[list[Any]]) -> dict[str, int]:
    """Count map_point_type across all acts and nodes."""
    counts: dict[str, int] = {}
    for act_nodes in map_point_history:
        for node in act_nodes:
            if not isinstance(node, dict):
                continue
            t = node.get("map_point_type")
            if t:
                counts[t] = counts.get(t, 0) + 1
    return counts


def _bosses_killed(map_point_counts: dict[str, int] | None) -> int:
    return (map_point_counts or {}).get("boss", 0)


def run_from_file(path: Path | str, user_id: str | None = None) -> Run:
    """
    Load a .run JSON file and return a Run SQLModel instance.

    path: Path or path string to the .run file.
    user_id: Optional Clerk user id (owner of the run). Set when signed in.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    return run_from_dict(data, user_id)


def _normalize_player(p: dict[str, Any]) -> dict[str, Any]:
    """Extract id, character, deck, relics for storage. id may be int (1) or Steam ID (int)."""
    return {
        "id": p.get("id"),
        "character": p.get("character", ""),
        "deck": p.get("deck") or [],
        "relics": p.get("relics") or [],
    }


def run_from_dict(data: dict[str, Any], user_id: str | None = None) -> Run:
    """
    Build a Run SQLModel instance from a parsed run JSON dict.

    data: The root object of a .run file (must contain start_time, players, etc.).
    user_id: Optional Clerk user id (owner). Set when uploaded while signed in.
    Supports single-player (one player, id often 1) and multiplayer (multiple players with Steam IDs).
    """
    start_time = data["start_time"]
    players_raw = data.get("players") or []
    map_point_history = data.get("map_point_history") or []

    # Store full player list for multiplayer; each entry has id, character, deck, relics
    players_stored = [_normalize_player(p) for p in players_raw]

    # First player for backward-compat fields (character, deck, relics, counts)
    player = players_raw[0] if players_raw else {}
    deck = player.get("deck") or []
    relics = player.get("relics") or []

    deck_size = len(deck)
    upgraded_card_count = sum(
        1 for c in deck if c.get("current_upgrade_level", 0) and c["current_upgrade_level"] >= 1
    )
    relic_count = len(relics)
    floor_reached = _floor_reached(players_raw)
    map_point_counts = _map_point_counts(map_point_history)
    bosses_killed = _bosses_killed(map_point_counts)

    return Run(
        user_id=user_id,
        start_time=start_time,
        seed=data.get("seed", ""),
        build_id=data.get("build_id", ""),
        schema_version=data.get("schema_version", 0),
        run_time=data.get("run_time", 0),
        win=data.get("win", False),
        was_abandoned=data.get("was_abandoned", False),
        killed_by_encounter=data.get("killed_by_encounter", "NONE.NONE"),
        killed_by_event=data.get("killed_by_event", "NONE.NONE"),
        character=player.get("character", ""),
        ascension=data.get("ascension", 0),
        game_mode=data.get("game_mode", "standard"),
        acts=data.get("acts"),
        modifiers=data.get("modifiers"),
        platform_type=data.get("platform_type"),
        deck_size=deck_size,
        upgraded_card_count=upgraded_card_count,
        relic_count=relic_count,
        floor_reached=floor_reached,
        bosses_killed=bosses_killed,
        map_point_counts=map_point_counts or None,
        deck=deck,
        relics=relics,
        players=players_stored if players_stored else None,
    )


async def ingest_run(session: AsyncSession, run: Run) -> Run:
    """
    Upsert a Run into the session (replace existing row with same start_time + seed).
    Caller must commit the session.
    """
    result = await session.execute(
        select(Run).where(
            Run.start_time == run.start_time,
            Run.seed == run.seed,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        await session.delete(existing)
    session.add(run)
    return run


async def ingest_run_file(
    session: AsyncSession, path: Path | str, user_id: str | None = None
) -> Run:
    """
    Load a .run file, create a Run model, and upsert it into the session.
    Uses (start_time, seed) for deduplication. Caller must commit the session.
    """
    run = run_from_file(path, user_id)
    return await ingest_run(session, run)
