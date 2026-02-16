from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_locale
from app.i18n import t
from app.services.bonus_analyzer import analyze_bonus
from app.utils.formatters import format_currency

router = APIRouter(prefix="/analyze", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    text: str
    locale: str = "pt_BR"


class AnalyzeResponse(BaseModel):
    jogai_score: float
    verdict_key: str
    verdict_text: str
    deposit: float
    bonus_amount: float
    bonus_percent: int
    total_balance: float
    wagering_multiplier: float
    wagering_total: float
    wagering_total_formatted: str
    deadline_days: int
    max_bet: float
    bets_needed: int
    bets_per_day: int
    bets_per_hour: int
    expected_loss: float
    expected_loss_formatted: str
    profit_probability: float
    free_spins: int
    ai_summary: str


@router.post("", response_model=AnalyzeResponse)
async def api_analyze_bonus(body: AnalyzeRequest):
    locale = body.locale
    result = await analyze_bonus(body.text, locale)
    score = result["score"]

    verdict_key = score.get("verdict_key", "verdict_caution")

    return AnalyzeResponse(
        jogai_score=score.get("jogai_score", 5.0),
        verdict_key=verdict_key,
        verdict_text=t(verdict_key, locale),
        deposit=score.get("deposit", 0),
        bonus_amount=score.get("bonus_amount", 0),
        bonus_percent=score.get("bonus_percent", 0),
        total_balance=score.get("total_balance", 0),
        wagering_multiplier=score.get("wagering_multiplier", 0),
        wagering_total=score.get("wagering_total", 0),
        wagering_total_formatted=format_currency(score.get("wagering_total", 0), locale),
        deadline_days=score.get("deadline_days", 0),
        max_bet=score.get("max_bet", 0),
        bets_needed=score.get("bets_needed", 0),
        bets_per_day=score.get("bets_per_day", 0),
        bets_per_hour=score.get("bets_per_hour", 0),
        expected_loss=score.get("expected_loss", 0),
        expected_loss_formatted=format_currency(score.get("expected_loss", 0), locale),
        profit_probability=score.get("profit_probability", 0),
        free_spins=score.get("free_spins", 0),
        ai_summary=result.get("ai_summary", ""),
    )
