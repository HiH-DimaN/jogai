import asyncio
import logging
import random
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.bot.bot import get_bot
from app.celery_app import celery
from app.config import settings
from app.database.engine import async_session, engine
from app.database.models import Bonus, Post, SportPick
from app.i18n import t
from app.services.content_generator import (
    generate_bonus_post,
    generate_slot_review,
    generate_sport_post,
)

logger = logging.getLogger(__name__)

# Multi-channel config: geo → {id, locale}
CHANNELS: dict[str, dict] = {
    "BR": {"id": settings.telegram_channel_br_id, "locale": "pt_BR"},
    "MX": {"id": settings.telegram_channel_mx_id, "locale": "es_MX"},
}


# Slot catalog — popular slots with real RTP data
SLOT_CATALOG = [
    {"name": "Gates of Olympus", "rtp": 96.5, "volatility": "high", "provider": "Pragmatic Play", "tip": "slot_tip_gates", "casino": "PIN-UP"},
    {"name": "Sweet Bonanza", "rtp": 96.48, "volatility": "high", "provider": "Pragmatic Play", "tip": "slot_tip_sweet", "casino": "PIN-UP"},
    {"name": "Big Bass Bonanza", "rtp": 96.71, "volatility": "high", "provider": "Pragmatic Play", "tip": "slot_tip_bigbass", "casino": "BET365"},
    {"name": "Book of Dead", "rtp": 96.21, "volatility": "high", "provider": "Play'n GO", "tip": "slot_tip_bookdead", "casino": "BET365"},
    {"name": "Starburst", "rtp": 96.09, "volatility": "low", "provider": "NetEnt", "tip": "slot_tip_starburst", "casino": "RIVALO"},
    {"name": "Gonzo's Quest", "rtp": 95.97, "volatility": "medium", "provider": "NetEnt", "tip": "slot_tip_gonzo", "casino": "RIVALO"},
    {"name": "The Dog House", "rtp": 96.51, "volatility": "high", "provider": "Pragmatic Play", "tip": "slot_tip_doghouse", "casino": "1WIN"},
    {"name": "Wolf Gold", "rtp": 96.01, "volatility": "medium", "provider": "Pragmatic Play", "tip": "slot_tip_wolfgold", "casino": "1WIN"},
    {"name": "Aviator", "rtp": 97.0, "volatility": "medium", "provider": "Spribe", "tip": "slot_tip_aviator", "casino": "PIN-UP"},
    {"name": "Fortune Tiger", "rtp": 96.81, "volatility": "medium", "provider": "PG Soft", "tip": "slot_tip_fortunetiger", "casino": "PIN-UP"},
]


