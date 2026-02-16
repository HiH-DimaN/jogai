"""Local development: run bot in polling mode."""
import asyncio
import logging

from app.bot.bot import dp, get_bot
from app.bot.handlers.bonus import router as bonus_router
from app.bot.handlers.start import router as start_router
from app.bot.middlewares import LocaleMiddleware, RateLimitMiddleware, UserMiddleware

logging.basicConfig(level=logging.INFO)


def setup_bot() -> None:
    # Register middlewares (order matters: User → Locale → RateLimit)
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.message.middleware(LocaleMiddleware())
    dp.callback_query.middleware(LocaleMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    # Register routers
    dp.include_router(start_router)
    dp.include_router(bonus_router)


async def main() -> None:
    setup_bot()
    bot = get_bot()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
