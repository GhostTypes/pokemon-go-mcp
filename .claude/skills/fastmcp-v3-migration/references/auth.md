# FastMCP v3 Authorization Reference

Complete guide to the Authorization system in FastMCP 3.0.

## Overview

FastMCP v3 introduces granular per-component authorization:

- **Component-level**: Apply auth to individual tools, resources, prompts
- **Server-level**: Apply auth across all components via middleware
- **Custom checks**: Create your own authorization logic

**Important**: STDIO transport bypasses all auth (no OAuth concept).

---

## Component-Level Authorization

### Basic Auth Requirement

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_auth

mcp = FastMCP()

@mcp.tool(auth=require_auth)
def protected_tool() -> str:
    """Requires any valid token."""
    return "You are authenticated!"
```

### Scope Requirements

```python
from fastmcp.server.auth import require_scopes

@mcp.tool(auth=require_scopes("read"))
def read_data() -> dict:
    """Requires 'read' scope."""
    return {"data": "sensitive"}

@mcp.tool(auth=require_scopes("write"))
def write_data(value: str) -> str:
    """Requires 'write' scope."""
    return f"Wrote: {value}"

@mcp.tool(auth=require_scopes("admin", "write"))
def admin_write(value: str) -> str:
    """Requires both 'admin' AND 'write' scopes."""
    return f"Admin wrote: {value}"
```

### Multiple Auth Checks

```python
@mcp.tool(auth=[require_auth, require_scopes("admin")])
def admin_only() -> str:
    """Multiple checks - all must pass."""
    return "Admin access granted"
```

### Resources and Prompts

```python
@mcp.resource("data://secret", auth=require_scopes("read"))
def secret_data() -> dict:
    return {"secret": "value"}

@mcp.prompt(auth=require_scopes("admin"))
def admin_prompt() -> str:
    return "Admin-only prompt template"
```

---

## Built-in Auth Checks

### require_auth

Requires any valid token (simplest check):

```python
from fastmcp.server.auth import require_auth

@mcp.tool(auth=require_auth)
def authenticated_tool() -> str:
    return "Token is valid!"
```

### require_scopes

Requires specific OAuth scopes:

```python
from fastmcp.server.auth import require_scopes

# Single scope
@mcp.tool(auth=require_scopes("read"))
def read_only() -> str: ...

# Multiple scopes (all required)
@mcp.tool(auth=require_scopes("read", "write"))
def read_write() -> str: ...
```

### restrict_tag

Requires scopes only for tagged components:

```python
from fastmcp.server.auth import restrict_tag
from fastmcp.server.middleware import AuthMiddleware

# Only components with "admin" tag require "admin" scope
mcp = FastMCP(middleware=[
    AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"]))
])

@mcp.tool(tags={"admin"})
def admin_tool() -> str:
    """Requires admin scope due to tag."""
    return "Admin only"

@mcp.tool
def public_tool() -> str:
    """No auth required - no admin tag."""
    return "Public access"
```

---

## Server-Wide Authorization

### AuthMiddleware

Apply auth to all components:

```python
from fastmcp import FastMCP
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.auth import require_auth, require_scopes, restrict_tag

# Require auth for ALL components
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_auth)])

# Require specific scopes for all
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_scopes("api"))])

# Tag-based restrictions
mcp = FastMCP(middleware=[
    AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"]))
])
```

### Combining Middleware and Component Auth

```python
from fastmcp import FastMCP
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.auth import require_auth, require_scopes

# Server requires basic auth for all
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_auth)])

# This tool requires additional "admin" scope
@mcp.tool(auth=require_scopes("admin"))
def admin_tool() -> str:
    """Requires auth (from middleware) AND admin scope."""
    return "Admin access"

# This tool only requires basic auth (from middleware)
@mcp.tool
def regular_tool() -> str:
    """Only requires basic auth."""
    return "Regular access"
```

---

## Custom Auth Checks

### AuthContext

Custom checks receive `AuthContext`:

```python
from fastmcp.server.auth import AuthContext

# AuthContext attributes:
# - token: The access token (or None)
# - component: The component being accessed
# - scopes: Set of scopes from token
```

### Simple Custom Check

```python
from fastmcp.server.auth import AuthContext

def is_admin(ctx: AuthContext) -> bool:
    """Check if user has admin scope."""
    return ctx.token is not None and "admin" in ctx.token.scopes

@mcp.tool(auth=is_admin)
def admin_only() -> str:
    return "Admin access"
```

### Check with Component Info

```python
def can_access_component(ctx: AuthContext) -> bool:
    """Check based on component metadata."""
    if ctx.token is None:
        return False

    component = ctx.component
    required_level = component.meta.get("access_level", "user")
    user_level = ctx.token.claims.get("level", "user")
    levels = ["user", "power", "admin"]

    return levels.index(user_level) >= levels.index(required_level)

@mcp.tool(auth=can_access_component, meta={"access_level": "power"})
def power_user_tool() -> str:
    return "Power user access"
```

### Async Custom Check

```python
async def check_user_status(ctx: AuthContext) -> bool:
    """Async check against external service."""
    if ctx.token is None:
        return False

    user_id = ctx.token.claims.get("sub")
    status = await user_service.get_status(user_id)
    return status == "active"

@mcp.tool(auth=check_user_status)
def active_users_only() -> str:
    return "Active user access"
```

---

## OAuth Provider Configuration

### v3 Breaking Change

Auth providers no longer auto-load from environment:

```python
# v2.x (auto-loaded from env)
from fastmcp.server.auth import GitHubProvider
auth = GitHubProvider()  # Read GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

# v3.0 (explicit configuration)
import os
from fastmcp.server.auth import GitHubProvider

auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
)
```

### Production OAuth Configuration

```python
from fastmcp.server.auth import GitHubProvider
from key_value.aio.stores.redis import RedisStore

auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
    base_url="https://your-server.com",
    jwt_signing_key=os.environ["JWT_SIGNING_KEY"],
    client_storage=RedisStore(host="redis.example.com"),
)
```

---

## Best Practices

### 1. Defense in Depth

Layer auth at multiple levels:

```python
# Server-wide: require authentication
mcp = FastMCP(middleware=[AuthMiddleware(auth=require_auth)])

# Sensitive tools: require additional scopes
@mcp.tool(auth=require_scopes("admin"))
def admin_tool(): ...
```

### 2. Use Tags for Grouping

```python
mcp = FastMCP(middleware=[
    AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"])),
])

@mcp.tool(tags={"admin"})
def admin_tool(): ...
```

### 3. Fail Securely

```python
def secure_check(ctx: AuthContext) -> bool:
    """Fail closed on any error."""
    try:
        if ctx.token is None:
            return False
        return validate_token(ctx.token)
    except Exception:
        return False  # Deny on error
```

### 4. Test Auth Thoroughly

```python
import pytest
from fastmcp.client import Client

async def test_protected_tool_without_auth(client):
    with pytest.raises(AuthorizationError):
        await client.call_tool("protected_tool", {})
```
