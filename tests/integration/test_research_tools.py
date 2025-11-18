"""Integration tests for Research-related MCP tools."""

import pytest


class TestResearchTools:
    """Integration tests for all research-related tools."""

    @pytest.mark.asyncio
    async def test_get_current_research(self, ensure_test_data, mcp_server):
        """Test get_current_research tool."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_current_research = captured_tools['get_current_research']
        result = await get_current_research()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Research" in result or "research" in result or "No" in result

    @pytest.mark.asyncio
    async def test_search_research_by_reward(self, ensure_test_data, sample_pokemon_name, mcp_server):
        """Test search_research_by_reward tool."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        search_research_by_reward = captured_tools['search_research_by_reward']
        result = await search_research_by_reward(pokemon_name=sample_pokemon_name)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_research_by_reward_not_found(self, ensure_test_data, mcp_server):
        """Test search_research_by_reward with Pokemon not in research."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        search_research_by_reward = captured_tools['search_research_by_reward']
        result = await search_research_by_reward(pokemon_name="mewtwo")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_research_by_task_type(self, ensure_test_data, mcp_server):
        """Test get_research_by_task_type tool."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_research_by_task_type = captured_tools['get_research_by_task_type']
        result = await get_research_by_task_type(task_type="catch")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_shiny_research_rewards(self, ensure_test_data, mcp_server):
        """Test get_shiny_research_rewards tool."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_shiny_research_rewards = captured_tools['get_shiny_research_rewards']
        result = await get_shiny_research_rewards()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "shiny" in result.lower() or "no" in result.lower()

    @pytest.mark.asyncio
    async def test_get_easy_research_tasks(self, ensure_test_data, mcp_server):
        """Test get_easy_research_tasks tool."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_easy_research_tasks = captured_tools['get_easy_research_tasks']
        result = await get_easy_research_tasks()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_research_tasks(self, ensure_test_data, mcp_server):
        """Test search_research_tasks tool."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        search_research_tasks = captured_tools['search_research_tasks']
        result = await search_research_tasks(query="catch")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_research_tasks_no_results(self, ensure_test_data, mcp_server):
        """Test search_research_tasks with query that returns no results."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        search_research_tasks = captured_tools['search_research_tasks']
        result = await search_research_tasks(query="xyznotfound123")

        assert isinstance(result, str)
        assert "No research" in result or "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_get_research_recommendations_balanced(self, ensure_test_data, mcp_server):
        """Test get_research_recommendations with balanced priority."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_research_recommendations = captured_tools['get_research_recommendations']
        result = await get_research_recommendations(priority="balanced")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_research_recommendations_shiny(self, ensure_test_data, mcp_server):
        """Test get_research_recommendations with shiny priority."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_research_recommendations = captured_tools['get_research_recommendations']
        result = await get_research_recommendations(priority="shiny")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_research_recommendations_easy(self, ensure_test_data, mcp_server):
        """Test get_research_recommendations with easy priority."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_research_recommendations = captured_tools['get_research_recommendations']
        result = await get_research_recommendations(priority="easy")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_research_recommendations_rare(self, ensure_test_data, mcp_server):
        """Test get_research_recommendations with rare priority."""
        from pogo_mcp.research import register_research_tools

        captured_tools = {}

        class MockMCP:
            def tool(self):
                def decorator(func):
                    captured_tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp = MockMCP()
        register_research_tools(mock_mcp)

        get_research_recommendations = captured_tools['get_research_recommendations']
        result = await get_research_recommendations(priority="rare")

        assert isinstance(result, str)
        assert len(result) > 0
