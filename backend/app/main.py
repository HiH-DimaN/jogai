from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router_analyze import router as analyze_router
from app.api.router_auth import router as auth_router
from app.api.router_bonuses import router as bonuses_router
from app.api.router_casinos import router as casinos_router
from app.api.router_digest import router as digest_router
from app.api.router_quiz import router as quiz_router
from app.api.router_tracker import router as tracker_router
from app.bot.bot import dp, get_bot
from app.bot.handlers.analyze import router as analyze_handler_router
from app.bot.handlers.bonus import router as bonus_handler_router
from app.bot.handlers.start import router as start_handler_router
from app.bot.middlewares import LocaleMiddleware, RateLimitMiddleware, UserMiddleware


def _setup_bot() -> None:
    """Register middlewares and handlers on the dispatcher."""
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.message.middleware(LocaleMiddleware())
    dp.callback_query.middleware(LocaleMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    dp.include_router(start_handler_router)
    dp.include_router(bonus_handler_router)
    dp.include_router(analyze_handler_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _setup_bot()
    yield


app = FastAPI(
    title="Jogai API",
    description="AI Gambling Assistant for LATAM",
    version="0.1.0",
    lifespan=lifespan,
)

# API routers
app.include_router(bonuses_router, prefix="/api")
app.include_router(casinos_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(tracker_router, prefix="/api")
app.include_router(digest_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "jogai"}


@app.post("/bot/webhook")
async def bot_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot=get_bot(), update=update)
    return JSONResponse(content={"ok": True})
