<div align="center">
  <h1>Pokemon Go MCP Server</h1>
  <p>A comprehensive Model Context Protocol (MCP) server providing real-time Pokemon Go data including events, raids, research tasks, egg hatches, and Team Rocket lineups</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=for-the-badge" alt="Platform Support">
</p>

---

<div align="center">
  <h2>Feature Overview</h2>
</div>

<div align="center">
<table>
  <tr>
    <th>Category</th>
    <th>Features</th>
    <th>Key Capabilities</th>
  </tr>
  <tr>
    <td><strong>Events</strong></td>
    <td>Current Events, Event Details, Community Days</td>
    <td>Real-time event tracking, spawn data, bonuses, exclusive moves</td>
  </tr>
  <tr>
    <td><strong>Raids</strong></td>
    <td>Raid Bosses, Tier Filtering, Shiny Tracking</td>
    <td>Complete raid listings, type filtering, weather boost detection</td>
  </tr>
  <tr>
    <td><strong>Research</strong></td>
    <td>Field Tasks, Reward Tracking, Task Filtering</td>
    <td>Task discovery, shiny rewards, easy completion paths</td>
  </tr>
  <tr>
    <td><strong>Eggs</strong></td>
    <td>Egg Pools, Distance Filtering, Shiny Tracking</td>
    <td>Distance-based filtering, regional exclusives, Adventure Sync rewards</td>
  </tr>
  <tr>
    <td><strong>Team Rocket</strong></td>
    <td>Lineups, Shadow Pokemon, Encounter Rewards</td>
    <td>Complete trainer lineups, type effectiveness, shiny shadows</td>
  </tr>
  <tr>
    <td><strong>Cross-Platform</strong></td>
    <td>Universal Search, Daily Priorities, Status</td>
    <td>Multi-source search, curated recommendations, cache management</td>
  </tr>
</table>
</div>

---

<div align="center">
  <h2>Quick Start</h2>
</div>

<div align="center">
<table>
  <tr>
    <th>Step</th>
    <th>Command</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><strong>1. Clone</strong></td>
    <td><code>git clone &lt;repository-url&gt;</code></td>
    <td>Clone the repository</td>
  </tr>
  <tr>
    <td><strong>2. Navigate</strong></td>
    <td><code>cd pokemon-go-mcp</code></td>
    <td>Enter project directory</td>
  </tr>
  <tr>
    <td><strong>3. Install (uv)</strong></td>
    <td><code>uv sync</code></td>
    <td>Install with uv package manager (recommended)</td>
  </tr>
  <tr>
    <td><strong>3. Install (pip)</strong></td>
    <td><code>pip install -e .</code></td>
    <td>Install with pip</td>
  </tr>
  <tr>
    <td><strong>4. Run</strong></td>
    <td><code>uv run python server.py</code></td>
    <td>Start the MCP server</td>
  </tr>
</table>
</div>

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended) or `pip`

---

<div align="center">
  <h2>Integration Options</h2>
</div>

<div align="center">
<table>
  <tr>
    <th>Platform</th>
    <th>Configuration</th>
    <th>Notes</th>
  </tr>
  <tr>
    <td><strong>Claude Desktop</strong></td>
    <td>Add to <code>claude_desktop_config.json</code></td>
    <td>Requires absolute path to server.py</td>
  </tr>
  <tr>
    <td><strong>Claude Code</strong></td>
    <td>Use <code>claude mcp add</code> command</td>
    <td>Or create <code>.mcp.json</code> manually</td>
  </tr>
  <tr>
    <td><strong>VS Code</strong></td>
    <td>Create <code>.vscode/mcp.json</code></td>
    <td>Supports stdio and HTTP transports</td>
  </tr>
  <tr>
    <td><strong>n8n Workflows</strong></td>
    <td>Install <code>n8n-nodes-mcp</code></td>
    <td>HTTP transport recommended</td>
  </tr>
  <tr>
    <td><strong>Docker</strong></td>
    <td>Use <code>docker build</code> and <code>docker run</code></td>
    <td>Supports HTTP/SSE transports</td>
  </tr>
</table>
</div>

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "pokemon-go": {
      "command": "uv",
      "args": ["run", "python", "/path/to/pokemon-go-mcp/pogo_mcp/server.py"]
    }
  }
}
```

### Claude Code Configuration

```bash
# Quick add with claude mcp command
claude mcp add pokemon-go uv run python /path/to/pokemon-go-mcp/pogo_mcp/server.py

