from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.database.models import User
from app.i18n import t
from app.services.casino_matcher import match_casinos
from app.utils.formatters import format_currency
from app.utils.telegram import format_casino_card

router = Router()


class QuizState(StatesGroup):
    q1_game = State()
    q2_deposit = State()
    q3_payment = State()
    q4_priority = State()
    q5_experience = State()


# --- Q1: Game type ---

@router.callback_query(F.data == "casino_quiz")
async def quiz_start(callback: CallbackQuery, locale: str, state: FSMContext) -> None:
    await state.set_state(QuizState.q1_game)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("casino_q1_slots", locale), callback_data="q1:slots")],
        [InlineKeyboardButton(text=t("casino_q1_crash", locale), callback_data="q1:crash")],
        [InlineKeyboardButton(text=t("casino_q1_sports", locale), callback_data="q1:sports")],
        [InlineKeyboardButton(text=t("casino_q1_table", locale), callback_data="q1:table")],
    ])
    await callback.message.answer(t("casino_q1", locale), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(QuizState.q1_game, F.data.startswith("q1:"))
async def quiz_q1(callback: CallbackQuery, locale: str, state: FSMContext) -> None:
    await state.update_data(game_type=callback.data.split(":")[1])
    await state.set_state(QuizState.q2_deposit)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("casino_q2_low", locale), callback_data="q2:low")],
        [InlineKeyboardButton(text=t("casino_q2_medium", locale), callback_data="q2:medium")],
        [InlineKeyboardButton(text=t("casino_q2_high", locale), callback_data="q2:high")],
        [InlineKeyboardButton(text=t("casino_q2_vip", locale), callback_data="q2:vip")],
    ])
    await callback.message.answer(t("casino_q2", locale), reply_markup=keyboard)
    await callback.answer()


# --- Q3: Payment ---

@router.callback_query(QuizState.q2_deposit, F.data.startswith("q2:"))
async def quiz_q2(callback: CallbackQuery, locale: str, state: FSMContext) -> None:
    await state.update_data(deposit_range=callback.data.split(":")[1])
    await state.set_state(QuizState.q3_payment)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("casino_q3_pix", locale), callback_data="q3:pix")],
        [InlineKeyboardButton(text=t("casino_q3_crypto", locale), callback_data="q3:crypto")],
        [InlineKeyboardButton(text=t("casino_q3_card", locale), callback_data="q3:card")],
    ])
    await callback.message.answer(t("casino_q3", locale), reply_markup=keyboard)
    await callback.answer()


# --- Q4: Priority ---

@router.callback_query(QuizState.q3_payment, F.data.startswith("q3:"))
async def quiz_q3(callback: CallbackQuery, locale: str, state: FSMContext) -> None:
    await state.update_data(payment=callback.data.split(":")[1])
    await state.set_state(QuizState.q4_priority)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("casino_q4_bonus", locale), callback_data="q4:bonus")],
        [InlineKeyboardButton(text=t("casino_q4_wagering", locale), callback_data="q4:wagering")],
        [InlineKeyboardButton(text=t("casino_q4_withdraw", locale), callback_data="q4:withdraw")],
    ])
    await callback.message.answer(t("casino_q4", locale), reply_markup=keyboard)
    await callback.answer()


# --- Q5: Experience ---

@router.callback_query(QuizState.q4_priority, F.data.startswith("q4:"))
async def quiz_q4(callback: CallbackQuery, locale: str, state: FSMContext) -> None:
    await state.update_data(priority=callback.data.split(":")[1])
    await state.set_state(QuizState.q5_experience)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("casino_q5_beginner", locale), callback_data="q5:beginner")],
        [InlineKeyboardButton(text=t("casino_q5_intermediate", locale), callback_data="q5:intermediate")],
        [InlineKeyboardButton(text=t("casino_q5_advanced", locale), callback_data="q5:advanced")],
    ])
    await callback.message.answer(t("casino_q5", locale), reply_markup=keyboard)
    await callback.answer()


# --- Result ---

@router.callback_query(QuizState.q5_experience, F.data.startswith("q5:"))
async def quiz_result(
    callback: CallbackQuery, locale: str, db_user: User, state: FSMContext
) -> None:
    data = await state.get_data()
    await state.clear()

    experience = callback.data.split(":")[1]

    results = await match_casinos(
        geo=db_user.geo,
        game_type=data.get("game_type", "slots"),
        deposit_range=data.get("deposit_range", "medium"),
        payment=data.get("payment", "pix"),
        priority=data.get("priority", "bonus"),
        experience=experience,
    )

    if not results:
        await callback.message.answer(t("error_generic", locale))
        await callback.answer()
        return

    text = t("casino_result_title", locale) + "\n"

    buttons = []
    for r in results:
        casino = r["casino"]
        match_pct = r["match_percent"]

        text += f"\n<b>{casino.name}</b> — {t('casino_match', locale, percent=match_pct)}\n"
        text += format_casino_card(casino, locale) + "\n"

        # Best bonus for this casino
        if casino.bonuses:
            best = max(casino.bonuses, key=lambda b: float(b.jogai_score or 0))
            text += t("casino_bonus_line", locale, bonus=best.title_pt or "") + "\n"

        text += t("casino_withdraw_line", locale, time=casino.withdrawal_time or "—") + "\n"

        if casino.affiliate_link_template:
            link = casino.affiliate_link_template.format(
                ref_id=casino.ref_id or "", user_id=db_user.id
            )
            buttons.append([
                InlineKeyboardButton(
                    text=f"{t('btn_register', locale)} [{casino.name}]",
                    url=link,
                )
            ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()
