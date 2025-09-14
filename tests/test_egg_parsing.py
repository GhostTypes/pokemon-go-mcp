import json
import sys
import os
import requests
import pytest

# Add the project root to the path so we can import the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from pogo_scraper.scraper import LeekDuckScraper
from pogo_scraper.eggs import parse_egg_item

def download_eggs_data():
    """Download current eggs data if it doesn't exist"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    html_file = os.path.join(fixtures_dir, 'current_eggs.html')
    
    if not os.path.exists(html_file):
        print("Downloading current eggs data...")
        response = requests.get('https://leekduck.com/eggs/')
        os.makedirs(fixtures_dir, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete!")
    return html_file

def test_egg_parsing():
    """Test that egg parsing works correctly"""
    # Download data if needed
    html_file = download_eggs_data()
    
    # Read the current eggs HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find all pokemon cards
    pokemon_cards = soup.select('.pokemon-card')
    
    # Should have at least some pokemon cards
    assert len(pokemon_cards) > 0, "No pokemon cards found in the HTML"
    
    # Get the first egg grid to test with
    first_grid = soup.select_one('.egg-grid')
    assert first_grid is not None, "No egg grid found in the HTML"

    first_cards = first_grid.select('.pokemon-card')
    assert len(first_cards) > 0, "No cards found in the first egg grid"

    # Test the first card
    first_card = first_cards[0]
    result = parse_egg_item(first_card, "2 km", False, False)
    
    # Should successfully parse the card
    assert result is not None, "Failed to parse first card"
    
    # Should have expected fields
    assert 'name' in result, "Parsed card missing 'name' field"
    assert 'combatPower' in result, "Parsed card missing 'combatPower' field"
    assert 'image' in result, "Parsed card missing 'image' field"
    assert 'canBeShiny' in result, "Parsed card missing 'canBeShiny' field"
    
    # CP value should be a positive integer (not -1)
    assert isinstance(result['combatPower'], int), "CP value should be an integer"
    assert result['combatPower'] > 0, f"CP value should be positive, got {result['combatPower']}"

def test_egg_cp_values():
    """Test that multiple egg CP values are correctly parsed"""
    # Download data if needed
    html_file = download_eggs_data()
    
    # Read the current eggs HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Get the first egg grid to test with
    first_grid = soup.select_one('.egg-grid')
    assert first_grid is not None, "No egg grid found in the HTML"

    first_cards = first_grid.select('.pokemon-card')

    # Test first 5 cards
    valid_cp_count = 0
    for i, card in enumerate(first_cards[:5]):
        result = parse_egg_item(card, "2 km", False, False)
        if result and result['combatPower'] > 0:
            valid_cp_count += 1
    
    # At least some should have valid CP values
    assert valid_cp_count > 0, "No cards with valid CP values found in first 5 cards"