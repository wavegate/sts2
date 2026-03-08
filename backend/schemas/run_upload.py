"""Pydantic schemas for run file upload validation."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RunFileSchema(BaseModel):
    """
    Schema for uploaded .run file contents.
    Matches the structure expected by run_ingest.run_from_dict.
    """

    start_time: int = Field(..., description="Run ID (Unix timestamp)")
    players: list[dict[str, Any]] = Field(default_factory=list)
    map_point_history: list[list[dict[str, Any]]] = Field(default_factory=list)

    # Optional top-level fields (type-checked if present)
    seed: str | None = None
    build_id: str | None = None
    schema_version: int | None = None
    run_time: int | None = None
    win: bool | None = None
    was_abandoned: bool | None = None
    killed_by_encounter: str | None = None
    killed_by_event: str | None = None
    ascension: int | None = None
    game_mode: str | None = None
    acts: list[str] | None = None
    modifiers: list[Any] | None = None
    platform_type: str | None = None

    model_config = {"extra": "allow"}
