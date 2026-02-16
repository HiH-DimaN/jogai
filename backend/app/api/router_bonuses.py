from fastapi import APIRouter, Depends

from app.api.deps import get_locale

router = APIRouter(prefix="/bonuses", tags=["bonuses"])


@router.get("")
async def get_bonuses(
    geo: str = "BR",
    locale: str = Depends(get_locale),
):
    return {"bonuses": [], "geo": geo, "locale": locale}


@router.get("/{bonus_id}")
async def get_bonus(
    bonus_id: int,
    locale: str = Depends(get_locale),
):
    return {"bonus_id": bonus_id, "locale": locale}
