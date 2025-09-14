#!/usr/bin/env python3
"""
Pokemon Go Research Scraper Module

Handles scraping and parsing of field research data from leekduck.com
"""

import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_research(scraper, base_url: str) -> List[Dict]:
    """Scrape field research data from leekduck.com"""
    logger.info("Scraping research data...")

    cache_file = scraper.output_dir / "research.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached research data")
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            return json.load(f)

    try:
        research_url = f"{base_url}/research/"
        response = await scraper.session.get(research_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        research_tasks = []

        # Find research items (updated selector)
        research_items = soup.select('.task-item')
        for item in research_items:
            try:
                task = parse_research_task(item)
                if task:
                    research_tasks.append(task)
            except Exception as e:
                logger.warning(f"Error parsing research task: {e}")
                continue

        scraper._save_data(research_tasks, "research.json")
        return research_tasks

    except Exception as e:
        logger.error(f"Error scraping research: {e}")
        return scraper._load_fallback_data("research.json", [])


def parse_research_task(item) -> Optional[Dict]:
    """Parse individual research task"""
    try:
        task = {
            'text': '',
            'rewards': []
        }

        # Task text (updated selector)
        text_elem = item.select_one('.task-text')
        task['text'] = text_elem.get_text(strip=True) if text_elem else ""

        # Rewards (updated selector)
        reward_items = item.select('.reward')
        for reward_item in reward_items:
            reward = parse_research_reward(reward_item)
            if reward:
                task['rewards'].append(reward)

        return task if task['text'] and task['rewards'] else None

    except Exception as e:
        logger.warning(f"Error parsing research task: {e}")
        return None


def parse_research_reward(reward_item) -> Optional[Dict]:
    """Parse individual research reward"""
    try:
        reward = {
            'name': '',
            'image': '',
            'can_be_shiny': False
        }

        # Name (updated selector)
        name_elem = reward_item.select_one('.reward-label span')
        reward['name'] = name_elem.get_text(strip=True) if name_elem else ""

        # Image (updated selector)
        img_elem = reward_item.select_one('.reward-image')
        reward['image'] = img_elem.get('src', '') if img_elem else ""

        # Shiny
        reward['can_be_shiny'] = bool(reward_item.select_one('.shiny-icon'))

        return reward if reward['name'] else None

    except Exception as e:
        logger.warning(f"Error parsing research reward: {e}")
        return None