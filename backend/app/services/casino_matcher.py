from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Casino


# Scoring weights for casino matching
GAME_TYPE_MAP = {
    "slots": {"weight_field": None},  # all casinos have slots
    "crash": {"weight_field": None},
    "sports": {"weight_field": None},
    "table": {"weight_field": None},
}

PAYMENT_SCORE = {
    "pix": "pix_supported",
    "spei": "spei_supported",
    "crypto": "crypto_supported",
    "card": None,  # all casinos accept cards
}


async def get_casinos_for_geo(geo: str) -> list[Casino]:
    async with async_session() as session:
        result = await session.execute(
            select(Casino)
            .where(Casino.is_active.is_(True))
            .where(Casino.geo.any(geo))
        )
        return list(result.scalars().all())


def score_casino(
    casino: Casino,
    game_type: str,
    deposit_range: str,
    payment: str,
    priority: str,
    experience: str,
) -> int:
    """Score a casino 0-100 based on user preferences."""
    score = 50  # base score

    # Payment method match
    payment_field = PAYMENT_SCORE.get(payment)
    if payment_field:
        if getattr(casino, payment_field, False):
            score += 20
        else:
            score -= 20
    else:
        score += 10  # card is universal

    # Deposit range vs min_deposit (use min_deposits dict if available)
    min_dep = float(casino.min_deposit or 0)
    if casino.min_deposits and isinstance(casino.min_deposits, dict):
        # Pick currency based on geo context (BRL for BR, MXN for MX)
        for currency in ("BRL", "MXN"):
            if currency in casino.min_deposits:
                min_dep = float(casino.min_deposits[currency])
                break

    deposit_limits = {
        "low": 50,
        "medium": 200,
        "high": 1000,
        "vip": 10000,
    }
    user_max = deposit_limits.get(deposit_range, 200)
    if min_dep <= user_max:
        score += 15
    else:
        score -= 15

    # Priority: bonus, wagering, withdraw
    if priority == "bonus":
        # Casinos with more bonuses score higher
        bonus_count = len(casino.bonuses) if casino.bonuses else 0
        score += min(bonus_count * 5, 15)
    elif priority == "wagering":
        # Check if casino has low-wagering bonuses
        if casino.bonuses:
            avg_wager = sum(
                float(b.wagering_multiplier or 35) for b in casino.bonuses
            ) / len(casino.bonuses)
            if avg_wager <= 25:
                score += 15
            elif avg_wager <= 35:
                score += 5
    elif priority == "withdraw":
        # Fast withdrawal
        wt = casino.withdrawal_time or ""
        if "1-12h" in wt or "instant" in wt.lower():
            score += 15
        elif "1-24h" in wt:
            score += 10

    return max(0, min(100, score))


async def match_casinos(
    geo: str,
    game_type: str,
    deposit_range: str,
    payment: str,
    priority: str,
    experience: str,
) -> list[dict]:
    """Match and rank casinos for the user."""
    casinos = await get_casinos_for_geo(geo)

    results = []
    for casino in casinos:
        match_score = score_casino(
            casino, game_type, deposit_range, payment, priority, experience
        )
        results.append({
            "casino": casino,
            "match_percent": match_score,
        })

    results.sort(key=lambda x: x["match_percent"], reverse=True)
    return results[:3]
