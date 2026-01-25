# MCP Server Reload & Test Prompt

**Copy and paste this into your fresh Claude Code session:**

---

## Current Status

We've been fixing the Pokemon Go MCP server. Here's what we've accomplished:

### ✅ COMPLETED:
1. **Fixed Scraper** - Changed raids URL from `/boss/` to `/raid-bosses/`
2. **Fresh Data Scraped** - 259 items (67 events, 17 raids, 60 research, 89 eggs, 26 rocket)
3. **Concatenated Names Fixed** - Egg scraper validation improved
4. **calculate_pokemon_weakness Tool** - Rewritten to work with ANY Pokemon using PokeAPI fallback
5. **All Tests Passing** - 167/167 tests pass

### ⚠️ REMAINING ISSUES:
1. **33 Ruff linting violations** - See CODE_QUALITY_ISSUES.md
2. **Duplicate events** - LeekDuck data source issue (has duplicate URLs for same event)
3. **calculate_pokemon_weakness** - Needs testing with fresh MCP server session to verify PokeAPI fallback works

### 📁 FILES MODIFIED:
- `pogo_scraper/raids.py` - Fixed raids URL
- `pogo_scraper/eggs.py` - Improved validation logic
- `pogo_mcp/pokemon_types.py` - NEW: Type lookup service
- `pogo_mcp/rocket_lineups.py` - Rewritten calculate_pokemon_weakness tool
- `tests/test_pokemon_types.py` - NEW: Tests for type lookup
- `tests/integration/test_rocket_tools.py` - Updated tests

### 🎯 NEXT STEPS:
1. **Test MCP server** with calculate_pokemon_weakness using Pokemon NOT in Team Rocket lineups (e.g., "Pikachu", "Mewtwo")
2. **Fix code quality issues** - Run through CODE_QUALITY_ISSUES.md
3. **Address duplicate events** if needed

### 🧪 TO TEST:
```bash
# After reload, test these MCP tools:
- mcp__pokemon-go__calculate_pokemon_weakness with pokemon_name="Pikachu" and attacking_type="ground"
- mcp__pokemon-go__get_egg_hatches
- mcp__pokemon-go__search_events with query="community"
```

All data is fresh and scraped as of 2026-01-25 01:01:24 UTC.
