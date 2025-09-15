"""
Handles parsing generic event details for events that don't have specific parsers
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


async def parse_generic_event_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse generic event details from event pages

    This extracts spawns, bonuses, features, and field research tasks
    from standard event pages that don't have specific parsers.

    Args:
        soup: BeautifulSoup object of the event page
        event: Event dictionary to update with extracted data
    """
    try:
        logger.debug(f"Parsing generic event details for: {event['name']}")

        # Initialize generic data structure
        generic_data = {
            'hasSpawns': False,
            'hasFieldResearchTasks': False,
            'spawns': [],
            'bonuses': [],
            'features': [],
            'fieldResearch': [],
            'raids': []
        }

        # Update existing generic data with new structure
        if 'generic' in event['extraData']:
            existing_generic = event['extraData']['generic']
            generic_data['hasSpawns'] = existing_generic.get('hasSpawns', False)
            generic_data['hasFieldResearchTasks'] = existing_generic.get('hasFieldResearchTasks', False)

        # Parse spawns section
        spawns_section = soup.find('h2', id='spawns')
        if spawns_section:
            generic_data['hasSpawns'] = True
            spawns_data = _parse_spawns_section(soup, spawns_section)
            generic_data['spawns'] = spawns_data
            logger.debug(f"Found {len(spawns_data)} spawn entries")

        # Parse bonuses section
        bonuses_section = soup.find('h2', id='bonuses')
        if bonuses_section:
            bonuses_data = _parse_bonuses_section(soup, bonuses_section)
            generic_data['bonuses'] = bonuses_data
            logger.debug(f"Found {len(bonuses_data)} bonus entries")

        # Parse features section - look for various possible feature sections
        features_section = soup.find('h2', id='features')
        if not features_section:
            # Look for "Featured Pokémon" or similar headings
            for heading in soup.find_all(['h2', 'h3']):
                heading_text = heading.get_text(strip=True).lower()
                if any(keyword in heading_text for keyword in ['featured', 'feature', 'spotlight']):
                    features_section = heading
                    break

        if features_section:
            features_data = _parse_features_section(soup, features_section)
            generic_data['features'] = features_data
            logger.debug(f"Found {len(features_data)} feature entries")

        # Parse field research section
        research_section = soup.find('h2', id='field-research-tasks')
        if research_section:
            generic_data['hasFieldResearchTasks'] = True
            research_data = _parse_field_research_section(soup, research_section)
            generic_data['fieldResearch'] = research_data
            logger.debug(f"Found {len(research_data)} field research entries")

        # Parse raids section (if present)
        raids_section = soup.find('h2', id='raids')
        if raids_section:
            raids_data = _parse_raids_section(soup, raids_section)
            generic_data['raids'] = raids_data
            logger.debug(f"Found {len(raids_data)} raid entries")

        # Update event with generic data
        event['extraData']['generic'] = generic_data

        logger.debug(f"Successfully parsed generic event data for: {event['name']}")

    except Exception as e:
        logger.warning(f"Error parsing generic event details for {event['name']}: {e}")
        # Keep the existing structure on error
        pass


def _parse_spawns_section(soup: BeautifulSoup, spawns_section) -> List[Dict]:
    """Parse the spawns section and extract Pokemon spawn data"""
    spawns = []

    try:
        # Find the container after the spawns header
        current = spawns_section.find_next_sibling()

        while current and current.name != 'h2':
            # Look for Pokemon lists - they can be in various container types
            pokemon_items = current.find_all(class_='pkmn-list-item') if current else []

            # Also check for simpler list structures
            if not pokemon_items:
                # Look for lists with Pokemon images
                pokemon_items = current.find_all('img', src=lambda x: x and 'pokemon_icons' in x) if current else []

                # Convert image tags to pseudo pkmn-list-item structure for consistent parsing
                pokemon_items = [img.find_parent() for img in pokemon_items if img.find_parent()]

            for item in pokemon_items:
                spawn = _extract_pokemon_data(item)
                if spawn and spawn not in spawns:  # Avoid duplicates
                    spawns.append(spawn)

            current = current.find_next_sibling()

    except Exception as e:
        logger.warning(f"Error parsing spawns section: {e}")

    return spawns


