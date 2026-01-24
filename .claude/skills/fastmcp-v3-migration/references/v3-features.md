# FastMCP v3 Features Reference

Complete guide to new features in FastMCP 3.0.

## Architecture Overview

FastMCP 3 is built on three fundamental primitives:

1. **Components**: The atoms of MCP (Tool, Resource, Prompt)
2. **Providers**: Where components come from
3. **Transforms**: How components are modified

This composable architecture means features emerge from combining primitives rather than requiring specialized code.

---

## Providers

Providers answer: "Where do components come from?"

### LocalProvider

The classic FastMCP experience - decorated functions:

```python
from fastmcp import FastMCP
from fastmcp.server.providers import LocalProvider

# Implicit: FastMCP creates LocalProvider automatically
mcp = FastMCP("MyServer")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Explicit: Reusable provider for multiple servers
provider = LocalProvider()

@provider.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

server1 = FastMCP("Server1", providers=[provider])
server2 = FastMCP("Server2", providers=[provider])
```

### FileSystemProvider

Source components from Python files in a directory:

```python
from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider

# Point at a directory of tool files
mcp = FastMCP("Server", providers=[FileSystemProvider("mcp/")])
```

Tool file structure:
```python
# mcp/tools/greet.py
from fastmcp.tools import tool

@tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"
```

With `reload=True`, changes take effect instantly without restart:
```python
FileSystemProvider("mcp/", reload=True)
```

### OpenAPIProvider

Generate tools from OpenAPI specifications:

```python
from fastmcp.server.providers.openapi import OpenAPIProvider
import httpx

client = httpx.AsyncClient(base_url="https://api.example.com")
provider = OpenAPIProvider(openapi_spec=spec, client=client)

mcp = FastMCP("API Server", providers=[provider])
```

Combine with ToolTransform to curate auto-generated tools:
```python
from fastmcp.server.transforms import ToolTransform
from fastmcp.tools.tool_transform import ToolTransformConfig

provider.add_transform(ToolTransform({
    "verbose_auto_generated_name": ToolTransformConfig(
        name="short_name",
        description="Better description",
        tags={"category"},
    ),
}))
```

### ProxyProvider

Source components from a remote MCP server:

```python
from fastmcp.server import create_proxy

# Proxy a remote server
server = create_proxy("http://remote-server/mcp")
```

### SkillsProvider

Expose skill files as MCP resources:

```python
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP("Skills Server")
mcp.add_provider(SkillsDirectoryProvider(roots=Path.home() / ".claude" / "skills"))
```

Each skill directory with SKILL.md becomes discoverable:
- `skill://{name}/SKILL.md` - Main instruction file
- `skill://{name}/_manifest` - JSON listing of files
- `skill://{name}/{path}` - Supporting files

### Custom Providers

Create custom providers by subclassing Provider:

```python
from fastmcp.server.providers import Provider
from fastmcp.tools import Tool

class DatabaseProvider(Provider):
    async def list_tools(self) -> list[Tool]:
        rows = await db.fetch("SELECT * FROM tools")
        return [Tool(name=row['name'], description=row['desc']) for row in rows]

    async def get_tool(self, name: str) -> Tool | None:
        row = await db.fetchrow("SELECT * FROM tools WHERE name = ?", name)
        return Tool(name=row['name'], description=row['desc']) if row else None

mcp = FastMCP("Database Server", providers=[DatabaseProvider()])
```

---

## Transforms

Transforms modify components as they flow from providers to clients.

### Application Levels

- **Provider-level**: `provider.add_transform()` - affects only that provider
- **Server-level**: `server.add_transform()` - affects all providers

### Namespace Transform

Add prefixes to prevent collisions:

```python
from fastmcp.server.transforms import Namespace

provider.add_transform(Namespace("api"))
# tool "greet" becomes "api_greet"
# resource "data://x" becomes "data://api/x"
```

### ToolTransform

Reshape tools - rename, redescribe, modify arguments:

```python
from fastmcp.server.transforms import ToolTransform
from fastmcp.tools.tool_transform import ToolTransformConfig

provider.add_transform(ToolTransform({
    "verbose_name": ToolTransformConfig(
        name="short_name",
        description="Better description for the agent",
        tags={"category"},
    ),
}))
```

### VersionFilter

Filter components by version range:

