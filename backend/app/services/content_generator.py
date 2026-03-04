import logging

from app.database.models import Bonus, SportPick
from app.i18n import get_language_name, t
from app.services.llm import chat, get_locale_params, load_prompt
from app.utils.formatters import format_currency

logger = logging.getLogger(__name__)


async def generate_bonus_post(bonus: Bonus, locale: str) -> str:
    """Generate an AI-enhanced bonus post for the Telegram channel.

    Falls back to a template-based post if AI fails.
    """
    language, currency_symbol = get_locale_params(locale)
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
    casino_name = bonus.casino.name if bonus.casino else "Casino"
    verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else ""

    try:
        prompt = load_prompt("content_post", language, currency_symbol)
        user_message = (
            f"Casino: {casino_name}\n"
            f"Bonus: {title}\n"
            f"Bonus percent: {bonus.bonus_percent}%\n"
            f"Max bonus: {format_currency(bonus.max_bonus_amount or 0, locale)}\n"
            f"Wagering: x{bonus.wagering_multiplier}\n"
            f"Deadline: {bonus.wagering_deadline_days} days\n"
            f"Free spins: {bonus.free_spins}\n"
            f"Jogai Score: {bonus.jogai_score}/10\n"
            f"Verdict: {verdict}"
        )
        return await chat(prompt, user_message, language, currency_symbol)
    except Exception:
        logger.warning("AI content generation failed, using template", exc_info=True)
        return _fallback_bonus_post(bonus, locale)


def _fallback_bonus_post(bonus: Bonus, locale: str) -> str:
    """Template-based fallback when AI is unavailable."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
    casino_name = bonus.casino.name if bonus.casino else "Casino"
    verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else ""
    expires = bonus.expires_at.strftime("%d/%m") if bonus.expires_at else "—"

    return t(
        "channel_bonus_day",
        locale,
        casino=casino_name,
        title=title,
        score=bonus.jogai_score,
        verdict=verdict,
        expires=expires,
    )


async def generate_slot_review(
    slot_name: str,
    rtp: float,
    volatility: str,
    tip: str,
    casino_name: str,
    locale: str,
) -> str:
    """Generate a slot review post for the channel."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    vol_key = f"slot_volatility_{volatility}"
    volatility_text = t(vol_key, locale)
    tip_text = t(tip, locale) if tip.startswith("slot_tip_") else tip
    return t(
        "channel_slot_review",
        locale,
        name=slot_name,
        rtp=rtp,
        volatility=volatility_text,
        tip=tip_text,
        casino=casino_name,
    )


async def generate_sport_post(pick: SportPick, locale: str) -> str:
    """Generate a sport pick post for the channel."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    analysis = getattr(pick, f"analysis_{lang_suffix}") or pick.analysis_pt or ""
    description = (
        getattr(pick, f"pick_description_{lang_suffix}")
        or pick.pick_description_pt
        or ""
    )

    return t(
        "channel_sport",
        locale,
        match=pick.match_name or "",
        analysis=analysis,
        pick=description,
        odds=pick.odds,
    )