def _parse_bonuses_section(soup: BeautifulSoup, bonuses_section) -> List[Dict]:
    """Parse the bonuses section and extract bonus data"""
    bonuses = []

    try:
        # Find bonus items in the section
        current = bonuses_section.find_next_sibling()

        while current and current.name != 'h2':
            # Look for bonus items
            bonus_items = current.find_all(class_='bonus-item') if current else []

            # Also look for simpler list structures
            if not bonus_items and current:
                # Check for lists or divs containing bonus information
                if current.find_all('li'):
                    bonus_items = current.find_all('li')
                elif current.find_all('p'):
                    bonus_items = current.find_all('p')

            for item in bonus_items:
                bonus = _extract_bonus_data(item)
                if bonus:
                    bonuses.append(bonus)

            current = current.find_next_sibling()

    except Exception as e:
        logger.warning(f"Error parsing bonuses section: {e}")

    return bonuses


def _parse_features_section(soup: BeautifulSoup, features_section) -> List[Dict]:
    """Parse the features section and extract feature data"""
    features = []

    try:
        current = features_section.find_next_sibling()

        while current and (current.name != 'h2' or current.get('id') in ['featured-pokémon', 'pokémon-debut', 'pokemon-debut']):
            if current:
                # Look for Pokemon in features first (common in featured Pokemon sections)
                pokemon_items = current.find_all(class_='pkmn-list-item')

                # Also look in flex lists which are common for featured Pokemon
                if not pokemon_items:
                    pokemon_items = current.find_all('li', class_='pkmn-list-item')
                if not pokemon_items:
                    flex_lists = current.find_all('ul', class_='pkmn-list-flex')
                    for flex_list in flex_lists:
                        pokemon_items.extend(flex_list.find_all('li', class_='pkmn-list-item'))

                if pokemon_items:
                    # This is likely a featured Pokemon section
                    for item in pokemon_items:
                        pokemon_data = _extract_pokemon_data(item)
                        if pokemon_data:
                            # Mark as featured Pokemon
                            pokemon_data['type'] = 'featured_pokemon'
                            features.append(pokemon_data)
                else:
                    # Look for general feature items
                    feature_items = []

                    # Check for list items
                    if current.find_all('li'):
                        feature_items = current.find_all('li')
                    # Check for paragraph items
                    elif current.find_all('p'):
                        feature_items = current.find_all('p')
                    # Check for divs with content
                    elif current.find_all('div', class_=True):
                        feature_items = current.find_all('div', class_=True)

                    for item in feature_items:
                        feature = _extract_feature_data(item)
                        if feature:
                            features.append(feature)

            current = current.find_next_sibling()

    except Exception as e:
        logger.warning(f"Error parsing features section: {e}")

    return features


def _parse_field_research_section(soup: BeautifulSoup, research_section) -> List[Dict]:
    """Parse the field research section and extract research task data"""
    research_tasks = []

    try:
        current = research_section.find_next_sibling()

        while current and current.name != 'h2':
            if current:
                # Research tasks might be in various formats
                task_items = []

                # Look for LeekDuck's specific event field research list
                if current.find_all(class_='event-field-research-list'):
                    research_list = current.find(class_='event-field-research-list')
                    if research_list:
                        task_items = research_list.find_all('li')
                # Look for general research task items
                elif current.find_all(class_='research-task'):
                    task_items = current.find_all(class_='research-task')
                # Look for list items
                elif current.find_all('li'):
                    task_items = current.find_all('li')
                # Look for paragraphs
                elif current.find_all('p'):
                    task_items = current.find_all('p')

                for item in task_items:
                    task = _extract_research_task_data(item)
                    if task:
                        research_tasks.append(task)

            current = current.find_next_sibling()

    except Exception as e:
        logger.warning(f"Error parsing field research section: {e}")

    return research_tasks


