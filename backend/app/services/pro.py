"""PRO subscription management."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import User

logger = logging.getLogger(__name__)

# PRO price in Telegram Stars (1 Star ≈ $0.02)
PRO_PRICE_STARS = 150  # ~$3/month
PRO_DURATION_DAYS = 30


async def is_pro(user_id: int) -> bool:
    """Check if user has active PRO subscription."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        return user.is_pro and (
            user.pro_expires_at is None or user.pro_expires_at > datetime.utcnow()
        )


async def activate_pro(user_id: int) -> datetime:
    """Activate PRO for a user. Returns expiration date."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Extend if already PRO, otherwise start fresh
        now = datetime.utcnow()
        if user.is_pro and user.pro_expires_at and user.pro_expires_at > now:
            expires_at = user.pro_expires_at + timedelta(days=PRO_DURATION_DAYS)
        else:
            expires_at = now + timedelta(days=PRO_DURATION_DAYS)

        user.is_pro = True
        user.pro_expires_at = expires_at
        await session.commit()

        logger.info("PRO activated for user %d until %s", user_id, expires_at)
        return expires_at


async def get_pro_status(user_id: int) -> dict:
    """Get PRO status for a user."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return {"is_pro": False, "expires_at": None}

        now = datetime.utcnow()
        active = user.is_pro and (
            user.pro_expires_at is None or user.pro_expires_at > now
        )

        return {
            "is_pro": active,
            "expires_at": user.pro_expires_at,
        }
