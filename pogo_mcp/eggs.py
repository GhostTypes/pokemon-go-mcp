"""Egg-related tools for the Pokemon Go MCP server."""

import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from .api_client import api_client
from .types import EggInfo
from .utils import (
    filter_eggs_by_distance, format_egg_summary, get_current_time_str,
    validate_pokemon_name, search_pokemon_by_name
)

logger = logging.getLogger(__name__)


def register_egg_tools(mcp: FastMCP) -> None:
    """Register all egg-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_egg_hatches() -> str:
        """Get all Pokemon currently available from eggs in Pokemon Go.
        
        Returns a comprehensive list of all Pokemon that can hatch from eggs,
        organized by egg distance with CP ranges, shiny availability, and special features.
        """
        try:
            eggs = await api_client.get_eggs()
            
            if not eggs:
                return "No egg hatch data available."
            
            # Organize by egg type
            egg_types = {}
            for egg in eggs:
                egg_type = egg.egg_type
                if egg_type not in egg_types:
                    egg_types[egg_type] = []
                egg_types[egg_type].append(egg)
            
            result = f"# Current Egg Hatches (as of {get_current_time_str()})\n\n"
            
            # Sort egg types by distance
            distance_order = ["2 km", "5 km", "7 km", "10 km", "12 km", "Adventure Sync"]
            sorted_types = []
            
            for distance in distance_order:
                if distance in egg_types:
                    sorted_types.append((distance, egg_types[distance]))
                    del egg_types[distance]
            
            # Add any remaining egg types
            for egg_type, egg_list in egg_types.items():
                sorted_types.append((egg_type, egg_list))
            
            for egg_type, egg_list in sorted_types:
                result += f"## {egg_type} Eggs ({len(egg_list)} Pokemon)\n\n"
                
                for egg in egg_list:
                    result += format_egg_summary(egg) + "\n\n"
            
            # Summary statistics
            total_eggs = len(eggs)
            shiny_eggs = len([e for e in eggs if e.can_be_shiny])
            regional_eggs = len([e for e in eggs if e.is_regional])
            
            result += f"**Summary:** {total_eggs} Pokemon in eggs, {shiny_eggs} can be shiny, {regional_eggs} are regional\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching egg hatches: {e}")
            return f"Error fetching egg hatches: {str(e)}"
    
    @mcp.tool()
    async def get_egg_hatches_by_distance(distance: str) -> str:
        """Get Pokemon available from eggs of a specific distance.
        
        Args:
            distance: Egg distance to filter by (2km, 5km, 7km, 10km, 12km, etc.)
            
        Returns Pokemon that can hatch from eggs of the specified distance.
        """
        try:
            eggs = await api_client.get_eggs()
            filtered_eggs = filter_eggs_by_distance(eggs, distance)
            
            if not filtered_eggs:
                return f"No Pokemon found in {distance} eggs."
            
            result = f"# {distance.title()} Egg Hatches ({len(filtered_eggs)} Pokemon)\n\n"
            
            for egg in filtered_eggs:
                result += format_egg_summary(egg) + "\n\n"
            
            # Statistics for this distance
            shiny_count = len([e for e in filtered_eggs if e.can_be_shiny])
            regional_count = len([e for e in filtered_eggs if e.is_regional])
            
            result += f"**Summary:** {len(filtered_eggs)} Pokemon in {distance} eggs, "
            result += f"{shiny_count} can be shiny, {regional_count} are regional\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching {distance} egg hatches: {e}")
            return f"Error fetching {distance} egg hatches: {str(e)}"
    
    @mcp.tool()
    async def get_shiny_egg_hatches() -> str:
        """Get all Pokemon from eggs that can be encountered as shiny.
        
        Returns Pokemon that can hatch from eggs in their shiny form,
        organized by egg distance for efficient shiny hunting planning.
        """
        try:
            eggs = await api_client.get_eggs()
            shiny_eggs = [e for e in eggs if e.can_be_shiny]
            
            if not shiny_eggs:
                return "No shiny-eligible Pokemon found in eggs."
            
            # Organize by egg type
            egg_types = {}
            for egg in shiny_eggs:
                egg_type = egg.egg_type
                if egg_type not in egg_types:
                    egg_types[egg_type] = []
                egg_types[egg_type].append(egg)
            
            result = f"# ✨ Shiny-Eligible Egg Hatches (as of {get_current_time_str()})\n\n"
            
            shiny_pokemon = sorted(list(set(e.name for e in shiny_eggs)))
            result += f"**Shiny Pokemon Available:** {', '.join(shiny_pokemon)}\n\n"
            
            # Sort by distance
            distance_order = ["2 km", "5 km", "7 km", "10 km", "12 km", "Adventure Sync"]
            
            for distance in distance_order:
                if distance in egg_types:
                    egg_list = egg_types[distance]
                    result += f"## {distance} Eggs ({len(egg_list)} shiny-eligible)\n\n"
                    
                    for egg in egg_list:
                        result += format_egg_summary(egg) + "\n\n"
            
            result += f"**Total:** {len(shiny_eggs)} shiny-eligible Pokemon out of {len(eggs)} total in eggs\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching shiny egg hatches: {e}")
            return f"Error fetching shiny egg hatches: {str(e)}"
    
    @mcp.tool()
    async def search_egg_pokemon(pokemon_name: str) -> str:
        """Search for a specific Pokemon in current egg pools.
        
        Args:
            pokemon_name: Name of the Pokemon to search for
            
        Returns information about the Pokemon if it's available from eggs.
        """
        try:
            if not validate_pokemon_name(pokemon_name):
                return f"Invalid Pokemon name: '{pokemon_name}'"
            
            eggs = await api_client.get_eggs()
            name_lower = pokemon_name.lower()
            
            matching_eggs = [e for e in eggs if name_lower in e.name.lower()]
            
            if not matching_eggs:
                return f"'{pokemon_name}' is not currently available from eggs."
            
            result = f"# Egg Availability: {pokemon_name.title()}\n\n"
            
            for egg in matching_eggs:
                result += format_egg_summary(egg) + "\n\n"
            
            # Additional info if multiple distances
            if len(matching_eggs) > 1:
                distances = [e.egg_type for e in matching_eggs]
                result += f"**Available from:** {', '.join(distances)}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching egg Pokemon: {e}")
            return f"Error searching egg Pokemon: {str(e)}"
    
    @mcp.tool()
    async def get_regional_egg_pokemon() -> str:
        """Get Pokemon from eggs that are region-locked.
        
        Returns regional Pokemon that can only be obtained from eggs in specific regions,
        useful for planning trades or travel.
        """
        try:
            eggs = await api_client.get_eggs()
            regional_eggs = [e for e in eggs if e.is_regional]
            
            if not regional_eggs:
                return "No regional Pokemon found in current egg pools."
            
            result = f"# 🌍 Regional Pokemon in Eggs ({len(regional_eggs)} found)\n\n"
            result += "These Pokemon are region-locked and may require trading to obtain:\n\n"
            
            # Group by egg type
            egg_types = {}
            for egg in regional_eggs:
                egg_type = egg.egg_type
                if egg_type not in egg_types:
                    egg_types[egg_type] = []
                egg_types[egg_type].append(egg)
            
            for egg_type in sorted(egg_types.keys()):
                egg_list = egg_types[egg_type]
                result += f"## {egg_type} Eggs\n\n"
                
                for egg in egg_list:
                    result += format_egg_summary(egg) + "\n\n"
            
            # List just the names for quick reference
            regional_names = sorted([e.name for e in regional_eggs])
            result += f"**Regional Pokemon:** {', '.join(regional_names)}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching regional egg Pokemon: {e}")
            return f"Error fetching regional egg Pokemon: {str(e)}"
    
    @mcp.tool()
    async def get_gift_exchange_pokemon() -> str:
        """Get Pokemon that are available from gift eggs (7km eggs from friends).
        
        Returns Pokemon that can be hatched from 7km eggs received from gifts,
        which often contain regional Pokemon and special variants.
        """
        try:
            eggs = await api_client.get_eggs()
            gift_eggs = [e for e in eggs if e.is_gift_exchange]
            
            if not gift_eggs:
                return "No gift exchange Pokemon found in current egg pools."
            
            result = f"# 🎁 Gift Exchange Pokemon ({len(gift_eggs)} found)\n\n"
            result += "These Pokemon can be hatched from 7km eggs received from friends:\n\n"
            
            for egg in gift_eggs:
                result += format_egg_summary(egg) + "\n\n"
            
            # Statistics
            shiny_count = len([e for e in gift_eggs if e.can_be_shiny])
            regional_count = len([e for e in gift_eggs if e.is_regional])
            
            result += f"**Summary:** {len(gift_eggs)} Pokemon from gifts, "
            result += f"{shiny_count} can be shiny, {regional_count} are regional\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching gift exchange Pokemon: {e}")
            return f"Error fetching gift exchange Pokemon: {str(e)}"

    @mcp.tool()
    async def get_route_gift_pokemon() -> str:
        """Get Pokemon that are available from route gift eggs (7km eggs from route gifts).
        
        Returns Pokemon that can be hatched from 7km eggs received from route gifts,
        which often contain special variants.
        """
        try:
            eggs = await api_client.get_eggs()
            route_gift_eggs = [e for e in eggs if e.is_route_gift]
            
            if not route_gift_eggs:
                return "No route gift Pokemon found in current egg pools."
            
            result = f"# 🎁 Route Gift Pokemon ({len(route_gift_eggs)} found)\n\n"
            result += "These Pokemon can be hatched from 7km eggs received from route gifts:\n\n"
            
            for egg in route_gift_eggs:
                result += format_egg_summary(egg) + "\n\n"
            
            # Statistics
            shiny_count = len([e for e in route_gift_eggs if e.can_be_shiny])
            regional_count = len([e for e in route_gift_eggs if e.is_regional])
            
            result += f"**Summary:** {len(route_gift_eggs)} Pokemon from route gifts, "
            result += f"{shiny_count} can be shiny, {regional_count} are regional\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching route gift Pokemon: {e}")
            return f"Error fetching route gift Pokemon: {str(e)}"
    
    @mcp.tool()
    async def get_adventure_sync_rewards() -> str:
        """Get Pokemon available as Adventure Sync rewards.
        
        Returns Pokemon that can be obtained from Adventure Sync reward eggs,
        which are earned by walking specific distances each week.
        """
        try:
            eggs = await api_client.get_eggs()
            as_eggs = [e for e in eggs if e.is_adventure_sync]
            
            if not as_eggs:
                return "No Adventure Sync reward Pokemon found."
            
            result = f"# 🏃 Adventure Sync Rewards ({len(as_eggs)} found)\n\n"
            result += "These Pokemon can be obtained from Adventure Sync reward eggs:\n\n"
            
            for egg in as_eggs:
                result += format_egg_summary(egg) + "\n\n"
            
            # Statistics
            shiny_count = len([e for e in as_eggs if e.can_be_shiny])
            
            result += f"**Summary:** {len(as_eggs)} Adventure Sync Pokemon, {shiny_count} can be shiny\n"
            result += "\n**Tip:** Walk 25km or 50km per week to earn Adventure Sync rewards!\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Adventure Sync rewards: {e}")
            return f"Error fetching Adventure Sync rewards: {str(e)}"
    
    @mcp.tool()
    async def get_egg_recommendations(priority: str = "shiny") -> str:
        """Get egg incubation recommendations based on specified priority.
        
        Args:
            priority: Priority type - "shiny" for shiny hunting, "rare" for uncommon Pokemon,
                     "quick" for fast hatches, or "distance" for specific distances
            
        Returns recommended eggs to prioritize based on the criteria.
        """
        try:
            eggs = await api_client.get_eggs()
            
            result = f"# Egg Incubation Recommendations ({priority.title()} Priority)\n\n"
            
            if priority.lower() == "shiny":
                recommended = [e for e in eggs if e.can_be_shiny]
                result += "Prioritize these eggs for shiny hunting:\n\n"
                
            elif priority.lower() == "rare":
                # Consider regional and gift exchange as "rare"
                recommended = [e for e in eggs if e.is_regional or e.is_gift_exchange]
                result += "These eggs contain rare or region-exclusive Pokemon:\n\n"
                
            elif priority.lower() == "quick":
                recommended = filter_eggs_by_distance(eggs, "2 km")
                result += "Quick hatches - 2km eggs for fast turnover:\n\n"
                
            else:  # distance-based or default
                # Focus on 10km eggs as they typically have the best Pokemon
                recommended = filter_eggs_by_distance(eggs, "10 km")
                if not recommended:
                    recommended = filter_eggs_by_distance(eggs, "5 km")
                result += "Best overall value eggs:\n\n"
            
            if not recommended:
                return f"No eggs found matching {priority} priority criteria."
            
            # Organize by distance for better recommendations
            distances = {}
            for egg in recommended:
                dist = egg.egg_type
                if dist not in distances:
                    distances[dist] = []
                distances[dist].append(egg)
            
            for distance in sorted(distances.keys()):
                egg_list = distances[distance]
                result += f"## {distance} Priority\n\n"
                
                # Show top recommendations for each distance
                shiny_eggs = [e for e in egg_list if e.can_be_shiny]
                other_eggs = [e for e in egg_list if not e.can_be_shiny]
                
                if shiny_eggs:
                    result += "**🌟 High Priority (Shiny Potential):**\n"
                    for egg in shiny_eggs[:5]:  # Top 5
                        result += f"• {egg.name}\n"
                    result += "\n"
                
                if other_eggs and priority.lower() != "shiny":
                    result += "**⭐ Standard Priority:**\n"
                    for egg in other_eggs[:3]:  # Top 3
                        result += f"• {egg.name}\n"
                    result += "\n"
            
            # General advice based on priority
            if priority.lower() == "shiny":
                result += "💡 **Tip:** Use premium incubators on 10km eggs with shiny potential!\n"
            elif priority.lower() == "quick":
                result += "💡 **Tip:** Use infinite incubator on 2km eggs to maximize hatches!\n"
            elif priority.lower() == "rare":
                result += "💡 **Tip:** Save super incubators for rare regional Pokemon!\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting egg recommendations: {e}")
            return f"Error getting egg recommendations: {str(e)}"
