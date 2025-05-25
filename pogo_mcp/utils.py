"""Utility functions for the Pokemon Go MCP server."""

import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
from dateutil import parser

from .types import EventInfo, RaidInfo, ResearchTaskInfo, EggInfo, PokemonInfo

logger = logging.getLogger(__name__)


def parse_datetime(date_string: str) -> Optional[datetime]:
    """Parse a date string into a datetime object."""
    if not date_string:
        return None
    
    try:
        # Try parsing with dateutil first
        return parser.parse(date_string)
    except Exception as e:
        logger.warning(f"Failed to parse date '{date_string}': {e}")
        return None


def is_event_active(event: EventInfo, current_time: Optional[datetime] = None) -> bool:
    """Check if an event is currently active."""
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    start_time = parse_datetime(event.start)
    end_time = parse_datetime(event.end)
    
    if not start_time or not end_time:
        return False
    
    # Make timezone-aware if necessary
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    return start_time <= current_time <= end_time


def is_event_upcoming(event: EventInfo, current_time: Optional[datetime] = None) -> bool:
    """Check if an event is upcoming (starts in the future)."""
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    start_time = parse_datetime(event.start)
    
    if not start_time:
        return False
    
    # Make timezone-aware if necessary
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    return start_time > current_time


def search_pokemon_by_name(name: str, pokemon_list: List[PokemonInfo]) -> List[PokemonInfo]:
    """Search for Pokemon by name (case-insensitive, partial match)."""
    name_lower = name.lower()
    return [p for p in pokemon_list if name_lower in p.name.lower()]


def filter_shiny_pokemon(pokemon_list: List[PokemonInfo]) -> List[PokemonInfo]:
    """Filter Pokemon list to only include those that can be shiny."""
    return [p for p in pokemon_list if p.can_be_shiny]


def filter_raids_by_tier(raids: List[RaidInfo], tier: str) -> List[RaidInfo]:
    """Filter raids by tier."""
    tier_lower = tier.lower()
    return [r for r in raids if tier_lower in r.tier.lower()]


def filter_raids_by_type(raids: List[RaidInfo], pokemon_type: str) -> List[RaidInfo]:
    """Filter raids by Pokemon type."""
    type_lower = pokemon_type.lower()
    return [r for r in raids if any(type_lower in t.name.lower() for t in r.types)]


def filter_eggs_by_distance(eggs: List[EggInfo], distance: str) -> List[EggInfo]:
    """Filter eggs by distance (e.g., '2 km', '5 km', '10 km')."""
    distance_lower = distance.lower()
    return [e for e in eggs if distance_lower in e.egg_type.lower()]


def filter_research_by_reward(research: List[ResearchTaskInfo], pokemon_name: str) -> List[ResearchTaskInfo]:
    """Filter research tasks by Pokemon reward name."""
    name_lower = pokemon_name.lower()
    return [r for r in research if any(name_lower in reward.name.lower() for reward in r.rewards)]


def format_event_summary(event: EventInfo) -> str:
    """Format an event into a readable summary."""
    start_time = parse_datetime(event.start)
    end_time = parse_datetime(event.end)
    
    start_str = start_time.strftime("%Y-%m-%d %H:%M UTC") if start_time else "Unknown"
    end_str = end_time.strftime("%Y-%m-%d %H:%M UTC") if end_time else "Unknown"
    
    status = "🔴 Ended"
    current_time = datetime.now(timezone.utc)
    
    if is_event_active(event, current_time):
        status = "🟢 Active"
    elif is_event_upcoming(event, current_time):
        status = "🔵 Upcoming"
    
    summary = f"""**{event.name}** ({status})
Type: {event.event_type}
Start: {start_str}
End: {end_str}
Link: {event.link}"""
    
    return summary


