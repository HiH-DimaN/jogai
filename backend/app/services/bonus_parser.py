"""Automated casino bonus parser: fetch promo pages → AI extract → upsert DB."""

import asyncio
import logging
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from app.celery_app import celery
from app.database.engine import async_session
from app.database.models import Bonus, Casino
from app.services.bonus_analyzer import calculate_jogai_score
from app.services.llm import chat_json, get_locale_params, load_prompt

logger = logging.getLogger(__name__)

# Casino sources for bonus parsing
CASINO_SOURCES: list[dict] = [
    {
        "slug": "bet365",
        "promo_url": "https://www.bet365.com/promotions",
        "geo": ["BR"],
    },
    {
        "slug": "rivalo",
        "promo_url": "https://www.rivalo.com/pt/promotions",
        "geo": ["BR"],
    },
    {
        "slug": "pinup",
        "promo_url": "https://pin-up.casino/promotions",
        "geo": ["BR", "MX"],
    },
    {
        "slug": "1win",
        "promo_url": "https://1win.com/promotions",
        "geo": ["BR", "MX"],
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


async def fetch_page(url: str) -> str | None:
    """Fetch HTML content from a URL."""
    try:
        async with httpx.AsyncClient(
            timeout=30.0, follow_redirects=True, headers=HEADERS
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except Exception:
        logger.warning("Failed to fetch %s", url, exc_info=True)
        return None


def extract_text_blocks(html: str, max_length: int = 8000) -> str:
    """Extract meaningful text from HTML, strip navigation/scripts."""
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Truncate to fit LLM context
    if len(text) > max_length:
        text = text[:max_length]

    return text


async def parse_casino_bonuses(source: dict) -> list[dict]:
    """Fetch promo page and extract bonuses via AI."""
    html = await fetch_page(source["promo_url"])
    if not html:
        logger.warning("No HTML for %s, skipping", source["slug"])
        return []

    text = extract_text_blocks(html)
    if len(text.strip()) < 50:
        logger.warning("Too little text from %s, skipping", source["slug"])
        return []

    # Use pt_BR as default locale for parsing
    language, currency_symbol = get_locale_params("pt_BR")
    prompt = load_prompt("bonus_parsing", language, currency_symbol)

    try:
        result = await chat_json(prompt, text, language, currency_symbol)
    except Exception:
        logger.error("AI parsing failed for %s", source["slug"], exc_info=True)
        return []

    # chat_json returns dict; we expect a list
    if isinstance(result, dict):
        # Maybe AI returned {"bonuses": [...]}
        if "bonuses" in result:
            result = result["bonuses"]
        else:
            result = [result] if result else []

    if not isinstance(result, list):
        logger.warning("Unexpected AI response type for %s: %s", source["slug"], type(result))
        return []

    # Calculate Jogai Score for each parsed bonus
    enriched = []
    for bonus_data in result:
        if not isinstance(bonus_data, dict) or not bonus_data.get("title_pt"):
            continue

        score_result = calculate_jogai_score(
            bonus_percent=bonus_data.get("bonus_percent") or 100,
            wagering_multiplier=bonus_data.get("wagering_multiplier") or 35,
            deadline_days=bonus_data.get("wagering_deadline_days") or 30,
            max_bet=bonus_data.get("max_bet") or 25,
            deposit=100.0,
            free_spins=bonus_data.get("free_spins") or 0,
            no_deposit=bonus_data.get("no_deposit", False),
        )

        bonus_data["jogai_score"] = score_result["jogai_score"]
        bonus_data["verdict_key"] = score_result["verdict_key"]
        bonus_data["expected_loss"] = score_result["expected_loss"]
        bonus_data["profit_probability"] = score_result["profit_probability"]
        enriched.append(bonus_data)

    logger.info("Parsed %d bonuses from %s", len(enriched), source["slug"])
    return enriched


async def upsert_bonuses(casino_slug: str, bonuses: list[dict], geo: list[str]) -> None:
    """Upsert parsed bonuses into DB. Deactivate stale ones."""
    async with async_session() as session:
        # Find casino
        result = await session.execute(
            select(Casino).where(Casino.slug == casino_slug)
        )
        casino = result.scalar_one_or_none()
        if not casino:
            logger.warning("Casino %s not found in DB, skipping upsert", casino_slug)
            return

        now = datetime.utcnow()
        seen_titles: set[str] = set()

        for bonus_data in bonuses:
            title_pt = bonus_data.get("title_pt", "")
            if not title_pt:
                continue
            seen_titles.add(title_pt)

            # Check if bonus already exists
            existing = await session.execute(
                select(Bonus).where(
                    Bonus.casino_id == casino.id,
                    Bonus.title_pt == title_pt,
                )
            )
            bonus = existing.scalar_one_or_none()

            if bonus:
                # Update existing
                bonus.title_es = bonus_data.get("title_es", bonus.title_es)
                bonus.bonus_percent = bonus_data.get("bonus_percent", bonus.bonus_percent)
                bonus.max_bonus_amount = bonus_data.get("max_bonus_amount", bonus.max_bonus_amount)
                bonus.wagering_multiplier = bonus_data.get("wagering_multiplier", bonus.wagering_multiplier)
                bonus.wagering_deadline_days = bonus_data.get("wagering_deadline_days", bonus.wagering_deadline_days)
                bonus.max_bet = bonus_data.get("max_bet", bonus.max_bet)
                bonus.free_spins = bonus_data.get("free_spins", bonus.free_spins)
                bonus.no_deposit = bonus_data.get("no_deposit", bonus.no_deposit)
                bonus.jogai_score = bonus_data.get("jogai_score", bonus.jogai_score)
                bonus.verdict_key = bonus_data.get("verdict_key", bonus.verdict_key)
                bonus.expected_loss = bonus_data.get("expected_loss", bonus.expected_loss)
                bonus.profit_probability = bonus_data.get("profit_probability", bonus.profit_probability)
                bonus.is_active = True
                bonus.updated_at = now
                logger.info("Updated bonus: %s", title_pt)
            else:
                # Create new
                new_bonus = Bonus(
                    casino_id=casino.id,
                    title_pt=title_pt,
                    title_es=bonus_data.get("title_es", ""),
                    bonus_percent=bonus_data.get("bonus_percent", 100),
                    max_bonus_amount=bonus_data.get("max_bonus_amount"),
                    max_bonus_currency="BRL",
                    wagering_multiplier=bonus_data.get("wagering_multiplier", 35),
                    wagering_deadline_days=bonus_data.get("wagering_deadline_days", 30),
                    max_bet=bonus_data.get("max_bet", 25),
                    free_spins=bonus_data.get("free_spins", 0),
                    no_deposit=bonus_data.get("no_deposit", False),
                    jogai_score=bonus_data.get("jogai_score"),
                    verdict_key=bonus_data.get("verdict_key"),
                    expected_loss=bonus_data.get("expected_loss"),
                    profit_probability=bonus_data.get("profit_probability"),
                    affiliate_link=casino.affiliate_link_template.format(
                        ref_id=casino.ref_id or "", user_id=""
                    ) if casino.affiliate_link_template else None,
                    is_active=True,
                    starts_at=now,
                    expires_at=now + timedelta(days=30),
                    geo=geo,
                )
                session.add(new_bonus)
                logger.info("Created bonus: %s", title_pt)

        # Deactivate bonuses no longer on the page
        all_bonuses = await session.execute(
            select(Bonus).where(
                Bonus.casino_id == casino.id,
                Bonus.is_active.is_(True),
            )
        )
        for bonus in all_bonuses.scalars():
            if bonus.title_pt and bonus.title_pt not in seen_titles:
                bonus.is_active = False
                logger.info("Deactivated stale bonus: %s", bonus.title_pt)

        await session.commit()


async def run_parser() -> dict[str, int]:
    """Run parser for all casino sources. Returns stats."""
    stats: dict[str, int] = {}
    for source in CASINO_SOURCES:
        try:
            bonuses = await parse_casino_bonuses(source)
            if bonuses:
                await upsert_bonuses(source["slug"], bonuses, source["geo"])
            stats[source["slug"]] = len(bonuses)
        except Exception:
            logger.error("Parser failed for %s", source["slug"], exc_info=True)
            stats[source["slug"]] = 0
    return stats


@celery.task(name="app.services.bonus_parser.task_parse_bonuses")
def task_parse_bonuses() -> dict[str, int]:
    """Celery task: parse all casino bonus pages."""
    loop = asyncio.new_event_loop()
    try:
        stats = loop.run_until_complete(run_parser())
        logger.info("Bonus parser completed: %s", stats)
        return stats
    finally:
        loop.close()
