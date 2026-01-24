import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add the project root to the path so we can import the scraper
sys.path.insert(0, str(Path(__file__).parent))

from pogo_scraper.research import parse_research_task


def download_research_data():
    """Download current research data if it doesn't exist"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    html_file = fixtures_dir / "current_research.html"

    if not html_file.exists():
        response = requests.get("https://leekduck.com/research/", timeout=30)
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        html_file.write_text(response.text, encoding="utf-8")
    return html_file


def test_research_parsing():
    """Test that research parsing works correctly"""
    # Download data if needed
    html_file = download_research_data()

    # Read the current research HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Find research items
    research_items = soup.select(".task-item")

    # Should have at least some research items
    assert len(research_items) > 0, "No research items found in the HTML"

    # Test the first research item
    first_item = research_items[0]
    result = parse_research_task(first_item)

    # Should successfully parse the item
    assert result is not None, "Failed to parse first research item"

    # Should have expected fields
    assert "text" in result, "Parsed research item missing 'text' field"
    assert "rewards" in result, "Parsed research item missing 'rewards' field"

    # Should have at least one reward
    assert len(result["rewards"]) > 0, "Parsed research item has no rewards"


def test_research_rewards_parsing():
    """Test that research rewards are correctly parsed"""
    # Download data if needed
    html_file = download_research_data()

    # Read the current research HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    research_items = soup.select(".task-item")

    # Test first 3 research items
    valid_rewards_count = 0
    for _i, item in enumerate(research_items[:3]):
        result = parse_research_task(item)
        if result and "rewards" in result and len(result["rewards"]) > 0:
            # Check the first reward
            first_reward = result["rewards"][0]
            if "name" in first_reward and "image" in first_reward:
                valid_rewards_count += 1

    # At least some should have valid rewards
    assert valid_rewards_count > 0, (
        "No research items with valid rewards found in first 3 items"
    )
