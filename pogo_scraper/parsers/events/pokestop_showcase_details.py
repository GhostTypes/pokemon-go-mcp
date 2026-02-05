"""
Handles parsing extra event information for PokéStop Showcase events
"""

import logging
from typing import Any

from bs4 import BeautifulSoup

from .generic_event_details import _extract_pokemon_data

logger = logging.getLogger(__name__)


def _parse_showcase_pokemon(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Parse showcase Pokemon from the event page."""
    pokemon: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    page_content = soup.select_one(".page-content")
    if not page_content:
        return pokemon

    for item in page_content.select(".pkmn-list-item"):
        data = _extract_pokemon_data(item)
        if data:
            name = data.get("name")
            if name and name not in seen_names:
                pokemon.append(data)
                seen_names.add(name)

    return pokemon


async def parse_pokestop_showcase_details(
    soup: BeautifulSoup,
    event: dict[str, Any],
) -> None:
    """Parse PokéStop Showcase specific details."""
    try:
        showcase_data: dict[str, Any] = {
            "showcasePokemon": _parse_showcase_pokemon(soup),
        }

        if showcase_data["showcasePokemon"]:
            event["extraData"]["pokestopshowcase"] = showcase_data  # type: ignore[dict-item]
            logger.info(
                "PokéStop Showcase details: %s showcase Pokemon",
                len(showcase_data["showcasePokemon"]),
            )
        else:
            logger.warning("No PokéStop Showcase Pokemon found")

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing PokéStop Showcase details: %s", e)
