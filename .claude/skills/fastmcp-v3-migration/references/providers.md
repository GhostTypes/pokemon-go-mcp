# FastMCP v3 Providers Reference

Complete guide to the Provider architecture in FastMCP 3.0.

## What Are Providers?

Providers answer the question: "Where do components come from?"

A Provider is anything that can:
1. List components (tools, resources, prompts)
2. Retrieve components by name
3. Optionally execute component logic

The key insight: A FastMCP server is itself a Provider, enabling infinite composition.

---

## Provider Interface

All providers implement this interface:

```python
from abc import ABC, abstractmethod
from typing import Sequence
from fastmcp.tools import Tool
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt

class Provider(ABC):
    @abstractmethod
    async def list_tools(self) -> Sequence[Tool]:
        """Return all available tools."""
        ...

    @abstractmethod
    async def get_tool(self, name: str) -> Tool | None:
        """Get a specific tool by name."""
        ...

    @abstractmethod
    async def list_resources(self) -> Sequence[Resource]:
        """Return all available resources."""
        ...

    @abstractmethod
    async def get_resource(self, uri: str) -> Resource | None:
        """Get a specific resource by URI."""
        ...

    @abstractmethod
    async def list_prompts(self) -> Sequence[Prompt]:
        """Return all available prompts."""
        ...

    @abstractmethod
    async def get_prompt(self, name: str) -> Prompt | None:
        """Get a specific prompt by name."""
        ...
```

---

## Built-in Providers

### LocalProvider

The default provider for decorated functions:

```python
from fastmcp import FastMCP
from fastmcp.server.providers import LocalProvider

# Implicit creation
mcp = FastMCP("MyServer")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Explicit creation for reuse
provider = LocalProvider()

@provider.tool
def add(a: int, b: int) -> int:
    return a + b

@provider.resource("config://app")
def get_config() -> dict:
    return {"version": "1.0"}

@provider.prompt
def greeting_prompt(name: str) -> str:
    return f"Say hello to {name}"

# Attach to multiple servers
server1 = FastMCP("Server1", providers=[provider])
server2 = FastMCP("Server2", providers=[provider])
```

### FileSystemProvider

Automatic discovery from Python files:

```python
from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider

# Basic usage
mcp = FastMCP("Server", providers=[
    FileSystemProvider("mcp/")
])

# With hot reload for development
mcp = FastMCP("Server", providers=[
    FileSystemProvider("mcp/", reload=True)
])
```

Directory structure:
```
mcp/
├── tools/
│   ├── greet.py
│   └── calculate.py
├── resources/
│   └── config.py
└── prompts/
    └── templates.py
```

Tool file example:
```python
# mcp/tools/greet.py
from fastmcp.tools import tool

@tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

@tool
def farewell(name: str) -> str:
    """Say goodbye to someone."""
    return f"Goodbye, {name}!"
```

### OpenAPIProvider

Generate tools from OpenAPI specs:

```python
from fastmcp.server.providers.openapi import OpenAPIProvider
import httpx

# From spec dict
spec = {
    "openapi": "3.0.0",
    "info": {"title": "My API", "version": "1.0"},
    "paths": {...}
}

client = httpx.AsyncClient(base_url="https://api.example.com")
provider = OpenAPIProvider(openapi_spec=spec, client=client)

# From URL
provider = OpenAPIProvider.from_url(
    "https://api.example.com/openapi.json",
    client=client
)

mcp = FastMCP("API Server", providers=[provider])
```

### ProxyProvider

Proxy a remote MCP server:

```python
from fastmcp.server import create_proxy
from fastmcp.server.providers import ProxyProvider

# Quick proxy creation
server = create_proxy("http://remote-server/mcp")

# Manual provider creation
from fastmcp import Client

async def client_factory():
    return Client("http://remote-server/mcp")

provider = ProxyProvider(client_factory=client_factory)
mcp = FastMCP("Proxy", providers=[provider])
```

### SkillsProvider

Expose skill directories as MCP resources:

```python
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers.skills import (
    SkillsDirectoryProvider,
    ClaudeSkillsProvider,
    CursorSkillsProvider,
)

mcp = FastMCP("Skills Server")

# Custom skills directory
mcp.add_provider(SkillsDirectoryProvider(
    roots=Path.home() / ".claude" / "skills"
))

# Vendor-specific providers with default paths
mcp.add_provider(ClaudeSkillsProvider())
mcp.add_provider(CursorSkillsProvider())
```

Exposed resources:
- `skill://{name}/SKILL.md` - Main instruction file
- `skill://{name}/_manifest` - JSON manifest with file list, sizes, hashes
- `skill://{name}/{path}` - Any file in the skill directory

---

## Creating Custom Providers

### Basic Custom Provider

