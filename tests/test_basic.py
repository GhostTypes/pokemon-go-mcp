"""Tests for the API client and basic functionality."""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from pogo_mcp.api_client import LeekDuckAPIClient
from pogo_mcp.types import EventInfo, RaidInfo, ResearchTaskInfo, EggInfo
from pogo_mcp.utils import (
    is_event_active, is_event_upcoming, parse_datetime, 
    validate_pokemon_name, format_event_summary
)


class TestUtils:
    """Test utility functions."""
    
    def test_validate_pokemon_name(self):
        """Test Pokemon name validation."""
        # Valid names
        assert validate_pokemon_name("Pikachu") is True
        assert validate_pokemon_name("Mr. Mime") is True
        assert validate_pokemon_name("Ho-Oh") is True
        assert validate_pokemon_name("Nidoran♂") is False  # Special character not allowed
        
        # Invalid names
        assert validate_pokemon_name("") is False
        assert validate_pokemon_name(None) is False
        assert validate_pokemon_name("a" * 51) is False  # Too long
        assert validate_pokemon_name("Test@Pokemon") is False  # Invalid character
    
    def test_parse_datetime(self):
        """Test datetime parsing."""
        # Valid datetime string
        dt = parse_datetime("2025-05-24T14:00:00.000")
        assert dt is not None
        assert dt.year == 2025
        assert dt.month == 5
        assert dt.day == 24
        
        # Invalid datetime string
        dt = parse_datetime("invalid-date")
        assert dt is None
        
        # Empty string
        dt = parse_datetime("")
        assert dt is None
    
    def test_event_timing(self):
        """Test event active/upcoming detection."""
        current_time = datetime(2025, 5, 24, 15, 0, 0, tzinfo=timezone.utc)
        
        # Create test event (active)
        active_event = EventInfo(
            event_id="test-active",
            name="Test Active Event",
            event_type="community-day",
            heading="Community Day",
            link="https://example.com",
            image="https://example.com/image.jpg",
            start="2025-05-24T14:00:00.000",
            end="2025-05-24T17:00:00.000"
        )
        
        # Create test event (upcoming)
        upcoming_event = EventInfo(
            event_id="test-upcoming",
            name="Test Upcoming Event",
            event_type="spotlight",
            heading="Spotlight Hour",
            link="https://example.com",
            image="https://example.com/image.jpg",
            start="2025-05-25T18:00:00.000",
            end="2025-05-25T19:00:00.000"
        )
        
        assert is_event_active(active_event, current_time) is True
        assert is_event_upcoming(active_event, current_time) is False
        
        assert is_event_active(upcoming_event, current_time) is False
        assert is_event_upcoming(upcoming_event, current_time) is True
    
    def test_format_event_summary(self):
        """Test event summary formatting."""
        event = EventInfo(
            event_id="test-event",
            name="Test Event",
            event_type="community-day",
            heading="Community Day", 
            link="https://example.com",
            image="https://example.com/image.jpg",
            start="2025-05-24T14:00:00.000",
            end="2025-05-24T17:00:00.000"
        )
        
        summary = format_event_summary(event)
        assert "Test Event" in summary
        assert "2025-05-24" in summary
        assert "https://example.com" in summary


class TestAPIClient:
    """Test the LeekDuck API client."""
    
    def test_client_initialization(self):
        """Test API client initialization."""
        client = LeekDuckAPIClient(timeout=60)
        assert client.timeout == 60
        assert client._cache_duration == 300
        assert len(client._cache) == 0
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test caching mechanism."""
        client = LeekDuckAPIClient()
        
        # Mock HTTP response
        mock_data = [{"test": "data"}]
        
        with patch('httpx.AsyncClient') as mock_client:
            # Create a proper mock response that matches httpx behavior
            mock_response = AsyncMock()
            mock_response.json = lambda: mock_data  # Synchronous method like real httpx
            mock_response.raise_for_status = lambda: None  # Regular function, not async
            
            # Set up the async context manager and get method
            mock_http_client = AsyncMock()
            mock_http_client.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_http_client
            
            # First call should fetch from API
            result1 = await client._fetch_data("events")
            assert result1 == mock_data
            assert "events" in client._cache
            
            # Second call should use cache
            result2 = await client._fetch_data("events") 
            assert result2 == mock_data
            
            # Should only have made one HTTP request
            mock_http_client.get.assert_called_once()
    
    def test_clear_cache(self):
        """Test cache clearing."""
        client = LeekDuckAPIClient()
        client._cache["test"] = {"data": "test"}
        client._cache_timestamp["test"] = datetime.now(timezone.utc)
        
        client.clear_cache()
        
        assert len(client._cache) == 0
        assert len(client._cache_timestamp) == 0


@pytest.mark.asyncio
async def test_integration():
    """Integration test with mocked API responses."""
    
    # Mock event data
    mock_events = [{
        "eventID": "test-event",
        "name": "Test Community Day",
        "eventType": "community-day",
        "heading": "Community Day",
        "link": "https://example.com",
        "image": "https://example.com/image.jpg",
        "start": "2025-05-24T14:00:00.000",
        "end": "2025-05-24T17:00:00.000",
        "extraData": {}
    }]
    
    # Mock raid data
    mock_raids = [{
        "name": "Pikachu",
        "tier": "Tier 1",
        "canBeShiny": True,
        "types": [{"name": "electric", "image": "https://example.com/electric.png"}],
        "combatPower": {"normal": {"min": 500, "max": 600}},
        "boostedWeather": [{"name": "rainy", "image": "https://example.com/rainy.png"}],
        "image": "https://example.com/pikachu.png"
    }]
    
    client = LeekDuckAPIClient()
    
    with patch('httpx.AsyncClient') as mock_client:
        # Setup mock responses with proper async handling
        async def mock_get(url):
            mock_response = AsyncMock()
            mock_response.raise_for_status = lambda: None  # Regular function
            
            if "events.json" in url:
                mock_response.json = lambda: mock_events  # Synchronous like real httpx
            elif "raids.json" in url:
                mock_response.json = lambda: mock_raids  # Synchronous like real httpx
            else:
                mock_response.json = lambda: []  # Synchronous like real httpx
            
            return mock_response
        
        # Set up the async context manager
        mock_http_client = AsyncMock()
        mock_http_client.get = mock_get
        mock_client.return_value.__aenter__.return_value = mock_http_client
        
        # Test events
        events = await client.get_events()
        assert len(events) == 1
        assert events[0].name == "Test Community Day"
        assert events[0].event_type == "community-day"
        
        # Test raids
        raids = await client.get_raids()
        assert len(raids) == 1
        assert raids[0].name == "Pikachu"
        assert raids[0].can_be_shiny is True


if __name__ == "__main__":
    pytest.main([__file__])
