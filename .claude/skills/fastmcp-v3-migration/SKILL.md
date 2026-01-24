---
name: fastmcp-v3-migration
description: Production-ready migration from FastMCP v2.x to v3.0. Use when upgrading MCP servers built on FastMCP to v3, migrating legacy FastMCP code, converting v2 patterns to v3 architecture (providers/transforms), or when user mentions FastMCP upgrade, migration, or v3. Covers breaking changes, deprecated patterns, new v3 features (providers, transforms, versioning, authorization), and testing strategies. Ensures zero-regression migrations with user confirmation checkpoints.
---

# FastMCP v3 Migration Skill

Migrate FastMCP MCP servers from v2.x to v3.0 with zero breaking changes or regressions.

## Critical: User Confirmation Protocol

**Use AskUserQuestionTool to confirm before any destructive or ambiguous operation:**

1. Before modifying any file, confirm the migration scope
2. Before changing imports, confirm which v2 patterns are in use
3. Before removing deprecated code, confirm replacement approach
4. Before testing, confirm the test strategy
5. After migration, confirm all features work as expected

## Quick Start Migration

Most servers need only one change:

```python
# BEFORE (v2.x)
from mcp.server.fastmcp import FastMCP

# AFTER (v3.0)
from fastmcp import FastMCP
```

If that's the only change needed, the migration is complete. Run tests to verify.

## Migration Workflow

### Phase 1: Assessment