```python
from fastmcp.server.providers import Provider
from fastmcp.tools import Tool

class DatabaseToolProvider(Provider):
    def __init__(self, connection_string: str):
        self.conn = connection_string
        self._db = None

    async def _get_db(self):
        if self._db is None:
            self._db = await connect(self.conn)
        return self._db

    async def list_tools(self) -> list[Tool]:
        db = await self._get_db()
        rows = await db.fetch("SELECT * FROM tools WHERE enabled = true")
        return [
            Tool(
                name=row['name'],
                description=row['description'],
                fn=self._create_tool_fn(row)
            )
            for row in rows
        ]

    async def get_tool(self, name: str) -> Tool | None:
        db = await self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM tools WHERE name = ? AND enabled = true",
            name
        )
        if row:
            return Tool(
                name=row['name'],
                description=row['description'],
                fn=self._create_tool_fn(row)
            )
        return None

    def _create_tool_fn(self, row):
        # Create callable from stored procedure name
        async def tool_fn(**kwargs):
            db = await self._get_db()
            return await db.execute(row['procedure'], kwargs)
        return tool_fn

    # Implement empty list/get for resources and prompts
    async def list_resources(self) -> list:
        return []

    async def get_resource(self, uri: str):
        return None

    async def list_prompts(self) -> list:
        return []

    async def get_prompt(self, name: str):
        return None
```

### Provider with Transforms

Providers can have their own transform chain:

```python
from fastmcp.server.providers import Provider
from fastmcp.server.transforms import Namespace, ToolTransform

class MyProvider(Provider):
    ...

provider = MyProvider()
provider.add_transform(Namespace("myns"))
provider.add_transform(ToolTransform({...}))

mcp = FastMCP("Server", providers=[provider])
```

---

## Provider Composition

### Multiple Providers

```python
from fastmcp import FastMCP
from fastmcp.server.providers import LocalProvider, FileSystemProvider

local = LocalProvider()

@local.tool
def local_tool() -> str:
    return "from local"

mcp = FastMCP("Server", providers=[
    local,
    FileSystemProvider("./tools"),
    OpenAPIProvider(spec, client),
])
```

### Mounting (FastMCPProvider)

When you mount a server, it creates a FastMCPProvider:

```python
main = FastMCP("Main")
sub = FastMCP("Sub")

@sub.tool
def sub_tool() -> str:
    return "from sub"

# This creates FastMCPProvider + Namespace transform
main.mount(sub, namespace="sub")
# sub_tool becomes "sub_sub_tool"
```

### Provider Hierarchy

```
Server
├── LocalProvider (decorated functions)
├── FileSystemProvider (./tools)
├── OpenAPIProvider (external API)
└── FastMCPProvider (mounted sub-server)
    ├── Namespace transform
    └── Sub-server's providers
```

---

## Provider Lifecycle

### Initialization

Providers can have async initialization:

```python
class AsyncProvider(Provider):
    async def initialize(self):
        """Called when provider is added to server."""
        self._client = await create_client()

    async def shutdown(self):
        """Called when server shuts down."""
        await self._client.close()
```

### With Lifespan

```python
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

@lifespan
async def provider_lifespan(server):
    provider = MyProvider()
    await provider.initialize()
    server.add_provider(provider)
    try:
        yield
    finally:
        await provider.shutdown()

mcp = FastMCP("Server", lifespan=provider_lifespan)
```

---

## Best Practices

### 1. Keep Providers Focused

Each provider should have a single responsibility:

```python
# Good: Separate providers for different sources
mcp = FastMCP("Server", providers=[
    DatabaseToolProvider(db_conn),
    FileResourceProvider("./data"),
    TemplatePromptProvider("./templates"),
])

# Avoid: One provider doing everything
```

### 2. Use Transforms for Modification

Don't modify components inside providers - use transforms:

```python
# Good: Provider returns raw components, transform modifies
provider = OpenAPIProvider(spec, client)
provider.add_transform(ToolTransform({
    "verbose_name": ToolTransformConfig(name="short")
}))

# Avoid: Modifying inside provider
```

### 3. Handle Errors Gracefully

```python
class RobustProvider(Provider):
    async def get_tool(self, name: str) -> Tool | None:
        try:
            return await self._fetch_tool(name)
        except ConnectionError:
            # Log error, return None to indicate not found
            logger.error(f"Failed to fetch tool {name}")
            return None
```

### 4. Cache When Appropriate

```python
from functools import lru_cache

class CachingProvider(Provider):
    def __init__(self, ttl: int = 60):
        self._cache = {}
        self._ttl = ttl

    async def list_tools(self) -> list[Tool]:
        if "tools" not in self._cache or self._cache_expired("tools"):
            self._cache["tools"] = await self._fetch_tools()
        return self._cache["tools"]
```
