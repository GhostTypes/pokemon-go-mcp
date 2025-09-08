"""Main MCP server for Pokemon Go events, raids, research, and eggs."""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from .api_client import api_client
from .events import register_event_tools
from .raids import register_raid_tools
from .research import register_research_tools
from .eggs import register_egg_tools
from .utils import (
    get_current_time_str, format_json_output, search_pokemon_by_name,
    filter_shiny_pokemon, validate_pokemon_name, is_event_active
)
from .types import PokemonInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP(
    "Pokemon Go MCP Server",
    dependencies=["httpx>=0.27.0", "python-dateutil>=2.8.2"]
)


def register_cross_cutting_tools():
    """Register tools that work across all data sources."""
    
    @mcp.tool()
    async def get_all_shiny_pokemon() -> str:
        """Get all Pokemon currently available as shiny across all sources.
        
        Returns a comprehensive list of all shiny-eligible Pokemon from events, 
        raids, research rewards, and egg hatches. Perfect for shiny hunters!
        """
        try:
            logger.info("Fetching all data for shiny Pokemon search...")
            all_data = await api_client.get_all_data()
            
            shiny_pokemon = set()
            sources = {}
            
            # From events (spawns and shinies)
            for event in all_data["events"]:
                if event.extra_data and "communityday" in event.extra_data:
                    cd_data = event.extra_data["communityday"]
                    for shiny in cd_data.get("shinies", []):
                        name = shiny.get("name", "")
                        if name:
                            shiny_pokemon.add(name)
                            if name not in sources:
                                sources[name] = []
                            sources[name].append(f"Event: {event.name}")
            
            # From raids
            for raid in all_data["raids"]:
                if raid.can_be_shiny:
                    shiny_pokemon.add(raid.name)
                    if raid.name not in sources:
                        sources[raid.name] = []
                    sources[raid.name].append(f"Raid: {raid.tier}")
            
            # From research
            for task in all_data["research"]:
                for reward in task.rewards:
                    if reward.can_be_shiny:
                        shiny_pokemon.add(reward.name)
                        if reward.name not in sources:
                            sources[reward.name] = []
                        sources[reward.name].append("Research Task")
            
            # From eggs
            for egg in all_data["eggs"]:
                if egg.can_be_shiny:
                    shiny_pokemon.add(egg.name)
                    if egg.name not in sources:
                        sources[egg.name] = []
                    sources[egg.name].append(f"Egg: {egg.egg_type}")
            
            if not shiny_pokemon:
                return "No shiny Pokemon found across all sources."
            
            result = f"# ✨ All Available Shiny Pokemon (as of {get_current_time_str()})\n\n"
            result += f"**Total Shiny Pokemon Available:** {len(shiny_pokemon)}\n\n"
            
            # Sort alphabetically
            sorted_shinies = sorted(shiny_pokemon)
            
            for pokemon in sorted_shinies:
                pokemon_sources = sources.get(pokemon, ["Unknown"])
                result += f"**{pokemon}**\n"
                result += f"Sources: {', '.join(pokemon_sources)}\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching all shiny Pokemon: {e}")
            return f"Error fetching all shiny Pokemon: {str(e)}"
    
    @mcp.tool()
    async def search_pokemon_everywhere(pokemon_name: str) -> str:
        """Search for a Pokemon across all data sources (events, raids, research, eggs).
        
        Args:
            pokemon_name: Name of the Pokemon to search for
            
        Returns comprehensive information about where and how the Pokemon can be obtained.
        """
        try:
            if not validate_pokemon_name(pokemon_name):
                return f"Invalid Pokemon name: '{pokemon_name}'"
            
            logger.info(f"Searching for {pokemon_name} across all sources...")
            all_data = await api_client.get_all_data()
            
            result = f"# Search Results: {pokemon_name.title()}\n\n"
            found_anywhere = False
            name_lower = pokemon_name.lower()
            
            # Search in events
            event_matches = []
            for event in all_data["events"]:
                if event.extra_data and "communityday" in event.extra_data:
                    cd_data = event.extra_data["communityday"]
                    
                    # Check spawns
                    for spawn in cd_data.get("spawns", []):
                        if name_lower in spawn.get("name", "").lower():
                            event_matches.append(f"Featured in {event.name}")
                    
                    # Check shinies
                    for shiny in cd_data.get("shinies", []):
                        if name_lower in shiny.get("name", "").lower():
                            event_matches.append(f"Shiny available in {event.name}")
            
            if event_matches:
                found_anywhere = True
                result += "## 🎉 Events\n\n"
                for match in event_matches:
                    result += f"• {match}\n"
                result += "\n"
            
            # Search in raids
            raid_matches = [r for r in all_data["raids"] if name_lower in r.name.lower()]
            if raid_matches:
                found_anywhere = True
                result += "## ⚔️ Raids\n\n"
                for raid in raid_matches:
                    shiny_status = "✨ Shiny Available" if raid.can_be_shiny else "❌ No Shiny"
                    result += f"• **{raid.name}** ({raid.tier}) - {shiny_status}\n"
                result += "\n"
            
            # Search in research
            research_matches = []
            for task in all_data["research"]:
                for reward in task.rewards:
                    if name_lower in reward.name.lower():
                        shiny_status = "✨" if reward.can_be_shiny else ""
                        research_matches.append(f"{task.text} → {reward.name} {shiny_status}")
            
            if research_matches:
                found_anywhere = True
                result += "## 🔬 Research Tasks\n\n"
                for match in research_matches:
                    result += f"• {match}\n"
                result += "\n"
            
            # Search in eggs
            egg_matches = [e for e in all_data["eggs"] if name_lower in e.name.lower()]
            if egg_matches:
                found_anywhere = True
                result += "## 🥚 Egg Hatches\n\n"
                for egg in egg_matches:
                    features = []
                    if egg.can_be_shiny:
                        features.append("✨ Shiny")
                    if egg.is_regional:
                        features.append("🌍 Regional")
                    if egg.is_gift_exchange:
                        features.append("🎁 Gift")
                    
                    feature_str = f" ({', '.join(features)})" if features else ""
                    result += f"• **{egg.name}** from {egg.egg_type}{feature_str}\n"
                result += "\n"
            
            if not found_anywhere:
                result += f"❌ **{pokemon_name.title()}** was not found in any current Pokemon Go data sources.\n\n"
                result += "This could mean:\n"
                result += "• The Pokemon is not currently available\n"
                result += "• The name might be misspelled\n"
                result += "• The Pokemon might be in a different form or region\n"
            else:
                result += f"✅ **{pokemon_name.title()}** found in Pokemon Go! Check the sources above for details.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching for Pokemon: {e}")
            return f"Error searching for Pokemon: {str(e)}"
    
    @mcp.tool()
    async def get_daily_priorities() -> str:
        """Get daily priorities and recommendations for Pokemon Go activities.
        
        Returns a curated list of what to focus on today based on active events,
        valuable raids, research tasks, and egg hatching recommendations.
        """
        try:
            logger.info("Generating daily priorities...")
            
            # Debug: Check api_client type
            logger.debug(f"api_client type: {type(api_client)}")
            logger.debug(f"api_client methods: {[m for m in dir(api_client) if not m.startswith('_')]}")
            
            # Get all data with explicit error handling
            logger.info("Calling api_client.get_all_data()...")
            all_data = await api_client.get_all_data()
            logger.info(f"Received all_data with keys: {list(all_data.keys()) if isinstance(all_data, dict) else 'NOT A DICT'}")
            
            # Verify data structure
            if not isinstance(all_data, dict):
                raise TypeError(f"Expected dict from get_all_data(), got {type(all_data)}")
            
            if "events" not in all_data:
                raise KeyError("Missing 'events' key in all_data")
                
            events_data = all_data["events"]
            if not isinstance(events_data, list):
                raise TypeError(f"Expected list for events, got {type(events_data)}")
                
            logger.info(f"Processing {len(events_data)} events...")
            
            current_time = datetime.now(timezone.utc)
            
            result = f"# 🎯 Daily Pokemon Go Priorities ({get_current_time_str()})\n\n"
            
            # Active events
            active_events = [e for e in events_data if is_event_active(e, current_time)]
            
            if active_events:
                result += "## 🔥 Active Events (Top Priority!)\n\n"
                for event in active_events[:3]:  # Top 3 events
                    result += f"**{event.name}**\n"
                    if event.extra_data and "communityday" in event.extra_data:
                        cd_data = event.extra_data["communityday"]
                        spawns = [s.get("name") for s in cd_data.get("spawns", [])]
                        if spawns:
                            result += f"Focus: {', '.join(spawns)}\n"
                    result += f"Link: {event.link}\n\n"
            
            # Priority raids (with fallback for missing data)
            raids_data = all_data.get("raids", [])
            if raids_data:
                shiny_raids = [r for r in raids_data if r.can_be_shiny]
                if shiny_raids:
                    result += "## ⚔️ Priority Raids (Shiny Hunting)\n\n"
                    
                    # Check if raids were extracted from events (fallback source)
                    is_from_events = any(r.extra_data and r.extra_data.get("source") == "events_fallback" for r in shiny_raids)
                    if is_from_events:
                        result += "*📅 Raid data extracted from active events*\n\n"
                    
                    for raid in shiny_raids[:5]:  # Top 5 shiny raids
                        tier_info = f" ({raid.tier})" if raid.tier != "Unknown" else ""
                        event_info = ""
                        
                        # Add event context if this raid was extracted from events
                        if raid.extra_data and raid.extra_data.get("source") == "events_fallback":
                            event_name = raid.extra_data.get("event_name", "")
                            event_info = f" - *{event_name}*"
                        
                        result += f"• **{raid.name}**{tier_info} ✨{event_info}\n"
                    result += "\n"
            else:
                result += "## ⚔️ Raids Status\n\n"
                result += "⚠️ No raid data available from either raids.json or active events.\n\n"
            
            # Quick research tasks
            research_data = all_data.get("research", [])
            easy_research = []
            for task in research_data:
                if any(pattern in task.text.lower() for pattern in ["catch 1", "catch 2", "catch 3", "make 1"]):
                    if any(r.can_be_shiny for r in task.rewards):
                        easy_research.append(task)
            
            if easy_research:
                result += "## 🔬 Quick Shiny Research (Easy Completions)\n\n"
                for task in easy_research[:3]:  # Top 3 easy tasks
                    shiny_rewards = [r.name for r in task.rewards if r.can_be_shiny]
                    result += f"• {task.text} → {', '.join(shiny_rewards)} ✨\n"
                result += "\n"
            
            # Egg recommendations
            eggs_data = all_data.get("eggs", [])
            shiny_eggs_2km = [e for e in eggs_data if e.can_be_shiny and "2 km" in e.egg_type]
            if shiny_eggs_2km:
                result += "## 🥚 Egg Hatching Focus\n\n"
                result += "**2km eggs with shiny potential (use infinite incubator):**\n"
                for egg in shiny_eggs_2km[:3]:
                    result += f"• {egg.name} ✨\n"
                result += "\n"
            
            # Summary recommendations (adaptive based on available data)
            result += "## 📋 Today's Action Plan\n\n"
            result += "1. **Events:** Participate in any active events first\n"
            if raids_data:
                result += "2. **Raids:** Focus on shiny-eligible raid bosses\n"
            else:
                result += "2. **Raids:** Check local raid apps for current bosses\n"
            result += "3. **Research:** Complete easy tasks with shiny rewards\n"
            result += "4. **Eggs:** Incubate 2km eggs for quick shiny chances\n"
            result += "5. **Walking:** Remember Adventure Sync rewards at 25km/50km\n"
            
            # Add data source status with improved messaging
            missing_sources = []
            fallback_used = []
            
            if not all_data.get("raids", []):
                missing_sources.append("raids")
            elif any(r.extra_data and r.extra_data.get("source") == "events_fallback" for r in all_data.get("raids", [])):
                fallback_used.append("raids (extracted from events)")
                
            if not all_data.get("research", []):
                missing_sources.append("research") 
            if not all_data.get("eggs", []):
                missing_sources.append("eggs")
            if not all_data.get("events", []):
                missing_sources.append("events")
            
            if missing_sources or fallback_used:
                result += "\n---\n"
                if fallback_used:
                    result += f"ℹ️ **Fallback data sources used:** {', '.join(fallback_used)}\n"
                if missing_sources:
                    result += f"⚠️ **Unavailable data sources:** {', '.join(missing_sources)}\n"
                result += "Recommendations are based on currently available data.\n"
            
            return result
            
        except Exception as e:
            error_msg = f"Error generating daily priorities: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return error_msg
    
    @mcp.tool()
    async def get_server_status() -> str:
        """Get the current status and statistics of the Pokemon Go MCP server.
        
        Returns information about data freshness, cache status, and summary statistics
        across all Pokemon Go data sources.
        """
        try:
            logger.info("Checking server status...")
            all_data = await api_client.get_all_data()
            current_time = datetime.now(timezone.utc)
            
            result = f"# 📊 Pokemon Go MCP Server Status\n\n"
            result += f"**Last Updated:** {get_current_time_str()}\n"
            result += f"**Data Source:** LeekDuck API (ScrapedDuck)\n\n"
            
            # Data statistics
            result += "## 📈 Data Statistics\n\n"
            result += f"• **Events:** {len(all_data['events'])} total\n"
            result += f"• **Raid Bosses:** {len(all_data['raids'])} total\n"
            result += f"• **Research Tasks:** {len(all_data['research'])} total\n"
            result += f"• **Egg Pokemon:** {len(all_data['eggs'])} total\n\n"
            
            # Active content
            active_events = [e for e in all_data["events"] if is_event_active(e, current_time)]
            shiny_raids = [r for r in all_data["raids"] if r.can_be_shiny]
            shiny_research = [t for t in all_data["research"] if any(r.can_be_shiny for r in t.rewards)]
            shiny_eggs = [e for e in all_data["eggs"] if e.can_be_shiny]
            
            result += "## 🎮 Active Content\n\n"
            result += f"• **Active Events:** {len(active_events)}\n"
            result += f"• **Shiny Raids:** {len(shiny_raids)}\n"
            result += f"• **Shiny Research:** {len(shiny_research)}\n"
            result += f"• **Shiny Eggs:** {len(shiny_eggs)}\n\n"
            
            # Cache status
            cache_info = []
            for endpoint in ["events", "raids", "research", "eggs"]:
                if endpoint in api_client._cache_timestamp:
                    last_fetch = api_client._cache_timestamp[endpoint]
                    age_seconds = (current_time - last_fetch).total_seconds()
                    cache_info.append(f"• **{endpoint.title()}:** {age_seconds:.0f}s ago")
                else:
                    cache_info.append(f"• **{endpoint.title()}:** Not cached")
            
            result += "## 💾 Cache Status\n\n"
            result += "\n".join(cache_info)
            result += f"\n\n**Cache Duration:** {api_client._cache_duration}s (24 hours)\n"
            
            # Available tools
            result += "\n## 🛠️ Available Tools\n\n"
            result += "### Event Tools\n"
            result += "• get_current_events, get_event_details, get_community_day_info\n"
            result += "• get_event_spawns, get_event_bonuses, search_events\n\n"
            
            result += "### Raid Tools\n"
            result += "• get_current_raids, get_raid_by_tier, get_shiny_raids\n"
            result += "• search_raid_boss, get_raids_by_type, get_weather_boosted_raids\n\n"
            
            result += "### Research Tools\n"
            result += "• get_current_research, search_research_by_reward, get_shiny_research_rewards\n"
            result += "• get_easy_research_tasks, get_research_recommendations\n\n"
            
            result += "### Egg Tools\n"
            result += "• get_egg_hatches, get_egg_hatches_by_distance, get_shiny_egg_hatches\n"
            result += "• search_egg_pokemon, get_regional_egg_pokemon, get_gift_exchange_pokemon\n\n"
            
            result += "### Cross-Platform Tools\n"
            result += "• get_all_shiny_pokemon, search_pokemon_everywhere, get_daily_priorities\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return f"Error getting server status: {str(e)}"
    
    @mcp.tool()
    async def clear_cache() -> str:
        """Clear the API data cache to force fresh data retrieval.
        
        Forces the server to fetch fresh data from the LeekDuck API on the next request.
        Use this if you suspect the data is stale or after major game updates.
        """
        try:
            api_client.clear_cache()
            logger.info("Cache cleared successfully")
            return f"✅ Cache cleared successfully at {get_current_time_str()}\n\nFresh data will be fetched on the next request."
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return f"Error clearing cache: {str(e)}"


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Pokemon Go MCP Server...")
    
    # Register all tools
    register_event_tools(mcp)
    register_raid_tools(mcp)
    register_research_tools(mcp)
    register_egg_tools(mcp)
    register_cross_cutting_tools()
    
    logger.info("All tools registered successfully")
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
