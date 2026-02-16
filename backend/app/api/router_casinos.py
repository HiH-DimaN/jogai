from fastapi import APIRouter, Depends

from app.api.deps import get_locale

router = APIRouter(prefix="/casinos", tags=["casinos"])


@router.get("")
async def get_casinos(
    geo: str = "BR",
    locale: str = Depends(get_locale),
):
    return {"casinos": [], "geo": geo, "locale": locale}


@router.get("/{slug}")
async def get_casino(
    slug: str,
    locale: str = Depends(get_locale),
):
    return {"slug": slug, "locale": locale}
