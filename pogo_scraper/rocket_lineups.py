#!/usr/bin/env python3
"""
Pokemon Go Team Rocket Lineups Scraper Module

Handles scraping and parsing of Team Rocket lineup data from leekduck.com
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

try:
    # Relative imports for when this module is imported as part of the package
    from .parsers.rocket_lineups.trainer_data import (
        parse_rocket_trainer,
        parse_shadow_pokemon,
    )
except ImportError:
    # Absolute imports for when running as a standalone script
    from parsers.rocket_lineups.trainer_data import (
        parse_rocket_trainer,
        parse_shadow_pokemon,  # noqa: F401
    )


async def scrape_rocket_lineups(
    scraper: "LeekDuckScraper", base_url: str
) -> list[dict[str, Any]]:
    """Scrape Team Rocket lineups data from leekduck.com"""
    logger.info("Scraping Team Rocket lineups data...")

    cache_file = scraper.output_dir / "rocket-lineups.json"
    if not scraper._should_fetch(cache_file):  # noqa: SLF001
        logger.info("Using cached rocket lineups data")
        with cache_file.open(encoding="utf-8") as f:
            return json.load(f)  # type: ignore[return-value]

    try:
        rocket_url = f"{base_url}/rocket-lineups/"
        response = await scraper.session.get(rocket_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        rocket_trainers = []

        # Find all rocket profiles
        rocket_profiles = soup.select(".rocket-profile")
        for profile in rocket_profiles:
            trainer = _safe_parse_rocket_trainer(profile, base_url)
            if trainer:
                rocket_trainers.append(trainer)

        scraper._save_data(rocket_trainers, "rocket-lineups.json")  # noqa: SLF001

    except (httpx.HTTPError, OSError, json.JSONDecodeError):
        logger.exception("Error scraping rocket lineups")
        return scraper._load_fallback_data("rocket-lineups.json", [])  # type: ignore[return-value]  # noqa: SLF001

    return rocket_trainers


def _safe_parse_rocket_trainer(profile: Tag, base_url: str) -> dict[str, Any] | None:
    """Safely parse individual rocket trainer with error handling"""
    try:
        return parse_rocket_trainer(profile, base_url)
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing rocket trainer: %s", e)
        return None
