# Python/FastMCP Testing Guide

Complete guide for testing MCP servers built with FastMCP using pytest.

## Why FastMCP for Testing?

FastMCP's `Client` class can connect **directly to a server instance in-memory**, eliminating:
- Subprocess management complexity
- Port conflicts and race conditions
- Network latency in tests
- Flaky connection issues

This is the gold standard for MCP server testing in Python.

## Project Setup

### 1. Install Dependencies

```bash
# Windows (Claude Code)
pip install fastmcp pytest pytest-asyncio

# Unix
pip3 install fastmcp pytest pytest-asyncio

# Optional but recommended
pip install inline-snapshot dirty-equals
```

### 2. Configure pytest for Async

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

Or create `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = tests
```

### 3. Project Structure

```
your-mcp-server/
├── src/
│   └── your_server/
│       ├── __init__.py
│       └── server.py      # FastMCP server definition
├── tests/
│   ├── conftest.py        # Shared fixtures
│   └── test_tools.py      # Tool tests
├── pyproject.toml
└── README.md
```

## Core Testing Pattern

### The In-Memory Client Pattern

```python
import pytest
from fastmcp import Client
from your_server.server import mcp  # Your FastMCP instance

@pytest.fixture
async def client():
    """Create a test client connected to the server."""
    async with Client(mcp) as client:
        yield client

async def test_tool_execution(client: Client):
    """Test a tool with real inputs and validate real outputs."""
    result = await client.call_tool(
        name="your_tool_name",
        arguments={"param1": "value1", "param2": 42}
    )
    
    # Validate the actual response data
    assert result.content[0].text == "expected output"
```

### Why This Works

When you pass a FastMCP server instance directly to `Client()`:
1. FastMCP creates an in-memory STDIO transport internally
2. Full MCP protocol compliance is maintained
3. No subprocess, no ports, no network
4. Tests run in milliseconds

## Complete Example

### Server (src/calculator/server.py)

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool
def greet(name: str, formal: bool = False) -> str:
    """Generate a greeting."""
    if formal:
        return f"Good day, {name}."
    return f"Hey {name}!"
```

### Test File (tests/test_calculator.py)

```python
import pytest
from fastmcp import Client
from calculator.server import mcp


@pytest.fixture
async def client():
    """Fixture providing a connected MCP client."""
    async with Client(mcp) as client:
        yield client


class TestToolDiscovery:
    """Verify all expected tools are registered."""

    async def test_lists_all_tools(self, client: Client):
        """All tools should be discoverable."""
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        
        assert "add" in tool_names
        assert "divide" in tool_names
        assert "greet" in tool_names

    async def test_tool_count(self, client: Client):
        """Should have exactly 3 tools."""
        tools = await client.list_tools()
        assert len(tools) == 3


class TestAddTool:
    """Tests for the add tool."""

    async def test_add_positive_numbers(self, client: Client):
        result = await client.call_tool("add", {"a": 5, "b": 3})
        assert result.content[0].text == "8"

    async def test_add_negative_numbers(self, client: Client):
        result = await client.call_tool("add", {"a": -5, "b": -3})
        assert result.content[0].text == "-8"

    async def test_add_zero(self, client: Client):
        result = await client.call_tool("add", {"a": 0, "b": 0})
        assert result.content[0].text == "0"

    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, "3"),
        (10, 20, "30"),
        (-5, 5, "0"),
        (100, -50, "50"),
    ])
    async def test_add_parametrized(self, client: Client, a, b, expected):
        result = await client.call_tool("add", {"a": a, "b": b})
        assert result.content[0].text == expected


class TestDivideTool:
    """Tests for the divide tool."""

    async def test_divide_basic(self, client: Client):
        result = await client.call_tool("divide", {"a": 10.0, "b": 2.0})
        assert result.content[0].text == "5.0"

    async def test_divide_by_zero_raises_error(self, client: Client):
        """Division by zero should return an error."""
        result = await client.call_tool("divide", {"a": 10.0, "b": 0.0})
        # FastMCP wraps exceptions - check for error indicator
        assert result.is_error or "zero" in result.content[0].text.lower()


