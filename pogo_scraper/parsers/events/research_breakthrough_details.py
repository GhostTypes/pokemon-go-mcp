"""
Handles parsing extra event information for research breakthrough
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict

logger = logging.getLogger(__name__)



async def parse_breakthrough_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse Research Breakthrough specific details"""
    try:
        breakthrough_data = {
            'name': '',
            'canBeShiny': False,
            'image': '',
            'list': []
        }

        # Find the first .pkmn-list-flex container (main breakthrough reward)
        pkmn_list_containers = soup.select('.pkmn-list-flex')
        if not pkmn_list_containers:
            logger.warning("No .pkmn-list-flex containers found for breakthrough parsing")
            return

        first_container = pkmn_list_containers[0]
        main_pokemon_item = first_container.select_one(':scope > .pkmn-list-item')

        if main_pokemon_item:
            # Main breakthrough reward Pokemon
            name_elem = main_pokemon_item.select_one(':scope > .pkmn-name')
            breakthrough_data['name'] = name_elem.get_text(strip=True) if name_elem else ""

            # Check for shiny icon
            breakthrough_data['canBeShiny'] = bool(main_pokemon_item.select_one(':scope > .shiny-icon'))

            # Image
            img_elem = main_pokemon_item.select_one(':scope > .pkmn-list-img > img')
            breakthrough_data['image'] = img_elem.get('src', '') if img_elem else ""

        # Get all Pokemon items (possible breakthrough rewards)
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

                breakthrough_data['list'].append(pokemon_data)

        # Only add breakthrough data if we found meaningful content
        if breakthrough_data['name'] or breakthrough_data['list']:
            event['extraData']['breakthrough'] = breakthrough_data

    except Exception as e:
        logger.warning(f"Error parsing Research Breakthrough details: {e}")