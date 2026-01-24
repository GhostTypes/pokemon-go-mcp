import asyncio
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add the project root to the path so we can import the scraper
sys.path.insert(0, str(Path(__file__).parent))

from pogo_scraper.events import infer_event_type, parse_timed_research_code_details


def download_timed_research_event_data():
    """Download timed research event data if it doesn't exist"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    html_file = fixtures_dir / "timed_research_event.html"

    if not html_file.exists():
        response = requests.get(
            "https://leekduck.com/events/max-finale-promo-code/", timeout=30
        )
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        html_file.write_text(response.text, encoding="utf-8")
    return html_file


def test_timed_research_event_type_inference():
    """Test that timed research event type is correctly inferred"""
    # Test event name with "promo" and "research"
    event_type = infer_event_type("Promo Code for Max Finale Timed Research", "Event")
    assert event_type == "timed-research-promo", (
        f"Expected 'timed-research-promo', got '{event_type}'"
    )

    # Test with different variations
    event_type = infer_event_type("Promo Code for Timed Research", "Event")
    assert event_type == "timed-research-promo", (
        f"Expected 'timed-research-promo', got '{event_type}'"
    )


def test_timed_research_code_extraction():
    """Test that timed research code is extracted correctly"""
    # Download data if needed
    html_file = download_timed_research_event_data()

    # Read the timed research event HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Look for the specific timed research code element
    # Looking for: <h2 id="timed-research-code-gofestmax">Timed Research Code:
    # GOFESTMAX</h2>
    code_header = soup.find("h2", id="timed-research-code-gofestmax")

    # Should find the timed research code header
    assert code_header is not None, "Timed research code header not found"

    # Extract code from header text
    header_text = code_header.get_text(strip=True)
    expected_text = "Timed Research Code: GOFESTMAX"
    assert header_text == expected_text, (
        f"Expected '{expected_text}', got '{header_text}'"
    )

    # Extract the code (GOFESTMAX)
    code = header_text.split(":")[-1].strip()
    assert code == "GOFESTMAX", f"Expected code 'GOFESTMAX', got '{code}'"


def test_timed_research_expiration_extraction():
    """Test that timed research expiration dates are extracted correctly"""
    # Download data if needed
    html_file = download_timed_research_event_data()

    # Read the timed research event HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Look for expiration information in list items
    list_items = soup.find_all("li")

    # Look for "Code expires" and "Research expires" information
    code_expires = None
    research_expires = None

    for li in list_items:
        text = li.get_text(strip=True)
        if "Code expires:" in text:
            code_expires = text
        elif "Research expires:" in text:
            research_expires = text

    # Should find both expiration dates
    assert code_expires is not None, "Code expiration date not found"
    assert research_expires is not None, "Research expiration date not found"

    # Check that they contain the expected dates
    code_date = "August 3, 2025"
    assert code_date in code_expires, (
        f"Code expiration should contain '{code_date}', got '{code_expires}'"
    )
    research_date = "Sunday, August 24, 2025"
    assert research_date in research_expires, (
        f"Research expiration should contain '{research_date}', "
        f"got '{research_expires}'"
    )


def test_timed_research_details_parsing():
    """Test that timed research details are correctly parsed"""
    # Download data if needed
    html_file = download_timed_research_event_data()

    # Read the timed research event HTML file
    html_content = html_file.read_text(encoding="utf-8")

    # Create a mock event dictionary
    event = {"extraData": {}}

    # Parse the live HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")

    # Call the function (it's async, so we need to handle that)
    asyncio.run(parse_timed_research_code_details(soup, event))

    # Check that the timed research data was added to extraData
    assert "timedresearch" in event["extraData"], (
        "Timed research data not found in extraData"
    )

    timed_research_data = event["extraData"]["timedresearch"]

    # Check that all expected fields are present
    assert "code" in timed_research_data, "Code field missing from timed research data"
    assert "code_expires" in timed_research_data, (
        "Code expires field missing from timed research data"
    )
    assert "research_expires" in timed_research_data, (
        "Research expires field missing from timed research data"
    )

    # Check the values
    assert timed_research_data["code"] == "GOFESTMAX", (
        f"Expected code 'GOFESTMAX', got '{timed_research_data['code']}'"
    )
    code_expiration = "August 3, 2025"
    assert code_expiration in timed_research_data["code_expires"], (
        f"Code expires should contain '{code_expiration}', "
        f"got '{timed_research_data['code_expires']}'"
    )
    research_expiration = "Sunday, August 24, 2025"
    assert research_expiration in timed_research_data["research_expires"], (
        f"Research expires should contain '{research_expiration}', "
        f"got '{timed_research_data['research_expires']}'"
    )
