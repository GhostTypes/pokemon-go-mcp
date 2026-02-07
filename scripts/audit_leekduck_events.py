#!/usr/bin/env python3
"""Audit LeekDuck event parsing across current and historical events.

This script uses cloudscraper to fetch event pages (current + sitemap)
then runs the existing parsers to ensure they handle all observed event types.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from collections.abc import Iterable

import cloudscraper
from bs4 import BeautifulSoup

from pogo_scraper.events import apply_event_parsers
from pogo_scraper.parsers.events.base_event import infer_event_type, parse_event_item

BASE_URL = "https://leekduck.com"
EVENTS_URL = urljoin(BASE_URL, "/events/")
EVENTS_FEED_URL = urljoin(BASE_URL, "/feeds/events.json")
SITEMAP_URL = urljoin(BASE_URL, "/sitemap.xml")

logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    parsed: int
    errors: int
    event_types: Counter


def _download_text(scraper: cloudscraper.CloudScraper, url: str) -> str:
    response = scraper.get(url, timeout=45)
    response.raise_for_status()
    return response.text


def _download_json(scraper: cloudscraper.CloudScraper, url: str) -> list[dict]:
    response = scraper.get(url, timeout=45)
    response.raise_for_status()
    return response.json()


def _load_event_dates(scraper: cloudscraper.CloudScraper) -> dict[str, dict[str, str]]:
    events_feed = _download_json(scraper, EVENTS_FEED_URL)
    dates: dict[str, dict[str, str]] = {}
    for event in events_feed:
        event_id = event.get("eventID")
        if event_id:
            dates[event_id] = {
                "start": event.get("start", ""),
                "end": event.get("end", ""),
            }
    return dates


def _collect_current_event_links(
    scraper: cloudscraper.CloudScraper, event_dates: dict[str, dict[str, str]]
) -> list[dict]:
    html = _download_text(scraper, EVENTS_URL)
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict] = []

    for link in soup.select("a.event-item-link"):
        parsed = parse_event_item(link, event_dates, BASE_URL)
        if parsed:
            events.append(parsed)

    return events


def _collect_sitemap_event_links(
    scraper: cloudscraper.CloudScraper, limit: int | None
) -> list[str]:
    sitemap_text = _download_text(scraper, SITEMAP_URL)
    root = ET.fromstring(sitemap_text)  # noqa: S314

    urls: list[str] = []
    for url in root.iter():
        if url.tag.endswith("loc") and url.text:
            loc = url.text.strip()
            if "/events/" in loc and loc.rstrip("/").split("/events/")[-1]:
                urls.append(loc)

    if limit:
        urls = urls[:limit]

    return urls


def _build_event_from_page(url: str, soup: BeautifulSoup) -> dict:
    title = soup.select_one(".page-title")
    name = title.get_text(strip=True) if title else url.split("/events/")[-1]

    return {
        "eventID": url.rstrip("/").split("/")[-1],
        "name": name,
        "heading": "",
        "eventType": infer_event_type(name, ""),
        "link": url,
        "image": "",
        "start": "",
        "end": "",
        "extraData": {"generic": {"hasSpawns": False, "hasFieldResearchTasks": False}},
    }


async def _apply_detail_parsers(soup: BeautifulSoup, event: dict) -> None:
    await apply_event_parsers(soup, event)


def _dedupe_events(events: Iterable[dict]) -> list[dict]:
    seen = set()
    unique: list[dict] = []
    for event in events:
        event_id = event.get("eventID")
        if event_id and event_id in seen:
            continue
        if event_id:
            seen.add(event_id)
        unique.append(event)
    return unique


async def _audit_events(
    scraper: cloudscraper.CloudScraper,
    events: list[dict],
) -> AuditResult:
    event_types: Counter = Counter()
    errors = 0
    parsed = 0

    for event in events:
        event_types[event.get("eventType", "unknown")] += 1
        html = _download_text(scraper, event["link"])
        soup = BeautifulSoup(html, "html.parser")
        try:
            await _apply_detail_parsers(soup, event)
            parsed += 1
        except Exception as exc:  # noqa: BLE001
            errors += 1
            logger.warning("Failed parsing %s: %s", event.get("link"), exc)

    return AuditResult(parsed=parsed, errors=errors, event_types=event_types)


async def _audit_sitemap(
    scraper: cloudscraper.CloudScraper,
    urls: list[str],
) -> AuditResult:
    event_types: Counter = Counter()
    errors = 0
    parsed = 0

    for url in urls:
        html = _download_text(scraper, url)
        soup = BeautifulSoup(html, "html.parser")
        event = _build_event_from_page(url, soup)
        event_types[event.get("eventType", "unknown")] += 1

        try:
            await _apply_detail_parsers(soup, event)
            parsed += 1
        except Exception as exc:  # noqa: BLE001
            errors += 1
            logger.warning("Failed parsing %s: %s", url, exc)

    return AuditResult(parsed=parsed, errors=errors, event_types=event_types)


def _log_summary(prefix: str, result: AuditResult) -> None:
    logger.info(
        "%s parsed %s events with %s errors", prefix, result.parsed, result.errors
    )
    for event_type, count in result.event_types.most_common():
        logger.info("%s event type: %s (%s)", prefix, event_type, count)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sitemap-limit",
        type=int,
        default=120,
        help="Limit number of historical events pulled from sitemap.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    scraper = cloudscraper.create_scraper()
    event_dates = _load_event_dates(scraper)
    current_events = _dedupe_events(_collect_current_event_links(scraper, event_dates))

    current_result = asyncio.run(_audit_events(scraper, current_events))
    _log_summary("Current", current_result)

    sitemap_urls = _collect_sitemap_event_links(scraper, args.sitemap_limit)
    sitemap_result = asyncio.run(_audit_sitemap(scraper, sitemap_urls))
    _log_summary("Sitemap", sitemap_result)


if __name__ == "__main__":
    main()
