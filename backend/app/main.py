from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router_analyze import router as analyze_router
from app.api.router_auth import router as auth_router
from app.api.router_bonuses import router as bonuses_router
from app.api.router_casinos import router as casinos_router
from app.api.router_digest import router as digest_router
from app.api.router_quiz import router as quiz_router
from app.api.router_tracker import router as tracker_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


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
    # TODO: pass update to aiogram dispatcher
    return JSONResponse(content={"ok": True})
