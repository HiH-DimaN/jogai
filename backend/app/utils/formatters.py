from datetime import datetime
from decimal import Decimal
from typing import Union

LOCALE_CONFIG = {
    "pt_BR": {
        "currency_symbol": "R$",
        "currency_code": "BRL",
        "decimal_sep": ",",
        "thousands_sep": ".",
        "date_format": "%d/%m/%Y",
    },
    "es_MX": {
        "currency_symbol": "MX$",
        "currency_code": "MXN",
        "decimal_sep": ".",
        "thousands_sep": ",",
        "date_format": "%d/%m/%Y",
    },
}

DEFAULT_LOCALE = "pt_BR"


def format_currency(
    amount: Union[int, float, Decimal], locale: str = DEFAULT_LOCALE
) -> str:
    config = LOCALE_CONFIG.get(locale, LOCALE_CONFIG[DEFAULT_LOCALE])
    symbol = config["currency_symbol"]
    dec_sep = config["decimal_sep"]
    thou_sep = config["thousands_sep"]

    amount = float(amount)
    is_negative = amount < 0
    amount = abs(amount)

    integer_part = int(amount)
    decimal_part = round(amount - integer_part, 2)

    # Format integer part with thousands separator
    int_str = ""
    int_s = str(integer_part)
    for i, digit in enumerate(reversed(int_s)):
        if i > 0 and i % 3 == 0:
            int_str = thou_sep + int_str
        int_str = digit + int_str

    # Format decimal part
    dec_str = f"{decimal_part:.2f}"[2:]

    formatted = f"{symbol}{int_str}{dec_sep}{dec_str}"
    if is_negative:
        formatted = f"-{formatted}"
    return formatted


def format_date(dt: datetime, locale: str = DEFAULT_LOCALE) -> str:
    config = LOCALE_CONFIG.get(locale, LOCALE_CONFIG[DEFAULT_LOCALE])
    return dt.strftime(config["date_format"])
