# FastMCP v3 Transforms Reference

Complete guide to the Transform architecture in FastMCP 3.0.

## What Are Transforms?

Transforms are middleware for the component pipeline. They intercept the flow of components from providers to clients and can modify what passes through.

Key uses:
- Rename tools
- Add namespace prefixes
- Filter by version
- Hide components by tag
- Apply security rules
- Convert resources to tools

---

## Transform Interface

```python
from abc import ABC
from typing import Sequence, Callable, Awaitable
from fastmcp.tools import Tool
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt

# Type aliases for call_next functions
GetToolNext = Callable[[str], Awaitable[Tool | None]]
GetResourceNext = Callable[[str], Awaitable[Resource | None]]
GetPromptNext = Callable[[str], Awaitable[Prompt | None]]

class Transform(ABC):
    # List operations receive and return sequences
    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        return tools

    async def list_resources(self, resources: Sequence[Resource]) -> Sequence[Resource]:
        return resources

    async def list_prompts(self, prompts: Sequence[Prompt]) -> Sequence[Prompt]:
        return prompts

    # Get operations use middleware pattern with call_next
    async def get_tool(self, name: str, call_next: GetToolNext) -> Tool | None:
        return await call_next(name)

    async def get_resource(self, uri: str, call_next: GetResourceNext) -> Resource | None:
        return await call_next(uri)

    async def get_prompt(self, name: str, call_next: GetPromptNext) -> Prompt | None:
        return await call_next(name)
```

---

## Application Levels

### Provider-Level Transforms

Affect only that provider's components:

```python
from fastmcp.server.providers import LocalProvider
from fastmcp.server.transforms import Namespace

provider = LocalProvider()
provider.add_transform(Namespace("api"))

@provider.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Tool exposed as "api_greet"
```

### Server-Level Transforms

Affect all components from all providers:

```python
from fastmcp import FastMCP
from fastmcp.server.transforms import Visibility

mcp = FastMCP("Server")
mcp.add_transform(Visibility(disable_tags={"internal"}))

# All components tagged "internal" are hidden
```

### Transform Order

1. Server collects components from all providers
2. Each provider runs its transform chain
3. Server runs its transform chain on aggregated result
4. Final list goes to client

---

## Built-in Transforms

### Namespace

Add prefixes to prevent naming collisions:

```python
from fastmcp.server.transforms import Namespace

# Basic usage
provider.add_transform(Namespace("api"))

# Tool "greet" -> "api_greet"
# Resource "data://config" -> "data://api/config"
```

Use cases:
- Mounting sub-servers
- Separating component groups
- Multi-tenant applications

### ToolTransform

Reshape tools - rename, redescribe, modify:

```python
from fastmcp.server.transforms import ToolTransform
from fastmcp.tools.tool_transform import ToolTransformConfig

provider.add_transform(ToolTransform({
    # Original name -> transformation config
    "get_user_by_id_v2_internal": ToolTransformConfig(
        name="get_user",
        description="Retrieve user information by ID",
        tags={"user", "read"},
    ),
    "delete_user_permanently": ToolTransformConfig(
        name="delete_user",
        description="Delete a user account",
        tags={"user", "write", "destructive"},
    ),
}))
```

ToolTransformConfig options:
- `name`: New tool name
- `description`: New description
- `tags`: New or additional tags
- `annotations`: MCP annotations

### VersionFilter

Filter components by version range:

```python
from fastmcp.server.transforms import VersionFilter

# Only versions less than 2.0
api_v1 = FastMCP("v1")
api_v1.add_transform(VersionFilter(version_lt="2.0"))

# Only versions >= 2.0
api_v2 = FastMCP("v2")
api_v2.add_transform(VersionFilter(version_gte="2.0"))

# Specific version range
beta = FastMCP("beta")
beta.add_transform(VersionFilter(
    version_gte="3.0.0-beta",
    version_lt="3.0.0"
))
```

### Visibility

Control component exposure:

```python
from fastmcp.server.transforms import Visibility

# Hide by tags
mcp.add_transform(Visibility(disable_tags={"admin", "internal"}))

# Hide by names
mcp.add_transform(Visibility(disable_names={"dangerous_tool"}))

# Allowlist mode - only show specific tags
mcp.add_transform(Visibility(enable_tags={"public"}, only=True))
```

Server convenience methods:
```python
mcp.disable(tags={"admin"})
mcp.disable(names={"dangerous"})
mcp.enable(tags={"public"}, only=True)
```

### ResourcesAsTools

Expose resources to tool-only clients:

```python
from fastmcp.server.transforms import ResourcesAsTools

mcp.add_transform(ResourcesAsTools(mcp))
```

Generated tools:
- `list_resources`: Returns available resource URIs
- `read_resource`: Reads a resource by URI

### PromptsAsTools

Expose prompts to tool-only clients:

```python
from fastmcp.server.transforms import PromptsAsTools

mcp.add_transform(PromptsAsTools(mcp))
```

Generated tools:
- `list_prompts`: Returns available prompt names
- `get_prompt`: Gets a prompt by name

---

## Creating Custom Transforms

### Filter Transform

Filter components based on criteria:

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
        if tool and tool.tags & self.required_tags:
            return tool
        return None
