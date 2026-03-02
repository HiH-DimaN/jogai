from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from app.config import settings
from app.database.engine import async_session
from app.database.models import Referral, User
from app.i18n import t

router = Router()


@router.message(Command("referral"))
async def cmd_referral(message: Message, locale: str, db_user: User) -> None:
    # Generate referral code if missing
    if not db_user.referral_code:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == db_user.id)
            )
            user = result.scalar_one()
            user.referral_code = str(db_user.id)[-8:]
            await session.commit()
            db_user.referral_code = user.referral_code

    # Count referrals
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).where(Referral.referrer_id == db_user.id)
        )
        referral_count = result.scalar() or 0

    bot_me = await message.bot.me()
    bot_username = bot_me.username
    referral_link = f"https://t.me/{bot_username}?start=ref_{db_user.referral_code}"

    text = (
        t("referral_your_link", locale)
        + f"\n{referral_link}\n\n"
        + t("referral_coins_balance", locale, coins=db_user.jogai_coins)
        + f"\n({referral_count} "
        + ("convidados" if locale.startswith("pt") else "invitados")
        + ")\n\n"
        + t("referral_reward", locale)
    )

    await message.answer(text)
