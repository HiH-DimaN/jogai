"""Educational content auto-poster for Telegram channels.

Maintains a bank of topics and rotates through them automatically.
AI generates unique content each time.
"""

import asyncio
import hashlib
import logging
from datetime import datetime

from sqlalchemy import select

from app.bot.bot import get_bot
from app.celery_app import celery
from app.config import settings
from app.database.engine import async_session, engine
from app.database.models import Post
from app.i18n import t
from app.services.channel_poster import CHANNELS, _save_post
from app.services.llm import chat, get_locale_params, load_prompt

logger = logging.getLogger(__name__)

# Bank of education topics — rotated automatically
# Each topic is a key used for tracking + a description for AI
EDUCATION_TOPICS = [
    {
        "key": "wagering_explained",
        "description": "What is wagering requirement (rollover) in casino bonuses. How x30 vs x40 makes a real difference. Example with real numbers.",
    },
    {
        "key": "rtp_explained",
        "description": "What is RTP (Return to Player) in slots. What 96.5% really means for your bankroll over time.",
    },
    {
        "key": "bankroll_management",
        "description": "Bankroll management basics for casino players. The 1-5% rule. How to set limits and stick to them.",
    },
    {
        "key": "volatility_explained",
        "description": "High vs medium vs low volatility slots. Which type suits which player style and bankroll size.",
    },
    {
        "key": "welcome_bonus_breakdown",
        "description": "Step-by-step breakdown of a typical welcome bonus. What happens from deposit to potential withdrawal.",
    },
    {
        "key": "free_spins_worth",
        "description": "When are free spins actually worth it? How to calculate the real value of free spins offers.",
    },
    {
        "key": "how_to_read_terms",
        "description": "How to read casino bonus terms and conditions. Red flags to watch for in the fine print.",
    },
    {
        "key": "payment_methods",
        "description": "PIX vs SPEI vs crypto vs card for casino deposits and withdrawals. Speed, fees, limits comparison.",
    },
    {
        "key": "casino_licenses",
        "description": "What casino licenses mean and why they matter. Curacao, Malta, UK — what's the difference for players?",
    },
    {
        "key": "rng_fairness",
        "description": "How RNG (Random Number Generator) works in online slots. Why slots are fair and what certified means.",
    },
    {
        "key": "betting_strategies_myths",
        "description": "Common betting strategies (Martingale, etc.) — why they don't work mathematically. House edge is real.",
    },
    {
        "key": "responsible_gambling",
        "description": "Responsible gambling: setting deposit limits, time limits, recognizing problem gambling signs. Resources for help.",
    },
    {
        "key": "slot_providers_comparison",
        "description": "Top slot providers compared: Pragmatic Play vs NetEnt vs Play'n GO. What makes each unique.",
    },
    {
        "key": "cashout_sports",
        "description": "Cash Out in sports betting — when to use it, when to let it ride. Practical decision framework.",
    },
    {
        "key": "max_bet_rule",
        "description": "The max bet rule in casino bonuses. Why breaking it can void your winnings and how to stay safe.",
    },
    {
        "key": "house_edge",
        "description": "What is house edge? How casinos make money. Which games have the lowest and highest house edge.",
    },
]


async def _get_next_topic() -> dict:
    """Get the next education topic that hasn't been posted recently."""
    async with async_session() as session:
        # Find topics already posted (by title matching the key)
        result = await session.execute(
            select(Post.title)
            .where(Post.post_type == "education")
            .order_by(Post.published_at.desc())
            .limit(len(EDUCATION_TOPICS))
        )
        posted_keys = {row[0] for row in result.all()}

    # Find first topic not recently posted
    for topic in EDUCATION_TOPICS:
        if topic["key"] not in posted_keys:
            return topic

    # All posted — restart from beginning (clear cycle)
    return EDUCATION_TOPICS[0]


async def post_education() -> None:
    """Generate and post an educational article to each channel."""
    topic = await _get_next_topic()

    for geo, ch in CHANNELS.items():
        locale = ch["locale"]
        channel_id = ch["id"]
        language, currency_symbol = get_locale_params(locale)

        try:
            prompt = load_prompt("education_post", language, currency_symbol)
            user_message = f"Topic: {topic['description']}"
            text = await chat(prompt, user_message, language, currency_symbol)
        except Exception:
            logger.warning("AI education post failed for %s", topic["key"], exc_info=True)
            continue

        if not text or len(text) < 50:
            logger.warning("Education post too short, skipping")
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
                logger.error("Failed to send education post to %s", channel_id, exc_info=True)

        await _save_post(
            post_type="education",
            title=topic["key"],
            content=text,
            locale=locale,
            geo=geo,
            telegram_message_id=msg_id,
            telegram_channel=channel_id,
        )
        logger.info("Posted education [%s] for geo=%s", topic["key"], geo)


# --- Celery task ---


async def _dispose_and_run(coro):
    await engine.dispose()
    await coro


@celery.task(name="app.services.education_poster.task_post_education")
def task_post_education() -> None:
    asyncio.run(_dispose_and_run(post_education()))
