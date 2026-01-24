#!/usr/bin/env python3
"""
Pokemon Go Eggs Scraper Module

Handles scraping and parsing of egg hatch data from leekduck.com
"""

import contextlib
import json
import logging
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup
from bs4.element import Tag

if TYPE_CHECKING:
    from scraper import LeekDuckScraper

logger = logging.getLogger(__name__)


async def scrape_eggs(
    scraper: "LeekDuckScraper",
    base_url: str,
) -> list[dict[str, Any]]:
    """Scrape egg hatch data from leekduck.com"""
    logger.info("Scraping eggs data...")

    cache_file = scraper.output_dir / "eggs.json"
    if not scraper._should_fetch(cache_file):  # noqa: SLF001
        logger.info("Using cached eggs data")
        with cache_file.open(encoding="utf-8") as f:
            return json.load(f)  # type: ignore[return-value]

    try:
        eggs_url = f"{base_url}/eggs/"
        response = await scraper.session.get(eggs_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
    except Exception:
        logger.exception("Error scraping eggs")
        return scraper._load_fallback_data("eggs.json", [])  # type: ignore[return-value]  # noqa: SLF001

    eggs: list[dict[str, Any]] = []

    # Process egg sections
    page_content = soup.select_one(".page-content")
    if not page_content:
        msg = "Could not find page content"
        raise ValueError(msg)

    current_type = ""
    current_adventure_sync = False
    current_gift_exchange = False
    current_route_gift = False

    # Find all h2 headers and their following egg-grid containers
    headers = page_content.find_all("h2")
    for header in headers:
        egg_type_text = header.get_text(strip=True)

        # Parse egg type info
        current_adventure_sync = "(Adventure Sync Rewards)" in egg_type_text
        current_gift_exchange = "(From Gift)" in egg_type_text
        current_route_gift = "(From Route Gift)" in egg_type_text
        current_type = egg_type_text.split(" Eggs")[0]
        if "(From" in current_type:
            current_type = current_type.split(" (From")[0]

        # Find the next egg-grid container after this header
        next_grid = header.find_next_sibling("ul", class_="egg-grid")
        if next_grid:
            # Process pokemon cards in this grid
            pokemon_cards = next_grid.select("li.pokemon-card")
            for card in pokemon_cards:
                egg = _safe_parse_egg_item(
                    card,
                    current_type,
                    is_adventure_sync=current_adventure_sync,
                    is_gift_exchange=current_gift_exchange,
                    is_route_gift=current_route_gift,
                )
                if egg:
                    eggs.append(egg)

    scraper._save_data(eggs, "eggs.json")  # noqa: SLF001

    return eggs


def _safe_parse_egg_item(
    item: Tag,
    egg_type: str,
    *,
    is_adventure_sync: bool = False,
    is_gift_exchange: bool = False,
    is_route_gift: bool = False,
) -> dict[str, Any] | None:
    """Safely parse individual egg item with error handling"""
    try:
        return parse_egg_item(
            item,
            egg_type,
            is_adventure_sync=is_adventure_sync,
            is_gift_exchange=is_gift_exchange,
            is_route_gift=is_route_gift,
        )
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing egg item: %s", e)
        return None


def parse_egg_item(
    item: Tag,
    egg_type: str,
    *,
    is_adventure_sync: bool = False,
    is_gift_exchange: bool = False,
    is_route_gift: bool = False,
) -> dict[str, Any] | None:
    """Parse individual egg item"""
    try:
        # Extract all elements upfront
        name_elem = item.select_one("span.name")
        name = name_elem.get_text(strip=True) if name_elem else ""

        if not name:
            return None

        img_elem = item.select_one("img")
        shiny_elem = item.select_one(".shiny-icon")
        regional_elem = item.select_one(".regional-icon")

        pokemon: dict[str, Any] = {
            "name": name,
            "eggType": egg_type,
            "isAdventureSync": is_adventure_sync,
            "image": img_elem.get("src", "") if img_elem else "",
            "canBeShiny": bool(shiny_elem),
            "combatPower": -1,
            "isRegional": bool(regional_elem),
            "isGiftExchange": is_gift_exchange,
            "isRouteGift": is_route_gift,
            "rarity": 1,
        }

        # Rarity - Count the number of mini-egg icons
        rarity_elem = item.select_one(".rarity")
        if rarity_elem:
            mini_eggs = rarity_elem.select("svg.mini-egg")
            pokemon["rarity"] = len(mini_eggs)

        # Combat Power - parse single CP value
        cp_elem = item.select_one(".cp-range")
        if cp_elem:
            cp_text = cp_elem.get_text(strip=True)
            if cp_text.startswith("CP"):
                with contextlib.suppress(ValueError):
                    pokemon["combatPower"] = int(cp_text[2:])

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing egg item: %s", e)
        return None
    else:
        return pokemon