1. **Identify FastMCP version**: Check `pip show fastmcp` or `requirements.txt`
2. **Scan for breaking patterns**: See [Breaking Changes Reference](#breaking-changes-reference)
3. **Use AskUserQuestionTool**: Confirm migration scope with user
4. **Create backup**: Ensure git commit or file backup exists

### Phase 2: Core Migration

Apply changes in order of priority:

1. Update imports (required)
2. Fix breaking changes (if any patterns detected)
3. Update deprecated patterns (optional but recommended)
4. Adopt new v3 features (optional enhancement)

### Phase 3: Validation

1. Run existing tests
2. Test with FastMCP Client
3. Verify with MCP Inspector: `fastmcp dev server.py`
4. **Use AskUserQuestionTool**: Confirm migration success with user

---

## Breaking Changes Reference

### Import Change (Required)

```python
# v2.x
from mcp.server.fastmcp import FastMCP

# v3.0
from fastmcp import FastMCP
```

### WSTransport Removed

```python
# v2.x (removed)
from fastmcp.client.transports import WSTransport

# v3.0 replacement
from fastmcp.client.transports import StreamableHttpTransport
```

### Auth Provider Environment Variables

Auth providers no longer auto-load from environment:

```python
# v2.x (auto-loaded)
auth = GitHubProvider()

# v3.0 (explicit)
import os
auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
)
```

### Component enable()/disable() Moved to Server

```python
# v2.x
tool = await server.get_tool("my_tool")
tool.disable()

# v3.0
server.disable(names={"my_tool"}, components=["tool"])
```

### Listing Methods Return Lists (Not Dicts)

```python
# v2.x
tools = await server.get_tools()
tool = tools["my_tool"]

# v3.0
tools = await server.get_tools()
tool = next((t for t in tools if t.name == "my_tool"), None)
```

### Prompts Use Message Class

```python
# v2.x
from mcp.types import PromptMessage, TextContent

@mcp.prompt
def my_prompt() -> PromptMessage:
    return PromptMessage(role="user", content=TextContent(type="text", text="Hello"))

# v3.0
from fastmcp.prompts import Message

@mcp.prompt
def my_prompt() -> Message:
    return Message("Hello")
```

### Context State Methods Are Async

```python
# v2.x (sync)
ctx.set_state("key", "value")
value = ctx.get_state("key")

# v3.0 (async)
await ctx.set_state("key", "value")
value = await ctx.get_state("key")
```

### Metadata Namespace Renamed

```python
# v2.x
tags = tool.meta.get("_fastmcp", {}).get("tags", [])

# v3.0
tags = tool.meta.get("fastmcp", {}).get("tags", [])
```

### Server Banner Environment Variable

```bash
# v2.x
FASTMCP_SHOW_CLI_BANNER=false

# v3.0
FASTMCP_SHOW_SERVER_BANNER=false
```

---

## Deprecated Patterns (Update When Convenient)

These still work but emit warnings:

### mount() prefix → namespace

```python
# Deprecated
main.mount(subserver, prefix="api")

# Recommended
main.mount(subserver, namespace="api")
```

### include_tags/exclude_tags → enable()/disable()

```python
# Deprecated
mcp = FastMCP("server", exclude_tags={"internal"})

# Recommended
mcp = FastMCP("server")
mcp.disable(tags={"internal"})
```

### tool_serializer → ToolResult

```python
# Deprecated: tool_serializer parameter

# Recommended: Return ToolResult for explicit serialization
from fastmcp.tools import ToolResult

@mcp.tool
def my_tool() -> ToolResult:
    return ToolResult(
        content=[TextContent(type="text", text="Done")],
        structured_content={"status": "success"}
    )
```

### add_tool_transformation() → add_transform()

```python
# Deprecated
mcp.add_tool_transformation("name", config)

# Recommended
from fastmcp.server.transforms import ToolTransform
mcp.add_transform(ToolTransform({"name": config}))
```

### FastMCP.as_proxy() → create_proxy()

```python
# Deprecated
proxy = FastMCP.as_proxy("http://example.com/mcp")

# Recommended
from fastmcp.server import create_proxy
proxy = create_proxy("http://example.com/mcp")
```

---

## Behavior Changes

### Decorators Return Functions

In v3, decorated functions stay callable (like Flask/FastAPI):

```python
@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# v3.0: Can call directly for testing
greet("World")  # Returns "Hello, World!"
```

For v2 compatibility (if code relies on FunctionTool objects):
```bash
export FASTMCP_DECORATOR_MODE=object
```

### Sync Tools Run in Threadpool

v3 automatically dispatches sync tools to a threadpool:

```python
@mcp.tool
def slow_tool():
    time.sleep(10)  # No longer blocks event loop
    return "done"
```

---

## New v3 Features

For detailed v3 feature adoption, see: [references/v3-features.md](references/v3-features.md)

Quick overview of new capabilities:

- **Providers**: Source components from anywhere (LocalProvider, FileSystemProvider, OpenAPIProvider, ProxyProvider, SkillsProvider)
- **Transforms**: Middleware for component modification (Namespace, ToolTransform, VersionFilter, Visibility)
- **Component Versioning**: Multiple versions of same tool with automatic routing
- **Authorization**: Per-component auth with require_auth, require_scopes
- **Session State**: Async state that persists across tool calls
- **Visibility System**: Dynamic enable/disable by tags, names, sessions
- **OpenTelemetry**: Native tracing instrumentation
- **Background Tasks**: SEP-1686 long-running operations
- **Hot Reload**: `fastmcp run --reload` for development

---

## Testing Strategy

### Using FastMCP Client

```python
import pytest
from fastmcp.client import Client

@pytest.fixture
async def client():
    from my_server import mcp
    async with Client(transport=mcp) as client:
        yield client

async def test_tools_available(client):
    tools = await client.list_tools()
    assert len(tools) > 0

async def test_tool_execution(client):
    result = await client.call_tool("my_tool", {"arg": "value"})
    assert result.data is not None
```

### Direct Function Testing (v3 Feature)

```python
# v3 decorated functions are callable
from my_server import greet

def test_greet():
    assert greet("World") == "Hello, World!"
```

### MCP Inspector

```bash
fastmcp dev server.py
```

---

## Migration Checklist

Use AskUserQuestionTool to walk through with user:

- [ ] Backup created (git commit or file copy)
- [ ] Import updated: `from fastmcp import FastMCP`
- [ ] WSTransport replaced with StreamableHttpTransport (if used)
- [ ] Auth providers have explicit configuration (if used)
- [ ] enable()/disable() moved to server level (if used)
- [ ] get_tools()/get_resources()/get_prompts() handle list return (if used)
- [ ] Prompts use Message class (if used)
- [ ] State methods are async (if ctx.get_state/set_state used)
- [ ] Metadata namespace updated `_fastmcp` → `fastmcp` (if accessed)
- [ ] Deprecated patterns updated (optional)
- [ ] Tests pass
- [ ] Manual verification with fastmcp dev

---

## Common Migration Scenarios

### Scenario 1: Simple Tool Server

Minimal migration - just update import:

```python
# BEFORE
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("MyServer")

@mcp.tool
def add(a: int, b: int) -> int:
    return a + b

# AFTER
from fastmcp import FastMCP  # Only change needed
mcp = FastMCP("MyServer")

@mcp.tool
def add(a: int, b: int) -> int:
    return a + b
```

### Scenario 2: Server with Auth

Update imports and explicit auth config:

```python
# BEFORE
from mcp.server.fastmcp import FastMCP
from fastmcp.server.auth import GitHubProvider

mcp = FastMCP("AuthServer")
auth = GitHubProvider()  # Auto-loaded from env

# AFTER
import os
from fastmcp import FastMCP
from fastmcp.server.auth import GitHubProvider

mcp = FastMCP("AuthServer")
auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
)
```

### Scenario 3: Server with Session State

Update to async state methods:

```python
# BEFORE
@mcp.tool
def counter(ctx: Context) -> int:
    count = ctx.get_state("count") or 0
    ctx.set_state("count", count + 1)
    return count + 1

# AFTER
@mcp.tool
async def counter(ctx: Context) -> int:
    count = await ctx.get_state("count") or 0
    await ctx.set_state("count", count + 1)
    return count + 1
```

### Scenario 4: Server with Mounted Sub-servers

Update prefix → namespace:

```python
# BEFORE
main = FastMCP("Main")
sub = FastMCP("Sub")
main.mount(sub, prefix="api")

# AFTER
main = FastMCP("Main")
sub = FastMCP("Sub")
main.mount(sub, namespace="api")
```

### Scenario 5: Server with Tag Filtering

Update to visibility system:

```python
# BEFORE
mcp = FastMCP("Server", exclude_tags={"internal"}, include_tags={"public"})

# AFTER
mcp = FastMCP("Server")
mcp.disable(tags={"internal"})
mcp.enable(tags={"public"}, only=True)  # Allowlist mode
```

---

## Troubleshooting

### Import Error After Upgrade

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

**Solution**: Update import to `from fastmcp import FastMCP`

### State Methods Not Async Error

```
TypeError: object NoneType can't be used in 'await' expression
```

**Solution**: Ensure ctx.get_state/set_state are awaited and function is async

### Decorator Returns Function Instead of Tool

In v3, `@mcp.tool` returns the original function, not a FunctionTool object.

**Solution**: If code depends on FunctionTool properties, either:
1. Set `FASTMCP_DECORATOR_MODE=object`
2. Use `await mcp.get_tool("name")` to get the Tool object

### List Changed Notifications Not Firing

v3 sends notifications automatically. Manual calls may be redundant.

**Solution**: Remove manual notification code unless custom logic requires it

---

## Reference Documentation

For comprehensive details, see reference files:

- [references/v3-features.md](references/v3-features.md) - Complete v3 feature guide
- [references/providers.md](references/providers.md) - Provider architecture
- [references/transforms.md](references/transforms.md) - Transform patterns
- [references/auth.md](references/auth.md) - Authorization system
- [references/testing.md](references/testing.md) - Testing patterns
