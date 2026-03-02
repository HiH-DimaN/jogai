from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import func, select

from app.database.engine import async_session
from app.database.models import Bet, User
from app.i18n import t
from app.utils.formatters import format_currency

router = Router()

GEO_CURRENCY = {"BR": "BRL", "MX": "MXN"}


class BetState(StatesGroup):
    waiting_for_input = State()


@router.message(Command("bet"))
async def cmd_bet(message: Message, locale: str, state: FSMContext) -> None:
    await state.set_state(BetState.waiting_for_input)
    text = (
        t("analyze_prompt", locale).split("—")[0].strip()
        + "\n\n"
        + "Format: game_type | game_name | bet_amount | result_amount\n"
        + "Ex: slots | Sweet Bonanza | 50 | 120"
    )
    await message.answer(text)


@router.message(BetState.waiting_for_input)
async def process_bet(
    message: Message, locale: str, db_user: User, state: FSMContext
) -> None:
    await state.clear()

    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) < 4:
        await message.answer(t("error_generic", locale))
        return

    try:
        game_type = parts[0]
        game_name = parts[1]
        bet_amount = float(parts[2])
        result_amount = float(parts[3])
    except (ValueError, IndexError):
        await message.answer(t("error_generic", locale))
        return

    currency = GEO_CURRENCY.get(db_user.geo, "BRL")
    profit = result_amount - bet_amount

    async with async_session() as session:
        bet = Bet(
            user_id=db_user.id,
            game_type=game_type,
            game_name=game_name,
            bet_amount=bet_amount,
            bet_currency=currency,
            result_amount=result_amount,
            profit=profit,
        )
        session.add(bet)
        await session.commit()

    profit_formatted = format_currency(profit, locale)
    sign = "+" if profit >= 0 else ""
    await message.answer(
        t("tracker_added", locale) + f"\n{game_name}: {sign}{profit_formatted}"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message, locale: str, db_user: User) -> None:
    currency_symbol = t("currency_symbol", locale)

    async with async_session() as session:
        result = await session.execute(
            select(
                func.count(Bet.id),
                func.coalesce(func.sum(Bet.bet_amount), 0),
                func.coalesce(func.sum(Bet.profit), 0),
            ).where(Bet.user_id == db_user.id)
        )
        row = result.one()
        total_bets = row[0]
        total_wagered = float(row[1])
        total_profit = float(row[2])

        wins_result = await session.execute(
            select(func.count()).where(
                Bet.user_id == db_user.id, Bet.profit > 0
            )
        )
        wins = wins_result.scalar() or 0

    if total_bets == 0:
        await message.answer(t("tracker_stats_title", locale) + "\n\n—")
        return

    roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0.0
    win_rate = (wins / total_bets * 100) if total_bets > 0 else 0.0

    text = (
        t("tracker_stats_title", locale)
        + "\n\n"
        + t("tracker_roi", locale, value=f"{roi:.1f}")
        + "\n"
        + t("tracker_win_rate", locale, value=f"{win_rate:.1f}")
        + "\n"
        + t(
            "tracker_profit",
            locale,
            currency=currency_symbol,
            value=format_currency(total_profit, locale).replace(currency_symbol, ""),
        )
    )

    # Bankroll recommendation (Kelly-inspired: 2% of estimated bankroll)
    if total_wagered > 0:
        avg_bet = total_wagered / total_bets
        bankroll_est = avg_bet * 50  # rough estimate
        recommended_bet = bankroll_est * 0.02
        text += "\n\n" + t(
            "bankroll_recommendation",
            locale,
            currency=currency_symbol,
            amount=format_currency(bankroll_est, locale).replace(currency_symbol, ""),
            bet=format_currency(recommended_bet, locale).replace(currency_symbol, ""),
        )

    await message.answer(text)
