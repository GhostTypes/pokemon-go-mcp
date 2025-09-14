from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TypeInfo:
    """Pokemon type information"""
    name: str
    image: str


@dataclass
class WeatherInfo:
    """Weather boost information"""
    name: str
    image: str


@dataclass
class PokemonInfo:
    """Basic Pokemon information"""
    name: str
    image: str
    can_be_shiny: bool = False
    combat_power: Optional[Dict] = None


@dataclass
class BonusInfo:
    """Community day bonus information"""
    text: str
    image: str


@dataclass
class EventExtraData:
    """Additional event-specific data"""
    generic: Optional[Dict] = None
    communityday: Optional[Dict] = None
    raidbattles: Optional[Dict] = None
    spotlight: Optional[Dict] = None
    breakthrough: Optional[Dict] = None


@dataclass
class EventInfo:
    """Event information"""
    event_id: str
    name: str
    event_type: str
    heading: str
    link: str
    image: str
    start: str
    end: str
    extra_data: Optional[EventExtraData] = None


@dataclass
class RaidInfo:
    """Raid boss information"""
    name: str
    tier: str
    can_be_shiny: bool
    types: List[TypeInfo]
    combat_power: Dict
    boosted_weather: List[WeatherInfo]
    image: str
    extra_data: Optional[Dict] = None


@dataclass
class ResearchTaskInfo:
    """Field research task information"""
    text: str
    rewards: List[PokemonInfo]
    task_type: Optional[str] = None


@dataclass
class EggInfo:
    """Egg hatch information"""
    name: str
    egg_type: str
    is_adventure_sync: bool
    image: str
    can_be_shiny: bool
    combat_power: int
    is_regional: bool
    is_gift_exchange: bool
    is_route_gift: bool
    rarity: int


@dataclass
class ShadowPokemonInfo:
    """Shadow Pokemon information for Team Rocket encounters"""
    name: str
    types: List[str]
    weaknesses: Dict[str, List[str]]
    image: str
    can_be_shiny: bool


@dataclass
class RocketLineupSlot:
    """Individual slot in a Rocket trainer's lineup"""
    slot: int
    is_encounter: bool
    pokemon: List[ShadowPokemonInfo]


@dataclass
class RocketTrainerInfo:
    """Team Rocket trainer information"""
    name: str
    title: str
    quote: str
    image: str
    type: str
    lineups: List[RocketLineupSlot]


@dataclass
class PromoCodeReward:
    """Reward information for a promo code"""
    name: str
    url: str
    type: str


@dataclass
class PromoCodeInfo:
    """Promo code information"""
    code: str
    title: str
    description: str
    redemption_url: str
    rewards: List[PromoCodeReward]
    expiration: str


@dataclass
class ApiData:
    """Complete API data structure"""
    events: List[EventInfo]
    raids: List[RaidInfo]
    research: List[ResearchTaskInfo]
    eggs: List[EggInfo]
    rocket_lineups: List[RocketTrainerInfo]
    promo_codes: List[PromoCodeInfo]
