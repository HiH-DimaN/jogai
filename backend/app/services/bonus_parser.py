"""Automated casino bonus parser: fetch per-casino review pages → AI extract → upsert DB.

Strategy: parse specific per-casino pages on review sites (legalbet.mx)
where each page focuses on one casino → clean data, no AI matching needed.
"""

import asyncio
import logging
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from app.celery_app import celery
from app.database.engine import async_session, engine
from app.database.models import Bonus, Casino
from app.services.bonus_analyzer import calculate_jogai_score
from app.services.llm import chat_json, get_locale_params, load_prompt

logger = logging.getLogger(__name__)

# Per-casino review pages — each URL is about a specific casino
# casino_slug must match Casino.slug in DB
CASINO_SOURCES: list[dict] = [
    # MX sources (legalbet.mx has detailed per-casino pages)
    {
        "url": "https://legalbet.mx/casas-de-apuestas/1win/",
        "casino_slug": "1win",
        "geo": "MX",
        "locale": "es_MX",
    },
    {
        "url": "https://legalbet.mx/casas-de-apuestas/caliente/",
        "casino_slug": "caliente",
        "geo": "MX",
        "locale": "es_MX",
    },
    {
        "url": "https://legalbet.mx/casas-de-apuestas/codere/",
        "casino_slug": "codere",
        "geo": "MX",
        "locale": "es_MX",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-MX,es;q=0.9,pt-BR;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
}


async def fetch_page(url: str) -> str | None:
    """Fetch HTML content from a URL with robust error handling."""
    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=HEADERS,
        ) as client:
            response = await client.get(url)
            if response.status_code == 403:
                logger.warning("403 Forbidden for %s, skipping", url)
                return None
            response.raise_for_status()
            return response.text
    except Exception:
        logger.warning("Failed to fetch %s", url, exc_info=True)
        return None


def extract_text_blocks(html: str, max_length: int = 20000) -> str:
    """Extract meaningful text from HTML, strip navigation/scripts."""
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Truncate to fit LLM context
    if len(text) > max_length:
        text = text[:max_length]

    return text


async def parse_casino_source(source: dict) -> list[dict]:
    """Fetch a per-casino review page and extract bonuses via AI."""
    html = await fetch_page(source["url"])
    if not html:
        return []

    text = extract_text_blocks(html)
    if len(text.strip()) < 100:
        logger.warning(
            "Too little text from %s (%d chars), skipping",
            source["url"], len(text.strip()),
        )
        return []

    locale = source["locale"]
    language, currency_symbol = get_locale_params(locale)
    prompt = load_prompt("bonus_parsing", language, currency_symbol)

    casino_slug = source["casino_slug"]
    casino_name = casino_slug.upper().replace("_", " ")

    # Tell AI which casino this page is about
    user_message = (
        f"This page is about casino: {casino_name}\n"
        f"Extract all bonuses for {casino_name} from this text:\n\n{text}"
    )

    try:
        result = await chat_json(prompt, user_message, language, currency_symbol, heavy=False)
    except Exception:
        logger.error("AI parsing failed for %s", source["url"], exc_info=True)
        return []

    # Normalize result to list
    if isinstance(result, dict):
        if "bonuses" in result:
            result = result["bonuses"]
        else:
            result = [result] if result else []

    if not isinstance(result, list):
        logger.warning(
            "Unexpected AI response type for %s: %s",
            source["url"], type(result),
        )
        return []

    logger.info(
        "AI returned %d items for %s: %s",
        len(result), casino_slug,
        str(result)[:500] if result else "[]",
    )

    # Enrich each bonus — casino_slug is pre-assigned, no matching needed
    enriched = []
    for bonus_data in result:
        if not isinstance(bonus_data, dict):
            continue

        # Require at least a title in one language
        if not bonus_data.get("title_pt") and not bonus_data.get("title_es"):
            continue

        # If only one language title provided, use it for both
        if not bonus_data.get("title_pt"):
            bonus_data["title_pt"] = bonus_data.get("title_es", "")
        if not bonus_data.get("title_es"):
            bonus_data["title_es"] = bonus_data.get("title_pt", "")

        bonus_data["casino_slug"] = casino_slug
        bonus_data["casino_name"] = casino_name
        bonus_data["geo"] = source["geo"]

        # Calculate Jogai Score
        deposit = 100.0 if source["geo"] == "BR" else 2000.0
        score_result = calculate_jogai_score(
            bonus_percent=bonus_data.get("bonus_percent") or 100,
            wagering_multiplier=bonus_data.get("wagering_multiplier") or 35,
            deadline_days=bonus_data.get("wagering_deadline_days") or 30,
            max_bet=bonus_data.get("max_bet") or 25,
            deposit=deposit,
            free_spins=bonus_data.get("free_spins") or 0,
            no_deposit=bonus_data.get("no_deposit", False),
        )

        bonus_data["jogai_score"] = score_result["jogai_score"]
        bonus_data["verdict_key"] = score_result["verdict_key"]
        bonus_data["expected_loss"] = score_result["expected_loss"]
        bonus_data["profit_probability"] = score_result["profit_probability"]
        enriched.append(bonus_data)

    logger.info(
        "Parsed %d bonuses for %s from %s",
        len(enriched), casino_slug, source["url"],
    )
    return enriched


