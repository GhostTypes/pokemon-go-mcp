"""Integration tests for Cross-cutting MCP tools."""

import pytest


class TestCrossCuttingTools:
    """Integration tests for all cross-cutting tools that span multiple data sources."""

    @pytest.mark.asyncio
    async def test_get_all_shiny_pokemon(self, ensure_test_data, mcp_server):
        """Test get_all_shiny_pokemon tool."""
        from pogo_mcp.server import register_cross_cutting_tools

        captured_tools = {}

        class MockMCP:
            def __init__(self):
                self.name = "Test MCP"

            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        # Save the original mcp
        from pogo_mcp import server
        original_mcp = server.mcp

        # Replace with our mock
        server.mcp = MockMCP()

        try:
            register_cross_cutting_tools()

            get_all_shiny_pokemon = captured_tools['get_all_shiny_pokemon']
            result = await get_all_shiny_pokemon()

            assert isinstance(result, str)
            assert len(result) > 0
            assert "Shiny" in result or "shiny" in result or "No" in result
        finally:
            # Restore original mcp
            server.mcp = original_mcp

    @pytest.mark.asyncio
    async def test_search_pokemon_everywhere(self, ensure_test_data, sample_pokemon_name, mcp_server):
        """Test search_pokemon_everywhere tool."""
        from pogo_mcp.server import register_cross_cutting_tools

        captured_tools = {}

        class MockMCP:
            def __init__(self):
                self.name = "Test MCP"

            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        # Save the original mcp
        from pogo_mcp import server
        original_mcp = server.mcp

        # Replace with our mock
        server.mcp = MockMCP()

        try:
            register_cross_cutting_tools()

            search_pokemon_everywhere = captured_tools['search_pokemon_everywhere']
            result = await search_pokemon_everywhere(pokemon_name=sample_pokemon_name)

            assert isinstance(result, str)
            assert len(result) > 0
            assert "Search Results" in result or sample_pokemon_name in result
        finally:
            # Restore original mcp
            server.mcp = original_mcp

    @pytest.mark.asyncio
    async def test_search_pokemon_everywhere_not_found(self, ensure_test_data, mcp_server):
        """Test search_pokemon_everywhere with Pokemon not found."""
        from pogo_mcp.server import register_cross_cutting_tools

        captured_tools = {}

        class MockMCP:
            def __init__(self):
                self.name = "Test MCP"

            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        # Save the original mcp
        from pogo_mcp import server
        original_mcp = server.mcp

        # Replace with our mock
        server.mcp = MockMCP()

        try:
            register_cross_cutting_tools()

            search_pokemon_everywhere = captured_tools['search_pokemon_everywhere']
            result = await search_pokemon_everywhere(pokemon_name="xyznotfound123")

            assert isinstance(result, str)
            assert len(result) > 0
            assert "not found" in result.lower() or "could mean" in result.lower()
        finally:
            # Restore original mcp
            server.mcp = original_mcp

    @pytest.mark.asyncio
    async def test_get_daily_priorities(self, ensure_test_data, mcp_server):
        """Test get_daily_priorities tool."""
        from pogo_mcp.server import register_cross_cutting_tools

        captured_tools = {}

        class MockMCP:
            def __init__(self):
                self.name = "Test MCP"

            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        # Save the original mcp
        from pogo_mcp import server
        original_mcp = server.mcp

        # Replace with our mock
        server.mcp = MockMCP()

        try:
            register_cross_cutting_tools()

            get_daily_priorities = captured_tools['get_daily_priorities']
            result = await get_daily_priorities()

            assert isinstance(result, str)
            assert len(result) > 0
            assert "Daily" in result or "Priorities" in result or "priorities" in result
        finally:
            # Restore original mcp
            server.mcp = original_mcp

    @pytest.mark.asyncio
    async def test_get_server_status(self, ensure_test_data, mcp_server):
        """Test get_server_status tool."""
        from pogo_mcp.server import register_cross_cutting_tools

        captured_tools = {}

        class MockMCP:
            def __init__(self):
                self.name = "Test MCP"

            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        # Save the original mcp
        from pogo_mcp import server
        original_mcp = server.mcp

        # Replace with our mock
        server.mcp = MockMCP()

        try:
            register_cross_cutting_tools()

            get_server_status = captured_tools['get_server_status']
            result = await get_server_status()

            assert isinstance(result, str)
            assert len(result) > 0
            assert "Server Status" in result or "Status" in result
            assert "Data Statistics" in result or "statistics" in result.lower()
        finally:
            # Restore original mcp
            server.mcp = original_mcp

    @pytest.mark.asyncio
    async def test_clear_cache(self, ensure_test_data, mcp_server):
        """Test clear_cache tool."""
        from pogo_mcp.server import register_cross_cutting_tools
        from pogo_mcp.api_client import api_client

        captured_tools = {}

        class MockMCP:
            def __init__(self):
                self.name = "Test MCP"

            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        # Save the original mcp
        from pogo_mcp import server
        original_mcp = server.mcp

        # Replace with our mock
        server.mcp = MockMCP()

        try:
            register_cross_cutting_tools()

            # Populate cache first
            await api_client.get_events()
            assert len(api_client._cache) > 0

            clear_cache = captured_tools['clear_cache']
            result = await clear_cache()

            assert isinstance(result, str)
            assert len(result) > 0
            assert "cleared" in result.lower() or "Cache" in result

            # Verify cache is actually cleared
            assert len(api_client._cache) == 0
        finally:
            # Restore original mcp
            server.mcp = original_mcp
