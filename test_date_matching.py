#!/usr/bin/env python3
"""
Test script to verify event date matching between HTML and feed
"""
import asyncio
import json

from bs4 import BeautifulSoup

from pogo_scraper.parsers.events.base_event import parse_event_item


async def test_date_matching():
    """Test that event IDs from HTML match event IDs from feed"""

    # Load the events feed
    with open("temp_events_feed.json", encoding="utf-8") as f:
        events_feed = json.load(f)

    # Create date lookup
    event_dates = {}
    for event in events_feed:
        event_id = event.get("eventID")
        if event_id:
            event_dates[event_id] = {
                "start": event.get("start"),
                "end": event.get("end"),
            }

    print(f"Loaded {len(event_dates)} events from feed with dates")

    # Load the events page HTML
    with open("temp_eggs_page.html", encoding="utf-8") as f:
        html_content = f.read()

    # Parse HTML
    soup = BeautifulSoup(html_content, "lxml")

    # Test parsing events
    matches = 0
    no_match = 0

    for category in ["current", "upcoming"]:
        event_links = soup.select(
            f"div.events-list.{category}-events a.event-item-link"
        )

        for link in event_links[:10]:  # Test first 10 from each category
            event = parse_event_item(link, event_dates, "https://leekduck.com")
            if event:
                if event.get("start") or event.get("end"):
                    matches += 1
                    print(f"✓ Matched: {event['eventID']} - {event['name']}")
                    print(f"  Start: {event.get('start', 'N/A')}")
                    print(f"  End: {event.get('end', 'N/A')}")
                else:
                    no_match += 1
                    print(f"✗ No dates: {event['eventID']} - {event['name']}")

    print(f"\nResults: {matches} matched, {no_match} no match")


if __name__ == "__main__":
    asyncio.run(test_date_matching())
