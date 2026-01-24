#!/usr/bin/env python3
"""
Pokemon Go Raids Scraper Module

Handles scraping and parsing of raid boss data from leekduck.com
"""

import json
import logging
from typing import TYPE_CHECKING, Any

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

if TYPE_CHECKING:
    from scraper import LeekDuckScraper

logger = logging.getLogger(__name__)

# Constants for CP range parsing
EXPECTED_CP_PARTS = 2


async def scrape_raids(
    scraper: "LeekDuckScraper",
    base_url: str,
) -> list[dict[str, Any]]:
    """Scrape raid bosses data from leekduck.com"""
    logger.info("Scraping raids data...")

    cache_file = scraper.output_dir / "raids.json"
    if not scraper._should_fetch(cache_file):  # noqa: SLF001
        logger.info("Using cached raids data")
        with cache_file.open(encoding="utf-8") as f:
            return json.load(f)  # type: ignore[return-value]

    try:
        raids_url = f"{base_url}/boss/"
        response = await scraper.session.get(raids_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        bosses: list[dict[str, Any]] = []

        # Find raid bosses container
        raid_bosses = soup.find(class_="raid-bosses")
        if not raid_bosses:
            msg = "Could not find raid-bosses container"
            raise ValueError(msg)

        # Process each tier in regular raids
        tiers = raid_bosses.find_all(class_="tier")
        for tier_div in tiers:
            # Get tier name
            tier_header = tier_div.find("h2", class_="header")
            current_tier = (
                tier_header.get_text(strip=True) if tier_header else "Unknown"
            )

            # Process cards in this tier
            cards = tier_div.select(".grid .card")
            for card in cards:
                boss = _safe_parse_raid_boss(card, current_tier, base_url)
                if boss:
                    bosses.append(boss)

        # Find shadow raid bosses container
        shadow_raid_bosses = soup.find(class_="shadow-raid-bosses")
        if shadow_raid_bosses:
            # Process each tier in shadow raids
            shadow_tiers = shadow_raid_bosses.find_all(class_="tier")
            for tier_div in shadow_tiers:
                # Get tier name
                tier_header = tier_div.find("h2", class_="header")
                current_tier = (
                    tier_header.get_text(strip=True) if tier_header else "Unknown"
                )

                # Process cards in this tier
                cards = tier_div.select(".grid .card")
                for card in cards:
                    boss = _safe_parse_raid_boss(card, current_tier, base_url)
                    if boss:
                        bosses.append(boss)

        scraper._save_data(bosses, "raids.json")  # noqa: SLF001

    except (httpx.HTTPError, OSError, json.JSONDecodeError):
        logger.exception("Error scraping raids")
        return scraper._load_fallback_data("raids.json", [])  # type: ignore[return-value]  # noqa: SLF001

    return bosses


def _safe_parse_raid_boss(
    card: Tag, current_tier: str, base_url: str
) -> dict[str, Any] | None:
    """Safely parse individual raid boss card with error handling"""
    try:
        return parse_raid_boss(card, current_tier, base_url)
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing raid boss: %s", e)
        return None


def parse_raid_boss(
    card: Tag, current_tier: str, base_url: str
) -> dict[str, Any] | None:
    """Parse individual raid boss card"""
    try:
        # Extract all needed elements upfront
        name_elem = card.select_one(".identity .name")
        img_elem = card.select_one(".boss-img img")
        shiny_elem = card.select_one(".boss-img .shiny-icon")

        boss: dict[str, Any] = {
            "name": name_elem.get_text(strip=True) if name_elem else "",
            "tier": current_tier,
            "canBeShiny": bool(shiny_elem),
            "types": [],
            "combatPower": {
                "normal": {"min": -1, "max": -1},
                "boosted": {"min": -1, "max": -1},
            },
            "boostedWeather": [],
            "image": img_elem.get("src", "") if img_elem else "",
        }

        # Types
        type_imgs = card.select(".boss-type .type img")
        types: list[dict[str, str]] = []
        for img in type_imgs:
            type_name = img.get("title", "").lower()
            if type_name:
                img_url = img.get("src", "")
                if img_url and img_url[0] == "/":
                    img_url = base_url + img_url
                types.append({"name": type_name, "image": img_url})
        boss["types"] = types

        # Combat Power (normal)
        cp_elem = card.select_one(".cp-range")
        if cp_elem:
            cp_text = cp_elem.get_text().replace("CP", "").strip()
            cp_parts = cp_text.split("-")
            if len(cp_parts) == EXPECTED_CP_PARTS:
                try:
                    normal_cp = boss["combatPower"]
                    if isinstance(normal_cp, dict):
                        normal = normal_cp.get("normal")
                        if isinstance(normal, dict):
                            normal["min"] = int(cp_parts[0].strip())  # type: ignore[index]
                            normal["max"] = int(cp_parts[1].strip())  # type: ignore[index]
                except ValueError:
                    pass

        # Combat Power (boosted)
        boosted_elem = card.select_one(".boosted-cp-row .boosted-cp")
        if boosted_elem:
            boosted_text = boosted_elem.get_text().replace("CP", "").strip()
            boosted_parts = boosted_text.split("-")
            if len(boosted_parts) == EXPECTED_CP_PARTS:
                try:
                    boosted_cp = boss["combatPower"]
                    if isinstance(boosted_cp, dict):
                        boosted = boosted_cp.get("boosted")
                        if isinstance(boosted, dict):
                            boosted["min"] = int(
                                boosted_parts[0].strip()
                            )  # type: ignore[index]
                            boosted["max"] = int(
                                boosted_parts[1].strip()
                            )  # type: ignore[index]
                except ValueError:
                    pass

        # Boosted Weather
        weather_imgs = card.select(".weather-boosted .boss-weather .weather-pill img")
        boosted_weather: list[dict[str, str]] = []
        for img in weather_imgs:
            weather_name = img.get("alt", "").lower()
            if weather_name:
                img_url = img.get("src", "")
                if img_url and img_url[0] == "/":
                    img_url = base_url + img_url
                boosted_weather.append({"name": weather_name, "image": img_url})
        boss["boostedWeather"] = boosted_weather

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing raid boss card: %s", e)
        return None
    else:
        return boss