# Or manually create .mcp.json in your project directory
echo '{"servers": {"pokemon-go": {"command": "uv", "args": ["run", "python", "/path/to/pokemon-go-mcp/pogo_mcp/server.py"]}}}' > .mcp.json
```

### VS Code Configuration

Create `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "pokemon-go-stdio": {
      "command": "uv",
      "args": ["run", "python", "/path/to/pokemon-go-mcp/pogo_mcp/server.py"]
    },
    "pokemon-go-http": {
      "type": "http",
      "url": "http://localhost:8000",
      "description": "Pokemon Go MCP Server via HTTP"
    }
  }
}
```

### n8n Workflows

1. **Install n8n MCP Node:**
   ```bash
   npm install n8n-nodes-mcp
   # Set environment: N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
   ```

2. **Configure MCP Client Node:**
   - Connection Type: HTTP Streamable (Recommended)
   - URL: `http://localhost:8000` (when running with `MCP_TRANSPORT=http`)
   - Headers: Optional authentication headers if needed

3. **Docker Deployment for n8n:**
   ```bash
   # Build and run the Pokemon Go MCP server
   docker build -t pokemon-go-mcp .
   docker run -d -p 8000:8000 -e MCP_TRANSPORT=http pokemon-go-mcp
   ```

### Transport Modes

<div align="center">
<table>
  <tr>
    <th>Transport</th>
    <th>Command</th>
    <th>Use Case</th>
  </tr>
  <tr>
    <td><strong>HTTP</strong></td>
    <td><code>MCP_TRANSPORT=http MCP_PORT=8000 python pogo_mcp/server.py</code></td>
    <td>Web integrations, automation tools</td>
  </tr>
  <tr>
    <td><strong>SSE</strong></td>
    <td><code>MCP_TRANSPORT=sse MCP_PORT=8000 python pogo_mcp/server.py</code></td>
    <td>Legacy systems</td>
  </tr>
  <tr>
    <td><strong>stdio</strong></td>
    <td><code>python pogo_mcp/server.py</code></td>
    <td>Default, Claude Desktop</td>
  </tr>
</table>
</div>

---

<div align="center">
  <h2>Showcase</h2>
</div>

<div align="center">

