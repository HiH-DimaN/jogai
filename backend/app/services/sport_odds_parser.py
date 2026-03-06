"""Sport picks parser using The Odds API.

Fetches upcoming matches with odds, generates AI analysis,
and saves sport picks to the database.
"""

import asyncio
import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select

from app.celery_app import celery
from app.config import settings
from app.database.engine import async_session, engine
from app.database.models import Casino, SportPick
from app.services.llm import chat_json, get_locale_params, load_prompt

logger = logging.getLogger(__name__)

# Leagues relevant to our geos
LEAGUES = {
    "BR": [
        "soccer_brazil_serie_a",
        "soccer_brazil_serie_b",
        "soccer_conmebol_copa_libertadores",
    ],
    "MX": [
        "soccer_mexico_ligamx",
        "soccer_conmebol_copa_libertadores",
    ],
    "GLOBAL": [
        "soccer_uefa_champs_league",
        "soccer_epl",
        "soccer_spain_la_liga",
    ],
}

# Max picks per fetch cycle per geo
MAX_PICKS_PER_GEO = 3

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"


async def _fetch_odds(sport_key: str) -> list[dict]:
    """Fetch upcoming odds for a sport from The Odds API."""
    if not settings.odds_api_key:
        logger.warning("ODDS_API_KEY not set, skipping sport fetch")
        return []

    url = f"{ODDS_API_BASE}/{sport_key}/odds/"
    params = {
        "apiKey": settings.odds_api_key,
        "regions": "us,eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        logger.warning("Failed to fetch odds for %s", sport_key, exc_info=True)
        return []


def _extract_best_odds(bookmakers: list[dict]) -> dict | None:
    """Extract best h2h odds from bookmakers list."""
    if not bookmakers:
        return None

    best = None
    for bm in bookmakers:
        for market in bm.get("markets", []):
            if market["key"] != "h2h":
                continue
            outcomes = {o["name"]: o["price"] for o in market.get("outcomes", [])}
            if not best or max(outcomes.values()) > max(best.values()):
                best = outcomes
    return best


async def _get_sport_casino(geo: str) -> Casino | None:
    """Get a casino that supports sports betting for the geo."""
    async with async_session() as session:
        result = await session.execute(
            select(Casino)
            .where(Casino.is_active.is_(True))
            .where(Casino.geo.any(geo))
            .limit(1)
        )
        return result.scalar_one_or_none()


async def _pick_exists(match_name: str, match_date: datetime) -> bool:
    """Check if a sport pick already exists for this match."""
    async with async_session() as session:
        result = await session.execute(
            select(SportPick.id)
            .where(SportPick.match_name == match_name)
            .where(SportPick.match_date == match_date)
        )
        return result.scalar_one_or_none() is not None


async def _generate_analysis(
    match_name: str, league: str, odds: dict, locale: str
) -> dict:
    """Use AI to generate analysis and pick for a match."""
    language, currency_symbol = get_locale_params(locale)
    prompt = load_prompt("sport_odds_analysis", language, currency_symbol)

    odds_str = ", ".join(f"{team}: {odd}" for team, odd in odds.items())
    user_message = (
        f"Match: {match_name}\n"
        f"League: {league}\n"
        f"Odds (h2h): {odds_str}\n"
    )

    try:
        result = await chat_json(prompt, user_message, language, currency_symbol, heavy=True)
        return result
    except Exception:
        logger.warning("AI sport analysis failed for %s", match_name, exc_info=True)
        return {}


async def fetch_and_save_picks() -> int:
    """Main function: fetch odds, generate analysis, save picks."""
    if not settings.odds_api_key:
        logger.info("ODDS_API_KEY not configured, skipping sport picks")
        return 0

    saved = 0

    for geo, league_keys in LEAGUES.items():
        # Determine locales and geos for this league group
        if geo == "GLOBAL":
            geos_for_pick = ["BR", "MX"]
        else:
            geos_for_pick = [geo]

        picks_this_geo = 0

        for sport_key in league_keys:
            if picks_this_geo >= MAX_PICKS_PER_GEO:
                break

            events = await _fetch_odds(sport_key)

            for event in events:
                if picks_this_geo >= MAX_PICKS_PER_GEO:
                    break

                match_date_str = event.get("commence_time")
                if not match_date_str:
                    continue

                match_date = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))

                # Only upcoming matches (next 3 days)
                if match_date < datetime.utcnow() or match_date > datetime.utcnow() + timedelta(days=3):
                    continue

                home = event.get("home_team", "")
                away = event.get("away_team", "")
                match_name = f"{home} vs {away}"
                league = event.get("sport_title", sport_key)

                # Skip if already exists
                if await _pick_exists(match_name, match_date):
                    continue

                odds = _extract_best_odds(event.get("bookmakers", []))
                if not odds:
                    continue

                # Generate AI analysis for each target geo
                for target_geo in geos_for_pick:
                    locale = "pt_BR" if target_geo == "BR" else "es_MX"
                    analysis = await _generate_analysis(match_name, league, odds, locale)

                    if not analysis.get("analysis") or not analysis.get("pick"):
                        continue

                    # Find best odds value for the recommended pick
                    pick_text = analysis["pick"]
                    best_odd = max(odds.values()) if odds else 1.5

                    casino = await _get_sport_casino(target_geo)

                    lang_suffix = "pt" if locale.startswith("pt") else "es"

                    async with async_session() as session:
                        pick = SportPick(
                            match_name=match_name,
                            league=league,
                            odds=best_odd,
                            match_date=match_date,
                            casino_id=casino.id if casino else None,
                            affiliate_link=casino.affiliate_link_template if casino else None,
                            geo=list(geos_for_pick) if geo == "GLOBAL" else [target_geo],
                        )
                        setattr(pick, f"pick_description_{lang_suffix}", pick_text)
                        setattr(pick, f"analysis_{lang_suffix}", analysis["analysis"])

                        session.add(pick)
                        await session.commit()
                        saved += 1
                        picks_this_geo += 1
                        logger.info(
                            "Saved sport pick: %s (%s) for %s",
                            match_name, league, target_geo,
                        )

                    # For GLOBAL leagues, generate both locales
                    if geo == "GLOBAL" and target_geo == "BR":
                        continue  # will do MX in next iteration
                    elif geo == "GLOBAL":
                        break  # done both

    return saved


# --- Celery task ---


async def _dispose_and_run(coro):
    from app.bot.bot import reset_bot
    reset_bot()
    await engine.dispose()
    return await coro


@celery.task(name="app.services.sport_odds_parser.task_fetch_sport_picks")
def task_fetch_sport_picks() -> None:
    count = asyncio.run(_dispose_and_run(fetch_and_save_picks()))
    logger.info("Fetched %d sport picks", count)
