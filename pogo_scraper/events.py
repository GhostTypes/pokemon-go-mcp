#!/usr/bin/env python3
"""
Pokemon Go Events Scraper Module

Handles scraping and parsing of event data from leekduck.com
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_events(scraper, base_url: str) -> List[Dict]:
    """Scrape events data from leekduck.com"""
    logger.info("Scraping events data...")

    cache_file = scraper.output_dir / "events.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached events data")
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            return json.load(f)

    try:
        # First get events feed for dates
        events_feed_url = f"{base_url}/feeds/events.json"
        response = await scraper.session.get(events_feed_url)
        response.raise_for_status()
        events_feed = response.json()

        # Create date lookup
        event_dates = {}
        for event in events_feed:
            event_id = event.get('eventID')
            if event_id:
                event_dates[event_id] = {
                    'start': event.get('start'),
                    'end': event.get('end')
                }

        # Now scrape events page for detailed info
        events_url = f"{base_url}/events/"
        response = await scraper.session.get(events_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        all_events = []
        seen_event_ids = set()  # Track event IDs to prevent duplicates

        # Process both current and upcoming events
        for category in ['current', 'upcoming']:
            event_links = soup.select(f'div.events-list.{category}-events a.event-item-link')

            for link in event_links:
                try:
                    event = parse_event_item(link, event_dates, base_url)
                    if event and event.get('link'):
                        event_id = event.get('eventID')
                        # Skip if we've already seen this event ID
                        if event_id and event_id in seen_event_ids:
                            logger.debug(f"Skipping duplicate event: {event_id}")
                            continue

                        # Add event ID to seen set
                        if event_id:
                            seen_event_ids.add(event_id)

                        # Fetch detailed event data from individual event page
                        await fetch_event_details(scraper, event)
                        all_events.append(event)
                except Exception as e:
                    logger.warning(f"Error parsing event: {e}")
                    continue

        scraper._save_data(all_events, "events.json")
        return all_events

    except Exception as e:
        logger.error(f"Error scraping events: {e}")
        return scraper._load_fallback_data("events.json", [])


def parse_event_item(link_element, event_dates: Dict, base_url: str) -> Optional[Dict]:
    """Parse individual event item from the events page"""
    try:
        wrapper = link_element.find('div', class_='event-item-wrapper')
        if not wrapper:
            return None

        # Extract basic info
        heading_elem = wrapper.find('p')
        heading = heading_elem.get_text(strip=True) if heading_elem else ""

        name_elem = wrapper.select_one('.event-text h2')
        name = name_elem.get_text(strip=True) if name_elem else ""

        img_elem = wrapper.select_one('.event-img-wrapper img')
        image = img_elem.get('src', '') if img_elem else ""

        # Clean up image URL (remove cloudflare caching)
        if 'cdn-cgi' in image:
            image = image.split('/cdn-cgi')[0]

        # Get event ID from link
        href = link_element.get('href', '')
        event_id = href.rstrip('/').split('/')[-1] if href else ""

        # Get dates from feed data
        dates = event_dates.get(event_id, {})

        event = {
            'eventID': event_id,
            'name': name,
            'eventType': infer_event_type(name, heading),
            'heading': heading,
            'link': f"{base_url}{href}" if href else "",
            'image': image,
            'start': dates.get('start', ''),
            'end': dates.get('end', ''),
            'extraData': {'generic': {'hasSpawns': False, 'hasFieldResearchTasks': False}}
        }

        return event

    except Exception as e:
        logger.warning(f"Error parsing event item: {e}")
        return None


def infer_event_type(name: str, heading: str) -> str:
    """Infer event type based on name and heading"""
    name_lower = name.lower()
    heading_lower = heading.lower()

    if 'raid day' in name_lower or 'raid day' in heading_lower:
        return 'raid-day'
    elif 'community day' in name_lower:
        return 'community-day'
    elif 'spotlight' in name_lower or 'spotlight' in heading_lower:
        return 'pokemon-spotlight-hour'
    elif 'breakthrough' in name_lower or 'breakthrough' in heading_lower:
        return 'research-breakthrough'
    elif 'raid' in heading_lower and 'battle' in heading_lower:
        return 'raid-battles'
    elif 'showcase' in name_lower or 'showcase' in heading_lower:
        return 'pokestop-showcase'
    elif heading_lower == 'event':
        return 'event'
    else:
        return 'event'


async def fetch_event_details(scraper, event: Dict) -> None:
    """Fetch detailed event data from individual event page"""
    try:
        logger.debug(f"Fetching details for event: {event['name']}")
        response = await scraper.session.get(event['link'])
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Initialize extraData with generic flags
        generic_data = {
            'hasSpawns': False,
            'hasFieldResearchTasks': False
        }

        # Check for spawns section (ScrapedDuck looks for id='spawns')
        if soup.find(id='spawns'):
            generic_data['hasSpawns'] = True

        # Check for field research section (ScrapedDuck looks for id='field-research-tasks')
        if soup.find(id='field-research-tasks'):
            generic_data['hasFieldResearchTasks'] = True

        # Set generic data
        event['extraData']['generic'] = generic_data

        # Get event-type specific data
        if event['eventType'] == 'community-day':
            await parse_community_day_details(soup, event)
        elif event['eventType'] == 'raid-battles':
            await parse_raid_battle_details(soup, event)
        elif event['eventType'] == 'pokemon-spotlight-hour':
            await parse_spotlight_details(soup, event)
        elif event['eventType'] == 'research-breakthrough':
            await parse_breakthrough_details(soup, event)
        # Add more event types as needed

    except Exception as e:
        logger.warning(f"Error fetching details for event {event['name']}: {e}")
        # Keep the default extraData structure
        pass


async def parse_community_day_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse Community Day specific details"""
    try:
        commday_data = {
            'spawns': [],
            'bonuses': [],
            'bonusDisclaimers': [],
            'shinies': [],
            'specialresearch': []
        }

        page_content = soup.select_one('.page-content')
        if not page_content:
            return

        last_header = ""

        # Process page content sections using ScrapedDuck's approach
        all_nodes = page_content.contents

        for element in all_nodes:
            # Get element classes and id (works for both tag elements and navigable strings)
            element_classes = []
            element_id = ''

            # Only try to get class and id attributes from actual HTML elements, not text nodes
            if hasattr(element, 'name') and element.name:
                element_classes = element.get('class', [])
                element_id = element.get('id', '')

            # Check if this is a section header
            if element_classes and 'event-section-header' in element_classes:
                last_header = element_id
                # Uncomment for debugging:
                # print(f"Found section header: {element_id}")

            # Parse spawns and shinies sections - check if 'pkmn-list-flex' is in classes like ScrapedDuck
            # (Changed from exact match to inclusion check to be more robust)
            elif element_classes and 'pkmn-list-flex' in element_classes:
                # Uncomment for debugging:
                # print(f"Found pkmn-list-flex, last_header: {last_header}")
                if last_header == "spawns":
                    spawns = element.select(':scope > .pkmn-list-item')
                    for spawn in spawns:
                        name_elem = spawn.select_one(':scope > .pkmn-name')
                        img_elem = spawn.select_one(':scope > .pkmn-list-img > img')
                        if name_elem and img_elem:
                            spawn_data = {
                                'name': name_elem.get_text(strip=True),
                                'image': img_elem.get('src', '')
                            }
                            commday_data['spawns'].append(spawn_data)

                elif last_header == "shiny":
                    shinies = element.select(':scope > .pkmn-list-item')
                    for shiny in shinies:
                        name_elem = shiny.select_one(':scope > .pkmn-name')
                        img_elem = shiny.select_one(':scope > .pkmn-list-img > img')
                        if name_elem and img_elem:
                            shiny_data = {
                                'name': name_elem.get_text(strip=True),
                                'image': img_elem.get('src', '')
                            }
                            commday_data['shinies'].append(shiny_data)

        # Parse bonuses
        bonuses = soup.select('.bonus-item')
        bonus_has_disclaimer = False

        for bonus in bonuses:
            text_elem = bonus.select_one('.bonus-text')
            img_elem = bonus.select_one('.item-circle img')
            if text_elem and img_elem:
                bonus_text = text_elem.get_text(strip=True)
                commday_data['bonuses'].append({
                    'text': bonus_text,
                    'image': img_elem.get('src', '')
                })

                if '*' in bonus_text:
                    bonus_has_disclaimer = True

        # Parse bonus disclaimers if present
        if bonus_has_disclaimer:
            bonus_list = soup.select_one('.bonus-list')
            if bonus_list and bonus_list.next_sibling:
                next_elem = bonus_list.next_sibling
                while next_elem and getattr(next_elem, 'name', '') != 'h2':
                    if getattr(next_elem, 'name', '') == 'p':
                        disclaimer_text = next_elem.get_text(strip=True)
                        if disclaimer_text:
                            # Split on <br> tags if present
                            if '<br>' in str(next_elem):
                                disclaimers = str(next_elem).split('<br>')
                                for disclaimer in disclaimers:
                                    clean_disclaimer = BeautifulSoup(disclaimer, 'html.parser').get_text(strip=True)
                                    if clean_disclaimer:
                                        commday_data['bonusDisclaimers'].append(clean_disclaimer)
                            else:
                                commday_data['bonusDisclaimers'].append(disclaimer_text)
                    next_elem = next_elem.next_sibling

        # Parse special research
        research_items = soup.select('.special-research-list .step-item')
        for item in research_items:
            research = {
                'name': '',
                'step': 0,
                'tasks': [],
                'rewards': []
            }

            # Step number and name
            step_num_elem = item.select_one('.step-number')
            step_name_elem = item.select_one('.step-name')

            if step_num_elem:
                try:
                    research['step'] = int(step_num_elem.get_text(strip=True))
                except ValueError:
                    pass

            if step_name_elem:
                research['name'] = step_name_elem.get_text(strip=True)

            # Tasks and their rewards
            task_rewards = item.select('.task-reward')
            for task_reward in task_rewards:
                task_text_elem = task_reward.select_one('.task-text')
                reward_label_elem = task_reward.select_one('.reward-label')
                reward_img_elem = task_reward.select_one('.reward-image')

                if task_text_elem:
                    task = {
                        'text': task_text_elem.get_text(strip=True),
                        'reward': {
                            'text': reward_label_elem.get_text(strip=True) if reward_label_elem else '',
                            'image': reward_img_elem.get('src', '') if reward_img_elem else ''
                        }
                    }
                    research['tasks'].append(task)

            # Page rewards
            page_rewards = item.select('.page-reward')
            for reward in page_rewards:
                reward_label_elem = reward.select_one('.reward-label span')
                reward_img_elem = reward.select_one('.reward-image')

                if reward_label_elem and reward_img_elem:
                    research['rewards'].append({
                        'text': reward_label_elem.get_text(strip=True),
                        'image': reward_img_elem.get('src', '')
                    })

            if research['name'] or research['tasks'] or research['rewards']:
                commday_data['specialresearch'].append(research)

        # Only add communityday data if we found meaningful content
        if (commday_data['spawns'] or commday_data['bonuses'] or
            commday_data['shinies'] or commday_data['specialresearch']):
            event['extraData']['communityday'] = commday_data

    except Exception as e:
        logger.warning(f"Error parsing Community Day details: {e}")


