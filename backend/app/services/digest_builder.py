import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.bot.bot import get_bot
from app.celery_app import celery
from app.database.engine import async_session, engine
from app.database.models import Bonus, User
from app.i18n import t
from app.utils.formatters import format_currency

logger = logging.getLogger(__name__)


async def _build_digest_message(locale: str, geo: str) -> str | None:
    """Build a digest message with top-5 bonuses for a given geo."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"

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
            .limit(5)
        )
        bonuses = result.scalars().all()

    if not bonuses:
        return None

    lines = [t("bonus_day_title", locale, date=datetime.utcnow().strftime("%d/%m"))]
    lines.append("")

    for i, bonus in enumerate(bonuses, 1):
        title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
        casino_name = bonus.casino.name if bonus.casino else "—"
        verdict = t(bonus.verdict_key or "verdict_caution", locale)
        score = float(bonus.jogai_score or 0)

        lines.append(
            t(
                "bonus_card",
                locale,
                casino=casino_name,
                title=title,
                wagering=float(bonus.wagering_multiplier or 0),
                deadline=bonus.wagering_deadline_days or 0,
                score=f"{score:.1f}",
                verdict=verdict,
            )
        )
        if i < len(bonuses):
            lines.append("")

    return "\n".join(lines)


async def send_digest() -> None:
    """Send daily digest DM to active users (last 30 days)."""
    cutoff = datetime.utcnow() - timedelta(days=30)

    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.last_active_at >= cutoff)
        )
        users = result.scalars().all()

    if not users:
        logger.info("No active users for digest")
        return

    # Build digest per geo (avoid regenerating for each user)
    digest_cache: dict[str, str | None] = {}
    bot = get_bot()
    sent_count = 0

    for user in users:
        geo = user.geo or "BR"
        locale = user.locale or "pt_BR"
        cache_key = f"{geo}:{locale}"

        if cache_key not in digest_cache:
            digest_cache[cache_key] = await _build_digest_message(locale, geo)

        message = digest_cache[cache_key]
        if not message:
            continue

        try:
            await bot.send_message(chat_id=user.id, text=message)
            sent_count += 1
        except Exception:
            logger.debug("Failed to send digest to user %d", user.id)

    logger.info("Digest sent to %d/%d active users", sent_count, len(users))


# --- Celery task (sync wrapper) ---


async def _dispose_and_run(coro):
    await engine.dispose()
    await coro


@celery.task(name="app.services.digest_builder.task_send_digest")
def task_send_digest() -> None:
    asyncio.run(_dispose_and_run(send_digest()))
