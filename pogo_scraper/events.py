#!/usr/bin/env python3
"""
Pokemon Go Events Scraper Module

Handles scraping and parsing of event data from leekduck.com
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

# Import sub-parsers
try:
    # Relative imports for when this module is imported as part of the package
    from .parsers.events.spotlight_details import parse_spotlight_details
    from .parsers.events.comday_details import  parse_community_day_details
    from .parsers.events.raid_battle_details import parse_raid_battle_details
    from .parsers.events.timed_reseach_code_details import parse_timed_research_code_details
    from .parsers.events.research_breakthrough_details import parse_breakthrough_details
    from .parsers.events.generic_event_details import parse_generic_event_details
    from .parsers.events.base_event import parse_event_item, infer_event_type
except ImportError:
    # Absolute imports for when running as a standalone script
    from parsers.events.spotlight_details import parse_spotlight_details
    from parsers.events.comday_details import  parse_community_day_details
    from parsers.events.raid_battle_details import parse_raid_battle_details
    from parsers.events.timed_reseach_code_details import parse_timed_research_code_details
    from parsers.events.research_breakthrough_details import parse_breakthrough_details
    from parsers.events.generic_event_details import parse_generic_event_details
    from parsers.events.base_event import parse_event_item, infer_event_type

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

        # Set basic generic data
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
        elif event['eventType'] == 'timed-research-promo':
            await parse_timed_research_code_details(soup, event)
        elif event['eventType'] == 'event':
            # Use generic parser for standard "event" type events
            await parse_generic_event_details(soup, event)
        # Add more event types as needed

    except Exception as e:
        logger.warning(f"Error fetching details for event {event['name']}: {e}")
        # Keep the default extraData structure
        pass
