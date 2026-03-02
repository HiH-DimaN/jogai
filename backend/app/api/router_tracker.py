from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_locale, get_session
from app.database.models import Bet, User
from app.utils.formatters import format_currency

router = APIRouter(prefix="/tracker", tags=["tracker"])

GEO_CURRENCY = {"BR": "BRL", "MX": "MXN"}


class BetCreate(BaseModel):
    game_type: str = "slots"
    game_name: str = ""
    bet_amount: float
    result_amount: float
    note: str = ""


class BetResponse(BaseModel):
    id: int
    game_type: str
    game_name: str
    bet_amount: float
    bet_currency: str
    result_amount: float
    profit: float
    note: str | None
    created_at: str


class BetStatsResponse(BaseModel):
    total_bets: int
    total_wagered: float
    total_wagered_formatted: str
    total_profit: float
    total_profit_formatted: str
    roi: float
    win_rate: float
    best_game: str | None
    worst_game: str | None
    currency: str


@router.get("/bets", response_model=list[BetResponse])
async def get_bets(
    limit: int = 20,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Bet)
        .where(Bet.user_id == user.id)
        .order_by(Bet.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    bets = result.scalars().all()

    return [
        BetResponse(
            id=b.id,
            game_type=b.game_type or "",
            game_name=b.game_name or "",
            bet_amount=float(b.bet_amount or 0),
            bet_currency=b.bet_currency,
            result_amount=float(b.result_amount or 0),
            profit=float(b.profit or 0),
            note=b.note,
            created_at=b.created_at.isoformat() if b.created_at else "",
        )
        for b in bets
    ]


@router.post("/bets", response_model=BetResponse)
async def add_bet(
    body: BetCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    currency = GEO_CURRENCY.get(user.geo, "BRL")
    profit = body.result_amount - body.bet_amount

    bet = Bet(
        user_id=user.id,
        game_type=body.game_type,
        game_name=body.game_name,
        bet_amount=body.bet_amount,
        bet_currency=currency,
        result_amount=body.result_amount,
        profit=profit,
        note=body.note or None,
    )
    session.add(bet)
    await session.commit()
    await session.refresh(bet)

    return BetResponse(
        id=bet.id,
        game_type=bet.game_type or "",
        game_name=bet.game_name or "",
        bet_amount=float(bet.bet_amount or 0),
        bet_currency=bet.bet_currency,
        result_amount=float(bet.result_amount or 0),
        profit=float(bet.profit or 0),
        note=bet.note,
        created_at=bet.created_at.isoformat() if bet.created_at else "",
    )


@router.get("/stats", response_model=BetStatsResponse)
async def get_stats(
    user: User = Depends(get_current_user),
    locale: str = Depends(get_locale),
    session: AsyncSession = Depends(get_session),
):
    currency = GEO_CURRENCY.get(user.geo, "BRL")

    # Aggregates
    result = await session.execute(
        select(
            func.count(Bet.id),
            func.coalesce(func.sum(Bet.bet_amount), 0),
            func.coalesce(func.sum(Bet.profit), 0),
        ).where(Bet.user_id == user.id)
    )
    row = result.one()
    total_bets = row[0]
    total_wagered = float(row[1])
    total_profit = float(row[2])

    roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0.0

    # Win rate
    wins_result = await session.execute(
        select(func.count()).where(Bet.user_id == user.id, Bet.profit > 0)
    )
    wins = wins_result.scalar() or 0
    win_rate = (wins / total_bets * 100) if total_bets > 0 else 0.0

    # Best/worst game by total profit
    best_game = None
    worst_game = None
    if total_bets > 0:
        game_stats = await session.execute(
            select(
                Bet.game_name,
                func.sum(Bet.profit).label("total_profit"),
            )
            .where(Bet.user_id == user.id, Bet.game_name.isnot(None), Bet.game_name != "")
            .group_by(Bet.game_name)
            .order_by(func.sum(Bet.profit).desc())
        )
        games = game_stats.all()
        if games:
            best_game = games[0][0]
            worst_game = games[-1][0]

    return BetStatsResponse(
        total_bets=total_bets,
        total_wagered=total_wagered,
        total_wagered_formatted=format_currency(total_wagered, locale),
        total_profit=total_profit,
        total_profit_formatted=format_currency(total_profit, locale),
        roi=round(roi, 1),
        win_rate=round(win_rate, 1),
        best_game=best_game,
        worst_game=worst_game,
        currency=currency,
    )
