"""Pokemon Go MCP Server - A comprehensive MCP server for Pokemon Go data."""

__version__ = "1.0.0"
__author__ = "GhostTypes"
__description__ = "A comprehensive MCP server for Pokemon Go events, raids, research, and eggs"

from .server import main
from .types import (
    BonusInfo,
    EggInfo,
    EventInfo,
    PokemonInfo,
    RaidInfo,
    ResearchTaskInfo,
    RocketLineupSlot,
    RocketTrainerInfo,
    ShadowPokemonInfo,
    TypeInfo,
    WeatherInfo,
)
from .utils import (
    format_egg_summary,
    format_event_summary,
    format_raid_summary,
    format_research_summary,
    is_event_active,
    is_event_upcoming,
)

__all__ = [
    "main",
    # Types
    "EventInfo",
    "RaidInfo",
    "ResearchTaskInfo",
    "EggInfo",
    "PokemonInfo",
    "TypeInfo",
    "WeatherInfo",
    "BonusInfo",
    "RocketTrainerInfo",
    "ShadowPokemonInfo",
    "RocketLineupSlot",
    # Utils
    "is_event_active",
    "is_event_upcoming",
    "format_event_summary",
    "format_raid_summary",
    "format_research_summary",
    "format_egg_summary",
]