![Pokemon Go MCP Server Showcase 1](https://github.com/user-attachments/assets/6f6c359d-52a9-4412-973a-0fc0542d0cdb)

![Pokemon Go MCP Server Showcase 2](https://github.com/user-attachments/assets/a465c6f6-beeb-421d-bbd3-9d2acad450b6)

![Pokemon Go MCP Server Showcase 3](https://github.com/user-attachments/assets/8de4533d-f9b2-4463-ba25-61b75ce85785)

</div>

---

<div align="center">
  <h2>Available Tools</h2>
</div>

<div align="center">
<table>
  <tr>
    <th>Tool Name</th>
    <th>Category</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>get_current_events</code></td>
    <td>Events</td>
    <td>List all active and upcoming events</td>
  </tr>
  <tr>
    <td><code>get_event_details</code></td>
    <td>Events</td>
    <td>Detailed information about a specific event</td>
  </tr>
  <tr>
    <td><code>get_community_day_info</code></td>
    <td>Events</td>
    <td>Community Day specifics and featured Pokemon</td>
  </tr>
  <tr>
    <td><code>get_event_spawns</code></td>
    <td>Events</td>
    <td>Pokemon spawning more frequently during events</td>
  </tr>
  <tr>
    <td><code>get_event_bonuses</code></td>
    <td>Events</td>
    <td>Active event bonuses (XP, Stardust, etc.)</td>
  </tr>
  <tr>
    <td><code>search_events</code></td>
    <td>Events</td>
    <td>Search events by name or type</td>
  </tr>
  <tr>
    <td><code>get_current_raids</code></td>
    <td>Raids</td>
    <td>All current raid bosses by tier</td>
  </tr>
  <tr>
    <td><code>get_raid_by_tier</code></td>
    <td>Raids</td>
    <td>Filter raids by tier (1, 3, 5, Mega)</td>
  </tr>
  <tr>
    <td><code>get_shiny_raids</code></td>
    <td>Raids</td>
    <td>Only shiny-eligible raid bosses</td>
  </tr>
  <tr>
    <td><code>search_raid_boss</code></td>
    <td>Raids</td>
    <td>Find specific Pokemon in raids</td>
  </tr>
  <tr>
    <td><code>get_raids_by_type</code></td>
    <td>Raids</td>
    <td>Filter raids by Pokemon type</td>
  </tr>
  <tr>
    <td><code>get_weather_boosted_raids</code></td>
    <td>Raids</td>
    <td>Raids boosted by weather conditions</td>
  </tr>
  <tr>
    <td><code>get_raid_recommendations</code></td>
    <td>Raids</td>
    <td>Smart raid recommendations based on priorities</td>
  </tr>
  <tr>
    <td><code>get_current_research</code></td>
    <td>Research</td>
    <td>All field research tasks and rewards</td>
  </tr>
  <tr>
    <td><code>search_research_by_reward</code></td>
    <td>Research</td>
    <td>Find tasks by Pokemon reward</td>
  </tr>
  <tr>
    <td><code>get_research_by_task_type</code></td>
    <td>Research</td>
    <td>Filter by task type (catch, battle, spin, etc.)</td>
  </tr>
  <tr>
    <td><code>get_shiny_research_rewards</code></td>
    <td>Research</td>
    <td>Tasks with shiny reward potential</td>
  </tr>
  <tr>
    <td><code>get_easy_research_tasks</code></td>
    <td>Research</td>
    <td>Quick-completion tasks for efficient farming</td>
  </tr>
  <tr>
    <td><code>search_research_tasks</code></td>
    <td>Research</td>
    <td>Search tasks by description</td>
  </tr>
  <tr>
    <td><code>get_research_recommendations</code></td>
    <td>Research</td>
    <td>Personalized research task recommendations</td>
  </tr>
  <tr>
    <td><code>get_egg_hatches</code></td>
    <td>Eggs</td>
    <td>All Pokemon currently hatching from eggs</td>
  </tr>
  <tr>
    <td><code>get_egg_hatches_by_distance</code></td>
    <td>Eggs</td>
    <td>Filter by egg distance (2km, 5km, 10km, etc.)</td>
  </tr>
  <tr>
    <td><code>get_shiny_egg_hatches</code></td>
    <td>Eggs</td>
    <td>Shiny-eligible egg Pokemon</td>
  </tr>
  <tr>
    <td><code>search_egg_pokemon</code></td>
    <td>Eggs</td>
    <td>Find specific Pokemon in egg pools</td>
  </tr>
  <tr>
    <td><code>get_regional_egg_pokemon</code></td>
    <td>Eggs</td>
    <td>Region-exclusive Pokemon from eggs</td>
  </tr>
  <tr>
    <td><code>get_gift_exchange_pokemon</code></td>
    <td>Eggs</td>
    <td>7km gift egg Pokemon from friends</td>
  </tr>
  <tr>
    <td><code>get_route_gift_pokemon</code></td>
    <td>Eggs</td>
    <td>7km route gift egg Pokemon</td>
  </tr>
  <tr>
    <td><code>get_adventure_sync_rewards</code></td>
    <td>Eggs</td>
    <td>Adventure Sync weekly walking rewards</td>
  </tr>
  <tr>
    <td><code>get_egg_recommendations</code></td>
    <td>Eggs</td>
    <td>Smart incubation strategy recommendations</td>
  </tr>
  <tr>
    <td><code>get_team_rocket_lineups</code></td>
    <td>Team Rocket</td>
    <td>All current Team Rocket trainer lineups</td>
  </tr>
  <tr>
    <td><code>search_rocket_by_pokemon</code></td>
    <td>Team Rocket</td>
    <td>Find trainers using specific Pokemon</td>
  </tr>
  <tr>
    <td><code>get_shiny_shadow_pokemon</code></td>
    <td>Team Rocket</td>
    <td>All Shadow Pokemon that can be shiny</td>
  </tr>
  <tr>
    <td><code>get_rocket_encounters</code></td>
    <td>Team Rocket</td>
    <td>Pokemon available as encounter rewards</td>
  </tr>
  <tr>
    <td><code>get_rocket_trainers_by_type</code></td>
    <td>Team Rocket</td>
    <td>Filter trainers by Pokemon type specialty</td>
  </tr>
  <tr>
    <td><code>calculate_pokemon_weakness</code></td>
    <td>Team Rocket</td>
    <td>Type effectiveness against Shadow Pokemon</td>
  </tr>
  <tr>
    <td><code>get_rocket_trainer_details</code></td>
    <td>Team Rocket</td>
    <td>Detailed information about a specific trainer</td>
  </tr>
  <tr>
    <td><code>get_all_shiny_pokemon</code></td>
    <td>Cross-Platform</td>
    <td>All shiny Pokemon across all sources</td>
  </tr>
  <tr>
    <td><code>search_pokemon_everywhere</code></td>
    <td>Cross-Platform</td>
    <td>Universal Pokemon search across all data</td>
  </tr>
  <tr>
    <td><code>get_daily_priorities</code></td>
    <td>Cross-Platform</td>
    <td>Curated daily activity recommendations</td>
  </tr>
  <tr>
    <td><code>get_server_status</code></td>
    <td>Cross-Platform</td>
    <td>Server status and data freshness information</td>
  </tr>
  <tr>
    <td><code>clear_cache</code></td>
    <td>Cross-Platform</td>
    <td>Force fresh data retrieval from sources</td>
  </tr>
</table>
</div>

---

<div align="center">
  <h2>Example Usage</h2>
</div>

### Get Today's Priorities

Use the `get_daily_priorities` tool to get curated recommendations for:
- Active events to participate in
- Priority raids for shiny hunting
- Easy research tasks with valuable rewards
- Optimal egg hatching strategy

### Find a Specific Pokemon

Use `search_pokemon_everywhere` with "Dratini" to find:
- If it's featured in any current events
- Whether it's available as a raid boss
- Which research tasks reward it
- If it can be hatched from eggs
- Shiny availability across all sources

### Plan Your Shiny Hunt

Use `get_all_shiny_pokemon` to see every shiny currently available, then:
- `get_shiny_raids` for raid targets
- `get_shiny_research_rewards` for research tasks
- `get_shiny_egg_hatches` for egg planning
- `get_route_gift_pokemon` for special route gift opportunities
- `get_shiny_shadow_pokemon` for Shadow Pokemon

---

<div align="center">
  <h2>Architecture</h2>
</div>

```
pokemon-go-mcp/
├── pogo_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # Main MCP server with cross-cutting tools
│   ├── api_client.py        # Local data client with caching
│   ├── types.py             # Type definitions and data classes
│   ├── utils.py             # Utility functions and formatters
│   ├── events.py            # Event-related tools
│   ├── raids.py             # Raid-related tools
│   ├── research.py          # Research-related tools
│   ├── eggs.py              # Egg-related tools
│   └── rocket_lineups.py    # Team Rocket-related tools
├── data/                    # Local JSON data files (git-ignored)
├── tests/                   # Test files
├── server.py                # Main entry point
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

<div align="center">
<table>
  <tr>
    <th>Component</th>
    <th>Technology</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td><strong>FastMCP</strong></td>
    <td>MCP Framework</td>
    <td>Modern MCP server framework for easy tool registration</td>
  </tr>
  <tr>
    <td><strong>Custom Scraper</strong></td>
    <td>Python</td>
    <td>Built-in scraper that collects and saves data to local JSON files</td>
  </tr>
  <tr>
    <td><strong>Local Data Client</strong></td>
    <td>Python</td>
    <td>Reads data from local JSON files with smart caching</td>
  </tr>
  <tr>
    <td><strong>Type Safety</strong></td>
    <td>Python Type Hints</td>
    <td>Full type hints and data validation throughout codebase</td>
  </tr>
  <tr>
    <td><strong>Modular Design</strong></td>
    <td>Python Modules</td>
    <td>Separate modules for each data domain (events, raids, etc.)</td>
  </tr>
</table>
</div>

---

<div align="center">
  <h2>Development</h2>
</div>

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd pokemon-go-mcp

# Install with development dependencies
uv sync --all-extras --dev

# Code formatting
ruff format .

# Linting
ruff check .

# Type checking
pyright
```

### Testing

<div align="center">
<table>
  <tr>
    <th>Command</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>python run_tests.py</code></td>
    <td>Run all tests</td>
  </tr>
  <tr>
    <td><code>pytest --cov=pogo_mcp</code></td>
    <td>Run tests with coverage report</td>
  </tr>
  <tr>
    <td><code>pytest tests/test_events_parsing.py</code></td>
    <td>Test specific module</td>
  </tr>
</table>
</div>

---

<div align="center">
  <h2>License</h2>
  <p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
</div>
