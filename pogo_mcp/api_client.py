"""API client for fetching data from LeekDuck Pokemon Go API."""

import asyncio
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timezone
from dateutil import parser

import httpx

from .types import (
    EventInfo, RaidInfo, ResearchTaskInfo, EggInfo, PokemonInfo, 
    TypeInfo, WeatherInfo, BonusInfo, EventExtraData, ApiData
)

logger = logging.getLogger(__name__)


class LeekDuckAPIClient:
    """Client for fetching Pokemon Go data from LeekDuck API."""
    
    BASE_URLS = {
        "events": "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/refs/heads/data/events.json",
        "raids": "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/refs/heads/data/raids.json", 
        "research": "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/refs/heads/data/research.json",
        "eggs": "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/refs/heads/data/eggs.json"
    }
    
    def __init__(self, timeout: int = 30):
        """Initialize the API client."""
        self.timeout = timeout
        self._cache: Dict[str, List[Dict]] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_duration = 300  # 5 minutes cache
    
    async def _fetch_data(self, endpoint: str) -> List[Dict]:
        """Fetch data from a specific endpoint with caching."""
        now = datetime.now(timezone.utc)
        
        # Check if we have fresh cached data
        if (endpoint in self._cache and 
            endpoint in self._cache_timestamp and
            (now - self._cache_timestamp[endpoint]).seconds < self._cache_duration):
            logger.info(f"Using cached data for {endpoint}")
            return self._cache[endpoint]
        
        url = self.BASE_URLS[endpoint]
        logger.info(f"Fetching data from {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()  # This is synchronous in httpx!
                
                # Cache the data
                self._cache[endpoint] = data
                self._cache_timestamp[endpoint] = now
                
                logger.info(f"Successfully fetched {len(data)} items from {endpoint}")
                return data
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching {endpoint}: {e}")
                raise
            except Exception as e:
                logger.error(f"Error fetching {endpoint}: {e}")
                raise
    
    async def get_events(self) -> List[EventInfo]:
        """Get all Pokemon Go events."""
        data = await self._fetch_data("events")
        events = []
        
        for item in data:
            # Parse extra data if present
            extra_data = None
            if "extraData" in item:
                extra_data = item["extraData"]
            
            event = EventInfo(
                event_id=item.get("eventID", ""),
                name=item.get("name", ""),
                event_type=item.get("eventType", ""),
                heading=item.get("heading", ""),
                link=item.get("link", ""),
                image=item.get("image", ""),
                start=item.get("start", ""),
                end=item.get("end", ""),
                extra_data=extra_data
            )
            events.append(event)
        
        return events
    
    async def get_raids(self) -> List[RaidInfo]:
        """Get all current raid bosses."""
        data = await self._fetch_data("raids")
        raids = []
        
        for item in data:
            # Parse types
            types = []
            for type_data in item.get("types", []):
                types.append(TypeInfo(
                    name=type_data.get("name", ""),
                    image=type_data.get("image", "")
                ))
            
            # Parse boosted weather
            weather = []
            for weather_data in item.get("boostedWeather", []):
                weather.append(WeatherInfo(
                    name=weather_data.get("name", ""),
                    image=weather_data.get("image", "")
                ))
            
            raid = RaidInfo(
                name=item.get("name", ""),
                tier=item.get("tier", ""),
                can_be_shiny=item.get("canBeShiny", False),
                types=types,
                combat_power=item.get("combatPower", {}),
                boosted_weather=weather,
                image=item.get("image", "")
            )
            raids.append(raid)
        
        return raids
    
    async def get_research(self) -> List[ResearchTaskInfo]:
        """Get all current field research tasks."""
        data = await self._fetch_data("research")
        research_tasks = []
        
        for item in data:
            # Parse rewards
            rewards = []
            for reward_data in item.get("rewards", []):
                pokemon = PokemonInfo(
                    name=reward_data.get("name", ""),
                    image=reward_data.get("image", ""),
                    can_be_shiny=reward_data.get("canBeShiny", False),
                    combat_power=reward_data.get("combatPower")
                )
                rewards.append(pokemon)
            
            task = ResearchTaskInfo(
                text=item.get("text", ""),
                rewards=rewards,
                task_type=item.get("type")
            )
            research_tasks.append(task)
        
        return research_tasks
    
    async def get_eggs(self) -> List[EggInfo]:
        """Get all Pokemon available from eggs."""
        data = await self._fetch_data("eggs")
        eggs = []
        
        for item in data:
            egg = EggInfo(
                name=item.get("name", ""),
                egg_type=item.get("eggType", ""),
                is_adventure_sync=item.get("isAdventureSync", False),
                image=item.get("image", ""),
                can_be_shiny=item.get("canBeShiny", False),
                combat_power=item.get("combatPower", {}),
                is_regional=item.get("isRegional", False),
                is_gift_exchange=item.get("isGiftExchange", False)
            )
            eggs.append(egg)
        
        return eggs
    
    async def get_all_data(self) -> Dict[str, Union[List[EventInfo], List[RaidInfo], List[ResearchTaskInfo], List[EggInfo]]]:
        """Get all data from all endpoints concurrently."""
        logger.info("Fetching all Pokemon Go data...")
        
        # Fetch all data concurrently
        events_task = asyncio.create_task(self.get_events())
        raids_task = asyncio.create_task(self.get_raids())
        research_task = asyncio.create_task(self.get_research())
        eggs_task = asyncio.create_task(self.get_eggs())
        
        events, raids, research, eggs = await asyncio.gather(
            events_task, raids_task, research_task, eggs_task
        )
        
        return {
            "events": events,
            "raids": raids, 
            "research": research,
            "eggs": eggs
        }
    
    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info("Cache cleared")


# Global API client instance - using a function to ensure proper initialization
def get_api_client() -> 'LeekDuckAPIClient':
    """Get the global API client instance."""
    global _api_client_instance
    if _api_client_instance is None:
        _api_client_instance = LeekDuckAPIClient()
    return _api_client_instance

# Initialize the global instance
_api_client_instance: Optional['LeekDuckAPIClient'] = None
api_client = get_api_client()
