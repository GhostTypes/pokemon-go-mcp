# Pokemon Go MCP Server

A comprehensive Model Context Protocol (MCP) server that provides real-time Pokemon Go data including events, raids, research tasks, egg hatches, and Team Rocket lineups.

## 🌟 Features

### 📅 Events
- **Current Events**: Get all active and upcoming Pokemon Go events
- **Event Details**: Detailed information about specific events including Community Days
- **Event Spawns**: See which Pokemon are spawning more frequently
- **Event Bonuses**: Track active XP, Stardust, and other bonuses
- **Community Day Info**: Specialized Community Day information with featured Pokemon and exclusive moves

### ⚔️ Raids
- **Current Raid Bosses**: Complete list of all raid bosses organized by tier
- **Shiny Raids**: Filter raids to show only shiny-eligible bosses
- **Raid Search**: Find specific Pokemon in raids
- **Type Filtering**: Get raids by Pokemon type (Fire, Water, etc.)
- **Weather Boosted**: Find raids boosted by current weather conditions
- **Raid Recommendations**: Smart recommendations based on your priorities

### 🔬 Research
- **Field Research Tasks**: Complete list of current research tasks and rewards
- **Reward Search**: Find tasks that reward specific Pokemon
- **Shiny Research**: Tasks that can reward shiny Pokemon
- **Easy Tasks**: Quick-completion tasks for efficient farming
- **Task Type Filtering**: Filter by catch, battle, spin, etc.
- **Smart Recommendations**: Personalized task recommendations

### 🥚 Egg Hatches
- **Egg Pool Data**: All Pokemon currently hatching from eggs
- **Distance Filtering**: Filter by 2km, 5km, 10km, etc.
- **Shiny Egg Hatches**: Pokemon that can hatch shiny
- **Regional Pokemon**: Region-exclusive Pokemon from eggs
- **Gift Exchange**: 7km egg Pokemon from friends
- **Adventure Sync**: Weekly walking reward Pokemon
- **Incubation Strategy**: Smart recommendations for egg prioritization

### 🚀 Team Rocket Lineups
- **Current Lineups**: All Team Rocket trainer lineups with Pokemon options
- **Shadow Pokemon**: Detailed information about Shadow Pokemon types and weaknesses
- **Encounter Rewards**: Find trainers that offer specific Pokemon as encounter rewards
- **Type Specialization**: Filter trainers by their Pokemon type specialty
- **Shiny Shadow Pokemon**: Find all Shadow Pokemon that can be shiny
- **Battle Effectiveness**: Calculate type effectiveness against specific Shadow Pokemon

### 🔍 Cross-Platform Tools
- **Universal Shiny Search**: Find all available shiny Pokemon across all sources  
- **Pokemon Finder**: Search for any Pokemon across events, raids, research, and eggs
- **Daily Priorities**: Curated daily recommendations based on active content
- **Server Status**: Data freshness and cache information

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd pogo-mcp-server
   ```

2. **Using uv (recommended):**
   ```bash
   uv sync
   ```

3. **Using pip:**
   ```bash
   pip install -e .
   ```

### Running the Server

1. **Start the server:**
   ```bash
   # Using uv
   uv run python server.py
   
   # Using pip
   python server.py
   
   # Direct module execution
   python -m pogo_mcp.server
   ```

2. **For development with auto-reload:**
   ```bash
   uv run mcp dev server.py
   ```

### Integration Options

#### Claude Desktop
Add to your Claude Desktop configuration:
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

#### Claude Code
Add the server using the built-in command:
```bash
# Quick add with claude mcp command
claude mcp add pokemon-go uv run python /path/to/pokemon-go-mcp/pogo_mcp/server.py

# Or manually create .mcp.json in your project directory
echo '{"servers": {"pokemon-go": {"command": "uv", "args": ["run", "python", "/path/to/pokemon-go-mcp/pogo_mcp/server.py"]}}}' > .mcp.json
```

#### VS Code
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

#### n8n Workflows
Install the MCP community node and configure:

1. **Install n8n MCP Node:**
   ```bash
   npm install n8n-nodes-mcp
   # Set environment: N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
   ```

2. **Configure MCP Client Node:**
   - **Connection Type:** HTTP Streamable (Recommended)
   - **URL:** `http://localhost:8000` (when running with `MCP_TRANSPORT=http`)
   - **Headers:** Optional authentication headers if needed

3. **Docker Deployment for n8n:**
   ```bash
   # Build and run the Pokemon Go MCP server
   docker build -t pokemon-go-mcp .
   docker run -d -p 8000:8000 -e MCP_TRANSPORT=http pokemon-go-mcp
   ```

#### HTTP/SSE Transport Modes
For automation tools and Docker deployments:
```bash
# HTTP transport (recommended for web integrations)
MCP_TRANSPORT=http MCP_PORT=8000 python pogo_mcp/server.py

# SSE transport (for legacy systems)
MCP_TRANSPORT=sse MCP_PORT=8000 python pogo_mcp/server.py

# Default stdio transport
python pogo_mcp/server.py
```
   
