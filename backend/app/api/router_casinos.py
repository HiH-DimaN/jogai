from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_locale, get_session
from app.database.models import Bonus, Casino
from app.utils.formatters import format_currency

router = APIRouter(prefix="/casinos", tags=["casinos"])


class BonusResponse(BaseModel):
    id: int
    casino_id: int
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


class CasinoResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    min_deposit: float | None
    min_deposit_formatted: str | None
    pix_supported: bool
    spei_supported: bool
    crypto_supported: bool
    withdrawal_time: str | None
    affiliate_link: str | None
    best_bonus: str | None
    best_jogai_score: float | None
    bonus_count: int


class CasinoListResponse(BaseModel):
    casinos: list[CasinoResponse]
    geo: str
    locale: str


class CasinoDetailResponse(CasinoResponse):
    bonuses: list[BonusResponse]


@router.get("", response_model=CasinoListResponse)
async def get_casinos(
    geo: str = "BR",
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    lang_suffix = "pt" if locale.startswith("pt") else "es"

    stmt = (
        select(Casino)
        .where(Casino.is_active.is_(True), Casino.geo.any(geo))
        .order_by(Casino.name)
    )
    result = await session.execute(stmt)
    casinos = result.scalars().all()

    items = []
    for c in casinos:
        description = getattr(c, f"description_{lang_suffix}") or c.description_pt or ""

        # Find best bonus and score among active bonuses for this geo
        active_bonuses = [
            b for b in c.bonuses if b.is_active and geo in (b.geo or [])
        ]

        best_score: float | None = None
        best_bonus_title: str | None = None
        for b in active_bonuses:
            score = float(b.jogai_score or 0)
            if best_score is None or score > best_score:
                best_score = score
                best_bonus_title = getattr(b, f"title_{lang_suffix}") or b.title_pt or ""

        # Build affiliate link from template
        affiliate_link = None
        if c.affiliate_link_template and c.ref_id:
            affiliate_link = c.affiliate_link_template.replace("{ref_id}", c.ref_id)
        elif c.affiliate_link_template:
            affiliate_link = c.affiliate_link_template

        min_deposit_formatted = None
        if c.min_deposit is not None:
            min_deposit_formatted = format_currency(float(c.min_deposit), locale)

        items.append(
            CasinoResponse(
                id=c.id,
                name=c.name,
                slug=c.slug,
                description=description,
                min_deposit=float(c.min_deposit) if c.min_deposit is not None else None,
                min_deposit_formatted=min_deposit_formatted,
                pix_supported=c.pix_supported,
                spei_supported=c.spei_supported,
                crypto_supported=c.crypto_supported,
                withdrawal_time=c.withdrawal_time,
                affiliate_link=affiliate_link,
                best_bonus=best_bonus_title,
                best_jogai_score=best_score,
                bonus_count=len(active_bonuses),
            )
        )

    return CasinoListResponse(casinos=items, geo=geo, locale=locale)


@router.get("/{slug}", response_model=CasinoDetailResponse)
async def get_casino(
    slug: str,
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    lang_suffix = "pt" if locale.startswith("pt") else "es"

    result = await session.execute(select(Casino).where(Casino.slug == slug))
    c = result.scalar_one_or_none()

    if not c:
        raise HTTPException(status_code=404, detail="Casino not found")

    description = getattr(c, f"description_{lang_suffix}") or c.description_pt or ""

    # Build affiliate link
    affiliate_link = None
    if c.affiliate_link_template and c.ref_id:
        affiliate_link = c.affiliate_link_template.replace("{ref_id}", c.ref_id)
    elif c.affiliate_link_template:
        affiliate_link = c.affiliate_link_template

    min_deposit_formatted = None
    if c.min_deposit is not None:
        min_deposit_formatted = format_currency(float(c.min_deposit), locale)

    # Build bonus list
    active_bonuses = [b for b in c.bonuses if b.is_active]
    bonus_items = []
    best_score: float | None = None
    best_bonus_title: str | None = None

    for b in sorted(active_bonuses, key=lambda x: float(x.jogai_score or 0), reverse=True):
        title = getattr(b, f"title_{lang_suffix}") or b.title_pt or ""
        score = float(b.jogai_score or 0)

        if best_score is None or score > best_score:
            best_score = score
            best_bonus_title = title

        bonus_items.append(
            BonusResponse(
                id=b.id,
                casino_id=b.casino_id or 0,
                title=title,
                bonus_percent=b.bonus_percent or 0,
                max_bonus_amount=float(b.max_bonus_amount or 0),
                max_bonus_currency=b.max_bonus_currency,
                wagering_multiplier=float(b.wagering_multiplier or 0),
                wagering_deadline_days=b.wagering_deadline_days or 0,
                max_bet=float(b.max_bet or 0),
                free_spins=b.free_spins,
                no_deposit=b.no_deposit,
                jogai_score=score,
                verdict_key=b.verdict_key or "verdict_caution",
                affiliate_link=b.affiliate_link,
                formatted_max_bonus=format_currency(
                    float(b.max_bonus_amount or 0), locale
                ),
            )
        )

    return CasinoDetailResponse(
        id=c.id,
        name=c.name,
        slug=c.slug,
        description=description,
        min_deposit=float(c.min_deposit) if c.min_deposit is not None else None,
        min_deposit_formatted=min_deposit_formatted,
        pix_supported=c.pix_supported,
        spei_supported=c.spei_supported,
        crypto_supported=c.crypto_supported,
        withdrawal_time=c.withdrawal_time,
        affiliate_link=affiliate_link,
        best_bonus=best_bonus_title,
        best_jogai_score=best_score,
        bonus_count=len(active_bonuses),
        bonuses=bonus_items,
    )