```python
from fastmcp.server.transforms import VersionFilter

# v1 server: only versions < 2.0
api_v1 = FastMCP("API v1", providers=[components])
api_v1.add_transform(VersionFilter(version_lt="2.0"))

# v2 server: only versions >= 2.0
api_v2 = FastMCP("API v2", providers=[components])
api_v2.add_transform(VersionFilter(version_gte="2.0"))
```

### Visibility Transform

Control which components are exposed:

```python
mcp.disable(tags={"admin"})          # Hide by tag
mcp.disable(names={"dangerous"})      # Hide by name
mcp.enable(tags={"public"}, only=True)  # Allowlist mode
```

### ResourcesAsTools / PromptsAsTools

Expose resources and prompts as tools for tool-only clients:

```python
from fastmcp.server.transforms import ResourcesAsTools, PromptsAsTools

mcp.add_transform(ResourcesAsTools(mcp))
mcp.add_transform(PromptsAsTools(mcp))
```

### Custom Transforms

Create custom transforms:

```python
from fastmcp.server.transforms import Transform, GetToolNext
from fastmcp.tools import Tool

class TagFilter(Transform):
    def __init__(self, required_tags: set[str]):
        self.required_tags = required_tags

    async def list_tools(self, tools: list[Tool]) -> list[Tool]:
        return [t for t in tools if t.tags & self.required_tags]

    async def get_tool(self, name: str, call_next: GetToolNext) -> Tool | None:
        tool = await call_next(name)
        return tool if tool and tool.tags & self.required_tags else None
```

---

## Component Versioning

Register multiple versions of the same component:

```python
@mcp.tool(version="1.0")
def add(x: int, y: int) -> int:
    return x + y

@mcp.tool(version="2.0")
def add(x: int, y: int, z: int = 0) -> int:
    return x + y + z

# Only v2.0 exposed via list_tools()
# Calling "add" invokes v2.0 implementation
```

### Version Metadata

```python
tools = await client.list_tools()
# Each tool's meta includes:
# - meta["fastmcp"]["version"]: "2.0"
# - meta["fastmcp"]["versions"]: ["2.0", "1.0"]
```

### Calling Specific Versions

```python
# Call latest (default)
result = await client.call_tool("add", {"x": 1, "y": 2})

# Call specific version
result = await client.call_tool("add", {"x": 1, "y": 2}, version="1.0")

# For generic MCP clients, use _meta
{"x": 1, "y": 2, "_meta": {"fastmcp": {"version": "1.0"}}}
```

---

## Authorization

### Component-Level Auth

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_auth, require_scopes

mcp = FastMCP()

@mcp.tool(auth=require_auth)
def protected_tool(): ...

@mcp.resource("data://secret", auth=require_scopes("read"))
def secret_data(): ...

@mcp.prompt(auth=require_scopes("admin"))
def admin_prompt(): ...
```

### Built-in Auth Checks

- `require_auth`: Requires any valid token
- `require_scopes(*scopes)`: Requires specific OAuth scopes
- `restrict_tag(tag, scopes)`: Requires scopes only for tagged components

### Server-Wide Auth

```python
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.auth import require_auth, restrict_tag

# Require auth for all components
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_auth)])

# Tag-based restrictions
mcp = FastMCP(middleware=[
    AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"]))
])
```

### Custom Auth Checks

```python
from fastmcp.server.auth import AuthContext

def custom_check(ctx: AuthContext) -> bool:
    return ctx.token is not None and "admin" in ctx.token.scopes

@mcp.tool(auth=custom_check)
def admin_tool(): ...
```

**Note**: STDIO transport bypasses all auth checks (no OAuth concept).

---

## Session State

State persists across tool calls within a session:

```python
@mcp.tool
async def increment_counter(ctx: Context) -> int:
    count = await ctx.get_state("counter") or 0
    await ctx.set_state("counter", count + 1)
    return count + 1
```

### Key Changes from v2

- Methods are now async: `await ctx.get_state()`, `await ctx.set_state()`, `await ctx.delete_state()`
- State expires after 1 day (TTL)

### Distributed Backends

```python
from key_value.aio.stores.redis import RedisStore

mcp = FastMCP("server", session_state_store=RedisStore(...))
```

---

## Visibility System

### Server-Level Visibility

```python
mcp = FastMCP("Server")

mcp.disable(names={"dangerous_tool"}, components=["tool"])
mcp.disable(tags={"admin"})
mcp.enable(tags={"public"}, only=True)  # Allowlist mode

