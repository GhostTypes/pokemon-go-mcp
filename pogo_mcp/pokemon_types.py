"""Pokemon type lookup service using PokeAPI.

This module provides functionality to look up Pokemon types from PokeAPI
for type effectiveness calculations, allowing weakness calculations for any
Pokemon (not just those in Team Rocket lineups).
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Cache for Pokemon type data to avoid repeated API calls
_pokemon_type_cache: dict[str, dict[str, Any]] = {}

# HTTP status code constants
HTTP_STATUS_NOT_FOUND = 404

# Weakness count thresholds
DOUBLE_WEAK_THRESHOLD = 2


async def fetch_pokemon_types(pokemon_name: str) -> dict[str, Any] | None:
    """Fetch Pokemon types from PokeAPI.

    Args:
        pokemon_name: Name of the Pokemon to look up (case-insensitive)

    Returns:
        Dictionary with 'types' (list of type names) and 'weaknesses' (calculated),
        or None if Pokemon not found
    """
    # Normalize Pokemon name (lowercase, replace spaces with hyphens)
    normalized_name = pokemon_name.lower().strip().replace(" ", "-").replace("'", "")

    # Check cache first
    if normalized_name in _pokemon_type_cache:
        logger.debug("Using cached type data for %s", pokemon_name)
        return _pokemon_type_cache[normalized_name]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to fetch from PokeAPI
            url = f"https://pokeapi.co/api/v2/pokemon/{normalized_name}"
            response = await client.get(url)

            if response.status_code == HTTP_STATUS_NOT_FOUND:
                logger.warning("Pokemon '%s' not found in PokeAPI", pokemon_name)
                return None

            response.raise_for_status()
            data = response.json()

            # Extract type names
            types = [type_info["type"]["name"] for type_info in data.get("types", [])]

            # Calculate weaknesses using type chart
            weaknesses = calculate_weaknesses_from_types(types)

            result = {
                "name": data.get("name", pokemon_name),
                "types": types,
                "weaknesses": weaknesses,
            }

            # Cache the result
            _pokemon_type_cache[normalized_name] = result
            logger.info("Fetched types for %s from PokeAPI: %s", pokemon_name, types)

            return result

    except httpx.TimeoutException:
        logger.exception(
            "Timeout fetching Pokemon data from PokeAPI for '%s'", pokemon_name
        )
        return None
    except httpx.HTTPError:
        logger.exception("HTTP error fetching Pokemon data")
        return None
    except Exception:
        logger.exception("Error fetching Pokemon types for '%s'", pokemon_name)
        return None


def calculate_weaknesses_from_types(types: list[str]) -> dict[str, list[str]]:
    """Calculate weaknesses from Pokemon types using the type chart.

    Args:
        types: List of Pokemon type names (lowercase)

    Returns:
        Dictionary with 'double' and 'single' weakness lists
    """
    # Complete type effectiveness chart
    # Key: defending type, Value: dict of weak_to, resists, immune_to
    type_chart = {
        "normal": {
            "weak_to": ["fighting"],
            "resists": [],
            "immune_to": ["ghost"],
        },
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

    # Calculate weaknesses
    weakness_counts: dict[str, int] = {}

    for pokemon_type in types:
        pokemon_type_lower = pokemon_type.lower()
        if pokemon_type_lower not in type_chart:
            continue

        type_data = type_chart[pokemon_type_lower]
        for weak_type in type_data["weak_to"]:
            weakness_counts[weak_type] = weakness_counts.get(weak_type, 0) + 1

    # Categorize weaknesses
    double_weak = [
        t for t, count in weakness_counts.items() if count >= DOUBLE_WEAK_THRESHOLD
    ]
    single_weak = [t for t, count in weakness_counts.items() if count == 1]

    return {"double": double_weak, "single": single_weak}


def clear_type_cache() -> None:
    """Clear the Pokemon type cache."""
    _pokemon_type_cache.clear()
    logger.info("Pokemon type cache cleared")
