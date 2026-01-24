import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add the project root to the path so we can import the scraper
sys.path.insert(0, str(Path(__file__).parent))

from pogo_scraper.rocket_lineups import (
    parse_rocket_trainer,
    parse_shadow_pokemon,
)


def download_rocket_lineups_data():
    """Download current rocket lineups data if it doesn't exist"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    html_file = fixtures_dir / "current_rocket_lineups.html"

    if not html_file.exists():
        response = requests.get("https://leekduck.com/rocket-lineups/", timeout=30)
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        html_file.write_text(response.text, encoding="utf-8")
    return html_file


def test_rocket_lineups_parsing():
    """Test that rocket lineups parsing works correctly"""
    # Download data if needed
    html_file = download_rocket_lineups_data()

    # Read the current rocket lineups HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Find rocket profiles
    rocket_profiles = soup.select(".rocket-profile")

    # Should have at least some rocket profiles
    assert len(rocket_profiles) > 0, "No rocket profiles found in the HTML"

    # Test the first rocket profile
    first_profile = rocket_profiles[0]
    result = parse_rocket_trainer(first_profile, "https://leekduck.com")

    # Should successfully parse the profile
    assert result is not None, "Failed to parse first rocket profile"

    # Should have expected fields
    assert "name" in result, "Parsed rocket profile missing 'name' field"
    assert "title" in result, "Parsed rocket profile missing 'title' field"
    assert "quote" in result, "Parsed rocket profile missing 'quote' field"
    assert "image" in result, "Parsed rocket profile missing 'image' field"
    assert "lineups" in result, "Parsed rocket profile missing 'lineups' field"


def test_rocket_lineup_slots_parsing():
    """Test that rocket lineup slots are correctly parsed"""
    # Download data if needed
    html_file = download_rocket_lineups_data()

    # Read the current rocket lineups HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    rocket_profiles = soup.select(".rocket-profile")

    # Test first 2 rocket profiles
    valid_lineups_count = 0
    for _i, profile in enumerate(rocket_profiles[:2]):
        result = parse_rocket_trainer(profile, "https://leekduck.com")
        if result and "lineups" in result and len(result["lineups"]) > 0:
            # Check the first lineup slot
            first_slot = result["lineups"][0]
            if (
                "slot" in first_slot
                and "pokemon" in first_slot
                and len(first_slot["pokemon"]) > 0
            ):
                valid_lineups_count += 1

    # At least some should have valid lineups
    assert valid_lineups_count > 0, (
        "No rocket profiles with valid lineups found in first 2 profiles"
    )


def test_shadow_pokemon_parsing():
    """Test that shadow Pokemon are correctly parsed"""
    # Download data if needed
    html_file = download_rocket_lineups_data()

    # Read the current rocket lineups HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    shadow_pokemon_elements = soup.select(".shadow-pokemon")

    # Should have at least some shadow Pokemon
    assert len(shadow_pokemon_elements) > 0, "No shadow Pokemon found in the HTML"

    # Test the first shadow Pokemon
    first_pokemon = shadow_pokemon_elements[0]
    result = parse_shadow_pokemon(first_pokemon)

    # Should successfully parse the Pokemon
    assert result is not None, "Failed to parse first shadow Pokemon"

    # Should have expected fields
    assert "name" in result, "Parsed shadow Pokemon missing 'name' field"
    assert "types" in result, "Parsed shadow Pokemon missing 'types' field"
    assert "weaknesses" in result, "Parsed shadow Pokemon missing 'weaknesses' field"
    assert "image" in result, "Parsed shadow Pokemon missing 'image' field"
    assert "can_be_shiny" in result, (
        "Parsed shadow Pokemon missing 'can_be_shiny' field"
    )
