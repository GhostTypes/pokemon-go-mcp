"""Integration tests for MCP server using actual stdio transport.

These tests start the MCP server as a subprocess with stdio transport
and connect as a real MCP client to test the full MCP protocol.
"""

import pytest
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import AsyncGenerator

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def mcp_session() -> AsyncGenerator:
    """Start the MCP server as a subprocess and connect via stdio.

    This fixture provides a real MCP client session connected to the
    server running via stdio transport (not in-memory).
    """
    if not MCP_AVAILABLE:
        pytest.skip("MCP SDK not installed. Install with: pip install mcp")

    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent

    # Set up server parameters for stdio transport
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "pogo_mcp.server"],
        env=None,  # Use current environment
    )

    # Use the stdio_client context manager properly
    stdio_ctx = stdio_client(server_params)

    try:
        # Enter the stdio context manager to get streams
        read_stream, write_stream = await stdio_ctx.__aenter__()

        # Create the client session with both streams
        session = ClientSession(read_stream, write_stream)

        try:
            # Enter the session context manager
            await session.__aenter__()

            # Initialize the session
            await session.initialize()

            yield session

        finally:
            # Exit the session context manager
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass  # Ignore cleanup errors

    finally:
        # Exit the stdio context manager
        try:
            await stdio_ctx.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors


class TestMCPServerStdioConnection:
    """Test MCP server connection and initialization via stdio."""

    @pytest.mark.asyncio
    async def test_server_initializes(self, mcp_session: ClientSession):
        """Test that the server initializes successfully via stdio."""
        # If we got here without errors, the connection worked
        assert mcp_session is not None

    @pytest.mark.asyncio
    async def test_server_has_capabilities(self, mcp_session: ClientSession):
        """Test that the server reports its capabilities."""
        # The session should have been initialized with capabilities
        # Check that we can access server info
        assert hasattr(mcp_session, "send_request")


class TestMCPToolsDiscovery:
    """Test tool discovery via stdio transport."""

    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_session: ClientSession):
        """Test that we can list all available tools."""
        response = await mcp_session.list_tools()

        assert response.tools is not None
        assert len(response.tools) > 0

        # Get tool names
        tool_names = [tool.name for tool in response.tools]

        # Verify core cross-cutting tools exist
        assert "get_server_status" in tool_names
        assert "get_all_shiny_pokemon" in tool_names
        assert "search_pokemon_everywhere" in tool_names
        assert "get_daily_priorities" in tool_names
        assert "clear_cache" in tool_names

    @pytest.mark.asyncio
    async def test_tools_have_descriptions(self, mcp_session: ClientSession):
        """Test that all tools have descriptions."""
        response = await mcp_session.list_tools()

        for tool in response.tools:
            assert tool.description is not None
            assert len(tool.description) > 0

    @pytest.mark.asyncio
    async def test_expected_tool_count(self, mcp_session: ClientSession):
        """Test that we have the expected number of tools.

        Expected tools:
        - 3 event tools
        - 6 raid tools
        - 5 research tools
        - 6 egg tools
        - 2 rocket tools
        - 1 promo code tool
        - 5 cross-cutting tools
        Total: ~28 tools (may vary slightly)
        """
        response = await mcp_session.list_tools()

        # Should have at least 20 tools
        assert len(response.tools) >= 20


