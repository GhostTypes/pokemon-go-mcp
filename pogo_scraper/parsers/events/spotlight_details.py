"""
Handles parsing extra event information for spotlight hours
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict

logger = logging.getLogger(__name__)


async def parse_spotlight_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse Pokemon Spotlight Hour specific details"""
    try:
        spotlight_data = {
            'name': '',
            'canBeShiny': False,
            'image': '',
            'bonus': '',
            'list': []
        }

        # Find the first .pkmn-list-flex container (main spotlight Pokemon)
        pkmn_list_containers = soup.select('.pkmn-list-flex')
        if not pkmn_list_containers:
            logger.warning("No .pkmn-list-flex containers found for spotlight parsing")
            return

        first_container = pkmn_list_containers[0]
        main_pokemon_item = first_container.select_one(':scope > .pkmn-list-item')

        if main_pokemon_item:
            # Main spotlight Pokemon
            name_elem = main_pokemon_item.select_one(':scope > .pkmn-name')
            spotlight_data['name'] = name_elem.get_text(strip=True) if name_elem else ""

            # Check for shiny icon
            spotlight_data['canBeShiny'] = bool(main_pokemon_item.select_one(':scope > .shiny-icon'))

            # Image
            img_elem = main_pokemon_item.select_one(':scope > .pkmn-list-img > img')
            spotlight_data['image'] = img_elem.get('src', '') if img_elem else ""

        # Extract bonus from event description
        event_descriptions = soup.select('.event-description')
        if event_descriptions:
            description_html = str(event_descriptions[0])
            # Look for text in <strong> tags (bonus information)
            strong_parts = description_html.split('<strong>')
            if len(strong_parts) > 1:
                last_strong = strong_parts[-1].split('</strong>')
                if last_strong:
                    # Clean up HTML tags and get plain text
                    bonus_text = BeautifulSoup(last_strong[0], 'html.parser').get_text(strip=True)
                    spotlight_data['bonus'] = bonus_text

        # Get all Pokemon items (spotlight rotation list)
        all_pokemon_items = soup.select('.pkmn-list-item')
        for pokemon_item in all_pokemon_items:
            name_elem = pokemon_item.select_one(':scope > .pkmn-name')
            if name_elem:
                pokemon_data = {
                    'name': name_elem.get_text(strip=True),
                    'canBeShiny': bool(pokemon_item.select_one(':scope > .shiny-icon')),
                    'image': ''
                }

                img_elem = pokemon_item.select_one(':scope > .pkmn-list-img > img')
                if img_elem:
                    pokemon_data['image'] = img_elem.get('src', '')

                spotlight_data['list'].append(pokemon_data)

        # Only add spotlight data if we found meaningful content
        if spotlight_data['name'] or spotlight_data['list']:
            event['extraData']['spotlight'] = spotlight_data

    except Exception as e:
        logger.warning(f"Error parsing Spotlight Hour details: {e}")