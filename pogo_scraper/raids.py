#!/usr/bin/env python3
"""
Pokemon Go Raids Scraper Module

Handles scraping and parsing of raid boss data from leekduck.com
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_raids(scraper, base_url: str) -> List[Dict]:
    """Scrape raid bosses data from leekduck.com"""
    logger.info("Scraping raids data...")

    cache_file = scraper.output_dir / "raids.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached raids data")
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            return json.load(f)

    try:
        raids_url = f"{base_url}/boss/"
        response = await scraper.session.get(raids_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        bosses = []

        # Find raid bosses container
        raid_bosses = soup.find(class_='raid-bosses')
        if not raid_bosses:
            raise ValueError("Could not find raid-bosses container")

        # Process each tier
        tiers = raid_bosses.find_all(class_='tier')
        for tier_div in tiers:
            # Get tier name
            tier_header = tier_div.find('h2', class_='header')
            current_tier = tier_header.get_text(strip=True) if tier_header else "Unknown"

            # Process cards in this tier
            cards = tier_div.select('.grid .card')
            for card in cards:
                try:
                    boss = parse_raid_boss(card, current_tier, base_url)
                    if boss:
                        bosses.append(boss)
                except Exception as e:
                    logger.warning(f"Error parsing raid boss: {e}")
                    continue

        scraper._save_data(bosses, "raids.json")
        return bosses

    except Exception as e:
        logger.error(f"Error scraping raids: {e}")
        return scraper._load_fallback_data("raids.json", [])


def parse_raid_boss(card, current_tier: str, base_url: str) -> Optional[Dict]:
    """Parse individual raid boss card"""
    try:
        boss = {
            'name': '',
            'tier': current_tier,
            'canBeShiny': False,
            'types': [],
            'combatPower': {
                'normal': {'min': -1, 'max': -1},
                'boosted': {'min': -1, 'max': -1}
            },
            'boostedWeather': [],
            'image': ''
        }

        # Name
        name_elem = card.select_one('.identity .name')
        boss['name'] = name_elem.get_text(strip=True) if name_elem else ""

        # Image
        img_elem = card.select_one('.boss-img img')
        boss['image'] = img_elem.get('src', '') if img_elem else ""

        # Shiny
        boss['canBeShiny'] = bool(card.select_one('.boss-img .shiny-icon'))

        # Types
        type_imgs = card.select('.boss-type .type img')
        for img in type_imgs:
            type_name = img.get('title', '').lower()
            if type_name:
                # Get the image URL and prepend base URL if it's a relative path
                img_url = img.get('src', '')
                if img_url.startswith('/'):
                    img_url = f"{base_url}{img_url}"
                boss['types'].append({
                    'name': type_name,
                    'image': img_url
                })

        # Combat Power (normal)
        cp_elem = card.select_one('.cp-range')
        if cp_elem:
            cp_text = cp_elem.get_text().replace('CP', '').strip()
            cp_parts = cp_text.split('-')
            if len(cp_parts) == 2:
                try:
                    boss['combatPower']['normal']['min'] = int(cp_parts[0].strip())
                    boss['combatPower']['normal']['max'] = int(cp_parts[1].strip())
                except ValueError:
                    pass

        # Combat Power (boosted)
        boosted_elem = card.select_one('.boosted-cp-row .boosted-cp')
        if boosted_elem:
            boosted_text = boosted_elem.get_text().replace('CP', '').strip()
            boosted_parts = boosted_text.split('-')
            if len(boosted_parts) == 2:
                try:
                    boss['combatPower']['boosted']['min'] = int(boosted_parts[0].strip())
                    boss['combatPower']['boosted']['max'] = int(boosted_parts[1].strip())
                except ValueError:
                    pass

        # Boosted Weather
        weather_imgs = card.select('.weather-boosted .boss-weather .weather-pill img')
        for img in weather_imgs:
            weather_name = img.get('alt', '').lower()
            if weather_name:
                # Get the image URL and prepend base URL if it's a relative path
                img_url = img.get('src', '')
                if img_url.startswith('/'):
                    img_url = f"{base_url}{img_url}"
                boss['boostedWeather'].append({
                    'name': weather_name,
                    'image': img_url
                })

        return boss

    except Exception as e:
        logger.warning(f"Error parsing raid boss card: {e}")
        return None