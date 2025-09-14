"""Team Rocket lineups tools for the Pokemon Go MCP server."""

import logging
from typing import List, Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

from .api_client import api_client
from .types import RocketTrainerInfo, ShadowPokemonInfo, RocketLineupSlot
from .utils import (
    format_rocket_summary, filter_trainers_by_type, search_rocket_trainers_by_pokemon,
    get_shiny_shadow_pokemon, get_rocket_encounters, calculate_type_effectiveness,
    get_current_time_str, validate_pokemon_name
)

logger = logging.getLogger(__name__)


def register_rocket_tools(mcp: FastMCP) -> None:
    """Register all Team Rocket lineup tools with the MCP server."""

    @mcp.tool()
    async def get_team_rocket_lineups() -> str:
        """Get all Team Rocket trainer lineups currently available.

        Returns comprehensive information about all Team Rocket trainers,
        their Pokemon lineups, types, and encounter rewards.
        """
        try:
            trainers = await api_client.get_rocket_lineups()

            if not trainers:
                return "No Team Rocket lineup data available."

            result = f"# Team Rocket Lineups (as of {get_current_time_str()})\n\n"
            result += f"**Total Trainers:** {len(trainers)}\n\n"

            # Organize trainers by type
            leaders = [t for t in trainers if 'leader' in t.title.lower() or 'boss' in t.title.lower()]
            grunts_by_type = {}
            other_trainers = []

            for trainer in trainers:
                if trainer in leaders:
                    continue
                elif trainer.type:
                    trainer_type = trainer.type.title()
                    if trainer_type not in grunts_by_type:
                        grunts_by_type[trainer_type] = []
                    grunts_by_type[trainer_type].append(trainer)
                else:
                    other_trainers.append(trainer)

            # Display leaders first
            if leaders:
                result += "## 🎯 Leaders\n\n"
                for leader in leaders:
                    result += format_rocket_summary(leader) + "\n\n"

            # Display grunts by type
            for trainer_type in sorted(grunts_by_type.keys()):
                result += f"## {trainer_type.title()} Type Grunts\n\n"
                for trainer in grunts_by_type[trainer_type]:
                    result += format_rocket_summary(trainer) + "\n\n"

            # Display other trainers
            if other_trainers:
                result += "## Other Trainers\n\n"
                for trainer in other_trainers:
                    result += format_rocket_summary(trainer) + "\n\n"

            # Summary statistics
            total_pokemon = sum(sum(len(slot.pokemon) for slot in trainer.lineups) for trainer in trainers)
            total_encounters = sum(sum(len(slot.pokemon) for slot in trainer.lineups if slot.is_encounter) for trainer in trainers)
            shiny_count = len(get_shiny_shadow_pokemon(trainers))

            result += "## 📊 Summary\n\n"
            result += f"• **{len(trainers)}** trainers total\n"
            result += f"• **{total_pokemon}** Pokemon options\n"
            result += f"• **{total_encounters}** possible encounters\n"
            result += f"• **{shiny_count}** shiny-eligible Shadow Pokemon\n"

            return result

        except Exception as e:
            logger.error(f"Error fetching Team Rocket lineups: {e}")
            return f"Error fetching Team Rocket lineups: {str(e)}"

    @mcp.tool()
    async def search_rocket_by_pokemon(pokemon_name: str) -> str:
        """Search for Team Rocket trainers that have a specific Pokemon.

        Args:
            pokemon_name: Name of the Pokemon to search for

        Returns information about which Team Rocket trainers use this Pokemon.
        """
        try:
            if not validate_pokemon_name(pokemon_name):
                return f"Invalid Pokemon name: '{pokemon_name}'"

            trainers = await api_client.get_rocket_lineups()
            matching_trainers = search_rocket_trainers_by_pokemon(trainers, pokemon_name)

            if not matching_trainers:
                return f"No Team Rocket trainers found using {pokemon_name.title()}."

            result = f"# Team Rocket Trainers with {pokemon_name.title()}\n\n"
            result += f"Found **{len(matching_trainers)}** trainers using {pokemon_name.title()}:\n\n"

            for trainer in matching_trainers:
                result += format_rocket_summary(trainer)

                # Show which slots have this Pokemon
                matching_slots = []
                for slot in trainer.lineups:
                    slot_pokemon = [p for p in slot.pokemon if pokemon_name.lower() in p.name.lower()]
                    if slot_pokemon:
                        encounter_text = " (Encounter)" if slot.is_encounter else ""
                        shiny_pokemon = [p for p in slot_pokemon if p.can_be_shiny]
                        shiny_text = f" - {len(shiny_pokemon)} can be shiny" if shiny_pokemon else ""
                        matching_slots.append(f"Slot {slot.slot}{encounter_text}: {len(slot_pokemon)} options{shiny_text}")

                if matching_slots:
                    result += "\n  " + "\n  ".join(matching_slots)

                result += "\n\n"

            return result

        except Exception as e:
            logger.error(f"Error searching for Pokemon in Team Rocket lineups: {e}")
            return f"Error searching for Pokemon: {str(e)}"

    @mcp.tool()
    async def get_shiny_shadow_pokemon() -> str:
        """Get all Shadow Pokemon that can be shiny from Team Rocket encounters.

        Returns a comprehensive list of all shiny-eligible Shadow Pokemon
        with their types, weaknesses, and which trainers use them.
        """
        try:
            trainers = await api_client.get_rocket_lineups()
            shiny_pokemon = get_shiny_shadow_pokemon(trainers)

            if not shiny_pokemon:
                return "No shiny Shadow Pokemon found in current Team Rocket lineups."

            result = f"# ✨ Shiny Shadow Pokemon (as of {get_current_time_str()})\n\n"
            result += f"**Total Shiny Shadow Pokemon:** {len(shiny_pokemon)}\n\n"

            for pokemon in shiny_pokemon:
                result += f"## {pokemon.name}\n\n"

                # Types
                if pokemon.types:
                    types_str = " / ".join(pokemon.types).title()
                    result += f"**Types:** {types_str}\n"

                # Weaknesses
                if pokemon.weaknesses:
                    double_weak = pokemon.weaknesses.get('double', [])
                    single_weak = pokemon.weaknesses.get('single', [])

                    if double_weak:
                        result += f"**Double Weakness:** {', '.join(double_weak).title()}\n"
                    if single_weak:
                        result += f"**Weakness:** {', '.join(single_weak).title()}\n"

                # Find which trainers have this Pokemon
                using_trainers = search_rocket_trainers_by_pokemon(trainers, pokemon.name)
                if using_trainers:
                    trainer_names = [t.name for t in using_trainers]
                    result += f"**Available from:** {', '.join(trainer_names)}\n"

                result += "\n"

            return result

        except Exception as e:
            logger.error(f"Error fetching shiny Shadow Pokemon: {e}")
            return f"Error fetching shiny Shadow Pokemon: {str(e)}"

    @mcp.tool()
    async def get_rocket_encounters() -> str:
        """Get all possible Team Rocket encounter rewards.

        Returns information about Pokemon you can catch after defeating
        Team Rocket trainers, organized by trainer.
        """
        try:
            trainers = await api_client.get_rocket_lineups()
            encounters = get_rocket_encounters(trainers)

            if not encounters:
                return "No Team Rocket encounter data found."

            result = f"# 🎁 Team Rocket Encounter Rewards (as of {get_current_time_str()})\n\n"

            total_encounters = sum(len(pokemon_list) for _, pokemon_list in encounters)
            shiny_encounters = 0

            for trainer_name, encounter_pokemon in encounters:
                shiny_count = sum(1 for p in encounter_pokemon if p.can_be_shiny)
                shiny_encounters += shiny_count

                result += f"## {trainer_name}\n\n"
                result += f"**Possible Encounters:** {len(encounter_pokemon)}"
                if shiny_count > 0:
                    result += f" ({shiny_count} can be shiny ✨)"
                result += "\n\n"

                for pokemon in encounter_pokemon:
                    shiny_indicator = " ✨" if pokemon.can_be_shiny else ""
                    types_str = f" ({'/'.join(pokemon.types)})" if pokemon.types else ""
                    result += f"• **{pokemon.name}**{types_str}{shiny_indicator}\n"

                result += "\n"

            result += f"## 📊 Summary\n\n"
            result += f"• **{len(encounters)}** trainers offer encounters\n"
            result += f"• **{total_encounters}** total encounter options\n"
            result += f"• **{shiny_encounters}** can be shiny ✨\n"

            return result

        except Exception as e:
            logger.error(f"Error fetching Team Rocket encounters: {e}")
            return f"Error fetching Team Rocket encounters: {str(e)}"

    @mcp.tool()
    async def get_rocket_trainers_by_type(trainer_type: str) -> str:
        """Get Team Rocket trainers filtered by Pokemon type.

        Args:
            trainer_type: Pokemon type to filter by (e.g., "water", "fire", "psychic")

        Returns information about Team Rocket trainers specialized in that type.
        """
        try:
            trainers = await api_client.get_rocket_lineups()
            filtered_trainers = filter_trainers_by_type(trainers, trainer_type)

            if not filtered_trainers:
                return f"No {trainer_type.title()} type Team Rocket trainers found."

            result = f"# {trainer_type.title()} Type Team Rocket Trainers\n\n"
            result += f"Found **{len(filtered_trainers)}** {trainer_type.lower()} type trainers:\n\n"

            for trainer in filtered_trainers:
                result += format_rocket_summary(trainer) + "\n"

                # Show type-specific Pokemon
                type_pokemon = []
                for slot in trainer.lineups:
                    for pokemon in slot.pokemon:
                        if trainer_type.lower() in [t.lower() for t in pokemon.types]:
                            shiny_indicator = " ✨" if pokemon.can_be_shiny else ""
                            type_pokemon.append(f"{pokemon.name}{shiny_indicator}")

                if type_pokemon:
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_pokemon = []
                    for p in type_pokemon:
                        if p not in seen:
                            unique_pokemon.append(p)
                            seen.add(p)

                    result += f"  **{trainer_type.title()} Pokemon:** {', '.join(unique_pokemon)}\n"

                result += "\n"

            return result

        except Exception as e:
            logger.error(f"Error filtering Team Rocket trainers by type: {e}")
            return f"Error filtering Team Rocket trainers: {str(e)}"

    @mcp.tool()
    async def calculate_pokemon_weakness(pokemon_name: str, attacking_type: str) -> str:
        """Calculate type effectiveness when attacking a specific Shadow Pokemon.

        Args:
            pokemon_name: Name of the Shadow Pokemon to attack
            attacking_type: Type of attack to use (e.g., "fire", "water", "fighting")

        Returns the damage multiplier and effectiveness description.
        """
        try:
            if not validate_pokemon_name(pokemon_name):
                return f"Invalid Pokemon name: '{pokemon_name}'"

            trainers = await api_client.get_rocket_lineups()

            # Find the Pokemon in Team Rocket lineups
            target_pokemon = None
            for trainer in trainers:
                for slot in trainer.lineups:
                    for pokemon in slot.pokemon:
                        if pokemon_name.lower() in pokemon.name.lower():
                            target_pokemon = pokemon
                            break
                    if target_pokemon:
                        break
                if target_pokemon:
                    break

            if not target_pokemon:
                return f"{pokemon_name.title()} not found in current Team Rocket lineups."

            if not target_pokemon.types:
                return f"No type information available for {target_pokemon.name}."

            effectiveness = calculate_type_effectiveness(attacking_type, target_pokemon.types)

            result = f"# Type Effectiveness: {attacking_type.title()} vs {target_pokemon.name}\n\n"
            result += f"**Target Pokemon:** {target_pokemon.name}\n"
            result += f"**Target Types:** {' / '.join(target_pokemon.types).title()}\n"
            result += f"**Attacking Type:** {attacking_type.title()}\n\n"

            # Effectiveness description
            if effectiveness == 0.0:
                result += "**Result:** No Effect (0× damage) 🚫\n"
                result += f"{attacking_type.title()} attacks have no effect on {' / '.join(target_pokemon.types).title()} types."
            elif effectiveness == 0.25:
                result += "**Result:** Not Very Effective (0.25× damage) 🔴\n"
                result += "This is a very poor matchup."
            elif effectiveness == 0.5:
                result += "**Result:** Not Very Effective (0.5× damage) 🟠\n"
                result += "This attack is resisted."
            elif effectiveness == 1.0:
                result += "**Result:** Normal Effectiveness (1× damage) ⚪\n"
                result += "This attack deals normal damage."
            elif effectiveness == 2.0:
                result += "**Result:** Super Effective (2× damage) 🟢\n"
                result += "This attack is super effective!"
            elif effectiveness == 4.0:
                result += "**Result:** Super Effective (4× damage) 🟢🟢\n"
                result += "This attack is super effective against both types!"
            else:
                result += f"**Result:** {effectiveness}× damage\n"

            # Show weaknesses from data
            if target_pokemon.weaknesses:
                double_weak = target_pokemon.weaknesses.get('double', [])
                single_weak = target_pokemon.weaknesses.get('single', [])

                if double_weak or single_weak:
                    result += "\n**Known Weaknesses:**\n"
                    if double_weak:
                        result += f"• **Double weakness:** {', '.join(double_weak).title()}\n"
                    if single_weak:
                        result += f"• **Weak to:** {', '.join(single_weak).title()}\n"

            return result

        except Exception as e:
            logger.error(f"Error calculating Pokemon weakness: {e}")
            return f"Error calculating weakness: {str(e)}"

    @mcp.tool()
    async def get_rocket_trainer_details(trainer_name: str) -> str:
        """Get detailed information about a specific Team Rocket trainer.

        Args:
            trainer_name: Name of the Team Rocket trainer (partial matches work)

        Returns comprehensive details about the trainer's lineup and Pokemon.
        """
        try:
            trainers = await api_client.get_rocket_lineups()

            # Find matching trainers
            matching_trainers = [t for t in trainers if trainer_name.lower() in t.name.lower()]

            if not matching_trainers:
                return f"No Team Rocket trainer found matching '{trainer_name}'."

            if len(matching_trainers) > 1:
                result = f"Multiple trainers found matching '{trainer_name}':\n\n"
                for trainer in matching_trainers:
                    result += f"• {trainer.name}\n"
                result += "\nPlease be more specific."
                return result

            trainer = matching_trainers[0]

            result = f"# {trainer.name} - Team Rocket Trainer Details\n\n"

            # Basic info
            if trainer.title:
                result += f"**Title:** {trainer.title}\n"
            if trainer.type:
                result += f"**Specialty:** {trainer.type.title()} type\n"
            if trainer.quote:
                result += f"**Quote:** *\"{trainer.quote}\"*\n"

            result += f"**Total Lineup Slots:** {len(trainer.lineups)}\n\n"

            # Detailed lineup
            result += "## 🔥 Pokemon Lineup\n\n"

            for slot in trainer.lineups:
                encounter_indicator = " 🎁" if slot.is_encounter else ""
                result += f"### Slot {slot.slot}{encounter_indicator}\n\n"

                if slot.is_encounter:
                    result += "*This slot determines your encounter reward*\n\n"

                for pokemon in slot.pokemon:
                    shiny_indicator = " ✨" if pokemon.can_be_shiny else ""
                    result += f"**{pokemon.name}**{shiny_indicator}\n"

                    if pokemon.types:
                        result += f"• **Type:** {' / '.join(pokemon.types).title()}\n"

                    if pokemon.weaknesses:
                        double_weak = pokemon.weaknesses.get('double', [])
                        single_weak = pokemon.weaknesses.get('single', [])

                        if double_weak:
                            result += f"• **Double weakness:** {', '.join(double_weak).title()}\n"
                        if single_weak:
                            result += f"• **Weak to:** {', '.join(single_weak).title()}\n"

                    result += "\n"

                result += "\n"

            # Summary stats
            total_pokemon = sum(len(slot.pokemon) for slot in trainer.lineups)
            shiny_pokemon = sum(sum(1 for p in slot.pokemon if p.can_be_shiny) for slot in trainer.lineups)
            encounter_pokemon = sum(len(slot.pokemon) for slot in trainer.lineups if slot.is_encounter)

            result += "## 📊 Summary\n\n"
            result += f"• **Total Pokemon Options:** {total_pokemon}\n"
            result += f"• **Possible Encounters:** {encounter_pokemon}\n"
            result += f"• **Shiny Opportunities:** {shiny_pokemon} ✨\n"

            return result

        except Exception as e:
            logger.error(f"Error getting trainer details: {e}")
            return f"Error getting trainer details: {str(e)}"