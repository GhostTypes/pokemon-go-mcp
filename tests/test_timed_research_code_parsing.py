import json
import sys
import os
import requests
import pytest

# Add the project root to the path so we can import the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from pogo_scraper.events import infer_event_type


def download_timed_research_event_data():
    """Download timed research event data if it doesn't exist"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    html_file = os.path.join(fixtures_dir, 'timed_research_event.html')
    
    if not os.path.exists(html_file):
        print("Downloading timed research event data...")
        response = requests.get('https://leekduck.com/events/max-finale-promo-code/')
        os.makedirs(fixtures_dir, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete!")
    return html_file


def test_timed_research_event_type_inference():
    """Test that timed research event type is correctly inferred"""
    # Test event name with "promo" and "research"
    event_type = infer_event_type("Promo Code for Max Finale Timed Research", "Event")
    assert event_type == 'timed-research-promo', f"Expected 'timed-research-promo', got '{event_type}'"
    
    # Test with different variations
    event_type = infer_event_type("Promo Code for Timed Research", "Event")
    assert event_type == 'timed-research-promo', f"Expected 'timed-research-promo', got '{event_type}'"


def test_timed_research_code_extraction():
    """Test that timed research code is extracted correctly"""
    # Download data if needed
    html_file = download_timed_research_event_data()
    
    # Read the timed research event HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Look for the specific timed research code element
    # Looking for: <h2 id="timed-research-code-gofestmax">Timed Research Code: GOFESTMAX</h2>
    code_header = soup.find('h2', id='timed-research-code-gofestmax')
    
    # Should find the timed research code header
    assert code_header is not None, "Timed research code header not found"
    
    # Extract code from header text
    header_text = code_header.get_text(strip=True)
    expected_text = "Timed Research Code: GOFESTMAX"
    assert header_text == expected_text, f"Expected '{expected_text}', got '{header_text}'"
    
    # Extract the code (GOFESTMAX)
    code = header_text.split(":")[-1].strip()
    assert code == "GOFESTMAX", f"Expected code 'GOFESTMAX', got '{code}'"


def test_timed_research_expiration_extraction():
    """Test that timed research expiration dates are extracted correctly"""
    # Download data if needed
    html_file = download_timed_research_event_data()
    
    # Read the timed research event HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Look for expiration information in list items
    list_items = soup.find_all('li')
    
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
    assert "August 3, 2025" in code_expires, f"Code expiration should contain 'August 3, 2025', got '{code_expires}'"
    assert "Sunday, August 24, 2025" in research_expires, f"Research expiration should contain 'Sunday, August 24, 2025', got '{research_expires}'"


def test_timed_research_details_parsing():
    """Test that timed research details are correctly parsed"""
    # Import the function we want to test
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from pogo_scraper.events import parse_timed_research_code_details
    
    # Download data if needed
    html_file = download_timed_research_event_data()
    
    # Read the timed research event HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Create a mock event dictionary
    event = {
        'extraData': {}
    }
    
    # Parse the live HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Call the function (it's async, so we need to handle that)
    import asyncio
    asyncio.run(parse_timed_research_code_details(soup, event))
    
    # Check that the timed research data was added to extraData
    assert 'timedresearch' in event['extraData'], "Timed research data not found in extraData"
    
    timed_research_data = event['extraData']['timedresearch']
    
    # Check that all expected fields are present
    assert 'code' in timed_research_data, "Code field missing from timed research data"
    assert 'code_expires' in timed_research_data, "Code expires field missing from timed research data"
    assert 'research_expires' in timed_research_data, "Research expires field missing from timed research data"
    
    # Check the values
    assert timed_research_data['code'] == 'GOFESTMAX', f"Expected code 'GOFESTMAX', got '{timed_research_data['code']}'"
    assert 'August 3, 2025' in timed_research_data['code_expires'], f"Code expires should contain 'August 3, 2025', got '{timed_research_data['code_expires']}'"
    assert 'Sunday, August 24, 2025' in timed_research_data['research_expires'], f"Research expires should contain 'Sunday, August 24, 2025', got '{timed_research_data['research_expires']}'"