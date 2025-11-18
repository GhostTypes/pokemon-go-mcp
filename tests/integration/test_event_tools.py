"""Integration tests for Event-related MCP tools."""

import pytest
from pogo_mcp.api_client import api_client


class TestEventTools:
    """Integration tests for all event-related tools."""

    @pytest.mark.asyncio
    async def test_get_current_events(self, ensure_test_data, mcp_server):
        """Test get_current_events tool."""
        # Import the tool function
        from pogo_mcp.events import register_event_tools

        # Create a mock mcp instance to capture the registered tool
        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        # Get the tool function
        get_current_events = captured_tools['get_current_events']

        # Call the tool
        result = await get_current_events()

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain events header
        assert "Pokemon Go Events" in result or "No active" in result

    @pytest.mark.asyncio
    async def test_get_event_details(self, ensure_test_data, sample_event_id, mcp_server):
        """Test get_event_details tool."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        get_event_details = captured_tools['get_event_details']

        # Call with a valid event ID
        result = await get_event_details(sample_event_id)

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_event_details_invalid_id(self, ensure_test_data, mcp_server):
        """Test get_event_details with invalid event ID."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        get_event_details = captured_tools['get_event_details']

        # Call with invalid event ID
        result = await get_event_details("invalid_event_id_12345")

        # Should return not found message
        assert isinstance(result, str)
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_get_community_day_info(self, ensure_test_data, mcp_server):
        """Test get_community_day_info tool."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        get_community_day_info = captured_tools['get_community_day_info']

        # Call the tool
        result = await get_community_day_info()

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0
        # Should mention Community Day or indicate none found
        assert "Community Day" in result or "No active" in result

    @pytest.mark.asyncio
    async def test_get_event_spawns(self, ensure_test_data, mcp_server):
        """Test get_event_spawns tool."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        get_event_spawns = captured_tools['get_event_spawns']

        # Call the tool without filter
        result = await get_event_spawns()

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Event Spawns" in result or "No spawn" in result

    @pytest.mark.asyncio
    async def test_get_event_spawns_with_filter(self, ensure_test_data, mcp_server):
        """Test get_event_spawns tool with event type filter."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        get_event_spawns = captured_tools['get_event_spawns']

        # Call the tool with a filter
        result = await get_event_spawns(event_type="community")

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_event_bonuses(self, ensure_test_data, mcp_server):
        """Test get_event_bonuses tool."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        get_event_bonuses = captured_tools['get_event_bonuses']

        # Call the tool
        result = await get_event_bonuses()

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Event Bonuses" in result or "No bonus" in result

    @pytest.mark.asyncio
    async def test_search_events(self, ensure_test_data, mcp_server):
        """Test search_events tool."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        search_events = captured_tools['search_events']

        # Call the tool with a common search term
        result = await search_events(query="event")

        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_events_no_results(self, ensure_test_data, mcp_server):
        """Test search_events tool with query that returns no results."""
        from pogo_mcp.events import register_event_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_event_tools(mock_mcp)

        search_events = captured_tools['search_events']

        # Call with unlikely search term
        result = await search_events(query="xyzabc123notfound")

        # Should indicate no results
        assert isinstance(result, str)
        assert "No events found" in result or "not found" in result.lower()