# Later enable overrides earlier disable
mcp.disable(tags={"internal"})
mcp.enable(names={"safe_tool"})  # visible despite internal tag
```

### Per-Session Visibility

```python
@mcp.tool(tags={"premium"})
def premium_analysis(data: str) -> str:
    return f"Premium analysis of: {data}"

@mcp.tool
async def unlock_premium(ctx: Context) -> str:
    """Unlock premium features for this session only."""
    await ctx.enable_components(tags={"premium"})
    return "Premium features unlocked"

@mcp.tool
async def reset_features(ctx: Context) -> str:
    """Reset to default feature set."""
    await ctx.reset_visibility()
    return "Features reset to defaults"

# Globally disabled - sessions unlock individually
mcp.disable(tags={"premium"})
```

Session visibility methods:
- `await ctx.enable_components(...)`: Enable for this session
- `await ctx.disable_components(...)`: Disable for this session
- `await ctx.reset_visibility()`: Clear session rules

---

## Production Features

### OpenTelemetry Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

# FastMCP automatically instruments all operations
```

### Background Tasks (SEP-1686)

```python
from fastmcp.server.tasks import TaskConfig

@mcp.tool(task=TaskConfig(mode="required"))
async def long_running_task():
    # Must be executed as background task
    ...

@mcp.tool(task=TaskConfig(mode="optional"))
async def flexible_task():
    # Supports both sync and task execution
    ...

@mcp.tool(task=True)  # Shorthand for mode="optional"
async def simple_task():
    ...
```

Task modes:
- `"forbidden"`: Default, no task execution
- `"optional"`: Both sync and task execution
- `"required"`: Must be background task

Install with `fastmcp[tasks]` for Docket integration.

### Tool Timeouts

```python
@mcp.tool(timeout=30.0)
async def fetch_data(url: str) -> dict:
    """Fetch with 30-second timeout."""
    ...
```

### Pagination

```python
server = FastMCP("ComponentRegistry", list_page_size=50)
```

### PingMiddleware

```python
from fastmcp.server.middleware import PingMiddleware

mcp = FastMCP("server")
mcp.add_middleware(PingMiddleware(interval_ms=5000))
```

---

## Developer Experience

### Decorators Return Functions

```python
@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Callable for testing
greet("World")  # "Hello, World!"
```

For v2 compatibility: `FASTMCP_DECORATOR_MODE=object`

### Hot Reload

```bash
fastmcp run server.py --reload
fastmcp run server.py --reload --reload-dir ./src --reload-dir ./lib
```

Or use `fastmcp dev` which includes `--reload` by default.

### Automatic Threadpool

Sync tools run in threadpool automatically:

```python
@mcp.tool
def slow_tool():
    time.sleep(10)  # No longer blocks event loop
    return "done"
```

### Composable Lifespans

```python
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

@lifespan
async def db_lifespan(server):
    db = await connect_db()
    try:
        yield {"db": db}
    finally:
        await db.close()

@lifespan
async def cache_lifespan(server):
    cache = await connect_cache()
    try:
        yield {"cache": cache}
    finally:
        await cache.close()

mcp = FastMCP("server", lifespan=db_lifespan | cache_lifespan)
```

### Rich Result Classes

#### ToolResult

```python
from fastmcp.tools import ToolResult
from mcp.types import TextContent

@mcp.tool
def process(data: str) -> ToolResult:
    return ToolResult(
        content=[TextContent(type="text", text="Done")],
        structured_content={"status": "success", "count": 42},
        meta={"processing_time_ms": 150}
    )
```

#### ResourceResult

```python
from fastmcp.resources import ResourceResult, ResourceContent

@mcp.resource("data://items")
def get_items() -> ResourceResult:
    return ResourceResult(
        contents=[
            ResourceContent({"key": "value"}),
            ResourceContent(b"binary data"),
        ],
        meta={"count": 2}
    )
```

#### PromptResult

```python
from fastmcp.prompts import PromptResult, Message

@mcp.prompt
def conversation() -> PromptResult:
    return PromptResult(
        messages=[
            Message("What's the weather?"),
            Message("It's sunny today.", role="assistant"),
        ],
        meta={"generated_at": "2024-01-01"}
    )
```

### Context.transport Property

```python
@mcp.tool
def my_tool(ctx: Context) -> str:
    if ctx.transport == "stdio":
        return "short response"
    return "detailed response with more context"
```

Returns `"stdio"`, `"sse"`, or `"streamable-http"`.
