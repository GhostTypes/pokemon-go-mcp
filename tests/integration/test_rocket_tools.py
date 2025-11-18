"""Integration tests for Team Rocket-related MCP tools."""

import pytest


class TestRocketTools:
    """Integration tests for all Team Rocket-related tools."""

    @pytest.mark.asyncio
    async def test_get_team_rocket_lineups(self, ensure_test_data, mcp_server):
        """Test get_team_rocket_lineups tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_team_rocket_lineups = captured_tools['get_team_rocket_lineups']
        result = await get_team_rocket_lineups()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Rocket" in result or "rocket" in result or "No" in result

    @pytest.mark.asyncio
    async def test_search_rocket_by_pokemon(self, ensure_test_data, sample_pokemon_name, mcp_server):
        """Test search_rocket_by_pokemon tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        search_rocket_by_pokemon = captured_tools['search_rocket_by_pokemon']
        result = await search_rocket_by_pokemon(pokemon_name=sample_pokemon_name)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_rocket_by_pokemon_not_found(self, ensure_test_data, mcp_server):
        """Test search_rocket_by_pokemon with Pokemon not in lineups."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        search_rocket_by_pokemon = captured_tools['search_rocket_by_pokemon']
        result = await search_rocket_by_pokemon(pokemon_name="xyznotfound")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_shiny_shadow_pokemon(self, ensure_test_data, mcp_server):
        """Test get_shiny_shadow_pokemon tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_shiny_shadow_pokemon = captured_tools['get_shiny_shadow_pokemon']
        result = await get_shiny_shadow_pokemon()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "shiny" in result.lower() or "Shiny" in result or "No" in result

    @pytest.mark.asyncio
    async def test_get_rocket_encounters(self, ensure_test_data, mcp_server):
        """Test get_rocket_encounters tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_rocket_encounters = captured_tools['get_rocket_encounters']
        result = await get_rocket_encounters()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Encounter" in result or "encounter" in result or "No" in result

    @pytest.mark.asyncio
    async def test_get_rocket_trainers_by_type(self, ensure_test_data, mcp_server):
        """Test get_rocket_trainers_by_type tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_rocket_trainers_by_type = captured_tools['get_rocket_trainers_by_type']
        result = await get_rocket_trainers_by_type(trainer_type="water")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_rocket_trainers_by_type_fire(self, ensure_test_data, mcp_server):
        """Test get_rocket_trainers_by_type with fire type."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_rocket_trainers_by_type = captured_tools['get_rocket_trainers_by_type']
        result = await get_rocket_trainers_by_type(trainer_type="fire")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_calculate_pokemon_weakness(self, ensure_test_data, sample_pokemon_name, mcp_server):
        """Test calculate_pokemon_weakness tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        calculate_pokemon_weakness = captured_tools['calculate_pokemon_weakness']
        result = await calculate_pokemon_weakness(
            pokemon_name=sample_pokemon_name,
            attacking_type="fire"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_calculate_pokemon_weakness_water_vs_fire(self, ensure_test_data, mcp_server):
        """Test calculate_pokemon_weakness with water vs fire."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        # Get a pokemon name from the data
        from pogo_mcp.api_client import api_client
        trainers = await api_client.get_rocket_lineups()
        if trainers and trainers[0].lineups and trainers[0].lineups[0].pokemon:
            pokemon_name = trainers[0].lineups[0].pokemon[0].name

            calculate_pokemon_weakness = captured_tools['calculate_pokemon_weakness']
            result = await calculate_pokemon_weakness(
                pokemon_name=pokemon_name,
                attacking_type="water"
            )

            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_rocket_trainer_details(self, ensure_test_data, sample_trainer_name, mcp_server):
        """Test get_rocket_trainer_details tool."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_rocket_trainer_details = captured_tools['get_rocket_trainer_details']
        result = await get_rocket_trainer_details(trainer_name=sample_trainer_name)

        assert isinstance(result, str)
        assert len(result) > 0
        assert sample_trainer_name in result or "Trainer Details" in result

    @pytest.mark.asyncio
    async def test_get_rocket_trainer_details_not_found(self, ensure_test_data, mcp_server):
        """Test get_rocket_trainer_details with invalid trainer name."""
        from pogo_mcp.rocket_lineups import register_rocket_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_rocket_tools(mock_mcp)

        get_rocket_trainer_details = captured_tools['get_rocket_trainer_details']
        result = await get_rocket_trainer_details(trainer_name="InvalidTrainerXYZ123")

        assert isinstance(result, str)
        assert "not found" in result.lower() or "No" in result
