from dataclasses import dataclass
from typing import Any, TypedDict


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
    combat_power: dict[str, Any] | None = None


@dataclass
class BonusInfo:
    """Community day bonus information"""

    text: str
    image: str


class EventExtraData(TypedDict, total=False):
    """Additional event-specific data"""

    generic: dict[str, Any]
    communityday: dict[str, Any]
    raidbattles: dict[str, Any]
    raidday: dict[str, Any]
    spotlight: dict[str, Any]
    breakthrough: dict[str, Any]


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
    extra_data: EventExtraData | None = None


@dataclass
class RaidInfo:
    """Raid boss information"""

    name: str
    tier: str
    can_be_shiny: bool
    types: list[TypeInfo]
    combat_power: dict[str, Any]
    boosted_weather: list[WeatherInfo]
    image: str
    extra_data: dict[str, Any] | None = None


@dataclass
class ResearchTaskInfo:
    """Field research task information"""

    text: str
    rewards: list[PokemonInfo]
    task_type: str | None = None


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
    types: list[str]
    weaknesses: dict[str, list[str]]
    image: str
    can_be_shiny: bool


@dataclass
class RocketLineupSlot:
    """Individual slot in a Rocket trainer's lineup"""

    slot: int
    is_encounter: bool
    pokemon: list[ShadowPokemonInfo]


@dataclass
class RocketTrainerInfo:
    """Team Rocket trainer information"""

    name: str
    title: str
    quote: str
    image: str
    type: str
    lineups: list[RocketLineupSlot]


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
    rewards: list[PromoCodeReward]
    expiration: str


@dataclass
class ApiData:
    """Complete API data structure"""

    events: list[EventInfo]
    raids: list[RaidInfo]
    research: list[ResearchTaskInfo]
    eggs: list[EggInfo]
    rocket_lineups: list[RocketTrainerInfo]
    promo_codes: list[PromoCodeInfo]
