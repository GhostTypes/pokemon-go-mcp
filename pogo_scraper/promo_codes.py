#!/usr/bin/env python3
"""
Pokemon Go Promo Codes Scraper Module

Handles scraping and parsing of promo code data from leekduck.com
"""

import json
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


async def scrape_promo_codes(scraper, base_url: str) -> List[Dict]:
    """Scrape promo codes data from leekduck.com"""
    logger.info("Scraping promo codes data...")

    cache_file = scraper.output_dir / "promo-codes.json"
    if not scraper._should_fetch(cache_file):
        logger.info("Using cached promo codes data")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    try:
        # Scrape promo codes page
        promo_codes_url = f"{base_url}/promo-codes/"
        response = await scraper.session.get(promo_codes_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        promo_cards = soup.select('div.promo-card:not(.expired):not(.-expired)')
        
        all_promo_codes = []
        
        for card in promo_cards:
            try:
                promo_code = parse_promo_card(card, base_url)
                if promo_code:
                    all_promo_codes.append(promo_code)
            except Exception as e:
                logger.warning(f"Error parsing promo card: {e}")
                continue

        scraper._save_data(all_promo_codes, "promo-codes.json")
        return all_promo_codes

    except Exception as e:
        logger.error(f"Error scraping promo codes: {e}")
        return scraper._load_fallback_data("promo-codes.json", [])


def parse_promo_card(card_element, base_url: str) -> Optional[Dict]:
    """Parse individual promo card element"""
    try:
        # Check if card is expired
        card_classes = card_element.get('class', [])
        if 'expired' in card_classes or '-expired' in card_classes:
            return None

        # Extract promo code
        code_display = card_element.select_one('.code-display')
        if not code_display:
            return None
            
        code_elem = code_display.select_one('p.text')
        promo_code = code_elem.get_text(strip=True) if code_elem else ""
        
        if not promo_code:
            return None

        # Build redemption URL
        redemption_url = f"https://store.pokemongo.com/offer-redemption?passcode={promo_code}"

        # Extract title
        title_elem = card_element.select_one('.title')
        title = title_elem.get_text(strip=True) if title_elem else ""

        # Extract description with markdown links
        description_elem = card_element.select_one('.description')
        description = ""
        if description_elem:
            # Convert HTML links to markdown format
            for link in description_elem.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                # Make relative URLs absolute
                if href.startswith('/'):
                    href = f"{base_url}{href}"
                markdown_link = f"[{text}]({href})"
                link.replace_with(markdown_link)
            description = description_elem.get_text(strip=True)

        # Extract rewards
        rewards = []
        reward_list = card_element.select('.reward-list .reward')
        for reward_elem in reward_list:
            reward_type = reward_elem.get('data-reward-type', '')
            
            reward_label_elem = reward_elem.select_one('.reward-label')
            reward_label = reward_label_elem.get_text(strip=True) if reward_label_elem else ""
            
            reward_img_elem = reward_elem.select_one('.reward-image')
            reward_img_url = ""
            if reward_img_elem:
                reward_img_url = reward_img_elem.get('src', '')
                # Make relative URLs absolute
                if reward_img_url.startswith('/'):
                    reward_img_url = f"{base_url}{reward_img_url}"
            
            rewards.append({
                'name': reward_label,
                'url': reward_img_url,
                'type': reward_type
            })

        # Extract expiration date
        expiry_elem = card_element.select_one('.expiry')
        expiration = ""
        if expiry_elem:
            expiration = expiry_elem.get('data-expires', '')

        promo_data = {
            'code': promo_code,
            'title': title,
            'description': description,
            'redemption_url': redemption_url,
            'rewards': rewards,
            'expiration': expiration
        }

        return promo_data

    except Exception as e:
        logger.warning(f"Error parsing promo card: {e}")
        return None