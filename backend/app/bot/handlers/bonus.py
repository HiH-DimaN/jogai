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


async def _get_top_bonuses(geo: str, limit: int = 3) -> list[Bonus]:
    async with async_session() as session:
        result = await session.execute(
            select(Bonus)
            .where(Bonus.is_active.is_(True))
            .where(Bonus.geo.any(geo))
            .order_by(Bonus.jogai_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


@router.message(Command("bonus"))
async def cmd_bonus(message: Message, locale: str, db_user: User) -> None:
    bonuses = await _get_top_bonuses(geo=db_user.geo)

    if not bonuses:
        await message.answer(t("error_generic", locale))
        return

    today = format_date(datetime.utcnow(), locale)
    text = t("bonus_day_title", locale, date=today) + "\n"

    for bonus in bonuses:
        text += "\n" + format_bonus_card(bonus, locale) + "\n"

    # Button for each bonus
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

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "bonuses")
async def cb_bonuses(callback: CallbackQuery, locale: str, db_user: User) -> None:
    bonuses = await _get_top_bonuses(geo=db_user.geo)

    if not bonuses:
        await callback.message.answer(t("error_generic", locale))
        await callback.answer()
        return

    today = format_date(datetime.utcnow(), locale)
    text = t("bonus_day_title", locale, date=today) + "\n"

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

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
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
