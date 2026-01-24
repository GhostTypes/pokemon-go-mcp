#!/usr/bin/env python3
"""
Pokemon Go Team Rocket Lineups Scraper Module

Handles scraping and parsing of Team Rocket lineup data from leekduck.com
"""

import json
import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    # Relative imports for when this module is imported as part of the package
    from .parsers.rocket_lineups.trainer_data import (
        parse_lineup_slot,
        parse_rocket_trainer,
        parse_shadow_pokemon,
    )
    from .parsers.rocket_lineups.weakness_data import calculate_weakness_effectiveness
except ImportError:
    # Absolute imports for when running as a standalone script
    from parsers.rocket_lineups.trainer_data import (
        parse_rocket_trainer,
    )


async def scrape_rocket_lineups(
    scraper: "LeekDuckScraper", base_url: str
) -> list[dict]:
    """Scrape Team Rocket lineups data from leekduck.com"""
    logger.info("Scraping Team Rocket lineups data...")

    cache_file = scraper.output_dir / "rocket-lineups.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached rocket lineups data")
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)

    try:
        rocket_url = f"{base_url}/rocket-lineups/"
        response = await scraper.session.get(rocket_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        rocket_trainers = []

        # Find all rocket profiles
        rocket_profiles = soup.select(".rocket-profile")
        for profile in rocket_profiles:
            try:
                trainer = parse_rocket_trainer(profile, base_url)
                if trainer:
                    rocket_trainers.append(trainer)
            except (AttributeError, KeyError, ValueError, TypeError) as e:
                logger.warning("Error parsing rocket trainer: %s", e)
                continue

        scraper._save_data(rocket_trainers, "rocket-lineups.json")
        return rocket_trainers

    except (httpx.HTTPError, OSError, json.JSONDecodeError) as e:
        logger.exception("Error scraping rocket lineups: %s", e)
        return scraper._load_fallback_data("rocket-lineups.json", [])
