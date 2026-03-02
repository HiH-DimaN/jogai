from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_locale, get_session
from app.database.models import Bonus, Casino
from app.i18n import t
from app.utils.formatters import format_currency

router = APIRouter(prefix="/bonuses", tags=["bonuses"])


class BonusResponse(BaseModel):
    id: int
    casino_id: int
    casino_name: str
    casino_slug: str
    title: str
    bonus_percent: int
    max_bonus_amount: float
    max_bonus_currency: str
    wagering_multiplier: float
    wagering_deadline_days: int
    max_bet: float
    free_spins: int
    no_deposit: bool
    jogai_score: float
    verdict_key: str
    affiliate_link: str | None
    formatted_max_bonus: str


class BonusListResponse(BaseModel):
    bonuses: list[BonusResponse]
    geo: str
    locale: str


class BonusDetailResponse(BonusResponse):
    expected_loss: float
    expected_loss_formatted: str
    profit_probability: float
    verdict_text: str
    casino_description: str | None
    casino_withdrawal_time: str | None


@router.get("", response_model=BonusListResponse)
async def get_bonuses(
    geo: str = "BR",
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    lang_suffix = "pt" if locale.startswith("pt") else "es"

    stmt = (
        select(Bonus)
        .where(Bonus.is_active.is_(True), Bonus.geo.any(geo))
        .order_by(Bonus.jogai_score.desc())
        .limit(10)
    )
    result = await session.execute(stmt)
    bonuses = result.scalars().all()

    items = []
    for b in bonuses:
        title = getattr(b, f"title_{lang_suffix}") or b.title_pt or ""
        casino = b.casino
        casino_name = casino.name if casino else ""
        casino_slug = casino.slug if casino else ""

        items.append(
            BonusResponse(
                id=b.id,
                casino_id=b.casino_id or 0,
                casino_name=casino_name,
                casino_slug=casino_slug,
                title=title,
                bonus_percent=b.bonus_percent or 0,
                max_bonus_amount=float(b.max_bonus_amount or 0),
                max_bonus_currency=b.max_bonus_currency,
                wagering_multiplier=float(b.wagering_multiplier or 0),
                wagering_deadline_days=b.wagering_deadline_days or 0,
                max_bet=float(b.max_bet or 0),
                free_spins=b.free_spins,
                no_deposit=b.no_deposit,
                jogai_score=float(b.jogai_score or 0),
                verdict_key=b.verdict_key or "verdict_caution",
                affiliate_link=b.affiliate_link,
                formatted_max_bonus=format_currency(
                    float(b.max_bonus_amount or 0), locale
                ),
            )
        )

    return BonusListResponse(bonuses=items, geo=geo, locale=locale)


@router.get("/{bonus_id}", response_model=BonusDetailResponse)
async def get_bonus(
    bonus_id: int,
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    lang_suffix = "pt" if locale.startswith("pt") else "es"

    result = await session.execute(select(Bonus).where(Bonus.id == bonus_id))
    b = result.scalar_one_or_none()

    if not b:
        raise HTTPException(status_code=404, detail="Bonus not found")

    title = getattr(b, f"title_{lang_suffix}") or b.title_pt or ""
    casino = b.casino
    casino_name = casino.name if casino else ""
    casino_slug = casino.slug if casino else ""
    casino_desc = getattr(casino, f"description_{lang_suffix}", None) if casino else None

    return BonusDetailResponse(
        id=b.id,
        casino_id=b.casino_id or 0,
        casino_name=casino_name,
        casino_slug=casino_slug,
        title=title,
        bonus_percent=b.bonus_percent or 0,
        max_bonus_amount=float(b.max_bonus_amount or 0),
        max_bonus_currency=b.max_bonus_currency,
        wagering_multiplier=float(b.wagering_multiplier or 0),
        wagering_deadline_days=b.wagering_deadline_days or 0,
        max_bet=float(b.max_bet or 0),
        free_spins=b.free_spins,
        no_deposit=b.no_deposit,
        jogai_score=float(b.jogai_score or 0),
        verdict_key=b.verdict_key or "verdict_caution",
        affiliate_link=b.affiliate_link,
        formatted_max_bonus=format_currency(
            float(b.max_bonus_amount or 0), locale
        ),
        expected_loss=float(b.expected_loss or 0),
        expected_loss_formatted=format_currency(
            float(b.expected_loss or 0), locale
        ),
        profit_probability=float(b.profit_probability or 0),
        verdict_text=t(b.verdict_key or "verdict_caution", locale),
        casino_description=casino_desc,
        casino_withdrawal_time=casino.withdrawal_time if casino else None,
    )
