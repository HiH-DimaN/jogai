from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_locale, get_session
from app.database.models import Bonus, User
from app.utils.formatters import format_currency

router = APIRouter(prefix="/digest", tags=["digest"])


class DigestBonusResponse(BaseModel):
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


class DigestResponse(BaseModel):
    bonuses: list[DigestBonusResponse]
    geo: str
    locale: str


@router.get("", response_model=DigestResponse)
async def get_digest(
    user: User = Depends(get_current_user),
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    geo = user.geo or "BR"
    lang_suffix = "pt" if locale.startswith("pt") else "es"

    stmt = (
        select(Bonus)
        .where(Bonus.is_active.is_(True), Bonus.geo.any(geo))
        .order_by(Bonus.jogai_score.desc())
        .limit(5)
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
            DigestBonusResponse(
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

    return DigestResponse(bonuses=items, geo=geo, locale=locale)
