#!/usr/bin/env python3
"""
Pokemon Go Team Rocket Lineups Scraper Module

Handles scraping and parsing of Team Rocket lineup data from leekduck.com
"""

import logging
from typing import Dict, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    # Relative imports for when this module is imported as part of the package
    from .parsers.rocket_lineups.trainer_data import parse_rocket_trainer, parse_lineup_slot, parse_shadow_pokemon
    from .parsers.rocket_lineups.weakness_data import calculate_weakness_effectiveness
except ImportError:
    # Absolute imports for when running as a standalone script
    from parsers.rocket_lineups.trainer_data import parse_rocket_trainer, parse_lineup_slot, parse_shadow_pokemon
    from parsers.rocket_lineups.weakness_data import calculate_weakness_effectiveness

async def scrape_rocket_lineups(scraper, base_url: str) -> List[Dict]:
    """Scrape Team Rocket lineups data from leekduck.com"""
    logger.info("Scraping Team Rocket lineups data...")

    cache_file = scraper.output_dir / "rocket-lineups.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached rocket lineups data")
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            return json.load(f)

    try:
        rocket_url = f"{base_url}/rocket-lineups/"
        response = await scraper.session.get(rocket_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        rocket_trainers = []

        # Find all rocket profiles
        rocket_profiles = soup.select('.rocket-profile')
        for profile in rocket_profiles:
            try:
                trainer = parse_rocket_trainer(profile, base_url)
                if trainer:
                    rocket_trainers.append(trainer)
            except Exception as e:
                logger.warning(f"Error parsing rocket trainer: {e}")
                continue

        scraper._save_data(rocket_trainers, "rocket-lineups.json")
        return rocket_trainers

    except Exception as e:
        logger.error(f"Error scraping rocket lineups: {e}")
        return scraper._load_fallback_data("rocket-lineups.json", [])
