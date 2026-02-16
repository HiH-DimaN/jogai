import json
import logging
from pathlib import Path

import httpx

from app.config import settings
from app.i18n import LANGUAGE_NAMES, get_language_name
from app.utils.formatters import LOCALE_CONFIG

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str, language: str, currency_symbol: str) -> str:
    """Load prompt template and substitute {language} and {currency_symbol}."""
    path = PROMPTS_DIR / f"{name}.md"
    template = path.read_text(encoding="utf-8")
    return template.replace("{language}", language).replace("{currency_symbol}", currency_symbol)


def get_locale_params(locale: str) -> tuple[str, str]:
    """Return (language_name, currency_symbol) for a locale."""
    language = get_language_name(locale)
    currency_symbol = LOCALE_CONFIG.get(locale, LOCALE_CONFIG["pt_BR"])["currency_symbol"]
    return language, currency_symbol


async def chat(
    prompt: str,
    message: str,
    language: str = "português brasileiro",
    currency_symbol: str = "R$",
) -> str:
    """Send a chat request to the configured LLM provider.

    Substitutes {language} and {currency_symbol} in the prompt if present.
    Retries up to 3 times with 30s timeout.
    """
    # Substitute variables in prompt
    prompt = prompt.replace("{language}", language).replace("{currency_symbol}", currency_symbol)

    for attempt in range(3):
        try:
            if settings.llm_provider == "anthropic":
                return await _chat_anthropic(prompt, message)
            else:
                return await _chat_openai(prompt, message)
        except Exception:
            logger.warning("LLM attempt %d failed", attempt + 1, exc_info=True)
            if attempt == 2:
                raise

    return ""


async def chat_json(
    prompt: str,
    message: str,
    language: str = "português brasileiro",
    currency_symbol: str = "R$",
) -> dict:
    """Chat and parse the response as JSON."""
    response = await chat(prompt, message, language, currency_symbol)

    # Extract JSON from response (may be wrapped in markdown code block)
    text = response.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM JSON response: %s", text[:200])
        return {}


async def _chat_anthropic(system_prompt: str, user_message: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "max_tokens": 2048,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]


async def _chat_openai(system_prompt: str, user_message: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 2048,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
