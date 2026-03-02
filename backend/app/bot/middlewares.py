import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy import select

from app.config import settings
from app.database.engine import async_session
from app.database.models import User
from app.i18n import DEFAULT_LOCALE, get_user_locale

logger = logging.getLogger(__name__)

# Locale → geo mapping
LOCALE_GEO_MAP = {
    "pt_BR": "BR",
    "es_MX": "MX",
}


class UserMiddleware(BaseMiddleware):
    """Upsert user in DB with locale and geo on every update."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user:
            async with async_session() as session:
                result = await session.execute(
                    select(User).where(User.id == user.id)
                )
                db_user = result.scalar_one_or_none()

                locale = get_user_locale(
                    user.language_code,
                    db_user.locale if db_user else None,
                )
                geo = LOCALE_GEO_MAP.get(locale, settings.default_geo)

                if db_user:
                    db_user.username = user.username
                    db_user.first_name = user.first_name
                    db_user.language_code = user.language_code
                    db_user.last_active_at = datetime.now(timezone.utc)
                else:
                    db_user = User(
                        id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        language_code=user.language_code,
                        locale=locale,
                        geo=geo,
                    )
                    session.add(db_user)

                await session.commit()
                await session.refresh(db_user)
                data["db_user"] = db_user

        return await handler(event, data)


class LocaleMiddleware(BaseMiddleware):
    """Inject locale into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db_user = data.get("db_user")
        if db_user:
            data["locale"] = db_user.locale
        else:
            # Fallback: detect from Telegram user
            tg_user = None
            if isinstance(event, Message) and event.from_user:
                tg_user = event.from_user
            elif isinstance(event, CallbackQuery) and event.from_user:
                tg_user = event.from_user

            if tg_user:
                data["locale"] = get_user_locale(tg_user.language_code)
            else:
                data["locale"] = DEFAULT_LOCALE

        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Simple Redis-based rate limiter."""

    def __init__(self, limit: int = 10, window: int = 60):
        self.limit = limit
        self.window = window
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            try:
                import redis.asyncio as aioredis

                r = aioredis.from_url(settings.redis_url)
                key = f"rate:{user_id}"
                count = await r.incr(key)
                if count == 1:
                    await r.expire(key, self.window)
                await r.aclose()

                if count > self.limit:
                    from app.i18n import t

                    locale = data.get("locale", DEFAULT_LOCALE)
                    if isinstance(event, Message):
                        await event.answer(t("error_rate_limit", locale))
                    elif isinstance(event, CallbackQuery):
                        await event.answer(t("error_rate_limit", locale), show_alert=True)
                    return None
            except Exception:
                logger.warning("Rate limit check failed, allowing request")

        return await handler(event, data)
