from app.database.models import Bonus, Casino
from app.i18n import t
from app.utils.formatters import format_currency, get_min_deposit


def _get_title(obj: Bonus | Casino, locale: str, field_prefix: str = "title") -> str:
    """Get localized field: title_pt or title_es based on locale."""
    suffix = "pt" if locale.startswith("pt") else "es"
    return getattr(obj, f"{field_prefix}_{suffix}", None) or getattr(obj, f"{field_prefix}_pt", "") or ""


def _get_description(obj: Casino, locale: str) -> str:
    suffix = "pt" if locale.startswith("pt") else "es"
    return getattr(obj, f"description_{suffix}", None) or getattr(obj, "description_pt", "") or ""


def format_bonus_card(
    bonus: Bonus, locale: str, medal: str = "🏆"
) -> str:
    casino_name = bonus.casino.name if bonus.casino else "—"
    title = _get_title(bonus, locale)
    # Strip casino name prefix to avoid "1WIN — 1WIN: ..."
    if title.upper().startswith(casino_name.upper()):
        colon_idx = title.find(":")
        if colon_idx != -1 and colon_idx < len(casino_name) + 15:
            title = title[colon_idx + 1:].strip()
    verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else "—"

    # Build wagering line
    wager = bonus.wagering_multiplier
    if wager is not None and wager > 0:
        deadline = bonus.wagering_deadline_days or 0
        if locale.startswith("pt"):
            wagering_line = f"🔄 Rollover: x{wager:.0f} | Prazo: {deadline} dias"
        else:
            wagering_line = f"🔄 Rollover: x{wager:.0f} | Plazo: {deadline} días"
    else:
        if locale.startswith("pt"):
            wagering_line = "🔄 Sem rollover!"
        else:
            wagering_line = "🔄 ¡Sin rollover!"

    return t(
        "bonus_card",
        locale,
        medal=medal,
        casino=casino_name,
        title=title,
        wagering_line=wagering_line,
        score=str(bonus.jogai_score or 0),
        verdict=verdict,
    )


def format_casino_card(casino: Casino, locale: str) -> str:
    description = _get_description(casino, locale)
    min_dep = format_currency(get_min_deposit(casino, locale), locale)

    lines = [
        f"<b>{casino.name}</b>",
        description,
        f"💰 Min: {min_dep}",
        f"⚡ {casino.withdrawal_time or '—'}",
    ]
    return "\n".join(lines)
