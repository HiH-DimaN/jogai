from app.database.models import Bonus, Casino
from app.i18n import t
from app.utils.formatters import format_currency


def _get_title(obj: Bonus | Casino, locale: str, field_prefix: str = "title") -> str:
    """Get localized field: title_pt or title_es based on locale."""
    suffix = "pt" if locale.startswith("pt") else "es"
    return getattr(obj, f"{field_prefix}_{suffix}", None) or getattr(obj, f"{field_prefix}_pt", "") or ""


def _get_description(obj: Casino, locale: str) -> str:
    suffix = "pt" if locale.startswith("pt") else "es"
    return getattr(obj, f"description_{suffix}", None) or getattr(obj, "description_pt", "") or ""


def format_bonus_card(bonus: Bonus, locale: str) -> str:
    casino_name = bonus.casino.name if bonus.casino else "—"
    title = _get_title(bonus, locale)
    verdict = t(bonus.verdict_key, locale) if bonus.verdict_key else "—"

    return t(
        "bonus_card",
        locale,
        casino=casino_name,
        title=title,
        wagering=str(bonus.wagering_multiplier or 0),
        deadline=str(bonus.wagering_deadline_days or 0),
        score=str(bonus.jogai_score or 0),
        verdict=verdict,
    )


def format_casino_card(casino: Casino, locale: str) -> str:
    description = _get_description(casino, locale)
    min_dep = format_currency(casino.min_deposit or 0, locale)

    lines = [
        f"<b>{casino.name}</b>",
        description,
        f"💰 Min: {min_dep}",
        f"⚡ {casino.withdrawal_time or '—'}",
    ]
    return "\n".join(lines)
