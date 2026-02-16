from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Casino


async def get_affiliate_link(casino_slug: str, user_id: int) -> str | None:
    async with async_session() as session:
        result = await session.execute(
            select(Casino).where(Casino.slug == casino_slug)
        )
        casino = result.scalar_one_or_none()

    if not casino or not casino.affiliate_link_template:
        return None

    return casino.affiliate_link_template.format(
        ref_id=casino.ref_id or "",
        user_id=user_id,
    )
