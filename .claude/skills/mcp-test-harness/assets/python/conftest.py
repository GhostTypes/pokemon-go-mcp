"""
Shared pytest fixtures for MCP server integration tests.

Copy this file to your tests/ directory and update the import
to point to your FastMCP server instance.
"""

import pytest
from fastmcp import Client

from server import mcp


@pytest.fixture
async def client():
    """
    Provide a connected MCP client for tests.

    Uses FastMCP's in-memory transport for fast, reliable testing.
    The client is automatically connected before each test
    and disconnected after, even if the test fails.

    Usage:
        async def test_something(client: Client):
            result = await client.call_tool("tool_name", {"arg": "value"})
            assert result.content[0].text == "expected"
    """
    async with Client(mcp) as client:
        yield client


@pytest.fixture
def expected_tools():
    """
    List of tools your server should expose.

    TODO: Update this list to match your server's tools.
    """
    return [
        "example_tool_1",
        "example_tool_2",
    ]


@pytest.fixture
def expected_resources():
    """
    List of resource URIs your server should expose.

    TODO: Update this list if your server exposes resources.
    """
    return []


@pytest.fixture
def expected_prompts():
    """
    List of prompt names your server should expose.

    TODO: Update this list if your server exposes prompts.
    """
    return []
