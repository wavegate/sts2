from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select as sqlmodel_select

from database import get_session
from models import Card

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=list[Card])
async def list_cards(
    session: AsyncSession = Depends(get_session),
    color: str | None = Query(None, description="Filter by character color (e.g. silent, defect)"),
    card_type: str | None = Query(None, alias="type", description="Filter by card type (Attack, Skill, Power)"),
    rarity: str | None = Query(None, description="Filter by rarity (Common, Uncommon, Rare)"),
    search: str | None = Query(None, description="Search in name and description"),
) -> list[Card]:
    stmt = sqlmodel_select(Card)
    if color:
        stmt = stmt.where(Card.color == color)
    if card_type:
        stmt = stmt.where(Card.type == card_type)
    if rarity:
        stmt = stmt.where(Card.rarity == rarity)
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            (Card.name.ilike(search_pattern)) | (Card.description.ilike(search_pattern))
        )
    stmt = stmt.order_by(Card.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{card_id}", response_model=Card)
async def get_card(
    card_id: str,
    session: AsyncSession = Depends(get_session),
) -> Card:
    result = await session.execute(sqlmodel_select(Card).where(Card.id == card_id))
    card = result.scalar_one_or_none()
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card
