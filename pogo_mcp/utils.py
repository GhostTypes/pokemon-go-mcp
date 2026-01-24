"""Utility functions for the Pokemon Go MCP server."""

import json
import logging
from datetime import datetime, timezone
from typing import Any, cast

from dateutil import parser

from .types import (
    EggInfo,
    EventInfo,
    PokemonInfo,
    RaidInfo,
    ResearchTaskInfo,
    RocketTrainerInfo,
    ShadowPokemonInfo,
)

logger = logging.getLogger(__name__)


def parse_datetime(date_string: str) -> datetime | None:
    """Parse a date string into a datetime object."""
    if not date_string:
        return None

    try:
        # Try parsing with dateutil first
        return parser.parse(date_string)
    except (ValueError, TypeError, OverflowError) as e:
        logger.warning("Failed to parse date '%s': %s", date_string, e)
        return None


def is_event_active(event: EventInfo, current_time: datetime | None = None) -> bool:
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


def is_event_upcoming(event: EventInfo, current_time: datetime | None = None) -> bool:
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


def search_pokemon_by_name(
    name: str, pokemon_list: list[PokemonInfo]
) -> list[PokemonInfo]:
    """Search for Pokemon by name (case-insensitive, partial match)."""
    name_lower = name.lower()
    return [p for p in pokemon_list if name_lower in p.name.lower()]


def filter_shiny_pokemon(pokemon_list: list[PokemonInfo]) -> list[PokemonInfo]:
    """Filter Pokemon list to only include those that can be shiny."""
    return [p for p in pokemon_list if p.can_be_shiny]


def filter_raids_by_tier(raids: list[RaidInfo], tier: str) -> list[RaidInfo]:
    """Filter raids by tier."""
    tier_lower = tier.lower()
    return [r for r in raids if tier_lower in r.tier.lower()]


def filter_raids_by_type(raids: list[RaidInfo], pokemon_type: str) -> list[RaidInfo]:
    """Filter raids by Pokemon type."""
    type_lower = pokemon_type.lower()
    return [r for r in raids if any(type_lower in t.name.lower() for t in r.types)]


def filter_eggs_by_distance(eggs: list[EggInfo], distance: str) -> list[EggInfo]:
    """Filter eggs by distance (e.g., '2 km', '5 km', '10 km', '5', 5)."""
    # Normalize distance input to handle both "5" and "5km" formats
    distance_str = str(distance).strip().lower()

    # If it's just a number, add " km" to match egg_type format
    if distance_str.isdigit() or (distance_str.replace(".", "").isdigit()):
        distance_normalized = f"{distance_str} km"
    else:
        # Remove "km" and add it back with proper spacing
        distance_clean = distance_str.replace("km", "").replace("k", "").strip()
        if distance_clean.isdigit() or (distance_clean.replace(".", "").isdigit()):
            distance_normalized = f"{distance_clean} km"
        else:
            # Use original if it doesn't match expected patterns
            distance_normalized = distance_str

    # Filter eggs by exact egg_type match
    filtered = []
    for egg in eggs:
        # Extract just the distance from egg_type (e.g., "2 km" from "2 km Adventure Sync")
        egg_distance = egg.egg_type.lower()
        # Handle cases like "2 km adventure sync" - extract just the "X km" part
        if " km" in egg_distance:
            parts = egg_distance.split()
            if len(parts) >= 2 and parts[1] == "km":
                egg_distance_only = f"{parts[0]} km"
                if egg_distance_only == distance_normalized:
                    filtered.append(egg)
        # Also check exact match for simple cases
        elif egg_distance == distance_normalized:
            filtered.append(egg)

    return filtered


def filter_research_by_reward(
    research: list[ResearchTaskInfo], pokemon_name: str
) -> list[ResearchTaskInfo]:
    """Filter research tasks by Pokemon reward name."""
    name_lower = pokemon_name.lower()
    return [
        r
        for r in research
        if any(name_lower in reward.name.lower() for reward in r.rewards)
    ]


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

    return f"""**{event.name}** ({status})
Type: {event.event_type}
Start: {start_str}
End: {end_str}
Link: {event.link}"""


def format_raid_summary(raid: RaidInfo) -> str:
    """Format a raid into a readable summary."""
    types_str = ", ".join([t.name.title() for t in raid.types])
    weather_str = ", ".join([w.name.title() for w in raid.boosted_weather])

    cp_normal = raid.combat_power.get("normal", {})
    cp_boosted = raid.combat_power.get("boosted", {})

    cp_info = ""
    if cp_normal:
        cp_info += (
            f"Normal CP: {cp_normal.get('min', 'N/A')}-{cp_normal.get('max', 'N/A')}"
        )
    if cp_boosted:
        if cp_info:
            cp_info += " | "
        cp_info += (
            f"Boosted CP: {cp_boosted.get('min', 'N/A')}-{cp_boosted.get('max', 'N/A')}"
        )

    shiny_status = "✨ Can be Shiny" if raid.can_be_shiny else "❌ Not Shiny"

    return f"""**{raid.name}** ({raid.tier})
Types: {types_str}
{cp_info}
Weather Boost: {weather_str}
{shiny_status}"""


