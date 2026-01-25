#!/usr/bin/env python3
"""
Test to verify the egg scraper correctly handles multi-word Pokemon names
and detects actual HTML parsing errors (multiple span.name elements).
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import pogo_scraper
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup


def test_multi_word_pokemon_names_accepted():
    """Test that legitimate multi-word Pokemon names are accepted."""
    # Sample HTML with legitimate multi-word names
    html = """
    <ul class="egg-grid">
        <li class="pokemon-card">
            <span class="name">Basculin (White Striped)</span>
            <img src="test.png" />
        </li>
        <li class="pokemon-card">
            <span class="name">Indeedee (Male)</span>
            <img src="test.png" />
        </li>
        <li class="pokemon-card">
            <span class="name">Hisuian Qwilfish</span>
            <img src="test.png" />
        </li>
        <li class="pokemon-card">
            <span class="name">Galarian Meowth</span>
            <img src="test.png" />
        </li>
    </ul>
    """

    from pogo_scraper.eggs import parse_egg_item

    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("li.pokemon-card")

    results = []
    for card in cards:
        result = parse_egg_item(card, "10 km", is_adventure_sync=False, is_gift_exchange=False, is_route_gift=False)
        if result:
            results.append(result["name"])

    assert len(results) == 4, f"Expected 4 Pokemon, got {len(results)}"
    assert "Basculin (White Striped)" in results, "Basculin (White Striped) should be accepted"
    assert "Indeedee (Male)" in results, "Indeedee (Male) should be accepted"
    assert "Hisuian Qwilfish" in results, "Hisuian Qwilfish should be accepted"
    assert "Galarian Meowth" in results, "Galarian Meowth should be accepted"

    print("[PASS] All legitimate multi-word Pokemon names are correctly accepted")


def test_malformed_html_with_multiple_names_detected():
    """Test that cards with multiple span.name elements are rejected."""
    # Malformed HTML with two name elements in one card
    html = """
    <ul class="egg-grid">
        <li class="pokemon-card">
            <span class="name">Sableye</span>
            <span class="name">Toxel</span>
            <img src="test.png" />
        </li>
        <li class="pokemon-card">
            <span class="name">Bulbasaur</span>
            <img src="test.png" />
        </li>
    </ul>
    """

    from pogo_scraper.eggs import parse_egg_item

    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("li.pokemon-card")

    results = []
    for card in cards:
        result = parse_egg_item(card, "5 km", is_adventure_sync=False, is_gift_exchange=False, is_route_gift=False)
        if result:
            results.append(result["name"])

    # Only Bulbasaur should be parsed; Sableye+Toxel card should be skipped
    assert len(results) == 1, f"Expected 1 Pokemon (malformed card skipped), got {len(results)}"
    assert results[0] == "Bulbasaur", "Only Bulbasaur should be parsed"
    assert "Sableye" not in results, "Malformed Sableye card should be skipped"
    assert "Toxel" not in results, "Malformed Toxel card should be skipped"

    print("[PASS] Malformed HTML with multiple span.name elements is correctly detected and skipped")


def test_scraped_data_quality():
    """Test that the actual scraped data has no concatenated names."""
    eggs_file = Path("data/eggs.json")

    if not eggs_file.exists():
        print("[SKIP] data/eggs.json not found, skipping data quality test")
        return

    with eggs_file.open(encoding="utf-8") as f:
        data = json.load(f)

    # Check for known bad concatenated names
    names = [item["name"] for item in data]
    bad_names = [name for name in names if " " in name and "(" not in name and "-" not in name and len(name.split()) > 2]

    assert len(bad_names) == 0, f"Found potentially concatenated names: {bad_names}"

    # Verify legitimate multi-word names are present
    assert "Basculin (White Striped)" in names, "Basculin (White Striped) should be in data"

    print(f"[PASS] Scraped data quality check passed ({len(data)} Pokemon, no concatenated names)")


if __name__ == "__main__":
    test_multi_word_pokemon_names_accepted()
    test_malformed_html_with_multiple_names_detected()
    test_scraped_data_quality()
    print("\n[SUCCESS] All tests passed!")
