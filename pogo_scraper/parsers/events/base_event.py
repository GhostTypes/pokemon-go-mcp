"""
Handles parsing base events
"""

import logging
import unicodedata
from typing import Any

from bs4.element import Tag

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    """Normalize text for matching by removing accents and extra whitespace."""
    normalized = unicodedata.normalize("NFKD", text or "")
    return " ".join(normalized.encode("ascii", "ignore").decode("ascii").split())


def infer_event_type(name: str, heading: str) -> str:
    """Infer event type based on name and heading"""
    name_lower = _normalize_text(name).lower()
    heading_lower = _normalize_text(heading).lower()

    # Match specific event patterns
    if "raid day" in name_lower or "raid day" in heading_lower:
        event_type = "raid-day"
    elif "community day" in name_lower:
        event_type = "community-day"
    elif "spotlight" in name_lower or "spotlight" in heading_lower:
        event_type = "pokemon-spotlight-hour"
    elif "breakthrough" in name_lower or "breakthrough" in heading_lower:
        event_type = "research-breakthrough"
    elif "raid" in heading_lower and "battle" in heading_lower:
        event_type = "raid-battles"
    elif "showcase" in name_lower or "showcase" in heading_lower:
        event_type = "pokestop-showcase"
    elif "promo" in name_lower and "research" in name_lower:
        event_type = "timed-research-promo"
    elif "raid hour" in name_lower or "raid hour" in heading_lower:
        event_type = "raid-hour"
    elif "max monday" in name_lower or "max monday" in heading_lower:
        event_type = "max-mondays"
    elif "max battle" in name_lower or "max battle" in heading_lower:
        event_type = "max-battles"
    elif "go battle league" in name_lower or "go battle league" in heading_lower:
        event_type = "go-battle-league"
    elif "go pass" in name_lower or "go pass" in heading_lower:
        event_type = "go-pass"
    elif "pokemon go tour" in name_lower or "pokemon go tour" in heading_lower:
        event_type = "pokemon-go-tour"
    elif "research day" in name_lower or "research day" in heading_lower:
        event_type = "research-day"
    elif heading_lower == "season" or "season" in heading_lower:
        event_type = "season"
    elif heading_lower == "event":
        event_type = "event"
    else:
        event_type = "event"

    return event_type


def parse_event_item(
    link_element: Tag, event_dates: dict[str, Any], base_url: str
) -> dict[str, Any] | None:
    """Parse individual event item from the events page"""
    try:
        wrapper = link_element.find("div", class_="event-item-wrapper")
        if not wrapper:
            return None

        # Extract basic info
        heading_elem = wrapper.find("p")
        heading = heading_elem.get_text(strip=True) if heading_elem else ""

        name_elem = wrapper.select_one(".event-text h2")
        name = name_elem.get_text(strip=True) if name_elem else ""

        img_elem = wrapper.select_one(".event-img-wrapper img")
        image = img_elem.get("src", "") if img_elem else ""

        # Clean up image URL (remove cloudflare caching)
        if "cdn-cgi" in image:
            image = image.split("/cdn-cgi")[0]

        # Get event ID from link
        href = link_element.get("href", "")
        event_id = href.rstrip("/").split("/")[-1] if href else ""

        # Get dates from feed data
        dates: dict[str, Any] = event_dates.get(event_id, {})  # type: ignore[assignment]

        # Debug: Log when dates are missing
        if not dates.get("start") and not dates.get("end"):
            # Log the first few missing date events for debugging
            import logging  # noqa: PLC0415

            logger_debug = logging.getLogger(__name__)
            logger_debug.debug(
                "No dates found for event ID: %s (href: %s)", event_id, href
            )

        return {
            "eventID": event_id,
            "name": name,
            "eventType": infer_event_type(name, heading),
            "heading": heading,
            "link": f"{base_url}{href}" if href else "",
            "image": image,
            "start": dates.get("start", ""),
            "end": dates.get("end", ""),
            "extraData": {
                "generic": {"hasSpawns": False, "hasFieldResearchTasks": False}  # type: ignore[dict-item]
            },
        }

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing event item: %s", e)
        return None
