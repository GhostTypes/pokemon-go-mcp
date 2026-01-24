"""
Handles parsing rocket lineup information
"""

import contextlib
import logging
from typing import Any

from bs4.element import Tag

logger = logging.getLogger(__name__)


def parse_rocket_trainer(profile: Tag, base_url: str) -> dict[str, Any] | None:
    """Parse individual rocket trainer profile"""
    try:
        trainer: dict[str, Any] = {
            "name": "",
            "title": "",
            "quote": "",
            "image": "",
            "type": None,  # For grunt types
            "lineups": [],
        }

        # Get trainer info
        employee_info = profile.select_one(".employee-info")
        if not employee_info:
            return None

        # Name
        name_elem = employee_info.select_one(".name")
        trainer["name"] = name_elem.get_text(strip=True) if name_elem else ""

        # Title
        title_elem = employee_info.select_one(".title")
        trainer["title"] = title_elem.get_text(strip=True) if title_elem else ""

        # Quote
        quote_text_elem = employee_info.select_one(".quote-text")
        trainer["quote"] = (
            quote_text_elem.get_text(strip=True) if quote_text_elem else ""
        )

        # Image
        photo_img = employee_info.select_one(".photo img")
        if photo_img:
            trainer["image"] = photo_img.get("src", "")
            # Convert relative URLs to absolute
            image = trainer["image"]
            if isinstance(image, str) and image.startswith("/"):
                trainer["image"] = f"{base_url}{image}"

        # Type (for grunts) - search in the entire profile, not just employee_info
        # because .type is a sibling of .employee-info
        type_img = profile.select_one(".type img")
        if type_img:
            type_src = type_img.get("src", "")
            # Extract type name from image path
            # (e.g., "/assets/img/type_symbols/normal.png" -> "normal")
            if type_src:
                type_name = type_src.split("/")[-1].split(".")[0]
                trainer["type"] = type_name

        # Parse lineup slots
        lineup_info = profile.select_one(".lineup-info")
        if lineup_info:
            slots = lineup_info.select(".slot")
            for slot in slots:
                slot_data = parse_lineup_slot(slot)
                if slot_data:
                    lineups = trainer["lineups"]
                    if isinstance(lineups, list):
                        lineups.append(slot_data)

        return trainer if trainer["name"] else None

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing rocket trainer profile: %s", e)
        return None


def parse_lineup_slot(slot: Tag) -> dict[str, Any] | None:
    """Parse individual lineup slot with Pokemon options"""
    try:
        slot_data: dict[str, Any] = {"slot": 0, "is_encounter": False, "pokemon": []}

        # Get slot number
        number_elem = slot.select_one(".number")
        if number_elem:
            with contextlib.suppress(ValueError):
                slot_data["slot"] = int(number_elem.get_text(strip=True))

        # Check if this is an encounter slot (reward Pokemon)
        slot_data["is_encounter"] = bool(slot.select_one(".encounter-icon"))

        # Get all Pokemon in this slot
        shadow_pokemon = slot.select(".shadow-pokemon")
        for pokemon_elem in shadow_pokemon:
            pokemon = parse_shadow_pokemon(pokemon_elem)
            if pokemon:
                pokemon_list = slot_data["pokemon"]
                if isinstance(pokemon_list, list):
                    pokemon_list.append(pokemon)

        return slot_data if slot_data["pokemon"] else None

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing lineup slot: %s", e)
        return None


def parse_shadow_pokemon(pokemon_elem: Tag) -> dict[str, Any] | None:
    """Parse individual shadow Pokemon with weakness data"""
    try:
        pokemon: dict[str, Any] = {
            "name": "",
            "types": [],
            "weaknesses": {"double": [], "single": []},
            "image": "",
            "can_be_shiny": False,
        }

        # Name
        pokemon["name"] = pokemon_elem.get("data-pokemon", "").strip()

        # Types
        type1 = pokemon_elem.get("data-type1", "").strip().lower()
        type2 = pokemon_elem.get("data-type2", "").strip().lower()

        if type1 and type1 != "none":
            types = pokemon["types"]
            if isinstance(types, list):
                types.append(type1)
        if type2 and type2 != "none":
            types = pokemon["types"]
            if isinstance(types, list):
                types.append(type2)

        # Weaknesses
        double_weaknesses = pokemon_elem.get("data-double-weaknesses", "").strip()
        single_weaknesses = pokemon_elem.get("data-single-weaknesses", "").strip()

        if double_weaknesses:
            weaknesses = pokemon["weaknesses"]
            if isinstance(weaknesses, dict):
                double = weaknesses["double"]
                if isinstance(double, list):
                    double.extend([w.strip().lower() for w in double_weaknesses.split(",") if w.strip()])

        if single_weaknesses:
            weaknesses = pokemon["weaknesses"]
            if isinstance(weaknesses, dict):
                single = weaknesses["single"]
                if isinstance(single, list):
                    single.extend([w.strip().lower() for w in single_weaknesses.split(",") if w.strip()])

        # Image
        img_elem = pokemon_elem.select_one(".pokemon-image")
        pokemon["image"] = img_elem.get("src", "") if img_elem else ""

        # Shiny availability
        pokemon["can_be_shiny"] = bool(pokemon_elem.select_one(".shiny-icon"))

        return pokemon if pokemon["name"] else None

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing shadow Pokemon: %s", e)
        return None
