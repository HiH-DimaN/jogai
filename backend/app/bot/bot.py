from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

dp = Dispatcher()

# Lazy bot init — token validated only when actually needed
_bot: Bot | None = None


def get_bot() -> Bot:
    """Get or create the singleton bot (for webhook/polling context)."""
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def reset_bot() -> None:
    """Reset the singleton bot. Must be called in Celery tasks
    before using get_bot(), because asyncio.run() closes the event loop
    and the old bot's aiohttp session becomes unusable."""
    global _bot
    _bot = None
