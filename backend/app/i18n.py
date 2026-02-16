import json
from pathlib import Path
from typing import Optional

LOCALES_DIR = Path(__file__).parent / "locales"
_cache: dict[str, dict] = {}

SUPPORTED_LOCALES = ["pt_BR", "es_MX"]
DEFAULT_LOCALE = "pt_BR"

LANGUAGE_NAMES = {
    "pt_BR": "português brasileiro",
    "es_MX": "español latinoamericano",
}


def _load_locale(locale: str) -> dict:
    if locale not in _cache:
        path = LOCALES_DIR / f"{locale}.json"
        if path.exists():
            _cache[locale] = json.loads(path.read_text(encoding="utf-8"))
        else:
            _cache[locale] = _load_locale(DEFAULT_LOCALE)
    return _cache[locale]


def t(key: str, locale: str = DEFAULT_LOCALE, **kwargs) -> str:
    strings = _load_locale(locale)
    text = strings.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_user_locale(
    language_code: Optional[str], saved_locale: Optional[str] = None
) -> str:
    if saved_locale and saved_locale in SUPPORTED_LOCALES:
        return saved_locale
    if language_code:
        lang = language_code.lower().replace("-", "_")
        if lang.startswith("pt"):
            return "pt_BR"
        if lang.startswith("es"):
            return "es_MX"
    return DEFAULT_LOCALE


def get_language_name(locale: str) -> str:
    return LANGUAGE_NAMES.get(locale, LANGUAGE_NAMES[DEFAULT_LOCALE])
