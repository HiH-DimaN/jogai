"""Casino comparison auto-poster for Telegram channels.

Automatically picks pairs of casinos and generates AI comparison posts.
"""

import asyncio
import logging
from datetime import datetime
from itertools import combinations

from sqlalchemy import select

from app.celery_app import celery
from app.config import settings
from app.database.engine import async_session, engine
from app.database.models import Bonus, Casino, Post
from app.i18n import t
from app.services.channel_poster import CHANNELS, _save_post
from app.services.llm import chat, get_locale_params, load_prompt
from app.utils.formatters import format_currency, get_min_deposit

logger = logging.getLogger(__name__)


async def _get_casino_pairs(geo: str) -> list[tuple[Casino, Casino]]:
    """Get all possible casino pairs for a geo."""
    async with async_session() as session:
        result = await session.execute(
            select(Casino)
            .where(Casino.is_active.is_(True))
            .where(Casino.geo.any(geo))
            .order_by(Casino.name)
        )
        casinos = list(result.scalars().all())

    return list(combinations(casinos, 2))


async def _get_best_bonus(casino_id: int, geo: str) -> Bonus | None:
    """Get the best active bonus for a casino in a geo."""
    async with async_session() as session:
        result = await session.execute(
            select(Bonus)
            .where(Bonus.casino_id == casino_id)
            .where(Bonus.is_active.is_(True))
            .where(Bonus.geo.any(geo))
            .order_by(Bonus.jogai_score.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _get_next_pair(geo: str) -> tuple[Casino, Casino] | None:
    """Get the next casino pair that hasn't been compared recently."""
    pairs = await _get_casino_pairs(geo)
    if not pairs:
        return None

    # Check which pairs were already posted
    async with async_session() as session:
        result = await session.execute(
            select(Post.title)
            .where(Post.post_type == "comparison")
            .where(Post.geo == geo)
            .order_by(Post.published_at.desc())
            .limit(50)
        )
        posted_titles = {row[0] for row in result.all()}

    for c1, c2 in pairs:
        pair_key = f"{c1.slug}_vs_{c2.slug}"
        if pair_key not in posted_titles:
            return (c1, c2)

    # All pairs compared — restart
    return pairs[0] if pairs else None


def _build_casino_data(casino: Casino, bonus: Bonus | None, locale: str) -> str:
    """Build casino data string for AI prompt."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    min_dep = get_min_deposit(casino, locale)
    lines = [
        f"Name: {casino.name}",
        f"Min deposit: {format_currency(min_dep, locale)}",
        f"PIX: {'Yes' if casino.pix_supported else 'No'}",
        f"SPEI: {'Yes' if casino.spei_supported else 'No'}",
        f"Crypto: {'Yes' if casino.crypto_supported else 'No'}",
        f"Withdrawal: {casino.withdrawal_time or 'N/A'}",
    ]

    if bonus:
        title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
        lines.extend([
            f"Best bonus: {title}",
            f"Bonus %: {bonus.bonus_percent}%",
            f"Wagering: x{bonus.wagering_multiplier}",
            f"Deadline: {bonus.wagering_deadline_days} days",
            f"Free spins: {bonus.free_spins}",
            f"Jogai Score: {bonus.jogai_score}/10",
        ])
    else:
        lines.append("Best bonus: No active bonus")

    return "\n".join(lines)


async def post_comparison() -> None:
    """Generate and post a casino comparison to each channel."""
    for geo, ch in CHANNELS.items():
        locale = ch["locale"]
        channel_id = ch["id"]
        language, currency_symbol = get_locale_params(locale)

        pair = await _get_next_pair(geo)
        if not pair:
            logger.info("No casino pairs for geo=%s, skipping", geo)
            continue

        c1, c2 = pair

        bonus1 = await _get_best_bonus(c1.id, geo)
        bonus2 = await _get_best_bonus(c2.id, geo)

        casino1_data = _build_casino_data(c1, bonus1, locale)
        casino2_data = _build_casino_data(c2, bonus2, locale)

        try:
            prompt = load_prompt("casino_comparison", language, currency_symbol)
            user_message = (
                f"Casino A:\n{casino1_data}\n\n"
                f"Casino B:\n{casino2_data}"
            )
            text = await chat(prompt, user_message, language, currency_symbol)
        except Exception:
            logger.warning(
                "AI comparison failed for %s vs %s",
                c1.name, c2.name, exc_info=True,
            )
            continue

        if not text or len(text) < 50:
            continue

        # Send to channel
        msg_id = None
        if channel_id and channel_id != "placeholder":
            try:
                from app.bot.bot import get_bot
                bot = get_bot()
                msg = await bot.send_message(chat_id=channel_id, text=text)
                msg_id = msg.message_id
            except Exception:
                logger.error("Failed to send comparison to %s", channel_id, exc_info=True)

        pair_key = f"{c1.slug}_vs_{c2.slug}"
        await _save_post(
            post_type="comparison",
            title=pair_key,
            content=text,
            locale=locale,
            geo=geo,
            telegram_message_id=msg_id,
            telegram_channel=channel_id,
        )
        logger.info("Posted comparison %s vs %s for geo=%s", c1.name, c2.name, geo)


# --- Celery task ---


async def _dispose_and_run(coro):
    await engine.dispose()
    await coro


@celery.task(name="app.services.comparison_poster.task_post_comparison")
def task_post_comparison() -> None:
    asyncio.run(_dispose_and_run(post_comparison()))
