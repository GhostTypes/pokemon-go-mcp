import json
import sys
import os
import requests
import pytest

# Add the project root to the path so we can import the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from pogo_scraper.scraper import LeekDuckScraper
from pogo_scraper.raids import parse_raid_boss

def download_raids_data():
    """Download current raids data if it doesn't exist"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    html_file = os.path.join(fixtures_dir, 'current_raids.html')
    
    if not os.path.exists(html_file):
        print("Downloading current raids data...")
        response = requests.get('https://leekduck.com/boss/')
        os.makedirs(fixtures_dir, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete!")
    return html_file

def test_raids_parsing():
    """Test that raids parsing works correctly"""
    # Download data if needed
    html_file = download_raids_data()
    
    # Read the current raids HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find raid cards
    raid_cards = soup.select('.card')
    
    # Should have at least some raid cards
    assert len(raid_cards) > 0, "No raid cards found in the HTML"
    
    # Test the first raid card
    first_card = raid_cards[0]
    result = parse_raid_boss(first_card, "Tier 1", 'https://leekduck.com')
    
    # Should successfully parse the card
    assert result is not None, "Failed to parse first raid card"
    
    # Should have expected fields
    assert 'name' in result, "Parsed raid card missing 'name' field"
    assert 'tier' in result, "Parsed raid card missing 'tier' field"
    assert 'image' in result, "Parsed raid card missing 'image' field"
    assert 'canBeShiny' in result, "Parsed raid card missing 'canBeShiny' field"
    assert 'types' in result, "Parsed raid card missing 'types' field"
    assert 'combatPower' in result, "Parsed raid card missing 'combatPower' field"
    assert 'boostedWeather' in result, "Parsed raid card missing 'boostedWeather' field"

def test_raids_cp_values():
    """Test that raid CP values are correctly parsed"""
    # Download data if needed
    html_file = download_raids_data()
    
    # Read the current raids HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    raid_cards = soup.select('.card')

    # Test first 3 raid cards
    valid_cp_count = 0
    for i, card in enumerate(raid_cards[:3]):
        result = parse_raid_boss(card, "Tier 1", 'https://leekduck.com')
        if result and 'combatPower' in result:
            cp_data = result['combatPower']
            # Check if either normal or boosted CP has valid values
            if ('normal' in cp_data and cp_data['normal']['min'] > 0) or \
               ('boosted' in cp_data and cp_data['boosted']['min'] > 0):
                valid_cp_count += 1
    
    # At least some should have valid CP values
    assert valid_cp_count > 0, "No raid cards with valid CP values found in first 3 cards"