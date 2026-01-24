# FastMCP v3 Testing Reference

Complete guide to testing FastMCP servers.

## Overview

FastMCP v3 makes testing easier with:

- **Callable decorators**: Test functions directly without MCP overhead
- **FastMCP Client**: Full integration testing
- **MCP Inspector**: Interactive debugging

---

## Direct Function Testing (v3 Feature)

In v3, decorated functions remain callable:

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool
def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
```

```python
# test_server.py
from server import add, greet

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0

def test_greet():
    assert greet("World") == "Hello, World!"
    assert greet("Alice") == "Hello, Alice!"
```

This is the fastest way to test tool logic.

---

## Integration Testing with FastMCP Client

### Setup

```bash
pip install pytest-asyncio
```

Configure pytest for async:

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Basic Client Testing

```python
import pytest
from fastmcp.client import Client

from my_server import mcp

@pytest.fixture
async def client():
    async with Client(transport=mcp) as client:
        yield client

async def test_list_tools(client):
    tools = await client.list_tools()
    assert len(tools) > 0

async def test_call_tool(client):
    result = await client.call_tool("add", {"a": 1, "b": 2})
    assert result.data == 3
```

### Testing Resources

```python
async def test_list_resources(client):
    resources = await client.list_resources()
    assert any(r.uri == "config://app" for r in resources)

async def test_read_resource(client):
    result = await client.read_resource("config://app")
    assert result[0].content is not None
```

### Testing Prompts

```python
async def test_list_prompts(client):
    prompts = await client.list_prompts()
    assert any(p.name == "greeting" for p in prompts)

async def test_get_prompt(client):
    result = await client.get_prompt("greeting", {"name": "Alice"})
    assert "Alice" in result.messages[0].content
```

---

## Parametrized Testing

```python
import pytest
from fastmcp.client import Client

from my_server import mcp

@pytest.fixture
async def client():
    async with Client(transport=mcp) as client:
        yield client

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
async def test_add(client, a, b, expected):
    result = await client.call_tool("add", {"a": a, "b": b})
    assert result.data == expected
```

---

## Testing with Snapshots

Use inline-snapshot for complex data structures:

```bash
pip install inline-snapshot
```

```python
from inline_snapshot import snapshot

async def test_tool_schema(client):
    tools = await client.list_tools()
    assert tools == snapshot()
```

Run with `pytest --inline-snapshot=fix,create` to populate snapshots.

---

## Testing Context-Dependent Tools

### Mocking Context

For tools that use Context:

```python
from unittest.mock import AsyncMock, MagicMock
from fastmcp.server.context import Context

def test_tool_with_context():
    # Create mock context
    ctx = MagicMock(spec=Context)
    ctx.get_state = AsyncMock(return_value=5)
    ctx.set_state = AsyncMock()

    # Test the function (v3 makes this possible)
    from my_server import increment_counter

    # Note: For async tools, you need to run in async context
    import asyncio
    result = asyncio.run(increment_counter(ctx))

    assert result == 6
    ctx.set_state.assert_called_once_with("counter", 6)
```

### Integration Test with State

```python
async def test_stateful_tool(client):
    # First call
    result1 = await client.call_tool("increment_counter", {})
    assert result1.data == 1

    # Second call (same session)
    result2 = await client.call_tool("increment_counter", {})
    assert result2.data == 2
```

---

## Testing Authorization

### Testing Protected Tools

```python
import pytest
from fastmcp.client import Client

@pytest.fixture
async def authenticated_client():
    async with Client(transport=mcp, auth_token="valid-token") as client:
        yield client

@pytest.fixture
async def unauthenticated_client():
    async with Client(transport=mcp) as client:
        yield client

async def test_protected_tool_with_auth(authenticated_client):
    result = await authenticated_client.call_tool("admin_tool", {})
    assert result.data is not None

async def test_protected_tool_without_auth(unauthenticated_client):
    with pytest.raises(Exception):  # AuthorizationError
        await unauthenticated_client.call_tool("admin_tool", {})
```

---

## Testing Providers

### Testing Custom Providers

```python
import pytest
from my_provider import DatabaseToolProvider

