"""Event-related tools for the Pokemon Go MCP server."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from .api_client import api_client
from .types import EventInfo
from .utils import (
    is_event_active, is_event_upcoming, format_event_summary, 
    get_current_time_str, extract_community_day_info, format_json_output
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
            logger.debug(f"api_client type: {type(api_client)}")
            
            # Get events with explicit error handling
            logger.info("Calling api_client.get_events()...")
            events = await api_client.get_events()
            logger.info(f"Received events: {type(events)} with {len(events) if isinstance(events, list) else 'NOT A LIST'} items")
            
            # Verify data structure
            if not isinstance(events, list):
                raise TypeError(f"Expected list from get_events(), got {type(events)}")
                
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
            
            result += f"\nTotal events found: {len(events)} (Active: {len(active_events)}, Upcoming: {len(upcoming_events)})"
            
            return result
            
        except Exception as e:
            error_msg = f"Error fetching events: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return error_msg
    
    @mcp.tool()
    async def get_event_details(event_id: str) -> str:
        """Get detailed information about a specific Pokemon Go event.
        
        Args:
            event_id: The ID of the event to get details for
            
        Returns detailed information including spawns, bonuses, and special research if available.
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
                        result += f"**Featured Pokemon:** {', '.join(cd_info['featured_pokemon'])}\n\n"
                    
                    if cd_info["bonuses"]:
                        result += "**Event Bonuses:**\n"
                        for bonus in cd_info["bonuses"]:
                            result += f"• {bonus}\n"
                        result += "\n"
                    
                    if cd_info["shiny_available"]:
                        result += f"**Shiny Available:** {', '.join(cd_info['shiny_available'])}\n\n"
                
                # Raw extra data
                result += "**Raw Event Data:**\n"
                result += f"```json\n{format_json_output(event.extra_data)}\n```\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching event details: {e}")
            return f"Error fetching event details: {str(e)}"
    
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
                e for e in events 
                if "community" in e.event_type.lower() and 
                (is_event_active(e, current_time) or is_event_upcoming(e, current_time))
            ]
            
            if not cd_events:
                return "No active or upcoming Community Day events found."
            
            result = f"# Community Day Events (as of {get_current_time_str()})\n\n"
            
            for event in cd_events:
                result += format_event_summary(event) + "\n\n"
                
                cd_info = extract_community_day_info(event)
                if cd_info:
                    if cd_info["featured_pokemon"]:
                        result += f"**Featured:** {', '.join(cd_info['featured_pokemon'])}\n"
                    
                    if cd_info["bonuses"]:
                        result += "**Bonuses:**\n"
                        for bonus in cd_info["bonuses"]:
                            result += f"• {bonus}\n"
                    
                    if cd_info["shiny_available"]:
                        result += f"**Shiny Pokemon:** {', '.join(cd_info['shiny_available'])}\n"
                
                result += "\n---\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Community Day info: {e}")
            return f"Error fetching Community Day info: {str(e)}"
    
    @mcp.tool()
    async def get_event_spawns(event_type: Optional[str] = None) -> str:
        """Get Pokemon spawns from active events.
        
        Args:
            event_type: Optional filter by event type (e.g., 'community-day', 'spotlight')
            
        Returns information about Pokemon that are currently spawning more frequently due to events.
        """
        try:
            events = await api_client.get_events()
            current_time = datetime.now(timezone.utc)
            
            active_events = [e for e in events if is_event_active(e, current_time)]
            
            if event_type:
                active_events = [e for e in active_events if event_type.lower() in e.event_type.lower()]
            
            result = f"# Event Spawns (as of {get_current_time_str()})\n\n"
            
            spawns_found = False
            for event in active_events:
                event_spawns = []
                
                if event.extra_data and "communityday" in event.extra_data:
                    cd_data = event.extra_data["communityday"]
                    spawns = cd_data.get("spawns", [])
                    for spawn in spawns:
                        event_spawns.append(spawn.get("name", "Unknown"))
                
                if event_spawns:
                    spawns_found = True
                    result += f"## {event.name}\n"
                    result += f"**Increased Spawns:** {', '.join(event_spawns)}\n\n"
            
            if not spawns_found:
                if event_type:
                    result += f"No spawn information found for active {event_type} events.\n"
                else:
                    result += "No spawn information found for active events.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching event spawns: {e}")
            return f"Error fetching event spawns: {str(e)}"
    
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
                event_bonuses = []
                
                if event.extra_data and "communityday" in event.extra_data:
                    cd_data = event.extra_data["communityday"]
                    bonuses = cd_data.get("bonuses", [])
                    for bonus in bonuses:
                        event_bonuses.append(bonus.get("text", "Unknown"))
                
                if event_bonuses:
                    bonuses_found = True
                    result += f"## {event.name}\n"
                    for bonus in event_bonuses:
                        result += f"• {bonus}\n"
                    result += "\n"
            
            if not bonuses_found:
                result += "No bonus information found for active events.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching event bonuses: {e}")
            return f"Error fetching event bonuses: {str(e)}"
    
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
                e for e in events 
                if (query_lower in e.name.lower() or 
                    query_lower in e.event_type.lower() or
                    query_lower in e.heading.lower())
            ]
            
            if not matching_events:
                return f"No events found matching '{query}'."
            
            result = f"# Events matching '{query}' ({len(matching_events)} found)\n\n"
            
            for event in matching_events:
                result += format_event_summary(event) + "\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return f"Error searching events: {str(e)}"
