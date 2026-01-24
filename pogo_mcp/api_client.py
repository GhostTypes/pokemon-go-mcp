"""API client for fetching data from LeekDuck Pokemon Go API."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .types import (
    EggInfo,
    EventInfo,
    PokemonInfo,
    PromoCodeInfo,
    PromoCodeReward,
    RaidInfo,
    ResearchTaskInfo,
    RocketLineupSlot,
    RocketTrainerInfo,
    ShadowPokemonInfo,
    TypeInfo,
    WeatherInfo,
)

logger = logging.getLogger(__name__)


class LeekDuckAPIClient:
    """Client for fetching Pokemon Go data using local scraper."""

    def __init__(self, timeout: int = 30) -> None:
        """Initialize the API client."""
        self.timeout = timeout
        self._cache: dict[str, list[dict[str, Any]]] = {}
        self._cache_timestamp: dict[str, datetime] = {}
        self._cache_duration = 86400  # 24 hours cache

        # Path to local scraped data directory
        self._local_data_dir = Path(__file__).parent.parent / "data"

    def _load_local_data(self, endpoint: str) -> list[dict[str, Any]]:
        """Load data from local JSON files."""
        local_file = self._local_data_dir / f"{endpoint}.json"

        if not local_file.exists():
            logger.error(
                "Local file %s does not exist. Run the scraper first.", local_file
            )
            return []

        try:
            with local_file.open(encoding="utf-8") as f:
                data: list[dict[str, Any]] = json.load(f)
                logger.info("Loaded %d items from local %s data", len(data), endpoint)
                return data
        except (OSError, json.JSONDecodeError) as e:
            logger.exception("Error loading local %s data: %s", endpoint, e)
            return []

    async def _fetch_data(self, endpoint: str) -> list[dict[str, Any]]:
        """Fetch data from local files with simple caching."""
        now = datetime.now(timezone.utc)

        # Check if we have fresh cached data
        if (
            endpoint in self._cache
            and endpoint in self._cache_timestamp
            and (now - self._cache_timestamp[endpoint]).seconds < self._cache_duration
        ):
            logger.info("Using cached data for %s", endpoint)
            return self._cache[endpoint]

        # Load from local file
        data = self._load_local_data(endpoint)

        # Cache the data
        self._cache[endpoint] = data
        self._cache_timestamp[endpoint] = now

        return data

    async def get_events(self) -> list[EventInfo]:
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
                extra_data=extra_data,
            )
            events.append(event)

        return events

    async def get_raids(self) -> list[RaidInfo]:
        """Get all current raid bosses."""
        data = await self._fetch_data("raids")
        raids = []

        for item in data:
            # Parse types
            types = []
            for type_data in item.get("types", []):
                types.append(
                    TypeInfo(
                        name=type_data.get("name", ""), image=type_data.get("image", "")
                    )
                )

            # Parse boosted weather
            weather = []
            for weather_data in item.get("boostedWeather", []):
                weather.append(
                    WeatherInfo(
                        name=weather_data.get("name", ""),
                        image=weather_data.get("image", ""),
                    )
                )

            raid = RaidInfo(
                name=item.get("name", ""),
                tier=item.get("tier", ""),
                can_be_shiny=item.get("canBeShiny", False),
                types=types,
                combat_power=item.get("combatPower", {}),
                boosted_weather=weather,
                image=item.get("image", ""),
                extra_data=item.get("extra_data"),
            )
            raids.append(raid)

        return raids

    async def get_research(self) -> list[ResearchTaskInfo]:
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
                    can_be_shiny=reward_data.get("can_be_shiny", False),
                    combat_power=reward_data.get("combatPower"),
                )
                rewards.append(pokemon)

            task = ResearchTaskInfo(
                text=item.get("text", ""), rewards=rewards, task_type=item.get("type")
            )
            research_tasks.append(task)

        return research_tasks

    async def get_eggs(self) -> list[EggInfo]:
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
                combat_power=item.get("combatPower", -1),
                is_regional=item.get("isRegional", False),
                is_gift_exchange=item.get("isGiftExchange", False),
                is_route_gift=item.get("isRouteGift", False),
                rarity=item.get("rarity", 1),
            )
            eggs.append(egg)

        return eggs

    async def get_rocket_lineups(self) -> list[RocketTrainerInfo]:
        """Get all Team Rocket trainer lineups."""
        data = await self._fetch_data("rocket-lineups")
        trainers = []

        for item in data:
            # Parse lineup slots
            lineups = []
            for lineup_data in item.get("lineups", []):
                # Parse Pokemon in each slot
                pokemon_list = []
                for pokemon_data in lineup_data.get("pokemon", []):
                    shadow_pokemon = ShadowPokemonInfo(
                        name=pokemon_data.get("name", ""),
                        types=pokemon_data.get("types", []),
                        weaknesses=pokemon_data.get(
                            "weaknesses", {"double": [], "single": []}
                        ),
                        image=pokemon_data.get("image", ""),
                        can_be_shiny=pokemon_data.get("can_be_shiny", False),
                    )
                    pokemon_list.append(shadow_pokemon)

                lineup_slot = RocketLineupSlot(
                    slot=lineup_data.get("slot", 0),
                    is_encounter=lineup_data.get("is_encounter", False),
                    pokemon=pokemon_list,
                )
                lineups.append(lineup_slot)

            trainer = RocketTrainerInfo(
                name=item.get("name", ""),
                title=item.get("title", ""),
                quote=item.get("quote", ""),
                image=item.get("image", ""),
                type=item.get("type", ""),
                lineups=lineups,
            )
            trainers.append(trainer)

        return trainers

    async def get_promo_codes(self) -> list[PromoCodeInfo]:
        """Get all active promo codes."""
        data = await self._fetch_data("promo-codes")
        promo_codes = []

        for item in data:
            # Parse rewards
            rewards = []
            for reward_data in item.get("rewards", []):
                reward = PromoCodeReward(
                    name=reward_data.get("name", ""),
                    url=reward_data.get("url", ""),
                    type=reward_data.get("type", ""),
                )
                rewards.append(reward)

            promo_code = PromoCodeInfo(
                code=item.get("code", ""),
                title=item.get("title", ""),
                description=item.get("description", ""),
                redemption_url=item.get("redemption_url", ""),
                rewards=rewards,
                expiration=item.get("expiration", ""),
            )
            promo_codes.append(promo_code)

        return promo_codes

    def extract_raids_from_events(self, events_data: list[EventInfo]) -> list[RaidInfo]:
        """Extract raid boss data from events as fallback when raids.json is unavailable."""
        extracted_raids = []
        datetime.now(timezone.utc)

        # Simple tier inference based on common patterns
        def infer_tier(name: str) -> str:
            name_lower = name.lower()
            if name_lower.startswith("mega "):
                return "Mega"
            if any(
                legendary in name_lower
                for legendary in [
                    "palkia",
                    "dialga",
                    "giratina",
                    "rayquaza",
                    "kyogre",
                    "groudon",
                    "lugia",
                    "ho-oh",
                    "mewtwo",
                    "mew",
                    "celebi",
                    "jirachi",
                    "deoxys",
                    "reshiram",
                    "zekrom",
                    "kyurem",
                    "xerneas",
                    "yveltal",
                    "zygarde",
                ]
            ):
                return "5*"
            return "Unknown"

        for event in events_data:
            # Check if event contains raid data (skip time check for now - let server handle filtering)
            if event.extra_data and "raidbattles" in event.extra_data:
                raid_data = event.extra_data["raidbattles"]
                bosses = raid_data.get("bosses", [])

                for boss in bosses:
                    boss_name = boss.get("name", "Unknown")
                    # Create RaidInfo object from event boss data
                    raid = RaidInfo(
                        name=boss_name,
                        tier=infer_tier(boss_name),
                        can_be_shiny=boss.get("canBeShiny", False),
                        types=[],  # Would need to lookup types elsewhere
                        combat_power={
                            "normal": {"min": -1, "max": -1},
                            "boosted": {"min": -1, "max": -1},
                        },
                        boosted_weather=[],
                        image=boss.get("image", ""),
                        extra_data={
                            "source": "events_fallback",
                            "event_name": event.name,
                            "event_end": event.end,
                        },
                    )
                    extracted_raids.append(raid)

        logger.info(
            "Extracted %d raid bosses from %d events",
            len(extracted_raids),
            len(events_data),
        )
        return extracted_raids

    async def get_all_data(
        self,
    ) -> dict[
        str,
        list[EventInfo]
        | list[RaidInfo]
        | list[ResearchTaskInfo]
        | list[EggInfo]
        | list[RocketTrainerInfo]
        | list[PromoCodeInfo],
    ]:
        """Get all data from all endpoints with individual error handling."""
        logger.info("Fetching all Pokemon Go data...")

        # Initialize results with empty lists
        events = []
        raids = []
        research = []
        eggs = []
        rocket_lineups = []
        promo_codes = []

        # Fetch each data source individually with error handling
        try:
            events = await self.get_events()
            logger.info("Successfully fetched %d events", len(events))
        except (OSError, KeyError, TypeError) as e:
            logger.warning("Failed to fetch events data: %s", e)
            events = []

        try:
            raids = await self.get_raids()
        except (OSError, KeyError, TypeError) as e:
            logger.warning("Failed to fetch raids data from raids.json: %s", e)
            logger.info("Attempting to extract raid data from events as fallback...")
        else:
            if len(raids) > 0:
                logger.info("Successfully fetched %d raids from raids.json", len(raids))
            else:
                logger.warning(
                    "No raids data found in raids.json - attempting fallback..."
                )
                msg = "Empty raids data"
                raise ValueError(msg)

        try:
            research = await self.get_research()
            logger.info("Successfully fetched %d research tasks", len(research))
        except (OSError, KeyError, TypeError) as e:
            logger.warning("Failed to fetch research data: %s", e)
            research = []

        try:
            eggs = await self.get_eggs()
            logger.info("Successfully fetched %d egg data", len(eggs))
        except (OSError, KeyError, TypeError) as e:
            logger.warning("Failed to fetch eggs data: %s", e)
            eggs = []

        try:
            rocket_lineups = await self.get_rocket_lineups()
            logger.info(
                "Successfully fetched %d Team Rocket trainers",
                len(rocket_lineups),
            )
        except (OSError, KeyError, TypeError) as e:
            logger.warning("Failed to fetch rocket lineups data: %s", e)
            rocket_lineups = []

        try:
            promo_codes = await self.get_promo_codes()
            logger.info("Successfully fetched %d promo codes", len(promo_codes))
        except (OSError, KeyError, TypeError) as e:
            logger.warning("Failed to fetch promo codes data: %s", e)
            promo_codes = []

        logger.info("Completed fetching Pokemon Go data with individual error handling")

        return {
            "events": events,
            "raids": raids,
            "research": research,
            "eggs": eggs,
            "rocket_lineups": rocket_lineups,
            "promo_codes": promo_codes,
        }

    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info("Cache cleared")


# Global API client instance - using a function to ensure proper initialization
def get_api_client() -> "LeekDuckAPIClient":
    """Get the global API client instance."""
    global _api_client_instance
    if _api_client_instance is None:
        _api_client_instance = LeekDuckAPIClient()
    return _api_client_instance


# Initialize the global instance
_api_client_instance: Optional["LeekDuckAPIClient"] = None
api_client = get_api_client()
