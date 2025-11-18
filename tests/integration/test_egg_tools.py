"""Integration tests for Egg-related MCP tools."""

import pytest


class TestEggTools:
    """Integration tests for all egg-related tools."""

    @pytest.mark.asyncio
    async def test_get_egg_hatches(self, ensure_test_data, mcp_server):
        """Test get_egg_hatches tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_hatches = captured_tools['get_egg_hatches']
        result = await get_egg_hatches()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Egg" in result or "egg" in result or "No" in result

    @pytest.mark.asyncio
    async def test_get_egg_hatches_by_distance_2km(self, ensure_test_data, mcp_server):
        """Test get_egg_hatches_by_distance with 2km eggs."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_hatches_by_distance = captured_tools['get_egg_hatches_by_distance']
        result = await get_egg_hatches_by_distance(distance="2")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_egg_hatches_by_distance_5km(self, ensure_test_data, mcp_server):
        """Test get_egg_hatches_by_distance with 5km eggs."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_hatches_by_distance = captured_tools['get_egg_hatches_by_distance']
        result = await get_egg_hatches_by_distance(distance="5 km")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_egg_hatches_by_distance_10km(self, ensure_test_data, mcp_server):
        """Test get_egg_hatches_by_distance with 10km eggs."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_hatches_by_distance = captured_tools['get_egg_hatches_by_distance']
        result = await get_egg_hatches_by_distance(distance="10km")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_shiny_egg_hatches(self, ensure_test_data, mcp_server):
        """Test get_shiny_egg_hatches tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_shiny_egg_hatches = captured_tools['get_shiny_egg_hatches']
        result = await get_shiny_egg_hatches()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "shiny" in result.lower() or "Shiny" in result or "No" in result

    @pytest.mark.asyncio
    async def test_search_egg_pokemon(self, ensure_test_data, sample_pokemon_name, mcp_server):
        """Test search_egg_pokemon tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        search_egg_pokemon = captured_tools['search_egg_pokemon']
        result = await search_egg_pokemon(pokemon_name=sample_pokemon_name)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_egg_pokemon_not_found(self, ensure_test_data, mcp_server):
        """Test search_egg_pokemon with Pokemon not in eggs."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        search_egg_pokemon = captured_tools['search_egg_pokemon']
        result = await search_egg_pokemon(pokemon_name="mewtwo")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_regional_egg_pokemon(self, ensure_test_data, mcp_server):
        """Test get_regional_egg_pokemon tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_regional_egg_pokemon = captured_tools['get_regional_egg_pokemon']
        result = await get_regional_egg_pokemon()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_gift_exchange_pokemon(self, ensure_test_data, mcp_server):
        """Test get_gift_exchange_pokemon tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_gift_exchange_pokemon = captured_tools['get_gift_exchange_pokemon']
        result = await get_gift_exchange_pokemon()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_route_gift_pokemon(self, ensure_test_data, mcp_server):
        """Test get_route_gift_pokemon tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_route_gift_pokemon = captured_tools['get_route_gift_pokemon']
        result = await get_route_gift_pokemon()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_adventure_sync_rewards(self, ensure_test_data, mcp_server):
        """Test get_adventure_sync_rewards tool."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_adventure_sync_rewards = captured_tools['get_adventure_sync_rewards']
        result = await get_adventure_sync_rewards()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_egg_recommendations_shiny(self, ensure_test_data, mcp_server):
        """Test get_egg_recommendations with shiny priority."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_recommendations = captured_tools['get_egg_recommendations']
        result = await get_egg_recommendations(priority="shiny")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_egg_recommendations_rare(self, ensure_test_data, mcp_server):
        """Test get_egg_recommendations with rare priority."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_recommendations = captured_tools['get_egg_recommendations']
        result = await get_egg_recommendations(priority="rare")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_egg_recommendations_quick(self, ensure_test_data, mcp_server):
        """Test get_egg_recommendations with quick priority."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_recommendations = captured_tools['get_egg_recommendations']
        result = await get_egg_recommendations(priority="quick")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_egg_recommendations_default(self, ensure_test_data, mcp_server):
        """Test get_egg_recommendations with default priority."""
        from pogo_mcp.eggs import register_egg_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_egg_tools(mock_mcp)

        get_egg_recommendations = captured_tools['get_egg_recommendations']
        result = await get_egg_recommendations()

        assert isinstance(result, str)
        assert len(result) > 0
