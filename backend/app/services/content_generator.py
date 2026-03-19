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

    affiliate_link = bonus.affiliate_link or ""

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
            f"Verdict: {verdict}\n"
            f"Affiliate link: {affiliate_link}"
        )
        text = await chat(prompt, user_message, language, currency_symbol)
        # Guarantee affiliate link is present even if AI omitted it
        if affiliate_link and affiliate_link not in text:
            cta = (
                "Cadastre-se e ganhe o bônus" if locale.startswith("pt")
                else "Regístrate y obtén el bono"
            )
            text += f'\n\n👉 <a href="{affiliate_link}">{cta}</a>'
        return text
    except Exception:
        logger.warning("AI content generation failed, using template", exc_info=True)
        return _fallback_bonus_post(bonus, locale)


def _fallback_bonus_post(bonus: Bonus, locale: str) -> str:
    """Template-based fallback when AI is unavailable."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
    casino_name = bonus.casino.name if bonus.casino else "Casino"
    verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else ""

    return t(
        "channel_bonus_day",
        locale,
        casino=casino_name,
        title=title,
        score=bonus.jogai_score,
        verdict=verdict,
        link=bonus.affiliate_link or "",
    )


def _strip_casino_prefix(title: str, casino_name: str) -> str:
    """Strip casino name prefix from title to avoid '1WIN — 1WIN: ...'."""
    if title.upper().startswith(casino_name.upper()):
        colon_idx = title.find(":")
        if colon_idx != -1 and colon_idx < len(casino_name) + 15:
            return title[colon_idx + 1:].strip()
    return title


async def generate_bonus_digest(bonuses: list[Bonus], locale: str) -> str:
    """Generate a bonus post for the Telegram channel.

    Alternates daily between two formats:
    - Even days: full list of all bonuses
    - Odd days: spotlight on the top bonus with detailed info
    """
    from datetime import datetime

    lang_suffix = "pt" if locale.startswith("pt") else "es"
    now = datetime.utcnow()
    today = now.strftime("%d/%m")
    is_spotlight = now.day % 2 == 1  # odd days = spotlight

    if is_spotlight and bonuses:
        return _generate_spotlight(bonuses, locale, lang_suffix, today)
    return _generate_full_digest(bonuses, locale, lang_suffix, today)


def _generate_spotlight(
    bonuses: list[Bonus], locale: str, lang_suffix: str, today: str
) -> str:
    """Single bonus spotlight with detailed info."""
    bonus = bonuses[0]
    title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
    casino_name = bonus.casino.name if bonus.casino else "Casino"
    title = _strip_casino_prefix(title, casino_name)
    casino = bonus.casino
    promo_code = casino.promo_code if casino else None
    verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else ""
    link = bonus.affiliate_link or ""

    if locale.startswith("pt"):
        lines = [
            f"🏆 <b>BÔNUS DO DIA ({today}):</b>\n",
            f"🎰 <b>{casino_name}</b> — {title}\n",
            f"⭐ Jogai Score: <b>{bonus.jogai_score}/10</b> — {verdict}\n",
        ]
        if bonus.bonus_percent:
            lines.append(f"💰 Bônus: <b>{bonus.bonus_percent}%</b>")
        if bonus.wagering_multiplier is not None and bonus.wagering_multiplier > 0:
            lines.append(f"🔄 Rollover: <b>x{bonus.wagering_multiplier}</b>")
        else:
            lines.append("🔄 Rollover: <b>SEM rollover!</b>")
        if bonus.free_spins:
            lines.append(f"🎡 Free Spins: <b>{bonus.free_spins}</b>")
        if promo_code:
            lines.append(f"\n🎟 Código: <b>{promo_code}</b>")
        if link:
            lines.append(f'\n👉 <a href="{link}">Cadastre-se e ganhe o bônus</a>')
        lines.append("\n⚡ Analisado por <b>Jogai AI</b> — só bônus verificados!")
    else:
        lines = [
            f"🏆 <b>BONO DEL DÍA ({today}):</b>\n",
            f"🎰 <b>{casino_name}</b> — {title}\n",
            f"⭐ Jogai Score: <b>{bonus.jogai_score}/10</b> — {verdict}\n",
        ]
        if bonus.bonus_percent:
            lines.append(f"💰 Bono: <b>{bonus.bonus_percent}%</b>")
        if bonus.wagering_multiplier is not None and bonus.wagering_multiplier > 0:
            lines.append(f"🔄 Rollover: <b>x{bonus.wagering_multiplier}</b>")
        else:
            lines.append("🔄 Rollover: <b>¡SIN rollover!</b>")
        if bonus.free_spins:
            lines.append(f"🎡 Free Spins: <b>{bonus.free_spins}</b>")
        if promo_code:
            lines.append(f"\n🎟 Código: <b>{promo_code}</b>")
        if link:
            lines.append(f'\n👉 <a href="{link}">Regístrate y obtén el bono</a>')
        lines.append(
            "\n⚡ Analizado por <b>Jogai AI</b> — ¡solo bonos verificados!"
        )

    return "\n".join(lines)


def _generate_full_digest(
    bonuses: list[Bonus], locale: str, lang_suffix: str, today: str
) -> str:
    """Full list of all active bonuses."""
    if locale.startswith("pt"):
        header = f"🔥 <b>MELHORES BÔNUS DE HOJE ({today}):</b>\n"
        cta_text = "Cadastre-se aqui"
        promo_label = "Código promocional"
        footer = "⚡ Analisado por <b>Jogai AI</b> — só bônus verificados!"
    else:
        header = f"🔥 <b>MEJORES BONOS DE HOY ({today}):</b>\n"
        cta_text = "Regístrate aquí"
        promo_label = "Código promocional"
        footer = "⚡ Analizado por <b>Jogai AI</b> — ¡solo bonos verificados!"

    lines = [header]
    for i, bonus in enumerate(bonuses, 1):
        title = getattr(bonus, f"title_{lang_suffix}") or bonus.title_pt or ""
        casino_name = bonus.casino.name if bonus.casino else "Casino"
        title = _strip_casino_prefix(title, casino_name)
        casino = bonus.casino
        promo_code = casino.promo_code if casino else None
        verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else ""
        link = bonus.affiliate_link or ""

        medal = ["🏆", "🥈", "🥉", "🎯", "💎"][i - 1] if i <= 5 else "▪️"

        line = (
            f"{medal} <b>{casino_name}</b> — {title}\n"
            f"    ⭐ Score: {bonus.jogai_score}/10 — {verdict}"
        )
        if promo_code:
            line += f"\n    🎟 {promo_label}: <b>{promo_code}</b>"
        if link:
            line += f'\n    👉 <a href="{link}">{cta_text}</a>'
        lines.append(line)
        lines.append("")

    lines.append(footer)
    return "\n".join(lines)


async def generate_slot_review(
    slot_name: str,
    rtp: float,
    volatility: str,
    tip: str,
    casino_name: str,
    locale: str,
    casino_link: str = "",
) -> str:
    """Generate a slot review post for the channel."""
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    vol_key = f"slot_volatility_{volatility}"
    volatility_text = t(vol_key, locale)
    tip_text = t(tip, locale) if tip.startswith("slot_tip_") else tip
    text = t(
        "channel_slot_review",
        locale,
        name=slot_name,
        rtp=rtp,
        volatility=volatility_text,
        tip=tip_text,
        casino=casino_name,
    )
    # Append casino affiliate link if available
    if casino_link:
        if locale.startswith("pt"):
            cta = f"Jogue agora no {casino_name}"
        else:
            cta = f"Juega ahora en {casino_name}"
        text += f'\n👉 <a href="{casino_link}">{cta}</a>'
    return text


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