## Showcase
![image](https://github.com/user-attachments/assets/6f6c359d-52a9-4412-973a-0fc0542d0cdb)
![image](https://github.com/user-attachments/assets/a465c6f6-beeb-421d-bbd3-9d2acad450b6)
![image](https://github.com/user-attachments/assets/8de4533d-f9b2-4463-ba25-61b75ce85785)


## 🛠️ Available Tools

### Event Tools
- `get_current_events` - List all active and upcoming events
- `get_event_details` - Detailed information about a specific event  
- `get_community_day_info` - Community Day specifics
- `get_event_spawns` - Pokemon spawning more frequently
- `get_event_bonuses` - Active event bonuses
- `search_events` - Search events by name/type

### Raid Tools
- `get_current_raids` - All current raid bosses by tier
- `get_raid_by_tier` - Filter raids by tier (1, 3, 5, Mega)
- `get_shiny_raids` - Only shiny-eligible raid bosses
- `search_raid_boss` - Find specific Pokemon in raids
- `get_raids_by_type` - Filter by Pokemon type
- `get_weather_boosted_raids` - Raids boosted by weather
- `get_raid_recommendations` - Smart raid recommendations

### Research Tools  
- `get_current_research` - All field research tasks
- `search_research_by_reward` - Find tasks by Pokemon reward
- `get_research_by_task_type` - Filter by task type
- `get_shiny_research_rewards` - Tasks with shiny rewards
- `get_easy_research_tasks` - Quick-completion tasks
- `search_research_tasks` - Search tasks by description
- `get_research_recommendations` - Personalized recommendations

### Egg Tools
- `get_egg_hatches` - All Pokemon from eggs  
- `get_egg_hatches_by_distance` - Filter by egg distance
- `get_shiny_egg_hatches` - Shiny-eligible egg Pokemon
- `search_egg_pokemon` - Find specific Pokemon in eggs
- `get_regional_egg_pokemon` - Region-exclusive egg Pokemon
- `get_gift_exchange_pokemon` - 7km gift egg Pokemon
- `get_route_gift_pokemon` - 7km route gift egg Pokemon
- `get_adventure_sync_rewards` - Adventure Sync rewards
- `get_egg_recommendations` - Smart incubation strategy

### Team Rocket Tools
- `get_team_rocket_lineups` - All current Team Rocket trainer lineups
- `search_rocket_by_pokemon` - Find trainers using specific Pokemon
- `get_shiny_shadow_pokemon` - All Shadow Pokemon that can be shiny
- `get_rocket_encounters` - Pokemon available as encounter rewards
- `get_rocket_trainers_by_type` - Filter trainers by Pokemon type
- `calculate_pokemon_weakness` - Type effectiveness against Shadow Pokemon
- `get_rocket_trainer_details` - Detailed information about a trainer

### Cross-Platform Tools
- `get_all_shiny_pokemon` - All shiny Pokemon across sources
- `search_pokemon_everywhere` - Universal Pokemon search
- `get_daily_priorities` - Daily activity recommendations  
- `get_server_status` - Server and data status
- `clear_cache` - Force fresh data retrieval

## 📊 Example Usage

### Get Today's Priorities
```
Use the get_daily_priorities tool to get curated recommendations for:
- Active events to participate in
- Priority raids for shiny hunting  
- Easy research tasks with valuable rewards
- Optimal egg hatching strategy
```

### Find a Specific Pokemon
```
Use search_pokemon_everywhere with "Dratini" to find:
- If it's featured in any current events
- Whether it's available as a raid boss
- Which research tasks reward it
- If it can be hatched from eggs
- Shiny availability across all sources
```

### Plan Your Shiny Hunt
```
Use get_all_shiny_pokemon to see every shiny currently available, then:
- get_shiny_raids for raid targets
- get_shiny_research_rewards for research tasks  
- get_shiny_egg_hatches for egg planning
- get_route_gift_pokemon for special route gift opportunities
- get_shiny_shadow_pokemon for Shadow Pokemon
```

## 🏗️ Architecture

```
pogo-mcp-server/
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

### Key Components

- **FastMCP**: Modern MCP server framework for easy tool registration
- **Custom Scraper**: Built-in scraper that collects and saves data to local JSON files
- **Local Data Client**: Reads data from local JSON files with smart caching
- **Type Safety**: Full type hints and data validation
- **Modular Design**: Separate modules for each data domain
- **Comprehensive Utilities**: Rich formatting and search capabilities

## 🧪 Development

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd pogo-mcp-server

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
```bash
# Run all tests
python run_tests.py

# Run with coverage
pytest --cov=pogo_mcp

# Test specific module
pytest tests/test_events_parsing.py
```
## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
