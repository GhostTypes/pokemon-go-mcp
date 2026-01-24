#!/usr/bin/env python3
"""
Pokemon Go Events Scraper Module

Handles scraping and parsing of event data from leekduck.com
"""

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from scraper import LeekDuckScraper

# Import sub-parsers
try:
    # Relative imports for when this module is imported as part of the package
    from .parsers.events.base_event import (
        infer_event_type,  # noqa: F401
        parse_event_item,
    )
    from .parsers.events.comday_details import parse_community_day_details
    from .parsers.events.generic_event_details import parse_generic_event_details
    from .parsers.events.raid_battle_details import parse_raid_battle_details
    from .parsers.events.raid_day_details import parse_raid_day_details
    from .parsers.events.research_breakthrough_details import parse_breakthrough_details
    from .parsers.events.spotlight_details import parse_spotlight_details
    from .parsers.events.timed_reseach_code_details import (
        parse_timed_research_code_details,
    )
except ImportError:
    # Absolute imports for when running as a standalone script
    from parsers.events.base_event import parse_event_item
    from parsers.events.comday_details import parse_community_day_details
    from parsers.events.generic_event_details import parse_generic_event_details
    from parsers.events.raid_battle_details import parse_raid_battle_details
    from parsers.events.raid_day_details import parse_raid_day_details
    from parsers.events.research_breakthrough_details import parse_breakthrough_details
    from parsers.events.spotlight_details import parse_spotlight_details
    from parsers.events.timed_reseach_code_details import (
        parse_timed_research_code_details,
    )

logger = logging.getLogger(__name__)


async def scrape_events(
    scraper: "LeekDuckScraper",
    base_url: str,
) -> list[dict[str, Any]]:
    """Scrape events data from leekduck.com"""
    logger.info("Scraping events data...")

    cache_file = scraper.output_dir / "events.json"
    if not scraper._should_fetch(cache_file):  # noqa: SLF001
        logger.info("Using cached events data")
        with cache_file.open(encoding="utf-8") as f:
            return json.load(f)  # type: ignore[return-value]

    try:
        # First get events feed for dates
        events_feed_url = f"{base_url}/feeds/events.json"
        response = await scraper.session.get(events_feed_url)
        response.raise_for_status()
        events_feed = response.json()

        # Create date lookup
        event_dates: dict[str, dict[str, Any]] = {}
        for event in events_feed:
            event_id = event.get("eventID")
            if event_id:
                event_dates[event_id] = {
                    "start": event.get("start"),
                    "end": event.get("end"),
                }

        # Now scrape events page for detailed info
        events_url = f"{base_url}/events/"
        response = await scraper.session.get(events_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        all_events = []
        seen_event_ids = set()  # Track event IDs to prevent duplicates

        # Process both current and upcoming events - collect first, fetch later
        events_to_fetch = []
        for category in ["current", "upcoming"]:
            event_links = soup.select(
                f"div.events-list.{category}-events a.event-item-link"
            )

            for link in event_links:
                try:
                    event = parse_event_item(link, event_dates, base_url)
                    if event and event.get("link"):
                        event_id = event.get("eventID")
                        # Skip if we've already seen this event ID
                        if event_id and event_id in seen_event_ids:
                            logger.debug("Skipping duplicate event: %s", event_id)
                            continue

                        # Add event ID to seen set
                        if event_id:
                            seen_event_ids.add(event_id)

                        events_to_fetch.append(event)
                except (AttributeError, KeyError, ValueError, TypeError) as e:
                    logger.warning("Error parsing event: %s", e)
                    continue

        # Batch fetch event details concurrently
        await asyncio.gather(
            *[fetch_event_details(scraper, event) for event in events_to_fetch],
            return_exceptions=True,
        )
        all_events.extend(events_to_fetch)

        scraper._save_data(all_events, "events.json")  # noqa: SLF001

    except Exception:
        logger.exception("Error scraping events")
        return scraper._load_fallback_data("events.json", [])  # type: ignore[return-value]  # noqa: SLF001

    return all_events


async def fetch_event_details(
    scraper: "LeekDuckScraper",
    event: dict[str, Any],
) -> None:
    """Fetch detailed event data from individual event page"""
    try:
        logger.debug("Fetching details for event: %s", event["name"])
        response = await scraper.session.get(event["link"])
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Initialize extraData with generic flags
        generic_data: dict[str, Any] = {
            "hasSpawns": False,
            "hasFieldResearchTasks": False,
        }

        # Check for spawns section (ScrapedDuck looks for id='spawns')
        if soup.find(id="spawns"):
            generic_data["hasSpawns"] = True

        # Check for field research section
        # (ScrapedDuck looks for id='field-research-tasks')
        if soup.find(id="field-research-tasks"):
            generic_data["hasFieldResearchTasks"] = True

        # Set basic generic data
        event["extraData"]["generic"] = generic_data

        # Get event-type specific data
        if event["eventType"] == "community-day":
            await parse_community_day_details(soup, event)
        elif event["eventType"] == "raid-day":
            await parse_raid_day_details(soup, event)
        elif event["eventType"] == "raid-battles":
            await parse_raid_battle_details(soup, event)
        elif event["eventType"] == "pokemon-spotlight-hour":
            await parse_spotlight_details(soup, event)
        elif event["eventType"] == "research-breakthrough":
            await parse_breakthrough_details(soup, event)
        elif event["eventType"] == "timed-research-promo":
            await parse_timed_research_code_details(soup, event)
        elif event["eventType"] == "event":
            # Use generic parser for standard "event" type events
            await parse_generic_event_details(soup, event)
        # Add more event types as needed

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error fetching details for event %s: %s", event["name"], e)
        # Keep the default extraData structure