async def parse_raid_battle_details(soup: BeautifulSoup, event: Dict) -> None:
    """Parse Raid Battle specific details"""
    try:
        raidbattle_data = {
            'bosses': [],
            'shinies': []
        }

        page_content = soup.select_one('.page-content')
        if not page_content:
            return

        last_header = ""

        # Process page content sections - get ALL child elements (including text nodes)
        # Use page_content.contents to get all nodes (like ScrapedDuck's childNodes)
        all_nodes = page_content.contents

        for element in all_nodes:
            # Check if this is a section header
            if element.name and element.get('class') and 'event-section-header' in element.get('class', []):
                last_header = element.get('id', '')

            # Parse raid bosses section
            elif element.name and element.get('class') and 'pkmn-list-flex' in element.get('class', []):
                if last_header == "raids":
                    bosses = element.select('.pkmn-list-item')
                    for boss in bosses:
                        name_elem = boss.select_one('.pkmn-name')
                        img_elem = boss.select_one('.pkmn-list-img img')
                        shiny_elem = boss.select_one('.shiny-icon')

                        if name_elem and img_elem:
                            raidbattle_data['bosses'].append({
                                'name': name_elem.get_text(strip=True),
                                'image': img_elem.get('src', ''),
                                'canBeShiny': shiny_elem is not None
                            })

                # Parse shinies section
                elif last_header == "shiny":
                    shinies = element.select('.pkmn-list-item')
                    for shiny in shinies:
                        name_elem = shiny.select_one('.pkmn-name')
                        img_elem = shiny.select_one('.pkmn-list-img img')

                        if name_elem and img_elem:
                            raidbattle_data['shinies'].append({
                                'name': name_elem.get_text(strip=True),
                                'image': img_elem.get('src', '')
                            })

        # Only add raidbattles data if we found meaningful content
        if raidbattle_data['bosses'] or raidbattle_data['shinies']:
            event['extraData']['raidbattles'] = raidbattle_data

    except Exception as e:
        logger.warning(f"Error parsing Raid Battle details: {e}")


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