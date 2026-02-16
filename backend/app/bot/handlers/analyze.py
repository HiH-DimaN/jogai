from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.database.engine import async_session
from app.database.models import Analysis, User
from app.i18n import t
from app.services.bonus_analyzer import analyze_bonus
from app.utils.formatters import format_currency

router = Router()


class AnalyzeState(StatesGroup):
    waiting_for_input = State()


@router.message(Command("analyze"))
async def cmd_analyze(message: Message, locale: str, state: FSMContext) -> None:
    await state.set_state(AnalyzeState.waiting_for_input)
    await message.answer(t("analyze_prompt", locale))


@router.callback_query(F.data == "analyze")
async def cb_analyze(callback: CallbackQuery, locale: str, state: FSMContext) -> None:
    await state.set_state(AnalyzeState.waiting_for_input)
    await callback.message.answer(t("analyze_prompt", locale))
    await callback.answer()


@router.message(AnalyzeState.waiting_for_input)
async def process_analysis(
    message: Message, locale: str, db_user: User, state: FSMContext
) -> None:
    await state.clear()

    user_text = message.text or ""
    if not user_text.strip():
        await message.answer(t("error_generic", locale))
        return

    try:
        result = await analyze_bonus(user_text, locale)
    except Exception:
        await message.answer(t("error_generic", locale))
        return

    score = result["score"]
    parsed = result.get("parsed", {})
    currency = t("currency_symbol", locale)

    # Build response — all strings through t()
    lines = [t("analyze_result_title", locale), ""]

    deposit = parsed.get("deposit") or score.get("deposit", 0)
    bonus_amount = parsed.get("bonus_amount") or score.get("bonus_amount", 0)
    bonus_percent = parsed.get("bonus_percent") or score.get("bonus_percent", 0)
    total = score.get("total_balance", 0)

    if deposit:
        lines.append(t("analyze_deposit", locale, currency=currency, amount=format_currency(deposit, locale).replace(currency, "")))
    if bonus_amount:
        lines.append(t("analyze_bonus_line", locale, currency=currency, amount=format_currency(bonus_amount, locale).replace(currency, ""), percent=bonus_percent))
    if total:
        lines.append(t("analyze_total", locale, currency=currency, amount=format_currency(total, locale).replace(currency, "")))

    lines.append("")

    wagering_mult = score.get("wagering_multiplier", 0)
    wagering_total = score.get("wagering_total", 0)
    lines.append(t("analyze_wagering", locale, multiplier=wagering_mult, currency=currency, total=format_currency(wagering_total, locale).replace(currency, "")))

    deadline = score.get("deadline_days", 0)
    lines.append(t("analyze_deadline", locale, days=deadline))

    max_bet = score.get("max_bet", 0)
    if max_bet:
        lines.append(t("analyze_max_bet", locale, currency=currency, amount=format_currency(max_bet, locale).replace(currency, "")))

    bets_needed = score.get("bets_needed", 0)
    bets_per_day = score.get("bets_per_day", 0)
    bets_per_hour = score.get("bets_per_hour", 0)
    lines.append(t("analyze_bets_needed", locale, count=bets_needed, per_day=bets_per_day, per_hour=bets_per_hour))

    lines.append("")

    expected_loss = score.get("expected_loss", 0)
    lines.append(t("analyze_expected_loss", locale, currency=currency, amount=format_currency(expected_loss, locale).replace(currency, "")))

    profit_prob = score.get("profit_probability", 0)
    lines.append(t("analyze_profit_chance", locale, percent=profit_prob))

    lines.append("")

    # Verdict through t() — key, not text!
    verdict_key = score.get("verdict_key", "verdict_caution")
    verdict_label_key = f"verdict_label_{verdict_key.replace('verdict_', '')}"
    jogai_score = score.get("jogai_score", 5.0)
    lines.append(f"⭐ Jogai Score: {jogai_score}/10")
    lines.append(t(verdict_label_key, locale))

    lines.append("")
    lines.append(t("analyze_see_recommended", locale))

    text = "\n".join(lines)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_see_recommended", locale), callback_data="bonuses")]
        ]
    )

    await message.answer(text, reply_markup=keyboard)

    # Save analysis to DB
    async with async_session() as session:
        analysis = Analysis(
            user_id=db_user.id,
            input_text=user_text,
            input_type="text",
            parsed_bonus_percent=bonus_percent,
            parsed_wagering=wagering_mult,
            parsed_deadline=deadline,
            parsed_max_bet=max_bet,
            jogai_score=jogai_score,
            verdict_key=verdict_key,
            ai_response=result.get("ai_summary", ""),
            locale=locale,
        )
        session.add(analysis)
        await session.commit()
