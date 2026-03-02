from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from app.config import settings
from app.database.engine import async_session
from app.database.models import Referral, User
from app.i18n import t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, locale: str, db_user: User) -> None:
    # Deep link referral: /start ref_CODE
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and args[1].startswith("ref_"):
        ref_code = args[1].replace("ref_", "")
        if ref_code and ref_code != db_user.referral_code:
            async with async_session() as session:
                result = await session.execute(
                    select(User).where(User.referral_code == ref_code)
                )
                referrer = result.scalar_one_or_none()
                if referrer and not db_user.referred_by:
                    db_user.referred_by = referrer.id
                    referrer.jogai_coins += 5
                    session.add(
                        Referral(
                            referrer_id=referrer.id,
                            referred_id=db_user.id,
                        )
                    )
                    session.add(referrer)
                    session.add(db_user)
                    await session.commit()

    # Generate referral code if not set
    if not db_user.referral_code:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == db_user.id)
            )
            user = result.scalar_one()
            user.referral_code = f"{db_user.id}"[-8:]
            await session.commit()

    text = t("welcome", locale) + "\n\n" + t("welcome_question", locale)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_bonuses", locale), callback_data="bonuses")],
            [InlineKeyboardButton(text=t("btn_casino", locale), callback_data="casino_quiz")],
            [InlineKeyboardButton(text=t("btn_analyze", locale), callback_data="analyze")],
            [
                InlineKeyboardButton(
                    text=t("btn_miniapp", locale),
                    web_app={"url": f"{settings.app_url}/miniapp"}
                    if settings.app_url.startswith("https")
                    else None,
                    callback_data="miniapp"
                    if not settings.app_url.startswith("https")
                    else None,
                )
            ],
        ]
    )

    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "miniapp")
async def cb_miniapp(callback: CallbackQuery, locale: str) -> None:
    await callback.answer(t("miniapp_coming_soon", locale), show_alert=True)