async def upsert_bonuses(bonuses: list[dict]) -> int:
    """Upsert parsed bonuses into DB. Returns count of upserted."""
    if not bonuses:
        return 0

    upserted = 0
    async with async_session() as session:
        # Load all casinos
        result = await session.execute(select(Casino))
        casino_map = {c.slug: c for c in result.scalars().all()}

        now = datetime.utcnow()

        for bonus_data in bonuses:
            casino_slug = bonus_data.get("casino_slug")
            casino = casino_map.get(casino_slug)
            if not casino:
                continue

            title_pt = bonus_data.get("title_pt", "")
            if not title_pt:
                continue

            geo = bonus_data.get("geo", "BR")

            # Check if similar bonus already exists (by casino + similar title)
            existing = await session.execute(
                select(Bonus).where(
                    Bonus.casino_id == casino.id,
                    Bonus.title_pt == title_pt,
                    Bonus.is_active.is_(True),
                )
            )
            bonus = existing.scalar_one_or_none()

            if bonus:
                # Update existing
                bonus.title_es = bonus_data.get("title_es", bonus.title_es)
                bonus.bonus_percent = bonus_data.get("bonus_percent", bonus.bonus_percent)
                bonus.max_bonus_amount = bonus_data.get("max_bonus_amount", bonus.max_bonus_amount)
                bonus.wagering_multiplier = bonus_data.get(
                    "wagering_multiplier", bonus.wagering_multiplier
                )
                bonus.wagering_deadline_days = bonus_data.get(
                    "wagering_deadline_days", bonus.wagering_deadline_days
                )
                bonus.max_bet = bonus_data.get("max_bet", bonus.max_bet)
                bonus.free_spins = bonus_data.get("free_spins", bonus.free_spins)
                bonus.no_deposit = bonus_data.get("no_deposit", bonus.no_deposit)
                bonus.jogai_score = bonus_data.get("jogai_score", bonus.jogai_score)
                bonus.verdict_key = bonus_data.get("verdict_key", bonus.verdict_key)
                bonus.expected_loss = bonus_data.get("expected_loss", bonus.expected_loss)
                bonus.profit_probability = bonus_data.get(
                    "profit_probability", bonus.profit_probability
                )
                bonus.updated_at = now
                logger.info("Updated bonus: %s (%s)", title_pt, casino_slug)
            else:
                # Create new
                affiliate_link = None
                if casino.affiliate_link_template:
                    affiliate_link = casino.affiliate_link_template.format(
                        ref_id=casino.ref_id or "", user_id=""
                    )

                new_bonus = Bonus(
                    casino_id=casino.id,
                    title_pt=title_pt,
                    title_es=bonus_data.get("title_es", ""),
                    bonus_percent=bonus_data.get("bonus_percent", 100),
                    max_bonus_amount=bonus_data.get("max_bonus_amount"),
                    max_bonus_currency="BRL" if geo == "BR" else "MXN",
                    wagering_multiplier=bonus_data.get("wagering_multiplier", 35),
                    wagering_deadline_days=bonus_data.get("wagering_deadline_days", 30),
                    max_bet=bonus_data.get("max_bet", 25),
                    free_spins=bonus_data.get("free_spins", 0),
                    no_deposit=bonus_data.get("no_deposit", False),
                    jogai_score=bonus_data.get("jogai_score"),
                    verdict_key=bonus_data.get("verdict_key"),
                    expected_loss=bonus_data.get("expected_loss"),
                    profit_probability=bonus_data.get("profit_probability"),
                    affiliate_link=affiliate_link,
                    is_active=True,
                    starts_at=now,
                    expires_at=now + timedelta(days=30),
                    geo=[geo],
                )
                session.add(new_bonus)
                logger.info("Created bonus: %s (%s)", title_pt, casino_slug)

            upserted += 1

        await session.commit()

    return upserted


async def run_parser() -> dict[str, int]:
    """Run parser for all casino sources. Returns stats."""
    stats: dict[str, int] = {}
    all_bonuses: list[dict] = []

    for i, source in enumerate(CASINO_SOURCES):
        try:
            bonuses = await parse_casino_source(source)
            all_bonuses.extend(bonuses)
            stats[source["url"]] = len(bonuses)
        except Exception:
            logger.error("Parser failed for %s", source["url"], exc_info=True)
            stats[source["url"]] = 0

        # Pause between sources to avoid AI rate limits
        if i < len(CASINO_SOURCES) - 1:
            await asyncio.sleep(5)

    # Deduplicate by (casino_slug, title_pt)
    seen: set[tuple[str, str]] = set()
    unique_bonuses = []
    for b in all_bonuses:
        key = (b.get("casino_slug", ""), b.get("title_pt", ""))
        if key not in seen:
            seen.add(key)
            unique_bonuses.append(b)

    upserted = await upsert_bonuses(unique_bonuses)
    stats["_upserted"] = upserted
    stats["_total_parsed"] = len(unique_bonuses)

    return stats


async def _dispose_and_run(coro):
    from app.bot.bot import reset_bot
    reset_bot()
    await engine.dispose()
    return await coro


@celery.task(name="app.services.bonus_parser.task_parse_bonuses")
def task_parse_bonuses() -> dict[str, int]:
    """Celery task: parse bonus pages from review/affiliate sites."""
    stats = asyncio.run(_dispose_and_run(run_parser()))
    logger.info("Bonus parser completed: %s", stats)
    return stats
