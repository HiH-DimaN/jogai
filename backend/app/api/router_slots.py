from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_locale, get_session
from app.database.models import Slot
from app.i18n import t

router = APIRouter(prefix="/slots", tags=["slots"])


class SlotResponse(BaseModel):
    id: int
    name: str
    slug: str
    provider: str | None
    rtp: float | None
    volatility: str | None
    max_win: str | None
    tip: str | None
    best_casino_id: int | None
    best_casino_name: str | None


class SlotListResponse(BaseModel):
    slots: list[SlotResponse]
    geo: str
    locale: str


class SlotDetailResponse(SlotResponse):
    reels: int | None
    lines: int | None
    features: list[str] | None
    source: str | None


def _slot_to_response(slot: Slot, locale: str) -> SlotResponse:
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    tip = getattr(slot, f"tip_{lang_suffix}") or slot.tip_pt
    casino_name = slot.best_casino.name if slot.best_casino else None
    return SlotResponse(
        id=slot.id,
        name=slot.name,
        slug=slot.slug,
        provider=slot.provider,
        rtp=float(slot.rtp) if slot.rtp else None,
        volatility=slot.volatility,
        max_win=slot.max_win,
        tip=tip,
        best_casino_id=slot.best_casino_id,
        best_casino_name=casino_name,
    )


@router.get("", response_model=SlotListResponse)
async def get_slots(
    geo: str = "BR",
    limit: int = 20,
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    limit = min(limit, 50)
    stmt = (
        select(Slot)
        .where(Slot.is_active.is_(True), Slot.geo.any(geo))
        .order_by(Slot.rtp.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    slots = result.scalars().all()

    return SlotListResponse(
        slots=[_slot_to_response(s, locale) for s in slots],
        geo=geo,
        locale=locale,
    )


@router.get("/{slug}", response_model=SlotDetailResponse)
async def get_slot(
    slug: str,
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Slot).where(Slot.slug == slug))
    slot = result.scalar_one_or_none()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    lang_suffix = "pt" if locale.startswith("pt") else "es"
    tip = getattr(slot, f"tip_{lang_suffix}") or slot.tip_pt
    casino_name = slot.best_casino.name if slot.best_casino else None

    return SlotDetailResponse(
        id=slot.id,
        name=slot.name,
        slug=slot.slug,
        provider=slot.provider,
        rtp=float(slot.rtp) if slot.rtp else None,
        volatility=slot.volatility,
        max_win=slot.max_win,
        tip=tip,
        best_casino_id=slot.best_casino_id,
        best_casino_name=casino_name,
        reels=slot.reels,
        lines=slot.lines,
        features=slot.features,
        source=slot.source,
    )
