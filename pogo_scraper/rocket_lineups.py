#!/usr/bin/env python3
"""
Pokemon Go Team Rocket Lineups Scraper Module

Handles scraping and parsing of Team Rocket lineup data from leekduck.com
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


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


def parse_rocket_trainer(profile, base_url: str) -> Optional[Dict]:
    """Parse individual rocket trainer profile"""
    try:
        trainer = {
            'name': '',
            'title': '',
            'quote': '',
            'image': '',
            'type': None,  # For grunt types
            'lineups': []
        }

        # Get trainer info
        employee_info = profile.select_one('.employee-info')
        if not employee_info:
            return None

        # Name
        name_elem = employee_info.select_one('.name')
        trainer['name'] = name_elem.get_text(strip=True) if name_elem else ""

        # Title
        title_elem = employee_info.select_one('.title')
        trainer['title'] = title_elem.get_text(strip=True) if title_elem else ""

        # Quote
        quote_text_elem = employee_info.select_one('.quote-text')
        trainer['quote'] = quote_text_elem.get_text(strip=True) if quote_text_elem else ""

        # Image
        photo_img = employee_info.select_one('.photo img')
        if photo_img:
            trainer['image'] = photo_img.get('src', '')
            # Convert relative URLs to absolute
            if trainer['image'].startswith('/'):
                trainer['image'] = f"{base_url}{trainer['image']}"

        # Type (for grunts)
        type_img = employee_info.select_one('.type img')
        if type_img:
            type_src = type_img.get('src', '')
            # Extract type name from image path (e.g., "/assets/img/type_symbols/normal.png" -> "normal")
            if type_src:
                type_name = type_src.split('/')[-1].split('.')[0]
                trainer['type'] = type_name

        # Parse lineup slots
        lineup_info = profile.select_one('.lineup-info')
        if lineup_info:
            slots = lineup_info.select('.slot')
            for slot in slots:
                slot_data = parse_lineup_slot(slot)
                if slot_data:
                    trainer['lineups'].append(slot_data)

        return trainer if trainer['name'] else None

    except Exception as e:
        logger.warning(f"Error parsing rocket trainer profile: {e}")
        return None


def parse_lineup_slot(slot) -> Optional[Dict]:
    """Parse individual lineup slot with Pokemon options"""
    try:
        slot_data = {
            'slot': 0,
            'is_encounter': False,
            'pokemon': []
        }

        # Get slot number
        number_elem = slot.select_one('.number')
        if number_elem:
            try:
                slot_data['slot'] = int(number_elem.get_text(strip=True))
            except ValueError:
                pass

        # Check if this is an encounter slot (reward Pokemon)
        slot_data['is_encounter'] = bool(slot.select_one('.encounter-icon'))

        # Get all Pokemon in this slot
        shadow_pokemon = slot.select('.shadow-pokemon')
        for pokemon_elem in shadow_pokemon:
            pokemon = parse_shadow_pokemon(pokemon_elem)
            if pokemon:
                slot_data['pokemon'].append(pokemon)

        return slot_data if slot_data['pokemon'] else None

    except Exception as e:
        logger.warning(f"Error parsing lineup slot: {e}")
        return None


def parse_shadow_pokemon(pokemon_elem) -> Optional[Dict]:
    """Parse individual shadow Pokemon with weakness data"""
    try:
        pokemon = {
            'name': '',
            'types': [],
            'weaknesses': {
                'double': [],
                'single': []
            },
            'image': '',
            'can_be_shiny': False
        }

        # Name
        pokemon['name'] = pokemon_elem.get('data-pokemon', '').strip()

        # Types
        type1 = pokemon_elem.get('data-type1', '').strip().lower()
        type2 = pokemon_elem.get('data-type2', '').strip().lower()

        if type1 and type1 != 'none':
            pokemon['types'].append(type1)
        if type2 and type2 != 'none':
            pokemon['types'].append(type2)

        # Weaknesses
        double_weaknesses = pokemon_elem.get('data-double-weaknesses', '').strip()
        single_weaknesses = pokemon_elem.get('data-single-weaknesses', '').strip()

        if double_weaknesses:
            pokemon['weaknesses']['double'] = [w.strip().lower() for w in double_weaknesses.split(',') if w.strip()]

        if single_weaknesses:
            pokemon['weaknesses']['single'] = [w.strip().lower() for w in single_weaknesses.split(',') if w.strip()]

        # Image
        img_elem = pokemon_elem.select_one('.pokemon-image')
        pokemon['image'] = img_elem.get('src', '') if img_elem else ""

        # Shiny availability
        pokemon['can_be_shiny'] = bool(pokemon_elem.select_one('.shiny-icon'))

        return pokemon if pokemon['name'] else None

    except Exception as e:
        logger.warning(f"Error parsing shadow Pokemon: {e}")
        return None


def calculate_weakness_effectiveness(attacking_type: str, defending_types: List[str]) -> float:
    """
    Calculate type effectiveness multiplier based on Pokemon type chart
    Returns: 2.0 for super effective, 1.0 for normal, 0.5 for not very effective, 0.0 for no effect
    """
    # Pokemon Go type effectiveness chart
    TYPE_CHART = {
        'normal': {
            'weak_to': ['fighting'],
            'resists': [],
            'immune_to': ['ghost']
        },
        'fire': {
            'weak_to': ['water', 'ground', 'rock'],
            'resists': ['fire', 'grass', 'ice', 'bug', 'steel', 'fairy'],
            'immune_to': []
        },
        'water': {
            'weak_to': ['grass', 'electric'],
            'resists': ['fire', 'water', 'ice', 'steel'],
            'immune_to': []
        },
        'grass': {
            'weak_to': ['fire', 'ice', 'poison', 'flying', 'bug'],
            'resists': ['water', 'electric', 'grass', 'ground'],
            'immune_to': []
        },
        'electric': {
            'weak_to': ['ground'],
            'resists': ['flying', 'steel', 'electric'],
            'immune_to': []
        },
        'ice': {
            'weak_to': ['fire', 'fighting', 'rock', 'steel'],
            'resists': ['ice'],
            'immune_to': []
        },
        'fighting': {
            'weak_to': ['flying', 'psychic', 'fairy'],
            'resists': ['rock', 'bug', 'dark'],
            'immune_to': []
        },
        'poison': {
            'weak_to': ['ground', 'psychic'],
            'resists': ['grass', 'fighting', 'poison', 'bug', 'fairy'],
            'immune_to': []
        },
        'ground': {
            'weak_to': ['water', 'grass', 'ice'],
            'resists': ['poison', 'rock'],
            'immune_to': ['electric']
        },
        'flying': {
            'weak_to': ['electric', 'ice', 'rock'],
            'resists': ['grass', 'fighting', 'bug'],
            'immune_to': ['ground']
        },
        'psychic': {
            'weak_to': ['bug', 'ghost', 'dark'],
            'resists': ['fighting', 'psychic'],
            'immune_to': []
        },
        'bug': {
            'weak_to': ['fire', 'flying', 'rock'],
            'resists': ['grass', 'fighting', 'ground'],
            'immune_to': []
        },
        'rock': {
            'weak_to': ['water', 'grass', 'fighting', 'ground', 'steel'],
            'resists': ['normal', 'fire', 'poison', 'flying'],
            'immune_to': []
        },
        'ghost': {
            'weak_to': ['ghost', 'dark'],
            'resists': ['poison', 'bug'],
            'immune_to': ['normal', 'fighting']
        },
        'dragon': {
            'weak_to': ['ice', 'dragon', 'fairy'],
            'resists': ['fire', 'water', 'electric', 'grass'],
            'immune_to': []
        },
        'dark': {
            'weak_to': ['fighting', 'bug', 'fairy'],
            'resists': ['ghost', 'dark'],
            'immune_to': ['psychic']
        },
        'steel': {
            'weak_to': ['fire', 'fighting', 'ground'],
            'resists': ['normal', 'grass', 'ice', 'flying', 'psychic', 'bug', 'rock', 'dragon', 'steel', 'fairy'],
            'immune_to': ['poison']
        },
        'fairy': {
            'weak_to': ['poison', 'steel'],
            'resists': ['fighting', 'bug', 'dark'],
            'immune_to': ['dragon']
        }
    }

    attacking_type = attacking_type.lower()
    effectiveness = 1.0

    for defending_type in defending_types:
        defending_type = defending_type.lower()

        if defending_type not in TYPE_CHART:
            continue

        type_data = TYPE_CHART[defending_type]

        # Check immunities (0x damage)
        if attacking_type in type_data['immune_to']:
            return 0.0

        # Check weaknesses (2x damage)
        elif attacking_type in type_data['weak_to']:
            effectiveness *= 2.0

        # Check resistances (0.5x damage)
        elif attacking_type in type_data['resists']:
            effectiveness *= 0.5

    return effectiveness