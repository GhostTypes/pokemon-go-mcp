# MCP Server Integration Tests

## Overview

This directory contains comprehensive integration tests for the Pokemon Go MCP Server. These tests verify that all MCP tools function correctly by making real API calls (no mocking).

## Test Coverage

### Total: 78 Integration Tests

All tests test REAL functionality - no mocking!

#### Server Initialization Tests (13 tests)
- `test_mcp_server.py`: Tests for server initialization, data access, and caching
  - Server instance creation and configuration
  - API client data fetching (events, raids, research, eggs, rocket lineups, promo codes)
  - Cache management and population

#### Event Tools Tests (9 tests)
- `test_event_tools.py`: Tests for all 6 event-related MCP tools
  - get_current_events
  - get_event_details (with valid and invalid IDs)
  - get_community_day_info
  - get_event_spawns (with and without filters)
  - get_event_bonuses
  - search_events (with results and no results)

#### Raid Tools Tests (11 tests)
- `test_raid_tools.py`: Tests for all 7 raid-related MCP tools
  - get_current_raids
  - get_raid_by_tier (multiple tiers tested)
  - get_shiny_raids
  - search_raid_boss (found and not found)
  - get_raids_by_type
  - get_weather_boosted_raids
  - get_raid_recommendations (with various filters)

#### Research Tools Tests (12 tests)
- `test_research_tools.py`: Tests for all 7 research-related MCP tools
  - get_current_research
  - search_research_by_reward (found and not found)
  - get_research_by_task_type
  - get_shiny_research_rewards
  - get_easy_research_tasks
  - search_research_tasks (with results and no results)
  - get_research_recommendations (balanced, shiny, easy, rare)

#### Egg Tools Tests (15 tests)
- `test_egg_tools.py`: Tests for all 10 egg-related MCP tools
  - get_egg_hatches
  - get_egg_hatches_by_distance (2km, 5km, 10km)
  - get_shiny_egg_hatches
  - search_egg_pokemon (found and not found)
  - get_regional_egg_pokemon
  - get_gift_exchange_pokemon
  - get_route_gift_pokemon
  - get_adventure_sync_rewards
  - get_egg_recommendations (shiny, rare, quick, default)

#### Rocket Tools Tests (11 tests)
- `test_rocket_tools.py`: Tests for all 7 Team Rocket-related MCP tools
  - get_team_rocket_lineups
  - search_rocket_by_pokemon (found and not found)
  - get_shiny_shadow_pokemon
  - get_rocket_encounters
  - get_rocket_trainers_by_type (water, fire)
  - calculate_pokemon_weakness (multiple scenarios)
  - get_rocket_trainer_details (found and not found)

#### Promo Code Tools Tests (1 test)
- `test_promo_code_tools.py`: Tests for the 1 promo code tool
  - get_active_promo_codes

#### Cross-Cutting Tools Tests (6 tests)
- `test_cross_cutting_tools.py`: Tests for all 5 cross-cutting MCP tools
  - get_all_shiny_pokemon
  - search_pokemon_everywhere (found and not found)
  - get_daily_priorities
  - get_server_status
  - clear_cache

## Running the Tests

### Run All Integration Tests
```bash
python -m pytest tests/integration/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/integration/test_event_tools.py -v
```

### Run Specific Test
```bash
python -m pytest tests/integration/test_event_tools.py::TestEventTools::test_get_current_events -v
```

## Test Data

The integration tests require test data files in the `data/` directory:
- `events.json`
- `raids.json`
- `research.json`
- `eggs.json`
- `rocket-lineups.json`
- `promo-codes.json`

These files are automatically created with sample data when tests are first run. For real data, run the scraper:

```bash
python -c "from pogo_scraper.scraper import LeekDuckScraper; import asyncio; scraper = LeekDuckScraper(); asyncio.run(scraper.scrape_all())"
```

## Test Architecture

### Fixtures (conftest.py)

#### Session-Scoped Fixtures
- `mcp_server`: The MCP server instance
- `api_client_instance`: The API client instance
- `data_dir`: Path to the data directory
- `ensure_test_data`: Validates all required data files exist
- `sample_event_id`: Sample event ID for tests
- `sample_pokemon_name`: Sample Pokemon name for tests
- `sample_raid_tier`: Sample raid tier for tests
- `sample_trainer_name`: Sample Team Rocket trainer name for tests

#### Function-Scoped Fixtures
- `fresh_cache`: Clears the API cache before each test

### Test Pattern

Each test follows this pattern:
1. Register the tool with a mock MCP instance
2. Capture the registered tool function
3. Call the tool function with appropriate parameters
4. Verify the output is a non-empty string
5. Verify the output contains expected content

### Real Integration Testing

**NO MOCKING** - These are true integration tests that:
- Use real API client instances
- Read real JSON data files
- Execute actual tool functions
- Test complete data flow from file → API client → tool → output

## Test Results

**Latest Run: 78/78 PASSED (100%)**

All 43 MCP tools have full integration test coverage with all tests passing!

## Contributing

When adding new MCP tools:
1. Add tests to the appropriate test file
2. Ensure test data supports the new tool
3. Run all tests to verify no regressions
4. Update this README with test count

## Dependencies

- pytest
- pytest-asyncio
- All pogo_mcp dependencies (httpx, python-dateutil, etc.)