```

### Modification Transform

Modify components as they pass through:

```python
class DescriptionEnhancer(Transform):
    def __init__(self, suffix: str):
        self.suffix = suffix

    async def list_tools(self, tools: list[Tool]) -> list[Tool]:
        return [
            Tool(
                name=t.name,
                description=f"{t.description} {self.suffix}",
                fn=t.fn,
                **{k: v for k, v in t.__dict__.items()
                   if k not in ('name', 'description', 'fn')}
            )
            for t in tools
        ]

    async def get_tool(self, name: str, call_next: GetToolNext) -> Tool | None:
        tool = await call_next(name)
        if tool:
            return Tool(
                name=tool.name,
                description=f"{tool.description} {self.suffix}",
                fn=tool.fn,
            )
        return None
```

### Logging Transform

Log component access:

```python
import logging

class LoggingTransform(Transform):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def get_tool(self, name: str, call_next: GetToolNext) -> Tool | None:
        self.logger.info(f"Tool requested: {name}")
        tool = await call_next(name)
        if tool:
            self.logger.info(f"Tool found: {name}")
        else:
            self.logger.warning(f"Tool not found: {name}")
        return tool
```

### Rate Limiting Transform

```python
from collections import defaultdict
from time import time

class RateLimitTransform(Transform):
    def __init__(self, max_per_minute: int = 60):
        self.max_per_minute = max_per_minute
        self.requests = defaultdict(list)

    def _is_allowed(self, key: str) -> bool:
        now = time()
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < 60]
        if len(self.requests[key]) >= self.max_per_minute:
            return False
        self.requests[key].append(now)
        return True

    async def get_tool(self, name: str, call_next: GetToolNext) -> Tool | None:
        if not self._is_allowed(name):
            raise Exception(f"Rate limit exceeded for tool: {name}")
        return await call_next(name)
```

---

## Transform Composition

### Stacking Transforms

Transforms process in order added:

```python
provider.add_transform(Namespace("api"))      # First: add prefix
provider.add_transform(ToolTransform({...}))  # Second: rename
provider.add_transform(Visibility(...))       # Third: filter
```

Result: `tool` -> `api_tool` -> renamed -> filtered

### Provider + Server Transforms

```python
# Provider-level
provider.add_transform(Namespace("sub"))

# Server-level
mcp.add_transform(Visibility(disable_tags={"internal"}))

# Flow:
# 1. Provider produces "tool"
# 2. Provider transform makes "sub_tool"
# 3. Server transform filters by tags
```

---

## Common Patterns

### Pattern: OpenAPI Curation

Clean up auto-generated OpenAPI tools:

```python
from fastmcp.server.providers.openapi import OpenAPIProvider
from fastmcp.server.transforms import ToolTransform, Visibility

provider = OpenAPIProvider(spec, client)

# Rename verbose auto-generated names
provider.add_transform(ToolTransform({
    "GET_api_v1_users_id": ToolTransformConfig(
        name="get_user",
        description="Get user by ID",
        tags={"user", "read"},
    ),
    "POST_api_v1_users": ToolTransformConfig(
        name="create_user",
        tags={"user", "write"},
    ),
}))

# Hide internal endpoints
provider.add_transform(Visibility(disable_tags={"internal"}))
```

### Pattern: Progressive Disclosure

Reveal tools based on session state:

```python
# Hide premium tools globally
mcp.disable(tags={"premium"})

@mcp.tool
async def unlock_premium(ctx: Context) -> str:
    """Unlock premium features."""
    await ctx.enable_components(tags={"premium"})
    return "Premium unlocked!"
```

### Pattern: Multi-Environment

Same code, different tool sets:

```python
import os

mcp = FastMCP("Server")

if os.environ.get("ENV") == "production":
    mcp.disable(tags={"debug", "dev-only"})
elif os.environ.get("ENV") == "staging":
    mcp.disable(tags={"debug"})
# Development shows everything
```

### Pattern: Tenant Isolation

Namespace tools per tenant:

```python
async def create_tenant_server(tenant_id: str) -> FastMCP:
    mcp = FastMCP(f"Tenant-{tenant_id}")

    provider = TenantToolProvider(tenant_id)
    provider.add_transform(Namespace(tenant_id))

    mcp.add_provider(provider)
    return mcp
```

---

## Best Practices

### 1. Keep Transforms Simple

Each transform should do one thing:

```python
# Good: Separate transforms
provider.add_transform(Namespace("api"))
provider.add_transform(ToolTransform({...}))
provider.add_transform(TagFilter({"public"}))

# Avoid: Complex multi-purpose transform
```

### 2. Order Matters

Consider the transform pipeline:

```python
# Namespace first, then filter
provider.add_transform(Namespace("api"))  # tool -> api_tool
provider.add_transform(TagFilter(...))     # filter api_tool

# vs. Filter first, then namespace
provider.add_transform(TagFilter(...))     # filter tool
provider.add_transform(Namespace("api"))  # filtered -> api_filtered
```

### 3. Handle Both List and Get

Always implement both for consistency:

```python
class MyTransform(Transform):
    async def list_tools(self, tools):
        # Filter/modify list
        return [self._process(t) for t in tools]

    async def get_tool(self, name, call_next):
        tool = await call_next(name)
        return self._process(tool) if tool else None

    def _process(self, tool):
        # Shared processing logic
        ...
```

### 4. Use call_next Correctly

The middleware pattern allows chaining:

```python
async def get_tool(self, name: str, call_next: GetToolNext) -> Tool | None:
    # Pre-processing
    modified_name = self._transform_name(name)

    # Call next in chain
    tool = await call_next(modified_name)

    # Post-processing
    if tool:
        return self._transform_tool(tool)
    return None
```
