from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Bonus, Click, User
from app.i18n import t
from app.utils.formatters import format_date
from app.utils.telegram import format_bonus_card

router = Router()


async def _get_bonuses(geo: str, limit: int | None = None) -> list[Bonus]:
    async with async_session() as session:
        query = (
            select(Bonus)
            .where(Bonus.is_active.is_(True))
            .where(Bonus.geo.any(geo))
            .order_by(Bonus.jogai_score.desc())
        )
        if limit:
            query = query.limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())


def _build_bonus_message(
    bonuses: list[Bonus], locale: str, show_all: bool = False,
) -> tuple[str, InlineKeyboardMarkup]:
    today = format_date(datetime.utcnow(), locale)
    title_key = "bonus_all_title" if show_all else "bonus_day_title"
    text = t(title_key, locale, date=today) + "\n"

    for bonus in bonuses:
        text += "\n" + format_bonus_card(bonus, locale) + "\n"

    buttons = []
    for bonus in bonuses:
        casino_name = bonus.casino.name if bonus.casino else "Casino"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{t('btn_get_bonus', locale)} [{casino_name}]",
                    callback_data=f"click:{bonus.id}",
                )
            ]
        )

    if not show_all:
        buttons.append(
            [InlineKeyboardButton(
                text=t("btn_see_all_bonuses", locale),
                callback_data="bonuses_all",
            )]
        )

    return text, InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("bonus"))
async def cmd_bonus(message: Message, locale: str, db_user: User) -> None:
    bonuses = await _get_bonuses(geo=db_user.geo, limit=3)

    if not bonuses:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_analyze", locale), callback_data="analyze")],
            ]
        )
        await message.answer(t("bonus_empty", locale), reply_markup=keyboard)
        return

    text, keyboard = _build_bonus_message(bonuses, locale)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "bonuses")
async def cb_bonuses(callback: CallbackQuery, locale: str, db_user: User) -> None:
    bonuses = await _get_bonuses(geo=db_user.geo, limit=3)

    if not bonuses:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_analyze", locale), callback_data="analyze")],
            ]
        )
        await callback.message.answer(t("bonus_empty", locale), reply_markup=keyboard)
        await callback.answer()
        return

    text, keyboard = _build_bonus_message(bonuses, locale)
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "bonuses_all")
async def cb_bonuses_all(callback: CallbackQuery, locale: str, db_user: User) -> None:
    bonuses = await _get_bonuses(geo=db_user.geo)

    if not bonuses:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_analyze", locale), callback_data="analyze")],
            ]
        )
        await callback.message.answer(t("bonus_empty", locale), reply_markup=keyboard)
        await callback.answer()
        return

    text, keyboard = _build_bonus_message(bonuses, locale, show_all=True)
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("click:"))
async def cb_click(callback: CallbackQuery, locale: str, db_user: User) -> None:
    bonus_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Bonus).where(Bonus.id == bonus_id)
        )
        bonus = result.scalar_one_or_none()

        if not bonus:
            await callback.answer(t("error_generic", locale), show_alert=True)
            return

        # Record click with locale
        click = Click(
            user_id=db_user.id,
            bonus_id=bonus.id,
            casino_id=bonus.casino_id,
            source="bot",
            locale=locale,
        )
        session.add(click)
        await session.commit()

    # Send affiliate link
    link = bonus.affiliate_link or "#"
    await callback.message.answer(f"<a href='{link}'>{t('btn_get_bonus', locale)}</a>")
    await callback.answer()
