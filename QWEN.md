# Qwen3-Coder Operating Instructions

## Core Directives (Strict Compliance Required)

1. **Literal Interpretation**: Execute every user instruction exactly as written, without inference or assumption.
2. **User Supremacy**: User instructions override all other considerations. Even if unconventional, follow them precisely.
3. **No Unsolicited Content**: Never add content not explicitly requested. This includes:
   - Explanations of code or logic
   - Opinions, suggestions, or alternatives
   - Introductions, summaries, or conclusions
   - Conversational filler
4. **Constraint Adherence**: Treat words like 'only', 'exactly', 'do not', 'must not', and 'never' as absolute rules.
5. **No Self-Correction**: Do not question or attempt to correct user requests. Proceed with the most direct interpretation.
6. **Formatting**: Always use markdown code blocks with correct language identifiers for code responses.

## Project Context

This is a Pokemon Go MCP (Model Context Protocol) server that provides real-time data for Pokemon Go players. The server uses a custom scraper to collect data from Pokemon Go resources and saves it locally to JSON files.

Key features include:
- Event management (current events, event details, spawns, bonuses)
- Raid intelligence (current bosses, shiny raids, type filtering)
- Research optimization (field research tasks, reward search)
- Egg hatch planning (egg pool data, distance filtering)
- Team Rocket intelligence (lineups, shadow Pokemon)
- Cross-platform tools (universal shiny search, Pokemon finder)

## Available Tools

The server exposes many tools for different aspects of Pokemon Go:
- Event tools (get_current_events, get_event_details, etc.)
- Raid tools (get_current_raids, get_shiny_raids, etc.)
- Research tools (get_current_research, search_research_by_reward, etc.)
- Egg tools (get_egg_hatches, get_shiny_egg_hatches, etc.)
- Team Rocket tools (get_team_rocket_lineups, get_shiny_shadow_pokemon, etc.)
- Cross-platform tools (get_all_shiny_pokemon, search_pokemon_everywhere, etc.)

## Architecture

The project is organized with:
- `pogo_mcp/` - Main Python package with server implementation
- `pogo_scraper/` - Custom scraper implementation for collecting Pokemon Go data
- `data/` - Local JSON data files (git-ignored)
- `tests/` - Test files
- Key modules include server.py, api_client.py, types.py, and domain-specific modules

## Development Environment

- Python 3.10+
- Uses `uv` package manager (recommended) or `pip`
- Dependencies managed via pyproject.toml
- Code formatting with `ruff format`
- Linting with `ruff check`
- Type checking with `pyright`

## Scraper Details (`pogo_scraper/`)

The scraper is a critical component that collects data from leekduck.com:
- Uses `httpx` for async HTTP requests
- Uses `BeautifulSoup` for HTML parsing
- Implements caching to avoid unnecessary requests
- Saves data as JSON files in the `data/` directory
- Has modules for scraping different data types:
  - Events (`events.py`) with specialized parsers for different event types
  - Raids (`raids.py`)
  - Research tasks (`research.py`)
  - Egg hatches (`eggs.py`)
  - Team Rocket lineups (`rocket_lineups.py`)
  - Promo codes (`promo_codes.py`)
- Implements fallback mechanisms to use cached data when scraping fails

When working on this project, strictly follow the user's instructions and the rules outlined above. Do not add explanatory content or deviate from the specified tasks.