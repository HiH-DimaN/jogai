"""One-time script:
1. Update PIN-UP casino with real affiliate link + expanded geo
2. Deactivate Caliente & Codere (no real affiliate links yet)

Run inside backend container:
    python -m app.database.update_pinup
"""

import asyncio

from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Bonus, Casino


async def run():
    async with async_session() as session:
        # 1. Update PIN-UP casino
        result = await session.execute(
            select(Casino).where(Casino.slug == "pinup")
        )
        casino = result.scalar_one_or_none()

        if not casino:
            print("ERROR: PIN-UP casino not found in DB")
            return

        casino.geo = ["MX", "CL", "EC"]
        casino.min_deposit = 50.00
        casino.min_deposits = {"MXN": 50.0, "CLP": 2500.0, "USD": 2.0}
        casino.affiliate_link_template = "https://onlinepnplnk.com/9euv1TI2/"

        print(f"Updated casino PIN-UP (id={casino.id}):")
        print(f"  geo: {casino.geo}")
        print(f"  min_deposits: {casino.min_deposits}")
        print(f"  affiliate_link_template: {casino.affiliate_link_template}")

        # 2. Update PIN-UP bonus affiliate link
        result = await session.execute(
            select(Bonus).where(Bonus.casino_id == casino.id)
        )
        for bonus in result.scalars().all():
            if not bonus.affiliate_link:
                bonus.affiliate_link = "https://onlinepnplnk.com/9euv1TI2/"
                print(f"Updated bonus id={bonus.id}: affiliate_link set")
            else:
                print(f"Bonus id={bonus.id}: already has link, skipping")

        # 3. Deactivate Caliente & Codere — no real affiliate links yet
        for slug in ("caliente", "codere"):
            result = await session.execute(
                select(Casino).where(Casino.slug == slug)
            )
            c = result.scalar_one_or_none()
            if not c:
                print(f"Casino {slug} not found, skipping")
                continue

            c.is_active = False
            c.affiliate_link_template = ""
            c.ref_id = ""
            print(f"Deactivated casino {c.name} (id={c.id})")

            # Deactivate their bonuses too
            result = await session.execute(
                select(Bonus).where(Bonus.casino_id == c.id)
            )
            for bonus in result.scalars().all():
                bonus.is_active = False
                print(f"  Deactivated bonus id={bonus.id}: {bonus.title_es}")

        await session.commit()
        print("\nDone. Summary:")
        print("  PIN-UP: active, link set, geo=[MX, CL, EC]")
        print("  Caliente: deactivated (waiting for real affiliate link)")
        print("  Codere: deactivated (waiting for real affiliate link)")


if __name__ == "__main__":
    asyncio.run(run())