@pytest.fixture
async def provider():
    provider = DatabaseToolProvider("sqlite:///:memory:")
    await provider.initialize()
    yield provider
    await provider.shutdown()

async def test_list_tools(provider):
    tools = await provider.list_tools()
    assert isinstance(tools, list)

async def test_get_tool(provider):
    tool = await provider.get_tool("existing_tool")
    assert tool is not None
    assert tool.name == "existing_tool"

async def test_get_nonexistent_tool(provider):
    tool = await provider.get_tool("nonexistent")
    assert tool is None
```

---

## Testing Transforms

```python
import pytest
from fastmcp.server.transforms import Namespace
from fastmcp.tools import Tool

@pytest.fixture
def namespace_transform():
    return Namespace("api")

async def test_namespace_list_tools(namespace_transform):
    tools = [
        Tool(name="greet", description="Greet", fn=lambda: None),
        Tool(name="add", description="Add", fn=lambda: None),
    ]

    result = await namespace_transform.list_tools(tools)

    assert result[0].name == "api_greet"
    assert result[1].name == "api_add"

async def test_namespace_get_tool(namespace_transform):
    async def call_next(name: str):
        if name == "greet":
            return Tool(name="greet", description="Greet", fn=lambda: None)
        return None

    # Request with prefix
    result = await namespace_transform.get_tool("api_greet", call_next)
    assert result is not None
    assert result.name == "api_greet"
```

---

## MCP Inspector

Interactive testing during development:

```bash
# Start server with inspector
fastmcp dev server.py

# With hot reload
fastmcp dev server.py --reload
```

The inspector provides:
- Tool listing and execution
- Resource browsing
- Prompt testing
- Real-time logs

---

## Testing HTTP Deployment

```python
import pytest
import httpx
from fastmcp import FastMCP

@pytest.fixture
async def http_server():
    mcp = FastMCP("TestServer")

    @mcp.tool
    def ping() -> str:
        return "pong"

    # Start server in background
    import asyncio
    task = asyncio.create_task(
        mcp.run_async(transport="http", port=8765)
    )
    await asyncio.sleep(0.5)  # Wait for startup

    yield "http://localhost:8765/mcp"

    task.cancel()

async def test_http_endpoint(http_server):
    from fastmcp.client import Client

    async with Client(http_server) as client:
        tools = await client.list_tools()
        assert any(t.name == "ping" for t in tools)
```

---

## Best Practices

### 1. Test at Multiple Levels

```python
# Unit: Direct function tests
def test_add_unit():
    from server import add
    assert add(1, 2) == 3

# Integration: Client tests
async def test_add_integration(client):
    result = await client.call_tool("add", {"a": 1, "b": 2})
    assert result.data == 3

# E2E: Full HTTP tests
async def test_add_e2e(http_server):
    async with Client(http_server) as client:
        result = await client.call_tool("add", {"a": 1, "b": 2})
        assert result.data == 3
```

### 2. Test Error Cases

```python
async def test_tool_with_invalid_args(client):
    with pytest.raises(Exception):
        await client.call_tool("add", {"a": "not_a_number", "b": 2})

async def test_nonexistent_tool(client):
    with pytest.raises(Exception):
        await client.call_tool("nonexistent", {})
```

### 3. Use Fixtures for Common Setup

```python
@pytest.fixture
async def client():
    async with Client(transport=mcp) as client:
        yield client

@pytest.fixture
async def seeded_client(client):
    # Seed some data
    await client.call_tool("create_user", {"name": "Test"})
    yield client
```

### 4. Clean Up State Between Tests

```python
@pytest.fixture(autouse=True)
async def reset_state():
    yield
    # Reset after each test
    await reset_database()
```

### 5. Test Versioned Components

```python
async def test_version_routing(client):
    # Default gets latest
    result = await client.call_tool("add", {"x": 1, "y": 2})
    assert result.data == 3  # v2 has z=0 default

    # Specific version
    result = await client.call_tool("add", {"x": 1, "y": 2}, version="1.0")
    assert result.data == 3  # v1 only has x, y
```