async def _get_best_bonus(geo: str) -> Bonus | None:
    """Get the best active bonus for a geo by jogai_score."""
    async with async_session() as session:
        result = await session.execute(
            select(Bonus)
            .options(selectinload(Bonus.casino))
            .where(Bonus.is_active.is_(True))
            .where(Bonus.geo.any(geo))
            .where(
                (Bonus.expires_at.is_(None)) | (Bonus.expires_at > datetime.utcnow())
            )
            .order_by(Bonus.jogai_score.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _get_sport_pick(geo: str) -> SportPick | None:
    """Get today's sport pick for a geo."""
    async with async_session() as session:
        result = await session.execute(
            select(SportPick)
            .where(SportPick.geo.any(geo))
            .where(SportPick.result.is_(None))
            .order_by(SportPick.match_date.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _save_post(
    post_type: str,
    title: str,
    content: str,
    locale: str,
    geo: str,
    bonus_id: int | None = None,
    casino_id: int | None = None,
    telegram_message_id: int | None = None,
    telegram_channel: str | None = None,
) -> None:
    """Save a published post to the database."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    async with async_session() as session:
        post = Post(
            post_type=post_type,
            title=title,
            geo=geo,
            bonus_id=bonus_id,
            casino_id=casino_id,
            telegram_message_id=telegram_message_id,
            telegram_channel=telegram_channel,
            published_at=datetime.utcnow(),
            status="published",
        )
        if lang_suffix == "pt":
            post.content_pt = content
        else:
            post.content_es = content
        session.add(post)
        await session.commit()


async def _send_to_channel(channel_id: str, text: str) -> int | None:
    """Send a message to a Telegram channel. Returns message_id."""
    if not channel_id or channel_id == "placeholder":
        logger.warning("Channel ID not configured, skipping send")
        return None

    try:
        bot = get_bot()
        msg = await bot.send_message(chat_id=channel_id, text=text)
        return msg.message_id
    except Exception:
        logger.error("Failed to send to channel %s", channel_id, exc_info=True)
        return None


async def post_bonus_day() -> None:
    """Post the best bonus of the day to each active channel."""
    for geo, ch in CHANNELS.items():
        locale = ch["locale"]
        channel_id = ch["id"]

        bonus = await _get_best_bonus(geo)
        if not bonus:
            logger.info("No active bonus for geo=%s, skipping", geo)
            continue

        text = await generate_bonus_post(bonus, locale)
        msg_id = await _send_to_channel(channel_id, text)

        await _save_post(
            post_type="bonus_day",
            title=bonus.title_pt or "",
            content=text,
            locale=locale,
            geo=geo,
            bonus_id=bonus.id,
            casino_id=bonus.casino_id,
            telegram_message_id=msg_id,
            telegram_channel=channel_id,
        )
        logger.info("Posted bonus_day for geo=%s: %s", geo, bonus.title_pt)


async def post_sport_pick() -> None:
    """Post the sport pick of the day to each active channel."""
    for geo, ch in CHANNELS.items():
        locale = ch["locale"]
        channel_id = ch["id"]

        pick = await _get_sport_pick(geo)
        if not pick:
            logger.info("No sport pick for geo=%s, skipping", geo)
            continue

        text = await generate_sport_post(pick, locale)
        msg_id = await _send_to_channel(channel_id, text)

        await _save_post(
            post_type="sport_pick",
            title=pick.match_name or "",
            content=text,
            locale=locale,
            geo=geo,
            casino_id=pick.casino_id,
            telegram_message_id=msg_id,
            telegram_channel=channel_id,
        )
        logger.info("Posted sport_pick for geo=%s: %s", geo, pick.match_name)


async def post_slot_review() -> None:
    """Post a slot review of the day to each active channel."""
    # Pick a slot based on day of year for variety (cycles through catalog)
    day_index = datetime.utcnow().timetuple().tm_yday % len(SLOT_CATALOG)
    slot = SLOT_CATALOG[day_index]

    for geo, ch in CHANNELS.items():
        locale = ch["locale"]
        channel_id = ch["id"]

        text = await generate_slot_review(
            slot_name=slot["name"],
            rtp=slot["rtp"],
            volatility=slot["volatility"],
            tip=slot["tip"],
            casino_name=slot["casino"],
            locale=locale,
        )
        msg_id = await _send_to_channel(channel_id, text)

        await _save_post(
            post_type="slot_review",
            title=slot["name"],
            content=text,
            locale=locale,
            geo=geo,
            telegram_message_id=msg_id,
            telegram_channel=channel_id,
        )
        logger.info("Posted slot_review for geo=%s: %s", geo, slot["name"])


async def deactivate_expired() -> None:
    """Deactivate bonuses past their expiration date."""
    async with async_session() as session:
        result = await session.execute(
            update(Bonus)
            .where(Bonus.is_active.is_(True))
            .where(Bonus.expires_at.isnot(None))
            .where(Bonus.expires_at < datetime.utcnow())
            .values(is_active=False)
            .returning(Bonus.id)
        )
        deactivated = result.scalars().all()
        await session.commit()

    if deactivated:
        logger.info("Deactivated %d expired bonuses: %s", len(deactivated), deactivated)


# --- Celery tasks (sync wrappers for async functions) ---


async def _dispose_and_run(coro):
    """Dispose stale connections from prefork, then run the coroutine."""
    await engine.dispose()
    await coro


@celery.task(name="app.services.channel_poster.task_post_bonus_day")
def task_post_bonus_day() -> None:
    asyncio.run(_dispose_and_run(post_bonus_day()))


@celery.task(name="app.services.channel_poster.task_post_slot_review")
def task_post_slot_review() -> None:
    asyncio.run(_dispose_and_run(post_slot_review()))


@celery.task(name="app.services.channel_poster.task_post_sport_pick")
def task_post_sport_pick() -> None:
    asyncio.run(_dispose_and_run(post_sport_pick()))


@celery.task(name="app.services.channel_poster.task_deactivate_expired")
def task_deactivate_expired() -> None:
    asyncio.run(_dispose_and_run(deactivate_expired()))
