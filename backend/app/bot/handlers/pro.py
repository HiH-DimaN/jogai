"""PRO subscription handler — Telegram Stars payment."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from app.database.models import User
from app.i18n import t
from app.services.pro import PRO_PRICE_STARS, activate_pro, get_pro_status
from app.utils.formatters import format_currency

router = Router()


def _pro_keyboard(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("pro_btn_subscribe", locale), callback_data="pro_buy")],
            [InlineKeyboardButton(text=t("pro_btn_status", locale), callback_data="pro_status")],
        ]
    )


@router.message(Command("pro"))
async def cmd_pro(message: Message, locale: str, db_user: User) -> None:
    """Show PRO info and subscribe button."""
    status = await get_pro_status(db_user.id)

    if status["is_pro"] and status["expires_at"]:
        date_str = status["expires_at"].strftime("%d/%m/%Y")
        text = t("pro_already_active", locale, date=date_str)
    else:
        text = (
            t("pro_title", locale)
            + "\n\n"
            + t("pro_features", locale)
            + "\n\n"
            + t("pro_description", locale)
            + "\n\n💎 "
            + str(PRO_PRICE_STARS)
            + " Telegram Stars"
        )

    await message.answer(text, reply_markup=_pro_keyboard(locale))


@router.callback_query(F.data == "pro_buy")
async def cb_pro_buy(callback: CallbackQuery, locale: str, db_user: User) -> None:
    """Send Telegram Stars invoice."""
    status = await get_pro_status(db_user.id)
    if status["is_pro"] and status["expires_at"]:
        date_str = status["expires_at"].strftime("%d/%m/%Y")
        await callback.answer(t("pro_already_active", locale, date=date_str), show_alert=True)
        return

    await callback.message.answer_invoice(
        title=t("pro_payment_title", locale, amount=str(PRO_PRICE_STARS)),
        description=t("pro_payment_description", locale),
        payload="pro_subscription",
        currency="XTR",
        prices=[LabeledPrice(label="Jogai PRO", amount=PRO_PRICE_STARS)],
    )
    await callback.answer()


@router.callback_query(F.data == "pro_status")
async def cb_pro_status(callback: CallbackQuery, locale: str, db_user: User) -> None:
    """Check PRO status."""
    status = await get_pro_status(db_user.id)

    if status["is_pro"] and status["expires_at"]:
        date_str = status["expires_at"].strftime("%d/%m/%Y")
        text = t("pro_activated", locale, date=date_str)
    else:
        text = t("pro_expired", locale)

    await callback.answer(text, show_alert=True)


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    """Approve the pre-checkout query."""
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, locale: str, db_user: User) -> None:
    """Handle successful Telegram Stars payment."""
    expires_at = await activate_pro(db_user.id)
    date_str = expires_at.strftime("%d/%m/%Y")
    await message.answer(t("pro_payment_success", locale, date=date_str))