def format_raid_summary(raid: RaidInfo) -> str:
    """Format a raid into a readable summary."""
    types_str = ", ".join([t.name.title() for t in raid.types])
    weather_str = ", ".join([w.name.title() for w in raid.boosted_weather])
    
    cp_normal = raid.combat_power.get("normal", {})
    cp_boosted = raid.combat_power.get("boosted", {})
    
    cp_info = ""
    if cp_normal:
        cp_info += f"Normal CP: {cp_normal.get('min', 'N/A')}-{cp_normal.get('max', 'N/A')}"
    if cp_boosted:
        if cp_info:
            cp_info += " | "
        cp_info += f"Boosted CP: {cp_boosted.get('min', 'N/A')}-{cp_boosted.get('max', 'N/A')}"
    
    shiny_status = "✨ Can be Shiny" if raid.can_be_shiny else "❌ Not Shiny"
    
    summary = f"""**{raid.name}** ({raid.tier})
Types: {types_str}
{cp_info}
Weather Boost: {weather_str}
{shiny_status}"""
    
    return summary


def format_research_summary(task: ResearchTaskInfo) -> str:
    """Format a research task into a readable summary."""
    rewards_str = ", ".join([
        f"{r.name}{'✨' if r.can_be_shiny else ''}" 
        for r in task.rewards
    ])
    
    task_type_str = f" ({task.task_type})" if task.task_type else ""
    
    summary = f"""**{task.text}**{task_type_str}
Possible Rewards: {rewards_str}
Note: You get ONE of the rewards listed, not all of them."""
    
    return summary


def format_egg_summary(egg: EggInfo) -> str:
    """Format an egg Pokemon into a readable summary."""
    cp_info = ""
    if egg.combat_power:
        cp_info = f"CP: {egg.combat_power.get('min', 'N/A')}-{egg.combat_power.get('max', 'N/A')}"
    
    features = []
    if egg.can_be_shiny:
        features.append("✨ Can be Shiny")
    if egg.is_regional:
        features.append("🌍 Regional")
    if egg.is_gift_exchange:
        features.append("🎁 Gift Exchange")
    if egg.is_adventure_sync:
        features.append("🏃 Adventure Sync")
    
    features_str = " | ".join(features) if features else "Standard"
    
    summary = f"""**{egg.name}** ({egg.egg_type})
{cp_info}
{features_str}"""
    
    return summary


def format_json_output(data: Any, indent: int = 2) -> str:
    """Format data as pretty-printed JSON."""
    try:
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to format JSON: {e}")
        return str(data)


def get_current_time_str() -> str:
    """Get current time as formatted string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def validate_pokemon_name(name: str) -> bool:
    """Validate that a Pokemon name is reasonable."""
    if not name or not isinstance(name, str):
        return False
    
    # Basic validation - should be 1-50 characters, alphanumeric plus spaces and hyphens
    if len(name) < 1 or len(name) > 50:
        return False
    
    # Allow letters, numbers, spaces, hyphens, and some special characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -'.")
    return all(c in allowed_chars for c in name)


def normalize_tier_name(tier: str) -> str:
    """Normalize tier names for consistent searching."""
    tier_lower = tier.lower().strip()
    
    # Handle common variations
    tier_mapping = {
        "1": "tier 1",
        "3": "tier 3", 
        "5": "tier 5",
        "mega": "mega",
        "legendary": "tier 5",
        "t1": "tier 1",
        "t3": "tier 3",
        "t5": "tier 5",
    }
    
    return tier_mapping.get(tier_lower, tier_lower)


def extract_community_day_info(event: EventInfo) -> Optional[Dict[str, Any]]:
    """Extract Community Day specific information from an event."""
    if not event.extra_data or "communityday" not in event.extra_data:
        return None
    
    cd_data = event.extra_data["communityday"]
    
    return {
        "featured_pokemon": [spawn.get("name") for spawn in cd_data.get("spawns", [])],
        "bonuses": [bonus.get("text") for bonus in cd_data.get("bonuses", [])],
        "shiny_available": [shiny.get("name") for shiny in cd_data.get("shinies", [])],
        "special_research": cd_data.get("specialresearch", [])
    }
