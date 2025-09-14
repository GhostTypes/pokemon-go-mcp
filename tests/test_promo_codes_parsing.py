import json
import sys
import os
import requests
import pytest

# Add the project root to the path so we can import the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from pogo_scraper.scraper import LeekDuckScraper
from pogo_scraper.promo_codes import parse_promo_card


def download_promo_data():
    """Download current promo codes data if it doesn't exist"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    html_file = os.path.join(fixtures_dir, 'current_promos.html')
    
    if not os.path.exists(html_file):
        print("Downloading current promo codes data...")
        response = requests.get('https://leekduck.com/promo-codes/')
        os.makedirs(fixtures_dir, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete!")
    return html_file


def test_promo_codes_parsing():
    """Test that promo codes parsing works correctly"""
    # Download data if needed
    html_file = download_promo_data()
    
    # Read the current promo codes HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find promo card items (only non-expired ones)
    promo_cards = soup.select('div.promo-card:not(.expired):not(.-expired)')
    
    # Should have at least some promo codes
    assert len(promo_cards) > 0, "No active promo codes found in the HTML"
    
    # Test the first promo card
    first_card = promo_cards[0]
    result = parse_promo_card(first_card, 'https://leekduck.com')
    
    # Should successfully parse the promo card
    assert result is not None, "Failed to parse first promo card"
    
    # Should have expected fields
    assert 'code' in result, "Parsed promo card missing 'code' field"
    assert 'title' in result, "Parsed promo card missing 'title' field"
    assert 'description' in result, "Parsed promo card missing 'description' field"
    assert 'redemption_url' in result, "Parsed promo card missing 'redemption_url' field"
    assert 'rewards' in result, "Parsed promo card missing 'rewards' field"
    assert 'expiration' in result, "Parsed promo card missing 'expiration' field"


def test_promo_codes_list_parsing():
    """Test that multiple promo codes are correctly parsed"""
    # Download data if needed
    html_file = download_promo_data()
    
    # Read the current promo codes HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    promo_cards = soup.select('div.promo-card:not(.expired):not(.-expired)')

    # Test first 3 promo cards
    parsed_count = 0
    for i, promo_card in enumerate(promo_cards[:3]):
        result = parse_promo_card(promo_card, 'https://leekduck.com')
        if result:
            parsed_count += 1
    
    # At least some should be successfully parsed
    assert parsed_count > 0, "No promo cards successfully parsed in first 3 cards"


def test_expired_promo_codes_filtering():
    """Test that expired promo codes are filtered out"""
    # Download data if needed
    html_file = download_promo_data()
    
    # Read the current promo codes HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find all promo cards including expired ones
    all_promo_cards = soup.select('div.promo-card')
    expired_promo_cards = soup.select('div.promo-card.expired, div.promo-card.-expired')
    
    # Should have some expired cards
    assert len(expired_promo_cards) > 0, "No expired promo cards found in the HTML"
    
    # Test that expired cards return None when parsed
    for expired_card in expired_promo_cards[:2]:  # Test first 2 expired cards
        result = parse_promo_card(expired_card, 'https://leekduck.com')
        assert result is None, "Expired promo card should not be parsed"


def test_promo_code_rewards_parsing():
    """Test that promo code rewards are correctly parsed"""
    # Download data if needed
    html_file = download_promo_data()
    
    # Read the current promo codes HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find promo card items (only non-expired ones)
    promo_cards = soup.select('div.promo-card:not(.expired):not(.-expired)')
    
    # Test the first promo card that has rewards
    for card in promo_cards:
        result = parse_promo_card(card, 'https://leekduck.com')
        if result and result.get('rewards'):
            # Should have at least one reward
            assert len(result['rewards']) > 0, "Promo card has rewards field but no rewards"
            
            # Each reward should have name and url
            for reward in result['rewards']:
                assert 'name' in reward, "Reward missing 'name' field"
                assert 'url' in reward, "Reward missing 'url' field"
                assert 'type' in reward, "Reward missing 'type' field"
            break