def format_research_summary(task: ResearchTaskInfo) -> str:
    """Format a research task into a readable summary."""
    rewards_str = ", ".join(
        [f"{r.name}{'✨' if r.can_be_shiny else ''}" for r in task.rewards]
    )

    task_type_str = f" ({task.task_type})" if task.task_type else ""

    return f"""**{task.text}**{task_type_str}
Possible Rewards: {rewards_str}
Note: You get ONE of the rewards listed, not all of them."""


def format_egg_summary(egg: EggInfo) -> str:
    """Format an egg Pokemon into a readable summary."""
    cp_info = ""
    if egg.combat_power and egg.combat_power != -1:
        cp_info = f"CP: {egg.combat_power}"

    features = []
    if egg.can_be_shiny:
        features.append("✨ Can be Shiny")
    if egg.is_regional:
        features.append("🌍 Regional")
    if egg.is_gift_exchange:
        features.append("🎁 Gift Exchange")
    if egg.is_route_gift:
        features.append("🛣️ Route Gift")
    if egg.is_adventure_sync:
        features.append("🏃 Adventure Sync")

    # Add rarity indicator
    if egg.rarity > 1:
        rarity_stars = "⭐" * egg.rarity
        features.append(f"Rarity: {rarity_stars}")

    features_str = " | ".join(features) if features else "Standard"

    return f"""**{egg.name}** ({egg.egg_type})
{cp_info}
{features_str}"""


def format_json_output(data: object, indent: int = 2) -> str:
    """Format data as pretty-printed JSON."""
    try:
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    except Exception as e:
        logger.exception("Failed to format JSON: %s", e)
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
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -'."
    )
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


def extract_community_day_info(event: EventInfo) -> dict[str, Any] | None:
    """Extract Community Day specific information from an event."""
    if not event.extra_data or "communityday" not in event.extra_data:
        return None

    cd_data = event.extra_data["communityday"]

    return {
        "featured_pokemon": [spawn.get("name") for spawn in cd_data.get("spawns", [])],
        "bonuses": [bonus.get("text") for bonus in cd_data.get("bonuses", [])],
        "shiny_available": [shiny.get("name") for shiny in cd_data.get("shinies", [])],
        "special_research": cd_data.get("specialresearch", []),
    }


def extract_raid_day_info(event: EventInfo) -> dict[str, Any] | None:
    """Extract Raid Day specific information from an event."""
    if not event.extra_data or "raidday" not in event.extra_data:
        return None

    rd_data = event.extra_data["raidday"]

    return {
        "raid_bosses": [boss.get("name") for boss in rd_data.get("bosses", [])],
        "bonuses": [bonus.get("text") for bonus in rd_data.get("bonuses", [])],
        "ticket_bonuses": [
            bonus.get("text") for bonus in rd_data.get("ticketBonuses", [])
        ],
        "research": rd_data.get("research", []),
        "shiny_available": [shiny.get("name") for shiny in rd_data.get("shinies", [])],
    }


# Team Rocket / Shadow Pokemon utilities
def format_rocket_summary(trainer: RocketTrainerInfo) -> str:
    """Format a Team Rocket trainer summary for display."""
    summary = f"**{trainer.name}**"
    if trainer.title:
        summary += f" - {trainer.title}"
    if trainer.type:
        summary += f" ({trainer.type.title()} type)"

    if trainer.quote:
        summary += f'\n*"{trainer.quote}"*'

    # Count total Pokemon options and encounters
    total_pokemon = sum(len(slot.pokemon) for slot in trainer.lineups)
    encounter_slots = [slot for slot in trainer.lineups if slot.is_encounter]
    encounter_pokemon = sum(len(slot.pokemon) for slot in encounter_slots)

    summary += (
        f"\n• {total_pokemon} Pokemon options across {len(trainer.lineups)} slots"
    )
    if encounter_pokemon > 0:
        summary += f"\n• {encounter_pokemon} possible encounter rewards"

    return summary


def filter_trainers_by_type(
    trainers: list[RocketTrainerInfo], trainer_type: str
) -> list[RocketTrainerInfo]:
    """Filter Team Rocket trainers by type."""
    trainer_type_lower = trainer_type.lower()
    return [t for t in trainers if t.type and t.type.lower() == trainer_type_lower]


def search_rocket_trainers_by_pokemon(
    trainers: list[RocketTrainerInfo], pokemon_name: str
) -> list[RocketTrainerInfo]:
    """Search for Team Rocket trainers that have a specific Pokemon."""
    pokemon_name_lower = pokemon_name.lower()
    matching_trainers = []

    for trainer in trainers:
        has_pokemon = False
        for slot in trainer.lineups:
            for pokemon in slot.pokemon:
                if pokemon_name_lower in pokemon.name.lower():
                    has_pokemon = True
                    break
            if has_pokemon:
                break

        if has_pokemon:
            matching_trainers.append(trainer)

    return matching_trainers


