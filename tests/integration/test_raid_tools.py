"""Integration tests for Raid-related MCP tools."""

import pytest


class TestRaidTools:
    """Integration tests for all raid-related tools."""

    @pytest.mark.asyncio
    async def test_get_current_raids(self, ensure_test_data, mcp_server):
        """Test get_current_raids tool."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_current_raids = captured_tools['get_current_raids']
        result = await get_current_raids()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Raid" in result or "No raid" in result

    @pytest.mark.asyncio
    async def test_get_raid_by_tier(self, ensure_test_data, sample_raid_tier, mcp_server):
        """Test get_raid_by_tier tool."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_raid_by_tier = captured_tools['get_raid_by_tier']
        result = await get_raid_by_tier(tier=sample_raid_tier)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_raid_by_tier_tier_5(self, ensure_test_data, mcp_server):
        """Test get_raid_by_tier with tier 5."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_raid_by_tier = captured_tools['get_raid_by_tier']
        result = await get_raid_by_tier(tier="5")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_shiny_raids(self, ensure_test_data, mcp_server):
        """Test get_shiny_raids tool."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_shiny_raids = captured_tools['get_shiny_raids']
        result = await get_shiny_raids()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Shiny" in result or "shiny" in result or "No" in result

    @pytest.mark.asyncio
    async def test_search_raid_boss(self, ensure_test_data, sample_pokemon_name, mcp_server):
        """Test search_raid_boss tool."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        search_raid_boss = captured_tools['search_raid_boss']
        result = await search_raid_boss(pokemon_name=sample_pokemon_name)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_raid_boss_not_found(self, ensure_test_data, mcp_server):
        """Test search_raid_boss with Pokemon not in raids."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        search_raid_boss = captured_tools['search_raid_boss']
        result = await search_raid_boss(pokemon_name="magikarp")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_raids_by_type(self, ensure_test_data, mcp_server):
        """Test get_raids_by_type tool."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_raids_by_type = captured_tools['get_raids_by_type']
        result = await get_raids_by_type(pokemon_type="water")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_weather_boosted_raids(self, ensure_test_data, mcp_server):
        """Test get_weather_boosted_raids tool."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_weather_boosted_raids = captured_tools['get_weather_boosted_raids']
        result = await get_weather_boosted_raids(weather="sunny")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_raid_recommendations(self, ensure_test_data, mcp_server):
        """Test get_raid_recommendations tool without filters."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_raid_recommendations = captured_tools['get_raid_recommendations']
        result = await get_raid_recommendations()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Raid" in result or "raid" in result

    @pytest.mark.asyncio
    async def test_get_raid_recommendations_shiny_only(self, ensure_test_data, mcp_server):
        """Test get_raid_recommendations with shiny_only filter."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_raid_recommendations = captured_tools['get_raid_recommendations']
        result = await get_raid_recommendations(shiny_only=True)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_raid_recommendations_with_tier(self, ensure_test_data, mcp_server):
        """Test get_raid_recommendations with tier filter."""
        from pogo_mcp.raids import register_raid_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_raid_tools(mock_mcp)

        get_raid_recommendations = captured_tools['get_raid_recommendations']
        result = await get_raid_recommendations(tier="5")

        assert isinstance(result, str)
        assert len(result) > 0
