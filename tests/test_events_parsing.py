import json
import sys
import os
import requests
import pytest

# Add the project root to the path so we can import the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from pogo_scraper.scraper import LeekDuckScraper
from pogo_scraper.events import parse_event_item

def download_events_data():
    """Download current events data if it doesn't exist"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    html_file = os.path.join(fixtures_dir, 'current_events.html')
    
    if not os.path.exists(html_file):
        print("Downloading current events data...")
        response = requests.get('https://leekduck.com/events/')
        os.makedirs(fixtures_dir, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Download complete!")
    return html_file

def test_events_parsing():
    """Test that events parsing works correctly"""
    # Download data if needed
    html_file = download_events_data()
    
    # Read the current events HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find event items
    event_items = soup.select('a.event-item-link')
    
    # Should have at least some events
    assert len(event_items) > 0, "No events found in the HTML"
    
    # Test the first event
    first_event = event_items[0]
    result = parse_event_item(first_event, {}, 'https://leekduck.com')
    
    # Should successfully parse the event
    assert result is not None, "Failed to parse first event"
    
    # Should have expected fields
    assert 'name' in result, "Parsed event missing 'name' field"
    assert 'link' in result, "Parsed event missing 'link' field"
    assert 'image' in result, "Parsed event missing 'image' field"
    assert 'eventType' in result, "Parsed event missing 'eventType' field"

def test_events_list_parsing():
    """Test that multiple events are correctly parsed"""
    # Download data if needed
    html_file = download_events_data()
    
    # Read the current events HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    event_items = soup.select('a.event-item-link')

    # Test first 3 events
    parsed_count = 0
    for i, event_item in enumerate(event_items[:3]):
        result = parse_event_item(event_item, {}, 'https://leekduck.com')
        if result:
            parsed_count += 1
    
    # At least some should be successfully parsed
    assert parsed_count > 0, "No events successfully parsed in first 3 events"