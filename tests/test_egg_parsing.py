import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add the project root to the path so we can import the scraper
sys.path.insert(0, str(Path(__file__).parent))

from pogo_scraper.eggs import parse_egg_item


def download_eggs_data():
    """Download current eggs data if it doesn't exist"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    html_file = fixtures_dir / "current_eggs.html"

    if not html_file.exists():
        response = requests.get("https://leekduck.com/eggs/", timeout=30)
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        html_file.write_text(response.text, encoding="utf-8")
    return html_file


def test_egg_parsing():
    """Test that egg parsing works correctly"""
    # Download data if needed
    html_file = download_eggs_data()

    # Read the current eggs HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Find all pokemon cards
    pokemon_cards = soup.select(".pokemon-card")

    # Should have at least some pokemon cards
    assert len(pokemon_cards) > 0, "No pokemon cards found in the HTML"

    # Get the first egg grid to test with
    first_grid = soup.select_one(".egg-grid")
    assert first_grid is not None, "No egg grid found in the HTML"

    first_cards = first_grid.select(".pokemon-card")
    assert len(first_cards) > 0, "No cards found in the first egg grid"

    # Test the first card
    first_card = first_cards[0]
    result = parse_egg_item(
        first_card, "2 km", is_adventure_sync=False, is_gift_exchange=False
    )

    # Should successfully parse the card
    assert result is not None, "Failed to parse first card"

    # Should have expected fields
    assert "name" in result, "Parsed card missing 'name' field"
    assert "combatPower" in result, "Parsed card missing 'combatPower' field"
    assert "image" in result, "Parsed card missing 'image' field"
    assert "canBeShiny" in result, "Parsed card missing 'canBeShiny' field"
    assert "rarity" in result, "Parsed card missing 'rarity' field"
    assert "isRouteGift" in result, "Parsed card missing 'isRouteGift' field"

    # CP value should be a positive integer (not -1)
    assert isinstance(result["combatPower"], int), "CP value should be an integer"
    assert result["combatPower"] > 0, (
        f"CP value should be positive, got {result['combatPower']}"
    )

    # Rarity should be a positive integer
    assert isinstance(result["rarity"], int), "Rarity value should be an integer"
    assert result["rarity"] >= 1, (
        f"Rarity value should be at least 1, got {result['rarity']}"
    )


def test_egg_cp_values():
    """Test that multiple egg CP values are correctly parsed"""
    # Download data if needed
    html_file = download_eggs_data()

    # Read the current eggs HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Get the first egg grid to test with
    first_grid = soup.select_one(".egg-grid")
    assert first_grid is not None, "No egg grid found in the HTML"

    first_cards = first_grid.select(".pokemon-card")

    # Test first 5 cards
    valid_cp_count = 0
    for _i, card in enumerate(first_cards[:5]):
        result = parse_egg_item(
            card, "2 km", is_adventure_sync=False, is_gift_exchange=False
        )
        if result and result["combatPower"] > 0:
            valid_cp_count += 1

    # At least some should have valid CP values
    assert valid_cp_count > 0, "No cards with valid CP values found in first 5 cards"


def test_egg_rarity_parsing():
    """Test that egg rarity is correctly parsed from mini-egg icons"""
    # Download data if needed
    html_file = download_eggs_data()

    # Read the current eggs HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Get the first egg grid to test with
    first_grid = soup.select_one(".egg-grid")
    assert first_grid is not None, "No egg grid found in the HTML"

    first_cards = first_grid.select(".pokemon-card")

    # Test first 5 cards for rarity parsing
    rarity_parsed = False
    for _i, card in enumerate(first_cards[:5]):
        result = parse_egg_item(
            card, "2 km", is_adventure_sync=False, is_gift_exchange=False
        )
        if result and "rarity" in result:
            # Rarity should be at least 1
            assert result["rarity"] >= 1, (
                f"Rarity should be at least 1, got {result['rarity']}"
            )
            rarity_parsed = True

    # At least some should have rarity values
    assert rarity_parsed, "No cards with rarity values found in first 5 cards"


def test_route_gift_egg_parsing():
    """Test that route gift eggs are correctly identified"""
    # Create a mock HTML element that represents a route gift egg

    # Mock HTML for a route gift egg card
    mock_html = """
    <li class="pokemon-card pokemon-card-7km">
        <div class="icon">
            <img
                src="https://cdn.leekduck.com/assets/img/pokemon_icons_crop/pm1.icon.png"
                alt="Bulbasaur"
            />
            <svg class="shiny-icon"><use href="#shiny-icon"/></svg>
        </div>
        <span class="name">Bulbasaur</span>
        <div class="cp-range">
            <span class="label">CP </span>637
        </div>
        <div class="rarity">
            <svg class="mini-egg"><use href="#mini-eggs-icon"/></svg>
            <svg class="mini-egg"><use href="#mini-eggs-icon"/></svg>
        </div>
    </li>
    """

    soup = BeautifulSoup(mock_html, "lxml")
    card = soup.select_one(".pokemon-card")

    # Test parsing with route gift flag
    result = parse_egg_item(
        card,
        "7 km",
        is_adventure_sync=False,
        is_gift_exchange=False,
        is_route_gift=True,
    )

    assert result is not None, "Failed to parse route gift egg card"
    assert result["isRouteGift"], "Route gift flag not set correctly"
    expected_rarity = 2
    assert (
        result["rarity"] == expected_rarity
    ), f"Expected rarity {expected_rarity}, got {result['rarity']}"
    assert result["name"] == "Bulbasaur", (
        f"Expected name 'Bulbasaur', got {result['name']}"
    )
