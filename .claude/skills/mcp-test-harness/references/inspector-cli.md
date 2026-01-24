# MCP Inspector CLI Guide

Use the official MCP Inspector CLI for testing any MCP server, regardless of implementation language.

## Overview

The MCP Inspector is Anthropic's official testing tool. Its CLI mode enables:
- Programmatic interaction with any MCP server
- Quick validation without writing test code
- Integration with shell scripts and CI pipelines
- Universal compatibility (works with Python, TypeScript, Rust, etc.)

## Installation

```bash
# Global install (recommended for CLI use)
npm install -g @modelcontextprotocol/inspector

# Or run directly with npx (no install needed)
npx @modelcontextprotocol/inspector --cli <command>
```

## Basic Usage

### List Available Tools

```bash
# Python server
npx @modelcontextprotocol/inspector --cli python server.py --method tools/list

# Node.js server
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list

# With uv (Python)
npx @modelcontextprotocol/inspector --cli uv run python server.py --method tools/list
```

### Call a Tool

```bash
# Basic tool call
npx @modelcontextprotocol/inspector --cli node build/index.js \
    --method tools/call \
    --tool-name add \
    --tool-arg a=5 \
    --tool-arg b=3

# With JSON arguments
npx @modelcontextprotocol/inspector --cli node build/index.js \
    --method tools/call \
    --tool-name search \
    --tool-arg 'options={"limit": 10, "sort": "date"}'
```

### List Resources

```bash
npx @modelcontextprotocol/inspector --cli node build/index.js --method resources/list
```

### List Prompts

```bash
npx @modelcontextprotocol/inspector --cli node build/index.js --method prompts/list
```

## Windows-Specific Commands

On Windows (PowerShell or cmd), the commands work the same. For Git Bash:

```bash
# Git Bash on Windows - same syntax
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list

# PowerShell with Python
npx @modelcontextprotocol/inspector --cli python server.py --method tools/list

# PowerShell - escape JSON properly
npx @modelcontextprotocol/inspector --cli node build/index.js `
    --method tools/call `
    --tool-name search `
    --tool-arg 'query={"term": "test"}'
```

## Configuration Files

Create a config file for complex setups:

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "node",
      "args": ["build/index.js"],
      "env": {
        "API_KEY": "test-key",
        "DEBUG": "true"
      }
    }
  }
}
```

Use with:
```bash
npx @modelcontextprotocol/inspector --cli --config mcp.json --server my-server --method tools/list
```

## Scripted Testing

### Bash Script (Linux/macOS/Git Bash)

```bash
#!/bin/bash
# test-mcp-server.sh

SERVER_CMD="node build/index.js"
INSPECTOR="npx @modelcontextprotocol/inspector --cli"

echo "=== Testing MCP Server ==="

# Test 1: Tool discovery
echo -e "\n[TEST 1] Listing tools..."
TOOLS=$($INSPECTOR $SERVER_CMD --method tools/list 2>&1)
if echo "$TOOLS" | grep -q "add"; then
    echo "✓ Tool 'add' found"
else
    echo "✗ Tool 'add' not found"
    exit 1
fi

# Test 2: Tool execution
echo -e "\n[TEST 2] Testing add tool..."
RESULT=$($INSPECTOR $SERVER_CMD \
    --method tools/call \
    --tool-name add \
    --tool-arg a=5 \
    --tool-arg b=3 2>&1)

if echo "$RESULT" | grep -q "8"; then
    echo "✓ add(5, 3) = 8"
else
    echo "✗ add(5, 3) failed"
    echo "Result: $RESULT"
    exit 1
fi

# Test 3: Error handling
echo -e "\n[TEST 3] Testing error handling..."
RESULT=$($INSPECTOR $SERVER_CMD \
    --method tools/call \
    --tool-name divide \
    --tool-arg a=10 \
    --tool-arg b=0 2>&1)

if echo "$RESULT" | grep -qi "error\|zero"; then
    echo "✓ Division by zero handled"
else
    echo "✗ Error handling failed"
    exit 1
fi

echo -e "\n=== All tests passed ==="
```

### PowerShell Script (Windows)

```powershell
# test-mcp-server.ps1

$ServerCmd = "node build/index.js"
$Inspector = "npx @modelcontextprotocol/inspector --cli"

Write-Host "=== Testing MCP Server ===" -ForegroundColor Cyan

# Test 1: Tool discovery
Write-Host "`n[TEST 1] Listing tools..." -ForegroundColor Yellow
$Tools = Invoke-Expression "$Inspector $ServerCmd --method tools/list" 2>&1

if ($Tools -match "add") {
    Write-Host "✓ Tool 'add' found" -ForegroundColor Green
} else {
    Write-Host "✗ Tool 'add' not found" -ForegroundColor Red
    exit 1
}

# Test 2: Tool execution
Write-Host "`n[TEST 2] Testing add tool..." -ForegroundColor Yellow
$Result = Invoke-Expression @"
$Inspector $ServerCmd --method tools/call --tool-name add --tool-arg a=5 --tool-arg b=3
"@ 2>&1

if ($Result -match "8") {
    Write-Host "✓ add(5, 3) = 8" -ForegroundColor Green
} else {
    Write-Host "✗ add(5, 3) failed" -ForegroundColor Red
    Write-Host "Result: $Result"
    exit 1
}