def _parse_raids_section(soup: BeautifulSoup, raids_section) -> List[Dict]:
    """Parse the raids section and extract raid data"""
    raids = []

    try:
        current = raids_section.find_next_sibling()

        while current and current.name != 'h2':
            if current:
                # Look for raid Pokemon
                raid_items = current.find_all(class_='pkmn-list-item') if current else []

                # Also check for tier-specific sections
                tier_sections = current.find_all(['h3', 'h4']) if current else []
                for tier_section in tier_sections:
                    tier_name = tier_section.get_text(strip=True)
                    # Find Pokemon in this tier
                    tier_current = tier_section.find_next_sibling()
                    while tier_current and tier_current.name not in ['h2', 'h3', 'h4']:
                        tier_pokemon = tier_current.find_all(class_='pkmn-list-item') if tier_current else []
                        for pokemon in tier_pokemon:
                            raid_data = _extract_pokemon_data(pokemon)
                            if raid_data:
                                raid_data['tier'] = tier_name
                                raids.append(raid_data)
                        tier_current = tier_current.find_next_sibling()

                # Process general raid items
                for item in raid_items:
                    raid_data = _extract_pokemon_data(item)
                    if raid_data:
                        raids.append(raid_data)

            current = current.find_next_sibling()

    except Exception as e:
        logger.warning(f"Error parsing raids section: {e}")

    return raids


def _extract_pokemon_data(item) -> Optional[Dict]:
    """Extract Pokemon data from a list item or container"""
    try:
        pokemon_data = {}

        # Try to find Pokemon name
        name_elem = item.find(class_='pkmn-name')
        if not name_elem:
            # Fallback: look for text content or alt text
            img_elem = item.find('img')
            if img_elem and img_elem.get('alt'):
                pokemon_data['name'] = img_elem.get('alt').strip()
            else:
                # Use text content as fallback
                text = item.get_text(strip=True)
                if text and len(text) < 50:  # Reasonable name length
                    pokemon_data['name'] = text
        else:
            pokemon_data['name'] = name_elem.get_text(strip=True)

        # Try to find Pokemon image
        img_elem = item.find('img')
        if img_elem and img_elem.get('src'):
            image_src = img_elem.get('src')
            # Clean up image URL
            if 'cdn-cgi' in image_src:
                image_src = image_src.split('/cdn-cgi')[0]
            pokemon_data['image'] = image_src

        # Check for shiny indicator - look for shiny images or icons
        shiny_elem = item.find('img', src=lambda x: x and 'shiny' in x.lower()) if item else None
        shiny_icon = item.find('img', src=lambda x: x and 'icon_shiny' in x.lower()) if item else None
        shiny_class = item.find(class_=lambda x: x and 'shiny' in x.lower()) if item else None
        # Check for LeekDuck's specific shiny-icon class
        shiny_icon_class = item.find('img', class_='shiny-icon') if item else None

        if shiny_elem or shiny_icon or shiny_class or shiny_icon_class or (item and 'shiny' in item.get_text().lower()):
            pokemon_data['can_be_shiny'] = True
        else:
            pokemon_data['can_be_shiny'] = False

        # Only return if we have at least a name
        if pokemon_data.get('name'):
            return pokemon_data

    except Exception as e:
        logger.debug(f"Error extracting Pokemon data: {e}")

    return None


def _extract_bonus_data(item) -> Optional[Dict]:
    """Extract bonus data from a list item or container"""
    try:
        bonus_data = {}

        # Try to find bonus text
        text_elem = item.find(class_='bonus-text')
        if not text_elem:
            # Fallback to item text content
            text = item.get_text(strip=True)
            if text:
                bonus_data['text'] = text
        else:
            bonus_data['text'] = text_elem.get_text(strip=True)

        # Try to find bonus image
        img_elem = item.find('img')
        if img_elem and img_elem.get('src'):
            image_src = img_elem.get('src')
            if 'cdn-cgi' in image_src:
                image_src = image_src.split('/cdn-cgi')[0]
            bonus_data['image'] = image_src

        # Only return if we have text
        if bonus_data.get('text'):
            return bonus_data

    except Exception as e:
        logger.debug(f"Error extracting bonus data: {e}")

    return None


