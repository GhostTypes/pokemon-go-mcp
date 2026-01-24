"""
Handles parsing extra event information for raid days
"""

import contextlib
import logging
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def parse_raid_day_details(soup: BeautifulSoup, event: dict[str, Any]) -> None:
    """Parse Raid Day specific details"""
    try:
        raidday_data: dict[str, Any] = {
            "bosses": [],
            "bonuses": [],
            "ticketBonuses": [],
            "research": [],
            "shinies": [],
        }

        # Parse all sections
        free_bonuses, ticket_bonuses = _parse_bonuses_with_sections(soup)
        research = _parse_research(soup)
        shinies = _parse_shinies(soup)
        bosses = _parse_raid_bosses(soup)

        raidday_data["bonuses"] = free_bonuses
        raidday_data["ticketBonuses"] = ticket_bonuses
        raidday_data["research"] = research
        raidday_data["shinies"] = shinies
        raidday_data["bosses"] = bosses

        # Only add raidday data if we found meaningful content
        if (
            raidday_data["bosses"]
            or raidday_data["bonuses"]
            or raidday_data["research"]
            or raidday_data["shinies"]
        ):
            event["extraData"]["raidday"] = raidday_data  # type: ignore[dict-item]
            logger.info(
                "Raid Day details: %s bosses, %s bonuses, %s ticket bonuses, "
                "%s research, %s shinies",
                len(bosses),
                len(free_bonuses),
                len(ticket_bonuses),
                len(research),
                len(shinies),
            )
        else:
            logger.warning("No raid day details found")

    except (AttributeError, KeyError, ValueError, TypeError) as e:
        logger.warning("Error parsing Raid Day details: %s", e, exc_info=True)


def _parse_bonuses_with_sections(
    soup: BeautifulSoup,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse bonuses and ticket bonuses separately"""
    free_bonuses: list[dict[str, Any]] = []
    ticket_bonuses: list[dict[str, Any]] = []

    # Find the bonuses section
    bonuses_section = soup.find("h2", id="bonuses")
    if not bonuses_section:
        return free_bonuses, ticket_bonuses

    current_section = "free"

    # Iterate through siblings
    current = bonuses_section.find_next_sibling()

    while current:
        # Check if we've hit another major section
        if current.name == "h2":
            section_id = current.get("id", "")
            if section_id == "event-ticket":
                current_section = "ticket"
            elif section_id not in ["bonuses", "event-ticket"]:
                # Hit a different section, stop
                break

        # Look for bonus lists
        if current.name == "div":
            classes = current.get("class", [])
            if isinstance(classes, list) and "bonus-list" in classes:
                bonus_items = current.select(".bonus-item")

                for bonus in bonus_items:
                    text_elem = bonus.select_one(".bonus-text")
                    img_elem = bonus.select_one(".item-circle img")

                    if text_elem:
                        bonus_data: dict[str, Any] = {
                            "text": text_elem.get_text(strip=True),
                            "image": img_elem.get("src", "") if img_elem else "",
                        }

                        if current_section == "free":
                            free_bonuses.append(bonus_data)
                        else:
                            ticket_bonuses.append(bonus_data)

        current = current.find_next_sibling()

    return free_bonuses, ticket_bonuses


def _parse_research(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Parse timed research tasks and rewards"""
    research_list: list[dict[str, Any]] = []

    research_items = soup.select(".special-research-list .step-item")

    for item in research_items:
        research: dict[str, Any] = {"name": "", "step": 0, "tasks": [], "rewards": []}

        # Step number
        step_num_elem = item.select_one(".step-number")
        if step_num_elem:
            with contextlib.suppress(ValueError):
                research["step"] = int(step_num_elem.get_text(strip=True))

        # Step name
        step_name_elem = item.select_one(".step-name")
        if step_name_elem:
            research["name"] = step_name_elem.get_text(strip=True)

        # Tasks with rewards
        task_rewards = item.select(".task-reward")

        for task_reward in task_rewards:
            task_text_elem = task_reward.select_one(".task-text")
            reward_label_elem = task_reward.select_one(".reward-label")
            reward_img_elem = task_reward.select_one(".reward-image")

            if task_text_elem:
                task: dict[str, Any] = {
                    "text": task_text_elem.get_text(strip=True),
                    "reward": {
                        "text": reward_label_elem.get_text(strip=True)
                        if reward_label_elem
                        else "",
                        "image": reward_img_elem.get("src", "")
                        if reward_img_elem
                        else "",
                    },
                }
                tasks = research["tasks"]
                if isinstance(tasks, list):
                    tasks.append(task)

        # Page-level rewards
        page_rewards = item.select(".page-reward")

        for reward in page_rewards:
            reward_label_elem = reward.select_one(".reward-label span")
            reward_img_elem = reward.select_one(".reward-image")

            if reward_img_elem:
                rewards = research["rewards"]
                if isinstance(rewards, list):
                    rewards.append(
                        {
                            "text": reward_label_elem.get_text(strip=True)
                            if reward_label_elem
                            else "",
                            "image": reward_img_elem.get("src", ""),
                        }
                    )

        if research["name"] or research["tasks"] or research["rewards"]:
            research_list.append(research)

    return research_list


def _parse_shinies(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Parse shiny Pokemon from dedicated #shiny section"""
    shinies: list[dict[str, Any]] = []

    shiny_section = soup.find("h2", id="shiny")
    if not shiny_section:
        return shinies

    # Find the next .pkmn-list-flex after the shiny header
    pkmn_list = shiny_section.find_next_sibling("ul", class_="pkmn-list-flex")

    if pkmn_list:
        shiny_items = pkmn_list.select(".pkmn-list-item")

        for shiny in shiny_items:
            name_elem = shiny.select_one(".pkmn-name")
            img_elem = shiny.select_one(".pkmn-list-img img")

            if name_elem and img_elem:
                shiny_data: dict[str, Any] = {
                    "name": name_elem.get_text(strip=True),
                    "image": img_elem.get("src", ""),
                }
                shinies.append(shiny_data)

    return shinies


def _parse_raid_bosses(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Parse raid bosses from #raids section"""
    bosses: list[dict[str, Any]] = []

    raids_section = soup.find("h2", id="raids")
    if not raids_section:
        return bosses

    # Find featured Pokemon after raids section
    current = raids_section.find_next_sibling()

    while current:
        if current.name == "h2":
            current_id = current.get("id")
            if current_id not in [
                "featured-pokémon",
                "featured-pokemon",
                "",
                None,
            ]:
                break

        if current.name == "ul":
            classes = current.get("class", [])
            if isinstance(classes, list) and "pkmn-list-flex" in classes:
                boss_items = current.select(".pkmn-list-item")

                for boss in boss_items:
                    name_elem = boss.select_one(".pkmn-name")
                    img_elem = boss.select_one(".pkmn-list-img img")
                    shiny_icon = boss.select_one(".shiny-icon")

                    if name_elem and img_elem:
                        boss_data: dict[str, Any] = {
                            "name": name_elem.get_text(strip=True),
                            "image": img_elem.get("src", ""),
                            "canBeShiny": shiny_icon is not None,
                        }
                        bosses.append(boss_data)

        current = current.find_next_sibling()

    return bosses