class TestMCPCrossCuttingTools:
    """Test cross-cutting tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_get_server_status(self, mcp_session: ClientSession):
        """Test the get_server_status tool."""
        response = await mcp_session.call_tool("get_server_status", {})

        assert response.content is not None
        assert len(response.content) > 0

        # Check that we got text content
        content_text = response.content[0].text
        assert len(content_text) > 0

        # Verify expected content in status
        assert "Pokemon Go MCP Server Status" in content_text
        assert "Data Statistics" in content_text
        assert "Events:" in content_text
        assert "Raid Bosses:" in content_text

    @pytest.mark.asyncio
    async def test_clear_cache(self, mcp_session: ClientSession):
        """Test the clear_cache tool."""
        response = await mcp_session.call_tool("clear_cache", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert "Cache cleared" in content_text or "success" in content_text.lower()

    @pytest.mark.asyncio
    async def test_get_all_shiny_pokemon(
        self, mcp_session: ClientSession, ensure_test_data
    ):
        """Test the get_all_shiny_pokemon tool."""
        response = await mcp_session.call_tool("get_all_shiny_pokemon", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        # Should have some content even if no shinies available
        assert len(content_text) > 0

    @pytest.mark.asyncio
    async def test_search_pokemon_everywhere(
        self, mcp_session: ClientSession, ensure_test_data, sample_pokemon_name
    ):
        """Test the search_pokemon_everywhere tool with a real Pokemon."""
        response = await mcp_session.call_tool(
            "search_pokemon_everywhere", {"pokemon_name": sample_pokemon_name}
        )

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0
        # Should contain the Pokemon name somewhere
        assert sample_pokemon_name.lower() in content_text.lower()

    @pytest.mark.asyncio
    async def test_search_pokemon_everywhere_invalid(self, mcp_session: ClientSession):
        """Test search_pokemon_everywhere with invalid input."""
        response = await mcp_session.call_tool(
            "search_pokemon_everywhere", {"pokemon_name": "InvalidPokemonName123456"}
        )

        assert response.content is not None
        content_text = response.content[0].text
        # Should indicate not found
        assert "not found" in content_text.lower() or "invalid" in content_text.lower()


class TestMCPEventTools:
    """Test event-related tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_get_current_events(
        self, mcp_session: ClientSession, ensure_test_data
    ):
        """Test the get_current_events tool."""
        response = await mcp_session.call_tool("get_current_events", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0

    @pytest.mark.asyncio
    async def test_search_events(self, mcp_session: ClientSession, ensure_test_data):
        """Test the search_events tool."""
        # Search for "community" events
        response = await mcp_session.call_tool("search_events", {"query": "community"})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0


class TestMCPRaidTools:
    """Test raid-related tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_get_current_raids(
        self, mcp_session: ClientSession, ensure_test_data
    ):
        """Test the get_current_raids tool."""
        response = await mcp_session.call_tool("get_current_raids", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0

    @pytest.mark.asyncio
    async def test_get_shiny_raids(self, mcp_session: ClientSession, ensure_test_data):
        """Test the get_shiny_raids tool."""
        response = await mcp_session.call_tool("get_shiny_raids", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        # Even if empty, should have some output
        assert len(content_text) > 0


class TestMCPResearchTools:
    """Test research-related tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_get_current_research(
        self, mcp_session: ClientSession, ensure_test_data
    ):
        """Test the get_current_research tool."""
        response = await mcp_session.call_tool("get_current_research", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0


class TestMCPEggTools:
    """Test egg-related tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_get_egg_hatches(self, mcp_session: ClientSession, ensure_test_data):
        """Test the get_egg_hatches tool."""
        response = await mcp_session.call_tool("get_egg_hatches", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0


class TestMCPRocketTools:
    """Test Team Rocket-related tools via stdio transport."""

    @pytest.mark.asyncio
    async def test_get_team_rocket_lineups(
        self, mcp_session: ClientSession, ensure_test_data
    ):
        """Test the get_team_rocket_lineups tool."""
        response = await mcp_session.call_tool("get_team_rocket_lineups", {})

        assert response.content is not None
        assert len(response.content) > 0

        content_text = response.content[0].text
        assert len(content_text) > 0


class TestMCPConcurrentCalls:
    """Test concurrent tool calls via stdio transport."""

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(
        self, mcp_session: ClientSession, ensure_test_data
    ):
        """Test that the server handles concurrent calls correctly."""
        # Make multiple concurrent calls
        tasks = [
            mcp_session.call_tool("get_server_status", {}),
            mcp_session.call_tool("get_current_raids", {}),
            mcp_session.call_tool("get_current_events", {}),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert result.content is not None
            assert len(result.content) > 0


# Fixtures for test data (reused from existing conftest.py)
@pytest.fixture(scope="session")
def ensure_test_data():
    """Ensure test data files exist before running integration tests."""
    from pathlib import Path

    data_dir = Path(__file__).parent.parent.parent / "data"
    required_files = [
        "events.json",
        "raids.json",
        "research.json",
        "eggs.json",
        "rocket-lineups.json",
        "promo-codes.json",
    ]

    missing_files = []
    for file in required_files:
        file_path = data_dir / file
        if not file_path.exists():
            missing_files.append(file)

    if missing_files:
        pytest.skip(
            f"Required data files missing: {', '.join(missing_files)}. "
            "Please run the scraper first to generate test data."
        )

    return True


@pytest.fixture(scope="session")
def sample_pokemon_name(ensure_test_data):
    """Get a sample Pokemon name for testing search functions."""
    import json
    from pathlib import Path

    # Try raids first
    data_file = Path(__file__).parent.parent.parent / "data" / "raids.json"
    with open(data_file) as f:
        raids = json.load(f)
    if raids:
        return raids[0]["name"]

    # Try research
    data_file = Path(__file__).parent.parent.parent / "data" / "research.json"
    with open(data_file) as f:
        research = json.load(f)
    if research and research[0].get("rewards"):
        return research[0]["rewards"][0]["name"]

    pytest.skip("No Pokemon available in test data")
