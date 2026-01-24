"""
Handles parsing extra event information for raid battles
"""

import logging
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import PageElement

logger = logging.getLogger(__name__)


async def parse_raid_battle_details(soup: BeautifulSoup, event: dict[str, Any]) -> None:
    """Parse Raid Battle specific details"""
    try:
        raidbattle_data: dict[str, Any] = {"bosses": [], "shinies": []}

        page_content = soup.select_one(".page-content")
        if not page_content:
            return

        last_header = ""

        # Process page content sections - get ALL child elements (including text nodes)
        # Use page_content.contents to get all nodes (like ScrapedDuck's childNodes)
        all_nodes = page_content.contents

        for element in all_nodes:
            # Check if this is a Tag element (skip NavigableString nodes)
            if isinstance(element, PageElement) and hasattr(element, "name") and element.name:
                # Get classes safely
                classes = element.get("class", [])
                if isinstance(classes, list) and "event-section-header" in classes:
                    last_header = element.get("id", "")

                # Parse raid bosses section
                elif isinstance(classes, list) and "pkmn-list-flex" in classes:
                    if last_header == "raids":
                        bosses = element.select(".pkmn-list-item")
                        for boss in bosses:
                            name_elem = boss.select_one(".pkmn-name")
                            img_elem = boss.select_one(".pkmn-list-img img")
                            shiny_elem = boss.select_one(".shiny-icon")

                            if name_elem and img_elem:
                                bosses_list = raidbattle_data["bosses"]
                                if isinstance(bosses_list, list):
                                    bosses_list.append(
                                        {
                                            "name": name_elem.get_text(strip=True),
                                            "image": img_elem.get("src", ""),
                                            "canBeShiny": shiny_elem is not None,
                                        }
                                    )

                    # Parse shinies section
                    elif last_header == "shiny":
                        shinies = element.select(".pkmn-list-item")
                        for shiny in shinies:
                            name_elem = shiny.select_one(".pkmn-name")
                            img_elem = shiny.select_one(".pkmn-list-img img")

                            if name_elem and img_elem:
                                shinies_list = raidbattle_data["shinies"]
                                if isinstance(shinies_list, list):
                                    shinies_list.append(
                                        {
                                            "name": name_elem.get_text(strip=True),
                                            "image": img_elem.get("src", ""),
                                        }
                                    )

        # Only add raidbattles data if we found meaningful content
        if raidbattle_data["bosses"] or raidbattle_data["shinies"]:
            event["extraData"]["raidbattles"] = raidbattle_data  # type: ignore[dict-item]

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing Raid Battle details: %s", e)
