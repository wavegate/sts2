from __future__ import annotations

from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Run(SQLModel, table=True):
    """A single game run (one .run file). Identified by (start_time, seed)."""

    __tablename__ = "runs"

    # Composite primary key: same (start_time, seed) = same run (upsert replaces)
    start_time: int = Field(primary_key=True, description="Run start Unix timestamp")
    seed: str = Field(primary_key=True)
    build_id: str
    schema_version: int
    run_time: int = Field(description="Duration in seconds")
    win: bool = False
    was_abandoned: bool = False
    killed_by_encounter: str = Field(default="NONE.NONE")
    killed_by_event: str = Field(default="NONE.NONE")
    character: str
    ascension: int = 0
    game_mode: str = Field(default="standard")
    acts: list[str] | None = Field(default=None, sa_column=Column(JSON))
    modifiers: list[Any] | None = Field(default=None, sa_column=Column(JSON))
    platform_type: str | None = None

    # Derived summary stats
    deck_size: int = 0
    upgraded_card_count: int = 0
    relic_count: int = 0
    floor_reached: int = 0
    bosses_killed: int = 0
    map_point_counts: dict[str, int] | None = Field(default=None, sa_column=Column(JSON))

    # Optional detail (card/relic ids and floor_added_to_deck)
    deck: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    relics: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    description_raw: str | None = None
    cost: int | None = None
    is_x_cost: bool | None = None
    is_x_star_cost: bool | None = None
    star_cost: int | None = None
    type: str | None = None  # Attack, Skill, Power, etc.
    rarity: str | None = None
    target: str | None = None
    color: str | None = None  # silent, defect, ironclad, etc.
    damage: int | None = None
    block: int | None = None
    hit_count: int | None = None
    powers_applied: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    cards_draw: int | None = None
    energy_gain: int | None = None
    hp_loss: int | None = None
    keywords: list[str] | None = Field(default=None, sa_column=Column(JSON))
    tags: list[str] | None = Field(default=None, sa_column=Column(JSON))
    vars: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    upgrade: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    image_url: str | None = None
    beta_image_url: str | None = None


class Character(SQLModel, table=True):
    __tablename__ = "characters"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    starting_hp: int | None = None
    starting_gold: int | None = None
    max_energy: int | None = None
    orb_slots: int | None = None
    starting_deck: list[str] | None = Field(default=None, sa_column=Column(JSON))
    starting_relics: list[str] | None = Field(default=None, sa_column=Column(JSON))
    unlocks_after: str | None = None
    gender: str | None = None
    color: str | None = None
    image_url: str | None = None


class Relic(SQLModel, table=True):
    __tablename__ = "relics"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    description_raw: str | None = None
    flavor: str | None = None
    rarity: str | None = None
    pool: str | None = None
    image_url: str | None = None


class Monster(SQLModel, table=True):
    __tablename__ = "monsters"

    id: str = Field(primary_key=True)
    name: str
    type: str | None = None  # Normal, Elite, Boss
    min_hp: int | None = None
    max_hp: int | None = None
    min_hp_ascension: int | None = None
    max_hp_ascension: int | None = None
    moves: list[dict[str, str]] | None = Field(default=None, sa_column=Column(JSON))
    damage_values: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    block_values: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    image_url: str | None = None


class Potion(SQLModel, table=True):
    __tablename__ = "potions"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    description_raw: str | None = None
    rarity: str | None = None
    image_url: str | None = None


class Enchantment(SQLModel, table=True):
    __tablename__ = "enchantments"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    description_raw: str | None = None
    extra_card_text: str | None = None
    card_type: str | None = None
    is_stackable: bool | None = None
    image_url: str | None = None


class Encounter(SQLModel, table=True):
    __tablename__ = "encounters"

    id: str = Field(primary_key=True)
    name: str
    room_type: str | None = None  # Monster, Elite, Boss
    is_weak: bool | None = None
    act: str | None = None
    tags: list[str] | None = Field(default=None, sa_column=Column(JSON))
    monsters: list[dict[str, str]] | None = Field(default=None, sa_column=Column(JSON))
    loss_text: str | None = None


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: str = Field(primary_key=True)
    name: str
    type: str | None = None  # Event, Shared
    act: str | None = None
    description: str | None = None
    options: list[dict[str, str]] | None = Field(default=None, sa_column=Column(JSON))
