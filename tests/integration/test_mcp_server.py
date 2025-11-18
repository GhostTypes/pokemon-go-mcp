"""Integration tests for MCP server initialization and basic functionality."""

import pytest
from pogo_mcp.server import mcp
from pogo_mcp import main


class TestMCPServerInitialization:
    """Test MCP server initialization and configuration."""

    def test_mcp_server_exists(self, mcp_server):
        """Test that MCP server instance is created."""
        assert mcp_server is not None
        assert hasattr(mcp_server, 'tool')

    def test_mcp_server_name(self, mcp_server):
        """Test that MCP server has correct name."""
        assert mcp_server.name == "Pokemon Go MCP Server"

    def test_mcp_server_has_tools(self, mcp_server):
        """Test that MCP server has tools registered."""
        # The server should have tools registered
        # We can check that the mcp object has the tool decorator
        assert hasattr(mcp_server, 'tool')
        # Check that it's callable
        assert callable(mcp_server.tool)

    def test_main_function_exists(self):
        """Test that main entry point exists."""
        assert callable(main)


class TestMCPServerDataAccess:
    """Test MCP server can access data through API client."""

    @pytest.mark.asyncio
    async def test_can_fetch_events(self, ensure_test_data, api_client_instance):
        """Test that server can fetch events data."""
        events = await api_client_instance.get_events()
        assert isinstance(events, list)
        # Should have at least some events or be empty (valid state)
        assert events is not None

    @pytest.mark.asyncio
    async def test_can_fetch_raids(self, ensure_test_data, api_client_instance):
        """Test that server can fetch raids data."""
        raids = await api_client_instance.get_raids()
        assert isinstance(raids, list)
        assert raids is not None

    @pytest.mark.asyncio
    async def test_can_fetch_research(self, ensure_test_data, api_client_instance):
        """Test that server can fetch research data."""
        research = await api_client_instance.get_research()
        assert isinstance(research, list)
        assert research is not None

    @pytest.mark.asyncio
    async def test_can_fetch_eggs(self, ensure_test_data, api_client_instance):
        """Test that server can fetch eggs data."""
        eggs = await api_client_instance.get_eggs()
        assert isinstance(eggs, list)
        assert eggs is not None

    @pytest.mark.asyncio
    async def test_can_fetch_rocket_lineups(self, ensure_test_data, api_client_instance):
        """Test that server can fetch Team Rocket lineups."""
        trainers = await api_client_instance.get_rocket_lineups()
        assert isinstance(trainers, list)
        assert trainers is not None

    @pytest.mark.asyncio
    async def test_can_fetch_promo_codes(self, ensure_test_data, api_client_instance):
        """Test that server can fetch promo codes."""
        promo_codes = await api_client_instance.get_promo_codes()
        assert isinstance(promo_codes, list)
        assert promo_codes is not None

    @pytest.mark.asyncio
    async def test_can_fetch_all_data(self, ensure_test_data, api_client_instance):
        """Test that server can fetch all data at once."""
        all_data = await api_client_instance.get_all_data()
        assert isinstance(all_data, dict)
        assert "events" in all_data
        assert "raids" in all_data
        assert "research" in all_data
        assert "eggs" in all_data
        assert "rocket_lineups" in all_data
        assert "promo_codes" in all_data


class TestMCPServerCaching:
    """Test MCP server caching functionality."""

    @pytest.mark.asyncio
    async def test_cache_clear(self, api_client_instance):
        """Test that cache can be cleared."""
        # Fetch some data to populate cache
        await api_client_instance.get_events()

        # Clear cache
        api_client_instance.clear_cache()

        # Verify cache is empty
        assert len(api_client_instance._cache) == 0
        assert len(api_client_instance._cache_timestamp) == 0

    @pytest.mark.asyncio
    async def test_cache_population(self, fresh_cache, api_client_instance):
        """Test that cache is populated after fetching data."""
        # Cache should be empty initially
        assert len(api_client_instance._cache) == 0

        # Fetch data
        await api_client_instance.get_events()

        # Cache should now have data
        assert "events" in api_client_instance._cache
        assert "events" in api_client_instance._cache_timestamp
