"""Type definitions for Pokemon Go MCP server."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PokemonInfo:
    """Information about a Pokemon."""
    name: str
    image: str
    can_be_shiny: bool = False
    combat_power: Optional[Dict[str, Dict[str, int]]] = None


@dataclass
class TypeInfo:
    """Pokemon type information."""
    name: str
    image: str


@dataclass
class WeatherInfo:
    """Weather information."""
    name: str
    image: str


@dataclass
class BonusInfo:
    """Event bonus information."""
    text: str
    image: str


@dataclass
class RewardInfo:
    """Research task reward information."""
    text: str
    image: str


@dataclass
class TaskInfo:
    """Research task information."""
    text: str
    reward: RewardInfo


@dataclass
class ResearchStepInfo:
    """Special research step information."""
    name: str
    step: int
    tasks: List[TaskInfo]


@dataclass
class EventExtraData:
    """Extra data for Community Day events."""
    spawns: List[PokemonInfo] = None
    bonuses: List[BonusInfo] = None
    bonus_disclaimers: List[str] = None
    shinies: List[PokemonInfo] = None
    special_research: List[ResearchStepInfo] = None

    def __post_init__(self):
        if self.spawns is None:
            self.spawns = []
        if self.bonuses is None:
            self.bonuses = []
        if self.bonus_disclaimers is None:
            self.bonus_disclaimers = []
        if self.shinies is None:
            self.shinies = []
        if self.special_research is None:
            self.special_research = []


@dataclass
class EventInfo:
    """Information about a Pokemon Go event."""
    event_id: str
    name: str
    event_type: str
    heading: str
    link: str
    image: str
    start: str
    end: str
    extra_data: Optional[Dict[str, Any]] = None


@dataclass
class RaidInfo:
    """Information about a raid boss."""
    name: str
    tier: str
    can_be_shiny: bool
    types: List[TypeInfo]
    combat_power: Dict[str, Dict[str, int]]
    boosted_weather: List[WeatherInfo]
    image: str
    extra_data: Optional[Dict[str, Any]] = None


@dataclass
class ResearchTaskInfo:
    """Information about a field research task."""
    text: str
    rewards: List[PokemonInfo]
    task_type: Optional[str] = None


@dataclass
class EggInfo:
    """Information about Pokemon hatching from eggs."""
    name: str
    egg_type: str
    is_adventure_sync: bool
    image: str
    can_be_shiny: bool
    combat_power: int
    is_regional: bool
    is_gift_exchange: bool


# Type aliases for common data structures
EventList = List[EventInfo]
RaidList = List[RaidInfo]
ResearchList = List[ResearchTaskInfo]
EggList = List[EggInfo]
ApiData = Dict[str, Any]
