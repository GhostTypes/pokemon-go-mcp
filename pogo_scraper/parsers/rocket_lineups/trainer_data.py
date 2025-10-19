"""
Handles parsing rocket lineup information
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional

logger = logging.getLogger(__name__)


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

        # Type (for grunts) - search in the entire profile, not just employee_info
        # because .type is a sibling of .employee-info
        type_img = profile.select_one('.type img')
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