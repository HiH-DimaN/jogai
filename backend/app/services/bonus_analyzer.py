import logging
import math
from dataclasses import dataclass
from typing import Any

from app.i18n import DEFAULT_LOCALE
from app.services.llm import chat_json, get_locale_params, load_prompt
from app.utils.formatters import LOCALE_CONFIG

logger = logging.getLogger(__name__)

HOUSE_EDGE = 0.04  # 4% average house edge


@dataclass
class JogaiScoreResult:
    jogai_score: float
    verdict_key: str
    deposit: float
    bonus_amount: float
    bonus_percent: int
    total_balance: float
    wagering_multiplier: float
    wagering_total: float
    deadline_days: int
    max_bet: float
    bets_needed: int
    bets_per_day: int
    bets_per_hour: int
    expected_loss: float
    profit_probability: float
    free_spins: int
    summary: str


def calculate_jogai_score(
    bonus_percent: int = 100,
    wagering_multiplier: float = 35.0,
    deadline_days: int = 30,
    max_bet: float = 25.0,
    deposit: float = 100.0,
    free_spins: int = 0,
    no_deposit: bool = False,
) -> dict[str, Any]:
    """Calculate Jogai Score. Returns verdict_key (i18n key), NOT text."""

    bonus_amount = deposit * bonus_percent / 100
    total_balance = deposit + bonus_amount

    # Wagering calculation
    wagering_base = bonus_amount if bonus_percent >= 100 else total_balance
    wagering_total = wagering_base * wagering_multiplier

    # Bets calculation
    effective_max_bet = max(max_bet, 1.0)
    bets_needed = math.ceil(wagering_total / effective_max_bet) if wagering_total > 0 else 0
    bets_per_day = math.ceil(bets_needed / max(deadline_days, 1))
    bets_per_hour = math.ceil(bets_per_day / 16)  # 16 active hours

    # Expected loss
    expected_loss = wagering_total * HOUSE_EDGE

    # Profit probability (simplified model)
    if wagering_total <= 0:
        profit_probability = 90.0
    else:
        ratio = expected_loss / max(total_balance, 1)
        profit_probability = max(5.0, min(90.0, (1 - ratio) * 100))

    # --- Jogai Score (0-10) ---
    score = 10.0

    # Wagering penalty: x35+ is bad, x25 is ok, x10 is great
    if wagering_multiplier > 50:
        score -= 4.0
    elif wagering_multiplier > 40:
        score -= 3.0
    elif wagering_multiplier > 30:
        score -= 2.0
    elif wagering_multiplier > 20:
        score -= 1.0
    elif wagering_multiplier > 10:
        score -= 0.5

    # Deadline penalty: too short = bad
    if deadline_days < 7:
        score -= 2.0
    elif deadline_days < 14:
        score -= 1.0
    elif deadline_days < 21:
        score -= 0.5

    # Max bet penalty: too low = very hard
    if max_bet < 5:
        score -= 2.0
    elif max_bet < 15:
        score -= 1.0
    elif max_bet < 25:
        score -= 0.5

    # Bonus percentage bonus
    if bonus_percent >= 200:
        score += 1.0
    elif bonus_percent >= 100:
        score += 0.5

    # Free spins bonus
    if free_spins > 100:
        score += 0.5
    elif free_spins > 0:
        score += 0.25

    # No deposit bonus
    if no_deposit:
        score += 1.0

    # Clamp
    jogai_score = round(max(1.0, min(10.0, score)), 1)

    # Verdict key (i18n key, NOT text!)
    if jogai_score >= 8.0:
        verdict_key = "verdict_excellent"
    elif jogai_score >= 6.0:
        verdict_key = "verdict_good"
    elif jogai_score >= 4.0:
        verdict_key = "verdict_caution"
    else:
        verdict_key = "verdict_bad"

    return {
        "jogai_score": jogai_score,
        "verdict_key": verdict_key,
        "deposit": deposit,
        "bonus_amount": bonus_amount,
        "bonus_percent": bonus_percent,
        "total_balance": total_balance,
        "wagering_multiplier": wagering_multiplier,
        "wagering_total": wagering_total,
        "deadline_days": deadline_days,
        "max_bet": max_bet,
        "bets_needed": bets_needed,
        "bets_per_day": bets_per_day,
        "bets_per_hour": bets_per_hour,
        "expected_loss": expected_loss,
        "profit_probability": round(profit_probability, 1),
        "free_spins": free_spins,
    }


async def parse_bonus_conditions(text: str, locale: str = DEFAULT_LOCALE) -> dict:
    """Use AI to parse bonus conditions from user text."""
    language, currency_symbol = get_locale_params(locale)
    prompt = load_prompt("bonus_analysis", language, currency_symbol)

    result = await chat_json(prompt, text, language, currency_symbol)
    return result


async def analyze_bonus(text: str, locale: str = DEFAULT_LOCALE) -> dict[str, Any]:
    """Full analysis pipeline: AI parse → Jogai Score calculation."""
    parsed = await parse_bonus_conditions(text, locale)

    if not parsed:
        # Fallback: return empty result
        return {
            "parsed": {},
            "score": calculate_jogai_score(),
            "ai_summary": "",
        }

    score_result = calculate_jogai_score(
        bonus_percent=parsed.get("bonus_percent") or 100,
        wagering_multiplier=parsed.get("wagering_multiplier") or 35,
        deadline_days=parsed.get("deadline_days") or 30,
        max_bet=parsed.get("max_bet") or 25,
        deposit=parsed.get("deposit") or 100,
        free_spins=parsed.get("free_spins") or 0,
    )

    return {
        "parsed": parsed,
        "score": score_result,
        "ai_summary": parsed.get("summary", ""),
    }