# Test 3: Error handling
Write-Host "`n[TEST 3] Testing error handling..." -ForegroundColor Yellow
$Result = Invoke-Expression @"
$Inspector $ServerCmd --method tools/call --tool-name divide --tool-arg a=10 --tool-arg b=0
"@ 2>&1

if ($Result -match "error|zero") {
    Write-Host "✓ Division by zero handled" -ForegroundColor Green
} else {
    Write-Host "✗ Error handling failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== All tests passed ===" -ForegroundColor Cyan
```

## JSON Output Parsing

The Inspector outputs JSON that can be parsed:

### With jq (Unix)

```bash
# Extract tool names
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list \
    | jq -r '.tools[].name'

# Check specific tool exists
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list \
    | jq -e '.tools[] | select(.name == "add")' > /dev/null && echo "Found"
```

### With PowerShell

```powershell
# Extract tool names
$result = npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list | ConvertFrom-Json
$result.tools.name

# Check specific tool exists
$tools = npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list | ConvertFrom-Json
if ($tools.tools.name -contains "add") {
    Write-Host "Found"
}
```

## Integration with Test Runners

### With pytest (Python wrapper)

```python
# test_mcp_inspector.py
import subprocess
import json
import pytest


def run_inspector(method: str, **kwargs) -> dict:
    """Run MCP Inspector CLI and return parsed JSON."""
    cmd = [
        "npx", "@modelcontextprotocol/inspector", "--cli",
        "node", "build/index.js",
        "--method", method,
    ]
    
    for key, value in kwargs.items():
        if key == "tool_name":
            cmd.extend(["--tool-name", value])
        elif key == "tool_args":
            for arg_key, arg_value in value.items():
                cmd.extend(["--tool-arg", f"{arg_key}={arg_value}"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse JSON from output
    for line in result.stdout.split('\n'):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    
    raise ValueError(f"No JSON in output: {result.stdout}")


class TestMCPServer:
    def test_list_tools(self):
        result = run_inspector("tools/list")
        tool_names = [t["name"] for t in result["tools"]]
        assert "add" in tool_names

    def test_add_tool(self):
        result = run_inspector(
            "tools/call",
            tool_name="add",
            tool_args={"a": 5, "b": 3}
        )
        assert result["content"][0]["text"] == "8"
```

### With Vitest (TypeScript wrapper)

```typescript
// tests/inspector.test.ts
import { describe, it, expect } from 'vitest';
import { execSync } from 'child_process';

function runInspector(method: string, options: {
  toolName?: string;
  toolArgs?: Record<string, string | number>;
} = {}): unknown {
  const args = [
    'npx', '@modelcontextprotocol/inspector', '--cli',
    'node', 'build/index.js',
    '--method', method,
  ];

  if (options.toolName) {
    args.push('--tool-name', options.toolName);
  }

  if (options.toolArgs) {
    for (const [key, value] of Object.entries(options.toolArgs)) {
      args.push('--tool-arg', `${key}=${value}`);
    }
  }

  const result = execSync(args.join(' '), { encoding: 'utf-8' });
  
  // Parse JSON from output
  for (const line of result.split('\n')) {
    try {
      return JSON.parse(line);
    } catch {
      continue;
    }
  }
  
  throw new Error(`No JSON in output: ${result}`);
}

describe('MCP Server via Inspector', () => {
  it('should list tools', () => {
    const result = runInspector('tools/list') as { tools: Array<{ name: string }> };
    const toolNames = result.tools.map((t) => t.name);
    expect(toolNames).toContain('add');
  });

  it('should execute add tool', () => {
    const result = runInspector('tools/call', {
      toolName: 'add',
      toolArgs: { a: 5, b: 3 },
    }) as { content: Array<{ text: string }> };
    
    expect(result.content[0].text).toBe('8');
  });
});
```

## Available Methods

| Method | Description |
|--------|-------------|
| `tools/list` | List all available tools |
| `tools/call` | Call a specific tool |
| `resources/list` | List all resources |
| `resources/read` | Read a specific resource |
| `prompts/list` | List all prompts |
| `prompts/get` | Get a specific prompt |

## CLI Options Reference

```
Options:
  --cli                    Enable CLI mode
  --config <path>          Path to config file
  --server <name>          Server name from config
  --method <method>        MCP method to call
  --tool-name <name>       Tool name for tools/call
  --tool-arg <key=value>   Tool argument (can be repeated)
  --transport <type>       Transport type (stdio, sse, http)
  --header <key:value>     HTTP header (can be repeated)
```

## Troubleshooting

### "Command not found" Errors

Ensure Node.js and npm are installed:
```bash
node --version
npm --version
```

### Timeout Errors

The inspector has default timeouts. For slow operations:
```bash
# Set timeout via environment
MCP_SERVER_REQUEST_TIMEOUT=60000 npx @modelcontextprotocol/inspector --cli ...
```

### JSON Parse Errors

The CLI may output non-JSON text (logs, errors). Filter for JSON:
```bash
# Only get JSON lines
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list 2>/dev/null \
    | grep '^{' | head -1
```

### Windows Path Issues

Use forward slashes even on Windows:
```bash
# Good
npx @modelcontextprotocol/inspector --cli node build/index.js

# May have issues
npx @modelcontextprotocol/inspector --cli node build\index.js
```
