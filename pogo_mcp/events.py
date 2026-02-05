"""Event-related tools for the Pokemon Go MCP server."""

import logging
from datetime import datetime, timezone

from fastmcp import FastMCP

from .api_client import api_client
from .utils import (
    extract_community_day_info,
    extract_pokestop_showcase_info,
    extract_raid_day_info,
    format_event_summary,
    format_json_output,
    get_current_time_str,
    is_event_active,
    is_event_upcoming,
)

logger = logging.getLogger(__name__)


def register_event_tools(mcp: FastMCP) -> None:
    """Register all event-related tools with the MCP server."""

    @mcp.tool()
    async def get_current_events() -> str:
        """Get all active and upcoming Pokemon Go events.

        Returns a formatted list of all current and upcoming events with their details,
        including event type, duration, and links for more information.
        """
        try:
            logger.info("Fetching current events...")

            # Debug: Check api_client type
            logger.debug("api_client type: %s", type(api_client))

            # Get events with explicit error handling
            logger.info("Calling api_client.get_events()...")
            events = await api_client.get_events()
            logger.info(
                "Received events: %s with %s items",
                type(events),
                len(events) if isinstance(events, list) else "NOT A LIST",
            )
        except Exception as e:
            error_msg = f"Error fetching events: {e!s}"
            logger.exception(error_msg)
            return error_msg
        else:
            # Verify data structure
            # Type is already validated by logger check above

            current_time = datetime.now(timezone.utc)

            active_events = [e for e in events if is_event_active(e, current_time)]
            upcoming_events = [e for e in events if is_event_upcoming(e, current_time)]

            result = f"# Pokemon Go Events (as of {get_current_time_str()})\n\n"

            if active_events:
                result += "## 🟢 Currently Active Events\n\n"
                for event in active_events:
                    result += format_event_summary(event) + "\n\n"

            if upcoming_events:
                result += "## 🔵 Upcoming Events\n\n"
                for event in upcoming_events:
                    result += format_event_summary(event) + "\n\n"

            if not active_events and not upcoming_events:
                result += "No active or upcoming events found.\n"

            result += (
                f"\nTotal events found: {len(events)} "
                f"(Active: {len(active_events)}, Upcoming: {len(upcoming_events)})"
            )

            return result

    @mcp.tool()
    async def get_event_details(event_id: str) -> str:
        """Get detailed information about a specific Pokemon Go event.

        Args:
            event_id: The ID of the event to get details for

        Returns detailed information including spawns, bonuses, and special
        research if available.
        """
        try:
            events = await api_client.get_events()
            event = next((e for e in events if e.event_id == event_id), None)

            if not event:
                return f"Event with ID '{event_id}' not found."

            result = format_event_summary(event) + "\n\n"

            # Add extra details if available
            if event.extra_data:
                result += "## Additional Details\n\n"

                # Community Day specific info
                cd_info = extract_community_day_info(event)
                if cd_info:
                    if cd_info["featured_pokemon"]:
                        featured = ", ".join(cd_info["featured_pokemon"])
                        result += f"**Featured Pokemon:** {featured}\n\n"

                    if cd_info["bonuses"]:
                        result += "**Event Bonuses:**\n"
                        for bonus in cd_info["bonuses"]:
                            result += f"• {bonus}\n"
                        result += "\n"

                    if cd_info["shiny_available"]:
                        shiny = ", ".join(cd_info["shiny_available"])
                        result += f"**Shiny Available:** {shiny}\n\n"

                # Raid Day specific info
                rd_info = extract_raid_day_info(event)
                if rd_info:
                    if rd_info["raid_bosses"]:
                        result += (
                            f"**Raid Bosses:** {', '.join(rd_info['raid_bosses'])}\n\n"
                        )

                    if rd_info["bonuses"]:
                        result += "**Free Bonuses:**\n"
                        for bonus in rd_info["bonuses"]:
                            result += f"• {bonus}\n"
                        result += "\n"

                    if rd_info["ticket_bonuses"]:
                        result += "**Ticket Bonuses:**\n"
                        for bonus in rd_info["ticket_bonuses"]:
                            result += f"• {bonus}\n"
                        result += "\n"

                    if rd_info["research"]:
                        result += "**Timed Research:**\n"
                        for research_step in rd_info["research"]:
                            result += f"• {research_step.get('name', 'Unknown')}\n"
                            tasks = research_step.get("tasks", [])
                            if tasks:
                                for task in tasks:
                                    result += (
                                        f"  - {task.get('text', 'Unknown task')}\n"
                                    )
                        result += "\n"

                    if rd_info["shiny_available"]:
                        shiny = ", ".join(rd_info["shiny_available"])
                        result += f"**Shiny Available:** {shiny}\n\n"

                # PokéStop Showcase specific info
                showcase_info = extract_pokestop_showcase_info(event)
                if showcase_info and showcase_info["showcase_pokemon"]:
                    showcase_pokemon = ", ".join(showcase_info["showcase_pokemon"])
                    result += (
                        f"**PokéStop Showcase Pokémon:** {showcase_pokemon}\n\n"
                    )

                # Raw extra data
                result += "**Raw Event Data:**\n"
                result += f"```json\n{format_json_output(event.extra_data)}\n```\n"

        except Exception as e:
            logger.exception("Error fetching event details")
            return f"Error fetching event details: {e!s}"
        else:
            return result

    @mcp.tool()
    async def get_community_day_info() -> str:
        """Get information about current or upcoming Community Day events.

        Returns detailed Community Day information including featured Pokemon,
        bonuses, exclusive moves, and special research tasks.
        """
        try:
            events = await api_client.get_events()
            current_time = datetime.now(timezone.utc)

            cd_events = [
                e
                for e in events
                if "community" in e.event_type.lower()
                and (
                    is_event_active(e, current_time)
                    or is_event_upcoming(e, current_time)
                )
            ]

            if not cd_events:
                return "No active or upcoming Community Day events found."

            result = f"# Community Day Events (as of {get_current_time_str()})\n\n"

            for event in cd_events:
                result += format_event_summary(event) + "\n\n"

                cd_info = extract_community_day_info(event)
                if cd_info:
                    if cd_info["featured_pokemon"]:
                        result += (
                            f"**Featured:** {', '.join(cd_info['featured_pokemon'])}\n"
                        )

                    if cd_info["bonuses"]:
                        result += "**Bonuses:**\n"
                        for bonus in cd_info["bonuses"]:
                            result += f"• {bonus}\n"

                    if cd_info["shiny_available"]:
                        shiny = ", ".join(cd_info["shiny_available"])
                        result += f"**Shiny Pokemon:** {shiny}\n"

                result += "\n---\n\n"

        except Exception as e:
            logger.exception("Error fetching Community Day info")
            return f"Error fetching Community Day info: {e!s}"
        else:
            return result

    @mcp.tool()
    async def get_event_spawns(event_type: str | None = None) -> str:
        """Get Pokemon spawns from active events.

        Args:
            event_type: Optional filter by event type (e.g., 'community-day',
                        'spotlight')

        Returns information about Pokemon that are currently spawning more
        frequently due to events.
        """
        try:
            events = await api_client.get_events()
            current_time = datetime.now(timezone.utc)

            active_events = [e for e in events if is_event_active(e, current_time)]

            if event_type:
                active_events = [
                    e
                    for e in active_events
                    if event_type.lower() in e.event_type.lower()
                ]

            result = f"# Event Spawns (as of {get_current_time_str()})\n\n"

            spawns_found = False
            for event in active_events:
                event_spawns: list[str] = []

                if event.extra_data and "communityday" in event.extra_data:
                    cd_data = event.extra_data["communityday"]
                    spawns = cd_data.get("spawns", [])
                    event_spawns.extend(
                        spawn.get("name", "Unknown") for spawn in spawns
                    )

                if event.extra_data and "generic" in event.extra_data:
                    generic_data = event.extra_data["generic"]
                    spawns = generic_data.get("spawns", [])
                    event_spawns.extend(
                        spawn.get("name", "Unknown") for spawn in spawns
                    )

                if event_spawns:
                    spawns_found = True
                    result += f"## {event.name}\n"
                    result += f"**Increased Spawns:** {', '.join(event_spawns)}\n\n"

            if not spawns_found:
                if event_type:
                    result += (
                        f"No spawn information found for active {event_type} events.\n"
                    )
                else:
                    result += "No spawn information found for active events.\n"

        except Exception as e:
            logger.exception("Error fetching event spawns")
            return f"Error fetching event spawns: {e!s}"
        else:
            return result

    @mcp.tool()
    async def get_event_bonuses() -> str:
        """Get active bonuses from current Pokemon Go events.

        Returns information about experience, stardust, candy, and other bonuses
        that are currently active from events.
        """
        try:
            events = await api_client.get_events()
            current_time = datetime.now(timezone.utc)

            active_events = [e for e in events if is_event_active(e, current_time)]

            result = f"# Active Event Bonuses (as of {get_current_time_str()})\n\n"

            bonuses_found = False
            for event in active_events:
                event_bonuses: list[str] = []

                if event.extra_data and "communityday" in event.extra_data:
                    cd_data = event.extra_data["communityday"]
                    bonuses = cd_data.get("bonuses", [])
                    event_bonuses.extend(
                        bonus.get("text", "Unknown") for bonus in bonuses
                    )

                if event.extra_data and "raidday" in event.extra_data:
                    rd_data = event.extra_data["raidday"]
                    # Add free bonuses
                    bonuses = rd_data.get("bonuses", [])
                    event_bonuses.extend(
                        bonus.get("text", "Unknown") for bonus in bonuses
                    )
                    # Add ticket bonuses (marked as premium)
                    ticket_bonuses = rd_data.get("ticketBonuses", [])
                    event_bonuses.extend(
                        f"[TICKET] {bonus.get('text', 'Unknown')}"
                        for bonus in ticket_bonuses
                    )

                if event.extra_data and "generic" in event.extra_data:
                    generic_data = event.extra_data["generic"]
                    bonuses = generic_data.get("bonuses", [])
                    event_bonuses.extend(
                        bonus.get("text", "Unknown") for bonus in bonuses
                    )

                if event_bonuses:
                    bonuses_found = True
                    result += f"## {event.name}\n"
                    for bonus in event_bonuses:
                        result += f"• {bonus}\n"
                    result += "\n"

            if not bonuses_found:
                result += "No bonus information found for active events.\n"

        except Exception as e:
            logger.exception("Error fetching event bonuses")
            return f"Error fetching event bonuses: {e!s}"
        else:
            return result

    @mcp.tool()
    async def search_events(query: str) -> str:
        """Search for Pokemon Go events by name or description.

        Args:
            query: Search term to look for in event names and types

        Returns events that match the search criteria.
        """
        try:
            events = await api_client.get_events()
            query_lower = query.lower()

            matching_events = [
                e
                for e in events
                if (
                    query_lower in e.name.lower()
                    or query_lower in e.event_type.lower()
                    or query_lower in e.heading.lower()
                )
            ]

            if not matching_events:
                return f"No events found matching '{query}'."

            result = f"# Events matching '{query}' ({len(matching_events)} found)\n\n"

            for event in matching_events:
                result += format_event_summary(event) + "\n\n"

        except Exception as e:
            logger.exception("Error searching events")
            return f"Error searching events: {e!s}"
        else:
            return result

    @mcp.tool()
    async def get_pokestop_showcase_info() -> str:
        """Get information about active or upcoming PokéStop Showcase events."""
        try:
            events = await api_client.get_events()
            current_time = datetime.now(timezone.utc)

            showcase_events = [
                e
                for e in events
                if "pokestop-showcase" in e.event_type.lower()
                and (
                    is_event_active(e, current_time)
                    or is_event_upcoming(e, current_time)
                )
            ]

            if not showcase_events:
                return "No active or upcoming PokéStop Showcase events found."

            result = (
                f"# PokéStop Showcase Events (as of {get_current_time_str()})\n\n"
            )

            for event in showcase_events:
                result += format_event_summary(event) + "\n\n"

                showcase_info = extract_pokestop_showcase_info(event)
                if showcase_info and showcase_info["showcase_pokemon"]:
                    pokemon_list = ", ".join(showcase_info["showcase_pokemon"])
                    result += f"**Showcase Pokémon:** {pokemon_list}\n"

                result += "\n---\n\n"

        except Exception as e:
            logger.exception("Error fetching PokéStop Showcase info")
            return f"Error fetching PokéStop Showcase info: {e!s}"
        else:
            return result
