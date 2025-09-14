import json
import sys
import os
import requests
import pytest

# Add the project root to the path so we can import the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from pogo_scraper.scraper import LeekDuckScraper
from pogo_scraper.rocket_lineups import parse_rocket_trainer, parse_lineup_slot, parse_shadow_pokemon


def download_rocket_lineups_data():
    """Download current rocket lineups data if it doesn't exist"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    html_file = os.path.join(fixtures_dir, 'current_rocket_lineups.html')
    
    if not os.path.exists(html_file):
        print("Downloading current rocket lineups data...")
        response = requests.get('https://leekduck.com/rocket-lineups/')
        os.makedirs(fixtures_dir, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete!")
    return html_file


def test_rocket_lineups_parsing():
    """Test that rocket lineups parsing works correctly"""
    # Download data if needed
    html_file = download_rocket_lineups_data()
    
    # Read the current rocket lineups HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find rocket profiles
    rocket_profiles = soup.select('.rocket-profile')
    
    # Should have at least some rocket profiles
    assert len(rocket_profiles) > 0, "No rocket profiles found in the HTML"
    
    # Test the first rocket profile
    first_profile = rocket_profiles[0]
    result = parse_rocket_trainer(first_profile, 'https://leekduck.com')
    
    # Should successfully parse the profile
    assert result is not None, "Failed to parse first rocket profile"
    
    # Should have expected fields
    assert 'name' in result, "Parsed rocket profile missing 'name' field"
    assert 'title' in result, "Parsed rocket profile missing 'title' field"
    assert 'quote' in result, "Parsed rocket profile missing 'quote' field"
    assert 'image' in result, "Parsed rocket profile missing 'image' field"
    assert 'lineups' in result, "Parsed rocket profile missing 'lineups' field"


def test_rocket_lineup_slots_parsing():
    """Test that rocket lineup slots are correctly parsed"""
    # Download data if needed
    html_file = download_rocket_lineups_data()
    
    # Read the current rocket lineups HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    rocket_profiles = soup.select('.rocket-profile')

    # Test first 2 rocket profiles
    valid_lineups_count = 0
    for i, profile in enumerate(rocket_profiles[:2]):
        result = parse_rocket_trainer(profile, 'https://leekduck.com')
        if result and 'lineups' in result and len(result['lineups']) > 0:
            # Check the first lineup slot
            first_slot = result['lineups'][0]
            if 'slot' in first_slot and 'pokemon' in first_slot and len(first_slot['pokemon']) > 0:
                valid_lineups_count += 1
    
    # At least some should have valid lineups
    assert valid_lineups_count > 0, "No rocket profiles with valid lineups found in first 2 profiles"


def test_shadow_pokemon_parsing():
    """Test that shadow Pokemon are correctly parsed"""
    # Download data if needed
    html_file = download_rocket_lineups_data()
    
    # Read the current rocket lineups HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    shadow_pokemon_elements = soup.select('.shadow-pokemon')
    
    # Should have at least some shadow Pokemon
    assert len(shadow_pokemon_elements) > 0, "No shadow Pokemon found in the HTML"

    # Test the first shadow Pokemon
    first_pokemon = shadow_pokemon_elements[0]
    result = parse_shadow_pokemon(first_pokemon)
    
    # Should successfully parse the Pokemon
    assert result is not None, "Failed to parse first shadow Pokemon"
    
    # Should have expected fields
    assert 'name' in result, "Parsed shadow Pokemon missing 'name' field"
    assert 'types' in result, "Parsed shadow Pokemon missing 'types' field"
    assert 'weaknesses' in result, "Parsed shadow Pokemon missing 'weaknesses' field"
    assert 'image' in result, "Parsed shadow Pokemon missing 'image' field"
    assert 'can_be_shiny' in result, "Parsed shadow Pokemon missing 'can_be_shiny' field"