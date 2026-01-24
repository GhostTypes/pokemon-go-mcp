# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two distinct projects that work together:

1. **`pogo_scraper/`** - A web scraper that fetches Pokemon Go data from LeekDuck.com and saves it to JSON files
2. **`pogo_mcp/`** - A Model Context Protocol (MCP) server that reads the scraped JSON data and exposes it via MCP tools

The scraper runs on a GitHub Actions schedule (every hour) and uploads data to a separate `data` branch. The MCP server reads from local JSON files in the `data/` directory.

## Development Commands

### MCP Server (`pogo_mcp/`)

```bash
# Install dependencies
uv sync

# Run the MCP server (stdio transport - default)
uv run python server.py

# Run with HTTP transport (for web integrations)
MCP_TRANSPORT=http MCP_PORT=8000 uv run python server.py

# Code formatting
ruff format .

# Linting
ruff check .

# Type checking
pyright

# Run tests
pytest

# Run tests with coverage
pytest --cov=pogo_mcp

# Run a specific test module
pytest tests/test_events_parsing.py
```

### Scraper (`pogo_scraper/`)

```bash
# Install scraper dependencies
pip install httpx beautifulsoup4 requests lxml brotli

# Run scraper for all data sources
python pogo_scraper/scraper.py --all --output-dir data --cache-duration 0

# Run scraper for specific source
python pogo_scraper/scraper.py --events --output-dir data

# Run with custom cache duration (in seconds)
python pogo_scraper/scraper.py --all --output-dir data --cache-duration 300
```

## Architecture

### Data Flow

```
LeekDuck.com → pogo_scraper → data/*.json → pogo_mcp → MCP Clients
```

1. **Scraper** (`pogo_scraper/`) fetches HTML from LeekDuck.com, parses it with BeautifulSoup, and outputs JSON files
2. **GitHub Action** runs the scraper hourly and commits to the `data` branch
3. **MCP Server** (`pogo_mcp/`) reads local JSON files and serves data via MCP protocol

### MCP Server Structure (`pogo_mcp/`)

- **`server.py`** - Main entry point, FastMCP server initialization, cross-cutting tools (shiny search, daily priorities)
- **`api_client.py`** - `LeekDuckAPIClient` class loads data from local JSON files with 24-hour caching
- **`types.py`** - Dataclass type definitions for all Pokemon Go data structures
- **`utils.py`** - Helper functions for filtering, formatting, and validation
- **`events.py`** - Event-related MCP tools
- **`raids.py`** - Raid-related MCP tools
- **`research.py`** - Research task-related MCP tools
- **`eggs.py`** - Egg hatch-related MCP tools
- **`rocket_lineups.py`** - Team Rocket lineup-related MCP tools
- **`promo_codes.py`** - Promo code-related MCP tools

### Scraper Structure (`pogo_scraper/`)

- **`scraper.py`** - Main scraper class with HTTP client and caching logic
- **`events.py`** - Scrapes events list page
- **`raids.py`** - Scrapes current raid bosses
- **`research.py`** - Scrapes field research tasks
- **`eggs.py`** - Scrapes egg hatch pools
- **`rocket_lineups.py`** - Scrapes Team Rocket lineups
- **`promo_codes.py`** - Scrapes active promo codes
- **`parsers/`** - Sub-modules for parsing specific event types and detailed data:
  - `events/` - Community Day details, raid battles, spotlight hours, etc.
  - `rocket_lineups/` - Trainer data, weakness calculations

### Key Patterns

#### Fallback Data Sources

The MCP server implements fallback logic for raid data:
- Primary: `data/raids.json`
- Fallback: Extracts raid bosses from event data (`events.json`)

See `api_client.py:extract_raids_from_events()`

#### Type System

All data structures use Python dataclasses defined in `types.py`. The scraper and MCP server must stay in sync - if you add fields to the scraper output, update the corresponding dataclass.

#### Transport Modes

The MCP server supports three transports via environment variables:
- `stdio` (default) - For Claude Desktop, Claude Code
- `http` - For web integrations (n8n, HTTP clients)
- `sse` - Server-Sent Events transport

#### Caching

- **Scraper**: File-based caching with configurable duration (default 5 minutes)
- **MCP Server**: In-memory caching with 24-hour duration (`api_client._cache_duration`)

## Common Tasks

### Adding a New Data Source

1. Add scraper module in `pogo_scraper/` following existing patterns
2. Add type definitions in `pogo_mcp/types.py`
3. Add fetch method in `pogo_mcp/api_client.py`
4. Add MCP tools in a new `pogo_mcp/<source>.py` file
5. Register tools in `pogo_mcp/server.py:main()`
6. Update GitHub Action to validate new data file

### Updating Parsers for LeekDuck Changes

LeekDuck.com page structure changes require parser updates:
1. Inspect the specific parser in `pogo_scraper/parsers/`
2. Update CSS selectors and HTML structure parsing
3. Test scraper locally with `python pogo_scraper/scraper.py --<source> --cache-duration 0`
4. Verify JSON output structure matches `pogo_mcp/types.py`

### Debugging MCP Tools

```bash
# Run server with verbose logging
LOGLEVEL=DEBUG uv run python server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python pogo_mcp/server.py
```

## Important Files

- **`data/`** - Local JSON data files (git-ignored, sourced from `data` branch)
- **`.github/workflows/scrape-pokemon-data.yml`** - Automated scraping workflow
- **`server.py`** (root) - Entry point that calls `pogo_mcp/server.py:main()`
- **`pyproject.toml`** - Project dependencies and tool configuration
- **`tests/`** - Test files for parser validation and MCP tool testing
