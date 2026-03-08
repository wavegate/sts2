from sqlmodel import SQLModel, Field


class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    character: str
    cost: int
    rarity: str
