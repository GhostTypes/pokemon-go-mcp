#!/usr/bin/env python3
"""
Pokemon Go Eggs Scraper Module

Handles scraping and parsing of egg hatch data from leekduck.com
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_eggs(scraper, base_url: str) -> List[Dict]:
    """Scrape egg hatch data from leekduck.com"""
    logger.info("Scraping eggs data...")

    cache_file = scraper.output_dir / "eggs.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached eggs data")
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            return json.load(f)

    try:
        eggs_url = f"{base_url}/eggs/"
        response = await scraper.session.get(eggs_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        eggs = []

        # Process egg sections
        page_content = soup.select_one('.page-content')
        if not page_content:
            raise ValueError("Could not find page content")

        current_type = ""
        current_adventure_sync = False
        current_gift_exchange = False

        # Find all h2 headers and their following egg-grid containers
        headers = page_content.find_all('h2')
        for header in headers:
            egg_type_text = header.get_text(strip=True)

            # Parse egg type info
            current_adventure_sync = "(Adventure Sync Rewards)" in egg_type_text
            current_gift_exchange = "(From Route Gift)" in egg_type_text
            current_type = egg_type_text.split(" Eggs")[0]

            # Find the next egg-grid container after this header
            next_grid = header.find_next_sibling('ul', class_='egg-grid')
            if next_grid:
                # Process pokemon cards in this grid
                pokemon_cards = next_grid.select('li.pokemon-card')
                for card in pokemon_cards:
                    try:
                        egg = parse_egg_item(card, current_type, current_adventure_sync, current_gift_exchange)
                        if egg:
                            eggs.append(egg)
                    except Exception as e:
                        logger.warning(f"Error parsing egg item: {e}")
                        continue

        scraper._save_data(eggs, "eggs.json")
        return eggs

    except Exception as e:
        logger.error(f"Error scraping eggs: {e}")
        return scraper._load_fallback_data("eggs.json", [])


def parse_egg_item(item, egg_type: str, is_adventure_sync: bool, is_gift_exchange: bool) -> Optional[Dict]:
    """Parse individual egg item"""
    try:
        pokemon = {
            'name': '',
            'eggType': egg_type,
            'isAdventureSync': is_adventure_sync,
            'image': '',
            'canBeShiny': False,
            'combatPower': -1,  # Single CP value instead of range
            'isRegional': False,
            'isGiftExchange': is_gift_exchange
        }

        # Name
        name_elem = item.select_one('span.name')
        pokemon['name'] = name_elem.get_text(strip=True) if name_elem else ""

        # Image
        img_elem = item.select_one('img')
        pokemon['image'] = img_elem.get('src', '') if img_elem else ""

        # Shiny
        pokemon['canBeShiny'] = bool(item.select_one('.shiny-icon'))

        # Regional
        pokemon['isRegional'] = bool(item.select_one('.regional-icon'))

        # Combat Power - Updated to correctly parse single CP values
        cp_elem = item.select_one('.cp-range')
        if cp_elem:
            # Get the text content and extract the CP value
            cp_text = cp_elem.get_text(strip=True)
            # The text is like "CP637", so we need to find where the number starts
            if cp_text.startswith('CP'):
                cp_value_str = cp_text[2:]  # Remove "CP" prefix
                try:
                    cp_value = int(cp_value_str)
                    # Store as single value
                    pokemon['combatPower'] = cp_value
                except ValueError:
                    pass  # Keep default -1 value if parsing fails

        return pokemon if pokemon['name'] else None

    except Exception as e:
        logger.warning(f"Error parsing egg item: {e}")
        return None