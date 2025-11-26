#!/usr/bin/env python3
"""
Pokemon Go Eggs Scraper Module

Handles scraping and parsing of egg hatch data from leekduck.com
"""

import json
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
        current_route_gift = False

        # Find all h2 headers and their following egg-grid containers
        headers = page_content.find_all('h2')
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
            next_grid = header.find_next_sibling('ul', class_='egg-grid')
            if next_grid:
                # Process pokemon cards in this grid
                pokemon_cards = next_grid.select('li.pokemon-card')
                for card in pokemon_cards:
                    try:
                        egg = parse_egg_item(card, current_type, current_adventure_sync, current_gift_exchange, current_route_gift)
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


def parse_egg_item(item, egg_type: str, is_adventure_sync: bool, is_gift_exchange: bool, is_route_gift: bool = False) -> Optional[Dict]:
    """Parse individual egg item"""
    try:
        # Extract all elements upfront
        name_elem = item.select_one('span.name')
        name = name_elem.get_text(strip=True) if name_elem else ""

        if not name:
            return None

        img_elem = item.select_one('img')
        shiny_elem = item.select_one('.shiny-icon')
        regional_elem = item.select_one('.regional-icon')

        pokemon = {
            'name': name,
            'eggType': egg_type,
            'isAdventureSync': is_adventure_sync,
            'image': img_elem.get('src', '') if img_elem else "",
            'canBeShiny': bool(shiny_elem),
            'combatPower': -1,
            'isRegional': bool(regional_elem),
            'isGiftExchange': is_gift_exchange,
            'isRouteGift': is_route_gift,
            'rarity': 1
        }

        # Rarity - Count the number of mini-egg icons
        rarity_elem = item.select_one('.rarity')
        if rarity_elem:
            mini_eggs = rarity_elem.select('svg.mini-egg')
            pokemon['rarity'] = len(mini_eggs)

        # Combat Power - parse single CP value
        cp_elem = item.select_one('.cp-range')
        if cp_elem:
            cp_text = cp_elem.get_text(strip=True)
            if cp_text.startswith('CP'):
                try:
                    pokemon['combatPower'] = int(cp_text[2:])
                except ValueError:
                    pass

        return pokemon

    except Exception as e:
        logger.warning(f"Error parsing egg item: {e}")
        return None