class TestGreetTool:
    """Tests for the greet tool."""

    async def test_informal_greeting(self, client: Client):
        result = await client.call_tool("greet", {"name": "Alice"})
        assert result.content[0].text == "Hey Alice!"

    async def test_formal_greeting(self, client: Client):
        result = await client.call_tool(
            "greet", 
            {"name": "Dr. Smith", "formal": True}
        )
        assert result.content[0].text == "Good day, Dr. Smith."
```

### conftest.py (tests/conftest.py)

```python
"""Shared pytest fixtures for MCP server tests."""

import pytest
from fastmcp import Client
from calculator.server import mcp


@pytest.fixture
async def client():
    """
    Provide a connected MCP client for tests.
    
    The client is automatically connected before the test
    and disconnected after, even if the test fails.
    """
    async with Client(mcp) as client:
        yield client


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "valid_numbers": [(1, 2), (10, 20), (-5, 5)],
        "edge_cases": [(0, 0), (float('inf'), 1)],
    }
```

## Advanced Patterns

### Testing Tools with External Dependencies

For tools that call external APIs, use environment variables and test with real calls:

```python
import os
import pytest
from fastmcp import Client
from your_server.server import mcp


@pytest.fixture
async def client():
    # Ensure required env vars are set
    assert os.environ.get("API_KEY"), "API_KEY environment variable required"
    async with Client(mcp) as client:
        yield client


async def test_external_api_tool(client: Client):
    """Test tool that calls external API with real data."""
    result = await client.call_tool(
        "fetch_weather",
        {"city": "New York"}
    )
    
    # Validate structure and reasonable data
    data = result.content[0].text
    assert "temperature" in data.lower() or "temp" in data.lower()
```

### Snapshot Testing with inline-snapshot

For complex outputs that are tedious to write by hand:

```python
from inline_snapshot import snapshot

async def test_complex_output(client: Client):
    result = await client.call_tool("generate_report", {"id": "test-123"})
    
    # First run: leave snapshot() empty, run with --inline-snapshot=create
    # It will fill in the actual value
    assert result.content[0].text == snapshot()
```

Run with:
```bash
# Create/update snapshots
pytest --inline-snapshot=create

# Fix outdated snapshots
pytest --inline-snapshot=fix
```

### Testing Concurrent Tool Calls

```python
import asyncio

async def test_concurrent_calls(client: Client):
    """Verify tools handle concurrent invocations correctly."""
    tasks = [
        client.call_tool("add", {"a": i, "b": i})
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    assert len(results) == 10
    for i, result in enumerate(results):
        expected = str(i + i)
        assert result.content[0].text == expected
```

### Testing Resources and Prompts

```python
async def test_list_resources(client: Client):
    """Test resource discovery."""
    resources = await client.list_resources()
    resource_uris = [r.uri for r in resources]
    
    assert "file://config.json" in resource_uris

async def test_read_resource(client: Client):
    """Test resource content."""
    content = await client.read_resource("file://config.json")
    assert "version" in content[0].text

async def test_list_prompts(client: Client):
    """Test prompt discovery."""
    prompts = await client.list_prompts()
    prompt_names = [p.name for p in prompts]
    
    assert "summarize" in prompt_names
```

## Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/test_tools.py

# Run specific test class
pytest tests/test_tools.py::TestAddTool

# Run specific test
pytest tests/test_tools.py::TestAddTool::test_add_positive_numbers

# Show print statements
pytest -s

# Generate coverage report
pip install pytest-cov
pytest --cov=your_server --cov-report=html
```

## Troubleshooting

### "Event loop is closed" Errors

Ensure `asyncio_mode = "auto"` is set in pytest config. This handles event loop lifecycle automatically.

### "Client not connected" Errors

Always use the async context manager pattern:
```python
async with Client(mcp) as client:
    # Use client here
```

### Import Errors

Ensure your server package is importable:
```bash
pip install -e .  # Install in editable mode
```

Or add to PYTHONPATH:
```bash
# Windows PowerShell
$env:PYTHONPATH = "src"
pytest

# Unix
PYTHONPATH=src pytest
```

### Slow Tests

If tests are slow, check if tools are making real external calls. For pure unit tests, consider mocking, but remember the goal is integration testing with real data.
