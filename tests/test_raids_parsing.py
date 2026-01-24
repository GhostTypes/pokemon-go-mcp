import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add the project root to the path so we can import the scraper
sys.path.insert(0, str(Path(__file__).parent))

from pogo_scraper.raids import parse_raid_boss


def download_raids_data():
    """Download current raids data if it doesn't exist"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    html_file = fixtures_dir / "current_raids.html"

    if not html_file.exists():
        response = requests.get("https://leekduck.com/boss/", timeout=30)
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        html_file.write_text(response.text, encoding="utf-8")
    return html_file


def test_raids_parsing():
    """Test that raids parsing works correctly"""
    # Download data if needed
    html_file = download_raids_data()

    # Read the current raids HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Find raid cards
    raid_cards = soup.select(".card")

    # Should have at least some raid cards
    assert len(raid_cards) > 0, "No raid cards found in the HTML"

    # Test the first raid card
    first_card = raid_cards[0]
    result = parse_raid_boss(first_card, "Tier 1", "https://leekduck.com")

    # Should successfully parse the card
    assert result is not None, "Failed to parse first raid card"

    # Should have expected fields
    assert "name" in result, "Parsed raid card missing 'name' field"
    assert "tier" in result, "Parsed raid card missing 'tier' field"
    assert "image" in result, "Parsed raid card missing 'image' field"
    assert "canBeShiny" in result, "Parsed raid card missing 'canBeShiny' field"
    assert "types" in result, "Parsed raid card missing 'types' field"
    assert "combatPower" in result, "Parsed raid card missing 'combatPower' field"
    assert "boostedWeather" in result, "Parsed raid card missing 'boostedWeather' field"


def test_raids_cp_values():
    """Test that raid CP values are correctly parsed"""
    # Download data if needed
    html_file = download_raids_data()

    # Read the current raids HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    raid_cards = soup.select(".card")

    # Test first 3 raid cards
    valid_cp_count = 0
    for _i, card in enumerate(raid_cards[:3]):
        result = parse_raid_boss(card, "Tier 1", "https://leekduck.com")
        if result and "combatPower" in result:
            cp_data = result["combatPower"]
            # Check if either normal or boosted CP has valid values
            if ("normal" in cp_data and cp_data["normal"]["min"] > 0) or (
                "boosted" in cp_data and cp_data["boosted"]["min"] > 0
            ):
                valid_cp_count += 1

    # At least some should have valid CP values
    assert valid_cp_count > 0, (
        "No raid cards with valid CP values found in first 3 cards"
    )
