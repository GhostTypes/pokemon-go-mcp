"""
Handles parsing base events
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional

logger = logging.getLogger(__name__)


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
    elif 'promo' in name_lower and 'research' in name_lower:
        return 'timed-research-promo'
    elif heading_lower == 'event':
        return 'event'
    else:
        return 'event'

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