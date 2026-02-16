from collections.abc import AsyncGenerator

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_session
from app.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def get_locale(locale: str = Query(DEFAULT_LOCALE)) -> str:
    if locale in SUPPORTED_LOCALES:
        return locale
    return DEFAULT_LOCALE


async def get_current_user() -> dict:
    # TODO: implement JWT auth from Telegram initData
    return {"id": 0, "locale": DEFAULT_LOCALE}
