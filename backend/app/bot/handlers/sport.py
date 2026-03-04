from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import SportPick, User
from app.i18n import t

router = Router()


def _get_localized_field(obj: SportPick, field_prefix: str, locale: str) -> str:
    """Get localized field: field_pt or field_es based on locale."""
    suffix = "pt" if locale.startswith("pt") else "es"
    return getattr(obj, f"{field_prefix}_{suffix}", None) or getattr(obj, f"{field_prefix}_pt", "") or ""


@router.message(Command("sport"))
async def cmd_sport(message: Message, locale: str, db_user: User) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(SportPick)
            .where(SportPick.geo.any(db_user.geo))
            .order_by(SportPick.match_date.desc())
            .limit(1)
        )
        pick = result.scalar_one_or_none()

    if not pick:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_analyze", locale), callback_data="analyze")],
            ]
        )
        await message.answer(t("sport_no_match", locale), reply_markup=keyboard)
        return

    # Parse match name for home/away
    parts = (pick.match_name or "").split(" vs ")
    home = parts[0].strip() if parts else "—"
    away = parts[1].strip() if len(parts) > 1 else "—"

    analysis = _get_localized_field(pick, "analysis", locale)
    description = _get_localized_field(pick, "pick_description", locale)

    text = t("sport_title", locale) + "\n\n"
    text += t("sport_match", locale, home=home, away=away) + "\n"
    text += f"🏆 {pick.league or ''}\n\n"
    text += t("sport_analysis", locale, text=analysis) + "\n\n"
    text += t("sport_recommendation", locale, pick=description, odds=pick.odds or 0) + "\n"

    buttons = []
    if pick.affiliate_link:
        buttons.append([
            InlineKeyboardButton(
                text=t("btn_bet", locale),
                url=pick.affiliate_link,
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await message.answer(text, reply_markup=keyboard)
