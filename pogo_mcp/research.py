"""Research-related tools for the Pokemon Go MCP server."""

import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from .api_client import api_client
from .types import ResearchTaskInfo
from .utils import (
    filter_research_by_reward, format_research_summary, get_current_time_str,
    validate_pokemon_name, search_pokemon_by_name
)

logger = logging.getLogger(__name__)


def register_research_tools(mcp: FastMCP) -> None:
    """Register all research-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_current_research() -> str:
        """Get all current field research tasks in Pokemon Go.
        
        Returns a comprehensive list of all field research tasks currently available
        from PokeStops, including task requirements and possible Pokemon rewards.
        Note: You receive ONE of the possible rewards, not all of them.
        """
        try:
            research_tasks = await api_client.get_research()
            
            if not research_tasks:
                return "No field research data available."
            
            result = f"# Current Field Research Tasks (as of {get_current_time_str()})\n\n"
            result += "**Important:** You get ONE of the possible rewards listed for each task, not all of them.\n\n"
            
            # Group by task type if available
            catch_tasks = []
            battle_tasks = []
            other_tasks = []
            
            for task in research_tasks:
                if task.task_type == "catch":
                    catch_tasks.append(task)
                elif task.task_type in ["battle", "raid"]:
                    battle_tasks.append(task)
                else:
                    other_tasks.append(task)
            
            if catch_tasks:
                result += "## 🎯 Catch Tasks\n\n"
                for task in catch_tasks:
                    result += format_research_summary(task) + "\n\n"
            
            if battle_tasks:
                result += "## ⚔️ Battle/Raid Tasks\n\n"
                for task in battle_tasks:
                    result += format_research_summary(task) + "\n\n"
            
            if other_tasks:
                result += "## 🎮 Other Tasks\n\n"
                for task in other_tasks:
                    result += format_research_summary(task) + "\n\n"
            
            # Summary statistics
            total_shiny_tasks = len([
                t for t in research_tasks 
                if any(r.can_be_shiny for r in t.rewards)
            ])
            
            result += f"**Summary:** {len(research_tasks)} research tasks available, "
            result += f"{total_shiny_tasks} have potential shiny rewards\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching research tasks: {e}")
            return f"Error fetching research tasks: {str(e)}"
    
    @mcp.tool()
    async def search_research_by_reward(pokemon_name: str) -> str:
        """Find field research tasks that reward a specific Pokemon.
        
        Args:
            pokemon_name: Name of the Pokemon to search for as a reward
            
        Returns research tasks that can give the specified Pokemon as a reward.
        """
        try:
            if not validate_pokemon_name(pokemon_name):
                return f"Invalid Pokemon name: '{pokemon_name}'"
            
            research_tasks = await api_client.get_research()
            matching_tasks = filter_research_by_reward(research_tasks, pokemon_name)
            
            if not matching_tasks:
                return f"No field research tasks found that reward '{pokemon_name}'."
            
            result = f"# Research Tasks Rewarding {pokemon_name.title()}\n\n"
            result += f"Found {len(matching_tasks)} task(s) that can reward {pokemon_name}:\n\n"
            
            for task in matching_tasks:
                result += format_research_summary(task) + "\n\n"
            
            # Check if any can be shiny
            shiny_tasks = [
                t for t in matching_tasks 
                if any(r.name.lower() == pokemon_name.lower() and r.can_be_shiny for r in t.rewards)
            ]
            
            if shiny_tasks:
                result += f"✨ **Shiny Alert:** {len(shiny_tasks)} of these tasks can reward shiny {pokemon_name}!\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching research by reward: {e}")
            return f"Error searching research by reward: {str(e)}"
    
    @mcp.tool()
    async def get_research_by_task_type(task_type: str) -> str:
        """Get field research tasks filtered by task type.
        
        Args:
            task_type: Type of task to filter by (catch, battle, raid, spin, walk, etc.)
            
        Returns research tasks that match the specified task type.
        """
        try:
            research_tasks = await api_client.get_research()
            task_type_lower = task_type.lower()
            
            # Filter by task type in the text or explicit type field
            matching_tasks = [
                t for t in research_tasks 
                if (t.task_type and task_type_lower in t.task_type.lower()) or
                   task_type_lower in t.text.lower()
            ]
            
            if not matching_tasks:
                return f"No field research tasks found for task type '{task_type}'."
            
            result = f"# {task_type.title()} Research Tasks ({len(matching_tasks)} found)\n\n"
            
            for task in matching_tasks:
                result += format_research_summary(task) + "\n\n"
            
            # Summary
            shiny_tasks = len([
                t for t in matching_tasks 
                if any(r.can_be_shiny for r in t.rewards)
            ])
            
            result += f"**Summary:** {len(matching_tasks)} {task_type} tasks, {shiny_tasks} have potential shiny rewards\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching {task_type} research: {e}")
            return f"Error fetching {task_type} research: {str(e)}"
    
    @mcp.tool()
    async def get_shiny_research_rewards() -> str:
        """Get all field research tasks that can reward shiny Pokemon.
        
        Returns research tasks where at least one of the possible rewards
        can be encountered as a shiny, perfect for shiny hunters.
        """
        try:
            research_tasks = await api_client.get_research()
            shiny_tasks = [
                t for t in research_tasks 
                if any(r.can_be_shiny for r in t.rewards)
            ]
            
            if not shiny_tasks:
                return "No field research tasks with shiny rewards found."
            
            result = f"# ✨ Research Tasks with Shiny Rewards (as of {get_current_time_str()})\n\n"
            result += f"Found {len(shiny_tasks)} tasks with potential shiny rewards:\n\n"
            
            # Group shiny Pokemon by task
            shiny_pokemon = set()
            for task in shiny_tasks:
                for reward in task.rewards:
                    if reward.can_be_shiny:
                        shiny_pokemon.add(reward.name)
            
            result += f"**Shiny Pokemon Available:** {', '.join(sorted(shiny_pokemon))}\n\n"
            
            for task in shiny_tasks:
                result += format_research_summary(task)
                
                # Highlight which rewards can be shiny
                shiny_rewards = [r.name for r in task.rewards if r.can_be_shiny]
                if shiny_rewards:
                    result += f"**✨ Shiny Possible:** {', '.join(shiny_rewards)}\n"
                
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching shiny research: {e}")
            return f"Error fetching shiny research: {str(e)}"
    
    @mcp.tool()
    async def get_easy_research_tasks() -> str:
        """Get field research tasks that are easy to complete.
        
        Returns tasks that can be completed quickly or with minimal effort,
        perfect for players who want to stack rewards efficiently.
        """
        try:
            research_tasks = await api_client.get_research()
            
            # Define easy task patterns
            easy_patterns = [
                "catch 1", "catch 2", "catch 3", "catch 4", "catch 5",
                "make 1", "make 2", "make 3",
                "spin 1", "spin 2", "spin 3", "spin 4", "spin 5",
                "transfer", "favorite", "trade",
                "snapshot", "buddy", "power up"
            ]
            
            easy_tasks = []
            for task in research_tasks:
                task_text_lower = task.text.lower()
                if any(pattern in task_text_lower for pattern in easy_patterns):
                    easy_tasks.append(task)
            
            if not easy_tasks:
                return "No easy research tasks found with current criteria."
            
            result = f"# 🚀 Easy Research Tasks ({len(easy_tasks)} found)\n\n"
            result += "These tasks can typically be completed quickly:\n\n"
            
            for task in easy_tasks:
                result += format_research_summary(task) + "\n\n"
            
            # Highlight valuable easy tasks
            valuable_easy = [
                t for t in easy_tasks 
                if any(r.can_be_shiny for r in t.rewards)
            ]
            
            if valuable_easy:
                result += f"⭐ **High Value:** {len(valuable_easy)} of these easy tasks have shiny potential!\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching easy research: {e}")
            return f"Error fetching easy research: {str(e)}"
    
    @mcp.tool()
    async def search_research_tasks(query: str) -> str:
        """Search field research tasks by task description.
        
        Args:
            query: Search term to look for in task descriptions
            
        Returns research tasks that match the search criteria.
        """
        try:
            research_tasks = await api_client.get_research()
            query_lower = query.lower()
            
            matching_tasks = [
                t for t in research_tasks 
                if query_lower in t.text.lower()
            ]
            
            if not matching_tasks:
                return f"No research tasks found matching '{query}'."
            
            result = f"# Research Tasks matching '{query}' ({len(matching_tasks)} found)\n\n"
            
            for task in matching_tasks:
                result += format_research_summary(task) + "\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching research tasks: {e}")
            return f"Error searching research tasks: {str(e)}"
    
    @mcp.tool()
    async def get_research_recommendations(priority: str = "balanced") -> str:
        """Get research task recommendations based on specified priority.
        
        Args:
            priority: Priority type - "shiny" for shiny hunters, "easy" for quick completion, 
                     "rare" for uncommon Pokemon, or "balanced" for general recommendations
            
        Returns recommended research tasks to focus on based on the priority.
        """
        try:
            research_tasks = await api_client.get_research()
            
            result = f"# Research Task Recommendations ({priority.title()} Priority)\n\n"
            
            if priority.lower() == "shiny":
                tasks = [t for t in research_tasks if any(r.can_be_shiny for r in t.rewards)]
                result += "Focus on these tasks for shiny hunting:\n\n"
                
            elif priority.lower() == "easy":
                easy_patterns = ["catch 1", "catch 2", "catch 3", "make 1", "make 2", "spin"]
                tasks = [
                    t for t in research_tasks 
                    if any(pattern in t.text.lower() for pattern in easy_patterns)
                ]
                result += "These tasks are quick and easy to complete:\n\n"
                
            elif priority.lower() == "rare":
                # Tasks with uncommon Pokemon (this is a simplified heuristic)
                rare_pokemon = ["dratini", "larvitar", "beldum", "gible", "deino", "axew"]
                tasks = []
                for task in research_tasks:
                    for reward in task.rewards:
                        if any(rare in reward.name.lower() for rare in rare_pokemon):
                            tasks.append(task)
                            break
                result += "These tasks reward rare or pseudo-legendary Pokemon:\n\n"
                
            else:  # balanced
                # Mix of shiny potential and reasonable difficulty
                tasks = []
                for task in research_tasks:
                    has_shiny = any(r.can_be_shiny for r in task.rewards)
                    is_moderate = not any(num in task.text for num in ["10", "15", "20", "25", "30"])
                    
                    if has_shiny or is_moderate:
                        tasks.append(task)
                
                result += "Balanced recommendations considering effort vs. reward:\n\n"
            
            if not tasks:
                return f"No research tasks found matching {priority} priority criteria."
            
            # Sort by potential value (shiny tasks first)
            tasks.sort(key=lambda t: any(r.can_be_shiny for r in t.rewards), reverse=True)
            
            for i, task in enumerate(tasks[:15]):  # Limit to top 15
                priority_marker = "🌟" if any(r.can_be_shiny for r in task.rewards) else "⭐"
                result += f"{priority_marker} **{task.text}**\n"
                
                rewards = [f"{r.name}{'✨' if r.can_be_shiny else ''}" for r in task.rewards]
                result += f"Rewards: {', '.join(rewards)}\n\n"
            
            if len(tasks) > 15:
                result += f"... and {len(tasks) - 15} more tasks match your criteria.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting research recommendations: {e}")
            return f"Error getting research recommendations: {str(e)}"
