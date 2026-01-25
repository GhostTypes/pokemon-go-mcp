---
name: mcp-setup
description: Set up MCP (Model Context Protocol) servers in Claude Code workspaces for testing. Use this skill when a user provides a local file path to an MCP server, a GitHub repository URL containing an MCP server, or asks to configure/install/set up an MCP server for testing. Handles creating .mcp.json configuration, cloning repositories, and guiding users through the setup process.
---

# MCP Server Setup Skill

Set up MCP servers in the current workspace for testing with Claude Code.

## Workflow

### 1. Identify the Source

Determine what the user has provided:

- **Local path**: A file path pointing to an existing MCP server on their system (e.g., `/home/user/my-mcp-server`, `./my-server`)
- **GitHub repo**: A repository URL (e.g., `https://github.com/user/mcp-server`, `github.com/user/mcp-server`)
- **npm package**: A package name to run via npx (e.g., `@modelcontextprotocol/server-filesystem`)

### 2. Prepare the Server

**For local paths:**
- Verify the path exists and identify the server type (Node.js, Python, etc.)
- Check for `package.json` (Node.js) or Python entry point

**For GitHub repos:**
- Ask the user where to clone: "Where would you like me to clone this repository? (e.g., `/home/claude/mcp-servers/` or a specific path)"
- Clone the repository to the specified location
- Install dependencies (`npm install`, `pip install -r requirements.txt`, etc.)

**For npm packages:**
- Use directly via npx in the configuration

### 3. Determine Server Configuration

Inspect the server to determine how to run it:

| Server Type | Command | Args Example |
|-------------|---------|--------------|
| Node.js (npm package) | `npx` | `["-y", "@package/name"]` |
| Node.js (local) | `node` | `["path/to/server.js"]` |
| TypeScript (local) | `npx` | `["tsx", "path/to/server.ts"]` |
| Python | `python` or `python3` | `["path/to/server.py"]` |
| Binary/Executable | Direct path | `["--flag", "value"]` |

Check for:
- `package.json` → look for `"main"`, `"bin"`, or scripts
- `*.py` entry point → usually `server.py`, `main.py`, or `__main__.py`
- README for run instructions
- Environment variables required (check `.env.example`, README, or code)

### 4. Create .mcp.json

Create or update `.mcp.json` in the **project root** (current working directory):

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["/absolute/path/to/server.js"],
      "env": {
        "API_KEY": "${API_KEY}",
        "DEBUG": "true"
      }
    }
  }
}
```

**Configuration rules:**
- Use **absolute paths** for reliability
- `command`: The executable to run
- `args`: Array of command-line arguments
- `env`: Environment variables (supports `${VAR}` and `${VAR:-default}` expansion)
- Server name should be descriptive and lowercase (e.g., `my-api-server`, `github-tools`)

**If .mcp.json already exists:**
- Read existing content
- Merge new server into `mcpServers` object
- Preserve existing server configurations

### 5. Remind User to Restart

After setup, always inform the user:

> **Important:** Claude Code must be restarted for the MCP server to load. Please restart your Claude Code session (close and reopen, or use the restart command) to activate the new MCP server. After restarting, you can verify the server is loaded by using `/mcp` command.

## Common Patterns

### Node.js server from local path
```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/home/user/my-mcp-server/dist/index.js"],
      "env": {}
    }
  }
}
```

### TypeScript server (uncompiled)
```json
{
  "mcpServers": {
    "my-ts-server": {
      "command": "npx",
      "args": ["tsx", "/home/user/my-mcp-server/src/index.ts"],
      "env": {}
    }
  }
}
```

### Python server
```json
{
  "mcpServers": {
    "python-server": {
      "command": "python3",
      "args": ["/home/user/mcp-server/server.py"],
      "env": {
        "PYTHONPATH": "/home/user/mcp-server"
      }
    }
  }
}
```

### npm package via npx
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
      "env": {}
    }
  }
}
```

## Troubleshooting Guidance

If the user reports issues after restart:
- **"Connection closed" errors**: Check command path, ensure dependencies installed
- **Server not appearing**: Verify .mcp.json is in project root and syntax is valid
- **Permission errors**: Check file permissions on server executable
- **Missing dependencies**: Run `npm install` or `pip install` in server directory

Suggest running `/mcp` after restart to check server status.
