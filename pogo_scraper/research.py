#!/usr/bin/env python3
"""
Pokemon Go Research Scraper Module

Handles scraping and parsing of field research data from leekduck.com
"""

import json
import logging
from typing import TYPE_CHECKING, Any

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

if TYPE_CHECKING:
    from scraper import LeekDuckScraper

logger = logging.getLogger(__name__)


async def scrape_research(
    scraper: "LeekDuckScraper",
    base_url: str,
) -> list[dict[str, Any]]:
    """Scrape field research data from leekduck.com"""
    logger.info("Scraping research data...")

    cache_file = scraper.output_dir / "research.json"
    if not scraper._should_fetch(cache_file):  # noqa: SLF001
        logger.info("Using cached research data")
        with cache_file.open(encoding="utf-8") as f:
            return json.load(f)  # type: ignore[return-value]

    try:
        research_url = f"{base_url}/research/"
        response = await scraper.session.get(research_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        research_tasks: list[dict[str, Any]] = []

        # Find research items (updated selector)
        research_items = soup.select(".task-item")
        for item in research_items:
            task = _safe_parse_research_task(item)
            if task:
                research_tasks.append(task)

        scraper._save_data(research_tasks, "research.json")  # noqa: SLF001

    except (httpx.HTTPError, OSError, json.JSONDecodeError):
        logger.exception("Error scraping research")
        return scraper._load_fallback_data("research.json", [])  # type: ignore[return-value]  # noqa: SLF001

    return research_tasks


def _safe_parse_research_task(item: Tag) -> dict[str, Any] | None:
    """Safely parse individual research task with error handling"""
    try:
        return parse_research_task(item)
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing research task: %s", e)
        return None


def parse_research_task(item: Tag) -> dict[str, Any] | None:
    """Parse individual research task"""
    try:
        # Task text (updated selector)
        text_elem = item.select_one(".task-text")
        task_text = text_elem.get_text(strip=True) if text_elem else ""

        if not task_text:
            return None

        # Rewards (updated selector) - collect all at once
        reward_items = item.select(".reward")
        rewards = [r for r in (parse_research_reward(ri) for ri in reward_items) if r]

        if not rewards:
            return None

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing research task: %s", e)
        return None
    else:
        return {"text": task_text, "rewards": rewards}


def parse_research_reward(reward_item: Tag) -> dict[str, Any] | None:
    """Parse individual research reward"""
    try:
        # Extract all elements upfront
        name_elem = reward_item.select_one(".reward-label span")
        name = name_elem.get_text(strip=True) if name_elem else ""

        if not name:
            return None

        img_elem = reward_item.select_one(".reward-image")
        shiny_elem = reward_item.select_one(".shiny-icon")

        return {
            "name": name,
            "image": img_elem.get("src", "") if img_elem else "",
            "can_be_shiny": bool(shiny_elem),
        }

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing research reward: %s", e)
        return None