def get_shiny_shadow_pokemon(
    trainers: list[RocketTrainerInfo],
) -> list[ShadowPokemonInfo]:
    """Get all Shadow Pokemon that can be shiny."""
    shiny_pokemon = []
    seen_names = set()

    for trainer in trainers:
        for slot in trainer.lineups:
            for pokemon in slot.pokemon:
                if pokemon.can_be_shiny and pokemon.name not in seen_names:
                    shiny_pokemon.append(pokemon)
                    seen_names.add(pokemon.name)

    return sorted(shiny_pokemon, key=lambda p: p.name)


def get_rocket_encounters(
    trainers: list[RocketTrainerInfo],
) -> list[tuple[str, list[ShadowPokemonInfo]]]:
    """Get all possible Team Rocket encounter rewards organized by trainer."""
    encounters = []

    for trainer in trainers:
        encounter_pokemon = []
        for slot in trainer.lineups:
            if slot.is_encounter:
                encounter_pokemon.extend(slot.pokemon)

        if encounter_pokemon:
            encounters.append((trainer.name, encounter_pokemon))

    return encounters


def calculate_type_effectiveness(
    attacking_type: str, defending_types: list[str]
) -> float:
    """Calculate type effectiveness multiplier for Team Rocket battles."""
    # Simplified type effectiveness chart for common interactions
    TYPE_CHART = {
        "normal": {"weak_to": ["fighting"], "resists": [], "immune_to": ["ghost"]},
        "fire": {
            "weak_to": ["water", "ground", "rock"],
            "resists": ["fire", "grass", "ice", "bug", "steel", "fairy"],
            "immune_to": [],
        },
        "water": {
            "weak_to": ["grass", "electric"],
            "resists": ["fire", "water", "ice", "steel"],
            "immune_to": [],
        },
        "grass": {
            "weak_to": ["fire", "ice", "poison", "flying", "bug"],
            "resists": ["water", "electric", "grass", "ground"],
            "immune_to": [],
        },
        "electric": {
            "weak_to": ["ground"],
            "resists": ["flying", "steel", "electric"],
            "immune_to": [],
        },
        "ice": {
            "weak_to": ["fire", "fighting", "rock", "steel"],
            "resists": ["ice"],
            "immune_to": [],
        },
        "fighting": {
            "weak_to": ["flying", "psychic", "fairy"],
            "resists": ["rock", "bug", "dark"],
            "immune_to": [],
        },
        "poison": {
            "weak_to": ["ground", "psychic"],
            "resists": ["grass", "fighting", "poison", "bug", "fairy"],
            "immune_to": [],
        },
        "ground": {
            "weak_to": ["water", "grass", "ice"],
            "resists": ["poison", "rock"],
            "immune_to": ["electric"],
        },
        "flying": {
            "weak_to": ["electric", "ice", "rock"],
            "resists": ["grass", "fighting", "bug"],
            "immune_to": ["ground"],
        },
        "psychic": {
            "weak_to": ["bug", "ghost", "dark"],
            "resists": ["fighting", "psychic"],
            "immune_to": [],
        },
        "bug": {
            "weak_to": ["fire", "flying", "rock"],
            "resists": ["grass", "fighting", "ground"],
            "immune_to": [],
        },
        "rock": {
            "weak_to": ["water", "grass", "fighting", "ground", "steel"],
            "resists": ["normal", "fire", "poison", "flying"],
            "immune_to": [],
        },
        "ghost": {
            "weak_to": ["ghost", "dark"],
            "resists": ["poison", "bug"],
            "immune_to": ["normal", "fighting"],
        },
        "dragon": {
            "weak_to": ["ice", "dragon", "fairy"],
            "resists": ["fire", "water", "electric", "grass"],
            "immune_to": [],
        },
        "dark": {
            "weak_to": ["fighting", "bug", "fairy"],
            "resists": ["ghost", "dark"],
            "immune_to": ["psychic"],
        },
        "steel": {
            "weak_to": ["fire", "fighting", "ground"],
            "resists": [
                "normal",
                "grass",
                "ice",
                "flying",
                "psychic",
                "bug",
                "rock",
                "dragon",
                "steel",
                "fairy",
            ],
            "immune_to": ["poison"],
        },
        "fairy": {
            "weak_to": ["poison", "steel"],
            "resists": ["fighting", "bug", "dark"],
            "immune_to": ["dragon"],
        },
    }

    attacking_type = attacking_type.lower()
    effectiveness = 1.0

    for defending_type in defending_types:
        defending_type = defending_type.lower()

        if defending_type not in TYPE_CHART:
            continue

        type_data = TYPE_CHART[defending_type]

        # Check immunities (0x damage)
        if attacking_type in type_data["immune_to"]:
            return 0.0
        # Check weaknesses (2x damage)
        if attacking_type in type_data["weak_to"]:
            effectiveness *= 2.0
        # Check resistances (0.5x damage)
        elif attacking_type in type_data["resists"]:
            effectiveness *= 0.5

    return effectiveness
