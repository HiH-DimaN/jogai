"""DM alert service for Telegram bot.

Sends targeted alerts to users:
- New high-score bonus alerts (score >= 8)
- Expiring bonus alerts (24h before expiry, only to users who clicked)
"""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.bot.bot import get_bot
from app.celery_app import celery
from app.database.engine import async_session, engine
from app.database.models import Bonus, Click, User
from app.i18n import t
from app.utils.formatters import format_currency

logger = logging.getLogger(__name__)

# Only alert for bonuses with score >= this threshold
NEW_BONUS_MIN_SCORE = 8.0

# Max DM alerts per user per day (across all alert types)
MAX_ALERTS_PER_USER_PER_DAY = 2


async def _count_today_alerts(user_id: int) -> int:
    """Count how many alert DMs were sent to user today."""
    from app.database.models import Post

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async with async_session() as session:
        result = await session.execute(
            select(Post.id)
            .where(Post.post_type.in_(["dm_new_bonus", "dm_expiring_bonus"]))
            .where(Post.telegram_channel == str(user_id))
            .where(Post.published_at >= today_start)
        )
        return len(result.all())


async def _save_dm_record(
    post_type: str, user_id: int, content: str, locale: str, geo: str, bonus_id: int | None = None
) -> None:
    """Save a DM alert record to track sending limits."""
    from app.database.models import Post

    lang_suffix = "pt" if locale.startswith("pt") else "es"
    async with async_session() as session:
        post = Post(
            post_type=post_type,
            title=f"dm_alert_{user_id}",
            geo=geo,
            bonus_id=bonus_id,
            telegram_channel=str(user_id),
            published_at=datetime.utcnow(),
            status="published",
        )
        if lang_suffix == "pt":
            post.content_pt = content
        else:
            post.content_es = content
        session.add(post)
        await session.commit()


async def alert_new_bonuses() -> None:
    """Send DM alerts for new high-score bonuses.

    Triggers after bonus parsing — checks for bonuses created in last 6h
    with jogai_score >= 8.
    """
    cutoff = datetime.utcnow() - timedelta(hours=6)

    async with async_session() as session:
        result = await session.execute(
            select(Bonus)
            .options(selectinload(Bonus.casino))
            .where(Bonus.is_active.is_(True))
            .where(Bonus.jogai_score >= NEW_BONUS_MIN_SCORE)
            .where(Bonus.created_at >= cutoff)
        )
        new_bonuses = list(result.scalars().all())

    if not new_bonuses:
        logger.info("No new high-score bonuses to alert about")
        return

    # Group bonuses by geo
    bonuses_by_geo: dict[str, list[Bonus]] = {}
    for bonus in new_bonuses:
        for geo in (bonus.geo or ["BR"]):
            bonuses_by_geo.setdefault(geo, []).append(bonus)

    bot = get_bot()
    sent_count = 0

    for geo, bonuses in bonuses_by_geo.items():
        # Get active users for this geo
        cutoff_active = datetime.utcnow() - timedelta(days=30)
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .where(User.geo == geo)
                .where(User.last_active_at >= cutoff_active)
            )
            users = list(result.scalars().all())

        for user in users:
            # Check daily limit
            today_count = await _count_today_alerts(user.id)
            if today_count >= MAX_ALERTS_PER_USER_PER_DAY:
                continue

            locale = user.locale or ("pt_BR" if geo == "BR" else "es_MX")
            lang_suffix = "pt" if locale.startswith("pt") else "es"

            # Pick the best new bonus for this user
            bonus = bonuses[0]
            title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
            casino_name = bonus.casino.name if bonus.casino else ""
            verdict = t(bonus.verdict_key or "verdict_excellent", locale)

            message = t(
                "dm_new_bonus",
                locale,
                casino=casino_name,
                title=title,
                score=bonus.jogai_score,
                verdict=verdict,
            )

            try:
                await bot.send_message(chat_id=user.id, text=message)
                await _save_dm_record(
                    "dm_new_bonus", user.id, message, locale, geo, bonus.id
                )
                sent_count += 1
            except Exception:
                logger.debug("Failed to send new bonus alert to %d", user.id)

    logger.info("Sent new bonus alerts to %d users", sent_count)


async def alert_expiring_bonuses() -> None:
    """Send DM alerts for bonuses expiring in 24h.

    Only alerts users who previously clicked on the bonus or its casino.
    """
    now = datetime.utcnow()
    expiry_window_start = now + timedelta(hours=12)
    expiry_window_end = now + timedelta(hours=36)

    async with async_session() as session:
        result = await session.execute(
            select(Bonus)
            .options(selectinload(Bonus.casino))
            .where(Bonus.is_active.is_(True))
            .where(Bonus.expires_at.isnot(None))
            .where(Bonus.expires_at >= expiry_window_start)
            .where(Bonus.expires_at <= expiry_window_end)
        )
        expiring = list(result.scalars().all())

    if not expiring:
        logger.info("No expiring bonuses to alert about")
        return

    bot = get_bot()
    sent_count = 0

    for bonus in expiring:
        # Find users who clicked on this bonus or its casino
        async with async_session() as session:
            result = await session.execute(
                select(Click.user_id)
                .where(
                    (Click.bonus_id == bonus.id)
                    | (Click.casino_id == bonus.casino_id)
                )
                .distinct()
            )
            interested_user_ids = {row[0] for row in result.all() if row[0]}

        if not interested_user_ids:
            continue

        # Get full user objects
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id.in_(interested_user_ids))
            )
            users = list(result.scalars().all())

        for user in users:
            today_count = await _count_today_alerts(user.id)
            if today_count >= MAX_ALERTS_PER_USER_PER_DAY:
                continue

            locale = user.locale or "pt_BR"
            lang_suffix = "pt" if locale.startswith("pt") else "es"

            title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
            casino_name = bonus.casino.name if bonus.casino else ""
            expires_str = bonus.expires_at.strftime("%d/%m %H:%M") if bonus.expires_at else ""

            message = t(
                "dm_expiring_bonus",
                locale,
                casino=casino_name,
                title=title,
                expires=expires_str,
            )

            try:
                await bot.send_message(chat_id=user.id, text=message)
                await _save_dm_record(
                    "dm_expiring_bonus", user.id, message, locale, user.geo or "BR", bonus.id
                )
                sent_count += 1
            except Exception:
                logger.debug("Failed to send expiry alert to %d", user.id)

    logger.info("Sent expiring bonus alerts to %d users", sent_count)


# --- Celery tasks ---


async def _dispose_and_run(coro):
    from app.bot.bot import reset_bot
    reset_bot()
    await engine.dispose()
    await coro


@celery.task(name="app.services.dm_alerts.task_alert_new_bonuses")
def task_alert_new_bonuses() -> None:
    asyncio.run(_dispose_and_run(alert_new_bonuses()))


@celery.task(name="app.services.dm_alerts.task_alert_expiring_bonuses")
def task_alert_expiring_bonuses() -> None:
    asyncio.run(_dispose_and_run(alert_expiring_bonuses()))