def _extract_feature_data(item) -> Optional[Dict]:
    """Extract feature data from a list item or container"""
    try:
        feature_data = {}

        # Extract text content
        text = item.get_text(strip=True)
        if text:
            feature_data['text'] = text

        # Try to find associated image
        img_elem = item.find('img')
        if img_elem and img_elem.get('src'):
            image_src = img_elem.get('src')
            if 'cdn-cgi' in image_src:
                image_src = image_src.split('/cdn-cgi')[0]
            feature_data['image'] = image_src

        # Only return if we have text
        if feature_data.get('text'):
            return feature_data

    except Exception as e:
        logger.debug(f"Error extracting feature data: {e}")

    return None


def _extract_research_task_data(item) -> Optional[Dict]:
    """Extract research task data from a list item or container"""
    try:
        task_data = {}

        # Check if this is LeekDuck's event field research structure
        task_elem = item.find(class_='task')
        reward_list = item.find(class_='reward-list')

        if task_elem and reward_list:
            # This is LeekDuck's structured format
            task_text = task_elem.get_text(strip=True).replace('???', '').strip()
            if not task_text:
                task_data['text'] = "Research task (details TBD)"
            else:
                task_data['text'] = task_text

            # Extract reward Pokemon name
            reward_label = reward_list.find(class_='reward-label')
            if reward_label:
                reward_name = reward_label.get_text(strip=True)
                task_data['reward'] = reward_name

            # Get reward image
            reward_image = reward_list.find('img', class_='reward-image')
            if reward_image and reward_image.get('src'):
                image_src = reward_image.get('src')
                if 'cdn-cgi' in image_src:
                    image_src = image_src.split('/cdn-cgi')[0]
                task_data['image'] = image_src

        else:
            # Fallback to original parsing for other formats
            full_text = item.get_text(strip=True)

            if not full_text:
                return None

            # Try to separate task from reward by common patterns
            if "REWARD" in full_text:
                # Split on "REWARD" to separate task from reward
                parts = full_text.split("REWARD", 1)
                if len(parts) == 2:
                    task_text = parts[0].replace("???", "").strip()
                    reward_text = parts[1].strip()

                    # Extract Pokemon name from reward (before Max CP)
                    if "Max CP" in reward_text:
                        pokemon_name = reward_text.split("Max CP")[0].strip()
                        task_data['reward'] = pokemon_name
                    else:
                        task_data['reward'] = reward_text

                    # If we have a clean task text, use it, otherwise use a placeholder
                    if task_text and len(task_text) > 3:
                        task_data['text'] = task_text
                    else:
                        task_data['text'] = "Research task (details TBD)"
                else:
                    # If split failed, try to extract Pokemon name differently
                    task_data['text'] = "Research task (details TBD)"
                    # Look for Pokemon name pattern
                    import re
                    # Match Pokemon name followed by CP info
                    match = re.search(r'([A-Za-z]+)(?:Max CP|Min CP)', full_text)
                    if match:
                        task_data['reward'] = match.group(1)
                    else:
                        task_data['reward'] = full_text
            else:
                # No clear REWARD separator, use full text as task
                task_data['text'] = full_text

            # Try to find associated image
            img_elem = item.find('img')
            if img_elem and img_elem.get('src'):
                image_src = img_elem.get('src')
                if 'cdn-cgi' in image_src:
                    image_src = image_src.split('/cdn-cgi')[0]
                task_data['image'] = image_src

            # Try to find reward element separately
            if not task_data.get('reward'):
                reward_elem = item.find(class_='reward')
                if reward_elem:
                    task_data['reward'] = reward_elem.get_text(strip=True)

        # Only return if we have meaningful content
        if task_data.get('text') or task_data.get('reward'):
            return task_data

    except Exception as e:
        logger.debug(f"Error extracting research task data: {e}")

    return None