"""Slot parser: Slotopol RTP data + casino catalog parsing + AI tips → upsert DB."""

import asyncio
import logging
import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from app.celery_app import celery
from app.config import settings
from app.database.engine import async_session, engine
from app.database.models import Casino, Slot
from app.services.llm import chat, chat_json, get_locale_params, load_prompt

logger = logging.getLogger(__name__)

# Slotopol server (internal Docker network)
SLOTOPOL_URL = "http://slotopol:8080"

# Casino slot catalog pages
CASINO_SLOT_SOURCES: list[dict] = [
    {
        "slug": "pinup",
        "catalog_url": "https://pin-up.casino/slots",
        "geo": ["MX"],
    },
    {
        "slug": "1win",
        "catalog_url": "https://1win.com/casino/slots",
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


def _slugify(name: str) -> str:
    """Convert a game name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


async def fetch_slotopol_games() -> list[dict]:
    """Fetch game list with RTP data from Slotopol server.

    Returns list of dicts with keys: name, rtp, provider, reels, lines, features, etc.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{SLOTOPOL_URL}/game/algs")
            response.raise_for_status()
            data = response.json()
    except Exception:
        logger.warning("Failed to fetch Slotopol games", exc_info=True)
        return []

    games = []
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("alias") or ""
            if not name:
                continue
            rtp = item.get("rtp")
            if isinstance(rtp, (int, float)) and rtp > 1:
                # Slotopol may return RTP as 0.96 or 96.0 — normalize to percentage
                if rtp < 1:
                    rtp = rtp * 100
            games.append({
                "name": name,
                "slug": _slugify(name),
                "provider": item.get("provider", ""),
                "rtp": round(float(rtp), 2) if rtp else None,
                "reels": item.get("reels"),
                "lines": item.get("lines"),
                "features": item.get("features") or [],
                "source": "slotopol",
                "source_id": item.get("id") or item.get("alias") or _slugify(name),
            })

    logger.info("Fetched %d games from Slotopol", len(games))
    return games


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
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    if len(text) > max_length:
        text = text[:max_length]
    return text


async def parse_casino_slots(source: dict) -> list[str]:
    """Fetch casino slot catalog page and extract game names via AI."""
    html = await fetch_page(source["catalog_url"])
    if not html:
        logger.warning("No HTML for %s slots, skipping", source["slug"])
        return []

    text = extract_text_blocks(html)
    if len(text.strip()) < 50:
        logger.warning("Too little text from %s slots, skipping", source["slug"])
        return []

    language, currency_symbol = get_locale_params("pt_BR")
    prompt = load_prompt("slot_parsing", language, currency_symbol)

    try:
        result = await chat_json(prompt, text, language, currency_symbol, heavy=True)
    except Exception:
        logger.error("AI slot parsing failed for %s", source["slug"], exc_info=True)
        return []

    # chat_json returns dict or list
    if isinstance(result, dict):
        result = result.get("slots") or result.get("games") or []
    if not isinstance(result, list):
        return []

    # Filter to strings only
    names = [str(s).strip() for s in result if isinstance(s, str) and s.strip()]
    logger.info("Parsed %d slot names from %s", len(names), source["slug"])
    return names


async def generate_slot_tip(slot_data: dict, locale: str) -> str:
    """Generate an AI tip for a specific slot."""
    language, currency_symbol = get_locale_params(locale)
    prompt = load_prompt("slot_tip", language, currency_symbol)

    features_str = ", ".join(slot_data.get("features") or []) or "standard"
    user_message = (
        f"Game: {slot_data['name']}\n"
        f"Provider: {slot_data.get('provider', 'Unknown')}\n"
        f"RTP: {slot_data.get('rtp', 'N/A')}%\n"
        f"Volatility: {slot_data.get('volatility', 'Unknown')}\n"
        f"Max Win: {slot_data.get('max_win', 'N/A')}\n"
        f"Features: {features_str}"
    )

    try:
        tip = await chat(prompt, user_message, language, currency_symbol)
        # Enforce 280 char limit
        return tip.strip()[:280]
    except Exception:
        logger.warning("AI tip generation failed for %s", slot_data["name"], exc_info=True)
        return ""


def _classify_volatility(rtp: float | None) -> str:
    """Rough volatility classification based on RTP when not provided by source."""
    if rtp is None:
        return "medium"
    if rtp >= 97:
        return "low"
    if rtp >= 95:
        return "medium"
    return "high"


async def upsert_slots(slots: list[dict]) -> int:
    """Upsert slots into DB. Returns count of new/updated slots."""
    count = 0
    async with async_session() as session:
        for slot_data in slots:
            slug = slot_data.get("slug")
            if not slug:
                continue

            result = await session.execute(
                select(Slot).where(Slot.slug == slug)
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update fields from source
                if slot_data.get("rtp") is not None:
                    existing.rtp = slot_data["rtp"]
                if slot_data.get("provider"):
                    existing.provider = slot_data["provider"]
                if slot_data.get("reels") is not None:
                    existing.reels = slot_data["reels"]
                if slot_data.get("lines") is not None:
                    existing.lines = slot_data["lines"]
                if slot_data.get("features"):
                    existing.features = slot_data["features"]
                if slot_data.get("volatility"):
                    existing.volatility = slot_data["volatility"]
                if slot_data.get("max_win"):
                    existing.max_win = slot_data["max_win"]
                if slot_data.get("tip_pt"):
                    existing.tip_pt = slot_data["tip_pt"]
                if slot_data.get("tip_es"):
                    existing.tip_es = slot_data["tip_es"]
                if slot_data.get("source"):
                    existing.source = slot_data["source"]
                if slot_data.get("source_id"):
                    existing.source_id = slot_data["source_id"]
                existing.is_active = True
                count += 1
            else:
                volatility = slot_data.get("volatility") or _classify_volatility(
                    slot_data.get("rtp")
                )
                new_slot = Slot(
                    name=slot_data["name"],
                    slug=slug,
                    provider=slot_data.get("provider"),
                    rtp=slot_data.get("rtp"),
                    volatility=volatility,
                    max_win=slot_data.get("max_win"),
                    reels=slot_data.get("reels"),
                    lines=slot_data.get("lines"),
                    features=slot_data.get("features"),
                    tip_pt=slot_data.get("tip_pt"),
                    tip_es=slot_data.get("tip_es"),
                    geo=slot_data.get("geo", ["BR"]),
                    is_active=True,
                    source=slot_data.get("source", "slotopol"),
                    source_id=slot_data.get("source_id"),
                )
                session.add(new_slot)
                count += 1

        await session.commit()

    logger.info("Upserted %d slots", count)
    return count


async def match_slots_to_casinos() -> None:
    """Match slots to casinos based on parsed catalog data.

    For each slot, find which casino has it and set best_casino_id
    to the first matching casino.
    """
    casino_slots: dict[str, list[str]] = {}  # casino_slug → [slot_name_lower, ...]

    for source in CASINO_SLOT_SOURCES:
        names = await parse_casino_slots(source)
        casino_slots[source["slug"]] = [n.lower() for n in names]

    if not any(casino_slots.values()):
        logger.info("No casino slot catalogs parsed, skipping matching")
        return

    async with async_session() as session:
        # Load casinos
        casinos_result = await session.execute(
            select(Casino).where(Casino.is_active.is_(True))
        )
        casinos_by_slug = {c.slug: c for c in casinos_result.scalars()}

        # Load all active slots
        slots_result = await session.execute(
            select(Slot).where(Slot.is_active.is_(True))
        )
        slots = slots_result.scalars().all()

        for slot in slots:
            slot_name_lower = slot.name.lower()
            for casino_slug, names in casino_slots.items():
                if slot_name_lower in names and casino_slug in casinos_by_slug:
                    slot.best_casino_id = casinos_by_slug[casino_slug].id
                    # Merge geo from casino
                    casino_geo = casinos_by_slug[casino_slug].geo or []
                    current_geo = set(slot.geo or [])
                    current_geo.update(casino_geo)
                    slot.geo = list(current_geo)
                    break

        await session.commit()
        logger.info("Matched slots to casinos")


async def _generate_tips_for_slots() -> None:
    """Generate AI tips for slots that don't have them yet."""
    async with async_session() as session:
        result = await session.execute(
            select(Slot).where(
                Slot.is_active.is_(True),
                Slot.tip_pt.is_(None),
                Slot.rtp.isnot(None),
            ).limit(20)
        )
        slots = result.scalars().all()

        for slot in slots:
            slot_data = {
                "name": slot.name,
                "provider": slot.provider or "Unknown",
                "rtp": float(slot.rtp) if slot.rtp else None,
                "volatility": slot.volatility or "medium",
                "max_win": slot.max_win or "N/A",
                "features": slot.features or [],
            }

            tip_pt = await generate_slot_tip(slot_data, "pt_BR")
            tip_es = await generate_slot_tip(slot_data, "es_MX")

            if tip_pt:
                slot.tip_pt = tip_pt
            if tip_es:
                slot.tip_es = tip_es

        await session.commit()
        logger.info("Generated tips for %d slots", len(slots))


async def run_slot_parser() -> dict[str, int]:
    """Full slot parsing pipeline: Slotopol → tips → casino matching → upsert."""
    stats: dict[str, int] = {}

    # 1. Fetch from Slotopol
    slotopol_games = await fetch_slotopol_games()
    stats["slotopol_fetched"] = len(slotopol_games)

    # 2. Upsert into DB
    if slotopol_games:
        upserted = await upsert_slots(slotopol_games)
        stats["upserted"] = upserted

    # 3. Generate AI tips for slots without tips
    await _generate_tips_for_slots()

    # 4. Match slots to casinos
    await match_slots_to_casinos()

    logger.info("Slot parser completed: %s", stats)
    return stats


# --- Celery task ---


@celery.task(name="app.services.slot_parser.task_parse_slots")
def task_parse_slots() -> dict[str, int]:
    """Celery task: parse slots from Slotopol + casino catalogs."""
    loop = asyncio.new_event_loop()
    try:
        from app.database.engine import engine
        loop.run_until_complete(engine.dispose())
        stats = loop.run_until_complete(run_slot_parser())
        logger.info("Slot parser task completed: %s", stats)
        return stats
    finally:
        loop.close()
