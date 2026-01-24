---
name: mcp-test-harness
description: Build fully automated integration test suites for MCP (Model Context Protocol) servers using STDIO transport. Use when creating pytest tests for Python/FastMCP servers, Vitest tests for TypeScript servers, or using MCP Inspector CLI for universal testing. Triggers include "test my MCP server", "create MCP tests", "automated MCP testing", "integration tests for MCP", or any request to verify MCP server functionality with real data validation.
---

# MCP Test Harness

Build production-ready, fully automated integration test suites for MCP servers using STDIO transport. Tests run against **live servers** and validate **real data**.

## Quick Start Decision

| Server Language | Testing Stack | Reference |
|-----------------|---------------|-----------|
| Python (FastMCP) | pytest + pytest-asyncio + FastMCP Client | [Python Guide](references/python-fastmcp.md) |
| TypeScript/Node | Vitest + @modelcontextprotocol/sdk | [TypeScript Guide](references/typescript-vitest.md) |
| Any language | MCP Inspector CLI (bash/PowerShell) | [Inspector CLI](references/inspector-cli.md) |

## Core Philosophy

These are **integration tests**, not unit tests:
- Tests run against the **actual MCP server** (not mocks)
- Tests validate **real data** returned from tools
- Tests use **STDIO transport** (the standard for local MCP servers)
- Tests should pass before any deployment or version bump

## Workflow

### Step 1: Gather Requirements

Before writing tests, ask the user for:

1. **Server location**: Path to the MCP server entry point
2. **Server language**: Python (FastMCP) or TypeScript
3. **Tool inventory**: List all tools the server exposes (or discover via Inspector)
4. **For each tool to test**:
   - Example valid inputs
   - Expected output values or patterns to validate
   - Edge cases and known error conditions
   - External dependencies (APIs, databases, files)
5. **Environment requirements**: API keys, config files, setup steps

### Step 2: Choose Testing Approach

**Python/FastMCP** (Recommended for Python servers):
- In-memory testing via `Client(server)` - no subprocess needed
- Fastest, most reliable approach
- Full protocol compliance
- See [references/python-fastmcp.md](references/python-fastmcp.md)

**TypeScript/Vitest** (Recommended for TS servers):
- Subprocess-based via `StdioClientTransport`
- Native TypeScript, excellent DX
- See [references/typescript-vitest.md](references/typescript-vitest.md)

**MCP Inspector CLI** (Universal fallback):
- Works with any language
- Good for quick validation or CI pipelines
- See [references/inspector-cli.md](references/inspector-cli.md)

### Step 3: Implement Tests

Follow the test patterns in [references/test-patterns.md](references/test-patterns.md):

1. **Discovery Tests**: Verify all expected tools appear in `tools/list`
2. **Execution Tests**: Call each tool with valid inputs, validate response data
3. **Validation Tests**: Confirm response structure and content matches expectations
4. **Error Tests**: Verify graceful handling of invalid inputs
5. **Concurrency Tests**: (Optional) Test parallel tool invocations

### Step 4: Run and Iterate

```bash
# Python
pytest tests/ -v --tb=short

# TypeScript  
npx vitest run

# Inspector CLI (any language)
npx @modelcontextprotocol/inspector --cli <server-command> --method tools/list
```

## Windows 11 / Claude Code Notes

When running commands in Claude Code on Windows:

| Unix Command | Windows Equivalent |
|--------------|-------------------|
| `python3` | `python` |
| `pip3` | `pip` |
| `export VAR=value` | `set VAR=value` (cmd) or `$env:VAR="value"` (PowerShell) |
| `./script.sh` | `bash script.sh` (Git Bash) or native PowerShell |
| `which command` | `where command` |
| Path separators `/` | Use `/` in Python/Node, `\` in native Windows commands |

For `npx` and `npm` commands, use them directly - they work cross-platform.

Python virtual environments on Windows:
```powershell
# Create venv
python -m venv .venv

# Activate (PowerShell)
.venv\Scripts\Activate.ps1

# Activate (cmd)
.venv\Scripts\activate.bat

# Activate (Git Bash)
source .venv/Scripts/activate
```

## Test Checklist

Before considering tests complete:

- [ ] All tools from `tools/list` have corresponding tests
- [ ] Each tool tested with at least one valid input
- [ ] Response data validated against expected values (not just "truthy")
- [ ] Error cases tested for each tool
- [ ] Tests run successfully in isolation
- [ ] Tests are deterministic (same result every run)
- [ ] No hardcoded secrets in test files (use environment variables)

## Reference Files

Load these as needed during implementation:

- [Python/FastMCP Testing Guide](references/python-fastmcp.md) - Complete pytest setup and patterns
- [TypeScript/Vitest Testing Guide](references/typescript-vitest.md) - Complete Vitest setup and patterns
- [MCP Inspector CLI Guide](references/inspector-cli.md) - Universal CLI-based testing
- [Universal Test Patterns](references/test-patterns.md) - Language-agnostic testing patterns

## Asset Templates

Copy and customize these starter files:

- `assets/python/` - pyproject.toml snippet, conftest.py, test template
- `assets/typescript/` - vitest.config.ts, package.json snippet, test template
