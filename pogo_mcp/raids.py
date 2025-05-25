"""Raid-related tools for the Pokemon Go MCP server."""

import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from .api_client import api_client
from .types import RaidInfo
from .utils import (
    filter_raids_by_tier, filter_raids_by_type, filter_shiny_pokemon,
    format_raid_summary, get_current_time_str, normalize_tier_name,
    search_pokemon_by_name, validate_pokemon_name
)

logger = logging.getLogger(__name__)


def register_raid_tools(mcp: FastMCP) -> None:
    """Register all raid-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_current_raids() -> str:
        """Get all current raid bosses in Pokemon Go.
        
        Returns a comprehensive list of all raid bosses currently available,
        organized by tier with CP ranges, types, weather boosts, and shiny availability.
        """
        try:
            raids = await api_client.get_raids()
            
            if not raids:
                return "No raid data available."
            
            # Organize raids by tier
            tiers = {}
            for raid in raids:
                tier = raid.tier
                if tier not in tiers:
                    tiers[tier] = []
                tiers[tier].append(raid)
            
            result = f"# Current Raid Bosses (as of {get_current_time_str()})\n\n"
            
            # Sort tiers for better display
            tier_order = ["Tier 1", "Tier 3", "Tier 5", "Mega", "Shadow"]
            sorted_tiers = []
            
            for tier in tier_order:
                if tier in tiers:
                    sorted_tiers.append((tier, tiers[tier]))
                    del tiers[tier]
            
            # Add any remaining tiers
            for tier, raid_list in tiers.items():
                sorted_tiers.append((tier, raid_list))
            
            for tier, raid_list in sorted_tiers:
                result += f"## {tier} Raids ({len(raid_list)} bosses)\n\n"
                for raid in raid_list:
                    result += format_raid_summary(raid) + "\n\n"
            
            total_shiny = len([r for r in raids if r.can_be_shiny])
            result += f"**Summary:** {len(raids)} total raid bosses, {total_shiny} can be shiny\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching raids: {e}")
            return f"Error fetching raids: {str(e)}"
    
    @mcp.tool()
    async def get_raid_by_tier(tier: str) -> str:
        """Get raid bosses filtered by tier.
        
        Args:
            tier: Raid tier to filter by (1, 3, 5, Mega, etc.)
            
        Returns raid bosses of the specified tier with full details.
        """
        try:
            raids = await api_client.get_raids()
            normalized_tier = normalize_tier_name(tier)
            
            filtered_raids = filter_raids_by_tier(raids, normalized_tier)
            
            if not filtered_raids:
                return f"No raid bosses found for tier '{tier}'."
            
            result = f"# {tier.title()} Raid Bosses ({len(filtered_raids)} found)\n\n"
            
            for raid in filtered_raids:
                result += format_raid_summary(raid) + "\n\n"
            
            shiny_count = len([r for r in filtered_raids if r.can_be_shiny])
            result += f"**Summary:** {len(filtered_raids)} {tier} raids, {shiny_count} can be shiny\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching {tier} raids: {e}")
            return f"Error fetching {tier} raids: {str(e)}"
    
    @mcp.tool()
    async def get_shiny_raids() -> str:
        """Get only raid bosses that can be encountered as shiny.
        
        Returns all current raid bosses where the shiny form is available,
        perfect for shiny hunters planning their raid activities.
        """
        try:
            raids = await api_client.get_raids()
            shiny_raids = [r for r in raids if r.can_be_shiny]
            
            if not shiny_raids:
                return "No shiny-eligible raid bosses found."
            
            # Organize by tier
            tiers = {}
            for raid in shiny_raids:
                tier = raid.tier
                if tier not in tiers:
                    tiers[tier] = []
                tiers[tier].append(raid)
            
            result = f"# ✨ Shiny-Eligible Raid Bosses (as of {get_current_time_str()})\n\n"
            
            for tier in sorted(tiers.keys()):
                raid_list = tiers[tier]
                result += f"## {tier} ({len(raid_list)} shiny-eligible)\n\n"
                for raid in raid_list:
                    result += format_raid_summary(raid) + "\n\n"
            
            result += f"**Total:** {len(shiny_raids)} shiny-eligible raid bosses out of {len(raids)} total\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching shiny raids: {e}")
            return f"Error fetching shiny raids: {str(e)}"
    
    @mcp.tool()
    async def search_raid_boss(pokemon_name: str) -> str:
        """Search for a specific Pokemon in current raids.
        
        Args:
            pokemon_name: Name of the Pokemon to search for
            
        Returns information about the Pokemon if it's currently a raid boss.
        """
        try:
            if not validate_pokemon_name(pokemon_name):
                return f"Invalid Pokemon name: '{pokemon_name}'"
            
            raids = await api_client.get_raids()
            name_lower = pokemon_name.lower()
            
            matching_raids = [r for r in raids if name_lower in r.name.lower()]
            
            if not matching_raids:
                return f"'{pokemon_name}' is not currently available as a raid boss."
            
            result = f"# Raid Boss: {pokemon_name}\n\n"
            
            for raid in matching_raids:
                result += format_raid_summary(raid) + "\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching for raid boss: {e}")
            return f"Error searching for raid boss: {str(e)}"
    
    @mcp.tool()
    async def get_raids_by_type(pokemon_type: str) -> str:
        """Get raid bosses filtered by Pokemon type.
        
        Args:
            pokemon_type: Pokemon type to filter by (e.g., Fire, Water, Electric)
            
        Returns raid bosses that have the specified type.
        """
        try:
            raids = await api_client.get_raids()
            filtered_raids = filter_raids_by_type(raids, pokemon_type)
            
            if not filtered_raids:
                return f"No {pokemon_type}-type raid bosses found."
            
            result = f"# {pokemon_type.title()}-Type Raid Bosses ({len(filtered_raids)} found)\n\n"
            
            for raid in filtered_raids:
                result += format_raid_summary(raid) + "\n\n"
            
            shiny_count = len([r for r in filtered_raids if r.can_be_shiny])
            result += f"**Summary:** {len(filtered_raids)} {pokemon_type}-type raids, {shiny_count} can be shiny\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching {pokemon_type} raids: {e}")
            return f"Error fetching {pokemon_type} raids: {str(e)}"
    
    @mcp.tool()
    async def get_weather_boosted_raids(weather: str) -> str:
        """Get raid bosses that are boosted by specific weather.
        
        Args:
            weather: Weather condition (Sunny, Rainy, Snowy, Foggy, Windy, Cloudy)
            
        Returns raid bosses that receive a weather boost in the specified weather.
        """
        try:
            raids = await api_client.get_raids()
            weather_lower = weather.lower()
            
            boosted_raids = [
                r for r in raids 
                if any(weather_lower in w.name.lower() for w in r.boosted_weather)
            ]
            
            if not boosted_raids:
                return f"No raid bosses are boosted by {weather} weather."
            
            result = f"# {weather.title()}-Boosted Raid Bosses ({len(boosted_raids)} found)\n\n"
            
            for raid in boosted_raids:
                result += format_raid_summary(raid) + "\n\n"
            
            shiny_count = len([r for r in boosted_raids if r.can_be_shiny])
            result += f"**Summary:** {len(boosted_raids)} raids boosted by {weather}, {shiny_count} can be shiny\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching weather boosted raids: {e}")
            return f"Error fetching weather boosted raids: {str(e)}"
    
    @mcp.tool()
    async def get_raid_recommendations(tier: Optional[str] = None, shiny_only: bool = False) -> str:
        """Get raid recommendations based on specified criteria.
        
        Args:
            tier: Optional tier filter (1, 3, 5, Mega)
            shiny_only: If True, only show raids where shiny is available
            
        Returns recommended raids to focus on based on the criteria.
        """
        try:
            raids = await api_client.get_raids()
            
            # Apply filters
            if tier:
                raids = filter_raids_by_tier(raids, normalize_tier_name(tier))
            
            if shiny_only:
                raids = [r for r in raids if r.can_be_shiny]
            
            if not raids:
                filter_desc = []
                if tier:
                    filter_desc.append(f"tier {tier}")
                if shiny_only:
                    filter_desc.append("shiny-eligible")
                return f"No raids found matching criteria: {', '.join(filter_desc)}"
            
            result = f"# Raid Recommendations (as of {get_current_time_str()})\n\n"
            
            if shiny_only:
                result += "## ✨ Priority: Shiny Hunting\n\n"
            
            if tier:
                result += f"## Tier {tier} Focus\n\n"
            
            # Organize by tier for recommendations
            tiers = {}
            for raid in raids:
                tier_name = raid.tier
                if tier_name not in tiers:
                    tiers[tier_name] = []
                tiers[tier_name].append(raid)
            
            for tier_name in sorted(tiers.keys()):
                raid_list = tiers[tier_name]
                result += f"### {tier_name}\n\n"
                
                for raid in raid_list:
                    priority = "🌟 High Priority" if raid.can_be_shiny else "⭐ Standard Priority"
                    result += f"**{raid.name}** - {priority}\n"
                    
                    # Quick summary
                    types_str = ", ".join([t.name.title() for t in raid.types])
                    result += f"Types: {types_str}"
                    
                    if raid.can_be_shiny:
                        result += " | ✨ Shiny Available"
                    
                    result += "\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting raid recommendations: {e}")
            return f"Error getting raid recommendations: {str(e)}"
