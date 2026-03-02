from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.config import settings
from app.database.models import Referral, User

router = APIRouter(prefix="/referrals", tags=["referrals"])


class ReferralStatsResponse(BaseModel):
    referral_code: str
    referral_link: str
    jogai_coins: int
    referral_count: int


@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Generate referral code if missing
    if not user.referral_code:
        user.referral_code = str(user.id)[-8:]
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Count referrals
    result = await session.execute(
        select(func.count()).where(Referral.referrer_id == user.id)
    )
    referral_count = result.scalar() or 0

    bot_username = settings.telegram_bot_token.split(":")[0] if ":" in settings.telegram_bot_token else "jogai_bot"
    referral_link = f"https://t.me/{bot_username}?start=ref_{user.referral_code}"

    return ReferralStatsResponse(
        referral_code=user.referral_code,
        referral_link=referral_link,
        jogai_coins=user.jogai_coins,
        referral_count=referral_count,
    )
