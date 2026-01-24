# TypeScript/Vitest Testing Guide

Complete guide for testing MCP servers built with the TypeScript SDK using Vitest.

## Overview

Unlike FastMCP's in-memory approach, TypeScript MCP testing uses **subprocess-based transport** via `StdioClientTransport`. The test spawns your server as a child process and communicates via STDIO.

## Project Setup

### 1. Install Dependencies

```bash
npm install -D vitest @vitest/ui @modelcontextprotocol/sdk
```

If using Zod for schema validation (recommended):
```bash
npm install zod
```

### 2. Configure Vitest

Create `vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    testTimeout: 30000, // 30s timeout for MCP operations
    hookTimeout: 30000,
    include: ['tests/**/*.test.ts'],
    // Run tests sequentially to avoid port/process conflicts
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true,
      },
    },
  },
});
```

### 3. Update package.json

```json
{
  "scripts": {
    "build": "tsc",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui"
  },
  "devDependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

### 4. Project Structure

```
your-mcp-server/
├── src/
│   └── index.ts           # MCP server entry point
├── tests/
│   ├── setup.ts           # Shared test utilities
│   └── tools.test.ts      # Tool tests
├── build/                  # Compiled output
├── vitest.config.ts
├── tsconfig.json
└── package.json
```

## Core Testing Pattern

### Basic Test Structure

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

describe('MCP Server Tests', () => {
  let client: Client;
  let transport: StdioClientTransport;

  beforeAll(async () => {
    // Spawn the server as a subprocess
    transport = new StdioClientTransport({
      command: 'node',
      args: ['build/index.js'],
    });

    client = new Client({
      name: 'test-client',
      version: '1.0.0',
    });

    await client.connect(transport);
  });

  afterAll(async () => {
    await client.close();
  });

  it('should list tools', async () => {
    const response = await client.listTools();
    expect(response.tools).toBeDefined();
    expect(response.tools.length).toBeGreaterThan(0);
  });

  it('should call a tool', async () => {
    const result = await client.callTool({
      name: 'add',
      arguments: { a: 5, b: 3 },
    });

    expect(result.content).toBeDefined();
    expect(result.content[0].type).toBe('text');
    expect((result.content[0] as { type: 'text'; text: string }).text).toBe('8');
  });
});
```

## Complete Example

### Server (src/index.ts)

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const server = new McpServer({
  name: 'calculator-server',
  version: '1.0.0',
});

// Register tools
server.tool(
  'add',
  'Add two numbers together',
  {
    a: z.number().describe('First number'),
    b: z.number().describe('Second number'),
  },
  async ({ a, b }) => ({
    content: [{ type: 'text', text: String(a + b) }],
  })
);

server.tool(
  'divide',
  'Divide a by b',
  {
    a: z.number().describe('Dividend'),
    b: z.number().describe('Divisor'),
  },
  async ({ a, b }) => {
    if (b === 0) {
      return {
        content: [{ type: 'text', text: 'Error: Cannot divide by zero' }],
        isError: true,
      };
    }
    return {
      content: [{ type: 'text', text: String(a / b) }],
    };
  }
);

server.tool(
  'greet',
  'Generate a greeting',
  {
    name: z.string().describe('Name to greet'),
    formal: z.boolean().optional().default(false).describe('Use formal greeting'),
  },
  async ({ name, formal }) => ({
    content: [{
      type: 'text',
      text: formal ? `Good day, ${name}.` : `Hey ${name}!`,
    }],
  })
);

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

### Test Utilities (tests/setup.ts)

```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

export interface TestContext {
  client: Client;
  transport: StdioClientTransport;
}

/**
 * Create a connected test client.
 * 
 * @param serverCommand - Command to run the server (e.g., 'node')
 * @param serverArgs - Arguments for the server command (e.g., ['build/index.js'])
 */
export async function createTestClient(
  serverCommand: string = 'node',
  serverArgs: string[] = ['build/index.js']
): Promise<TestContext> {
  const transport = new StdioClientTransport({
    command: serverCommand,
    args: serverArgs,
  });

  const client = new Client({
    name: 'test-client',
    version: '1.0.0',
  });

  await client.connect(transport);

  return { client, transport };
}

/**
 * Extract text content from a tool result.
 */
export function getTextContent(result: Awaited<ReturnType<Client['callTool']>>): string {
  const textContent = result.content.find((c) => c.type === 'text');
  if (!textContent || textContent.type !== 'text') {
    throw new Error('No text content in result');
  }
  return textContent.text;
}

/**
 * Check if result is an error.
 */
export function isErrorResult(result: Awaited<ReturnType<Client['callTool']>>): boolean {
  return result.isError === true;
}
```

### Test File (tests/tools.test.ts)

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { createTestClient, getTextContent, isErrorResult, TestContext } from './setup';

describe('Calculator MCP Server', () => {
  let ctx: TestContext;

  beforeAll(async () => {
    // Build first if needed
    ctx = await createTestClient('node', ['build/index.js']);
  });

  afterAll(async () => {
    await ctx.client.close();
  });

  describe('Tool Discovery', () => {
    it('should list all expected tools', async () => {
      const response = await ctx.client.listTools();
      const toolNames = response.tools.map((t) => t.name);

      expect(toolNames).toContain('add');
      expect(toolNames).toContain('divide');
      expect(toolNames).toContain('greet');
    });

    it('should have correct tool count', async () => {
      const response = await ctx.client.listTools();
      expect(response.tools).toHaveLength(3);
    });

    it('should have descriptions for all tools', async () => {
      const response = await ctx.client.listTools();
      
      for (const tool of response.tools) {
        expect(tool.description).toBeDefined();
        expect(tool.description!.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Add Tool', () => {
    it('should add positive numbers', async () => {
      const result = await ctx.client.callTool({
        name: 'add',
        arguments: { a: 5, b: 3 },
      });

      expect(getTextContent(result)).toBe('8');
    });

    it('should add negative numbers', async () => {
      const result = await ctx.client.callTool({
        name: 'add',
        arguments: { a: -5, b: -3 },
      });

      expect(getTextContent(result)).toBe('-8');
    });

    it('should handle zero', async () => {
      const result = await ctx.client.callTool({
        name: 'add',
        arguments: { a: 0, b: 0 },
      });

      expect(getTextContent(result)).toBe('0');
    });

    it.each([
      { a: 1, b: 2, expected: '3' },
      { a: 10, b: 20, expected: '30' },
      { a: -5, b: 5, expected: '0' },
      { a: 100, b: -50, expected: '50' },
    ])('should compute $a + $b = $expected', async ({ a, b, expected }) => {
      const result = await ctx.client.callTool({
        name: 'add',
        arguments: { a, b },
      });

      expect(getTextContent(result)).toBe(expected);
    });
  });

  describe('Divide Tool', () => {
    it('should divide numbers', async () => {
      const result = await ctx.client.callTool({
        name: 'divide',
        arguments: { a: 10, b: 2 },
      });

      expect(getTextContent(result)).toBe('5');
    });

    it('should handle division by zero', async () => {
      const result = await ctx.client.callTool({
        name: 'divide',
        arguments: { a: 10, b: 0 },
      });

      // Either marked as error or contains error message
      const isError = isErrorResult(result) || 
        getTextContent(result).toLowerCase().includes('error');
      
      expect(isError).toBe(true);
    });

    it('should handle decimal results', async () => {
      const result = await ctx.client.callTool({
        name: 'divide',
        arguments: { a: 5, b: 2 },
      });

      expect(getTextContent(result)).toBe('2.5');
    });
  });

  describe('Greet Tool', () => {
    it('should generate informal greeting by default', async () => {
      const result = await ctx.client.callTool({
        name: 'greet',
        arguments: { name: 'Alice' },
      });

      expect(getTextContent(result)).toBe('Hey Alice!');
    });

    it('should generate formal greeting when requested', async () => {
      const result = await ctx.client.callTool({
        name: 'greet',
        arguments: { name: 'Dr. Smith', formal: true },
      });

      expect(getTextContent(result)).toBe('Good day, Dr. Smith.');
    });

    it('should handle empty name', async () => {
      const result = await ctx.client.callTool({
        name: 'greet',
        arguments: { name: '' },
      });

      // Should still work, just with empty name
      expect(getTextContent(result)).toContain('Hey');
    });
  });
});
```

## Advanced Patterns

### Testing with Environment Variables

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';

describe('Server with Environment Variables', () => {
  let client: Client;

  beforeAll(async () => {
    const transport = new StdioClientTransport({
      command: 'node',
      args: ['build/index.js'],
      env: {
        ...process.env,
        API_KEY: process.env.TEST_API_KEY || 'test-key',
        DEBUG: 'true',
      },
    });

    client = new Client({ name: 'test', version: '1.0.0' });
    await client.connect(transport);
  });

  afterAll(async () => {
    await client.close();
  });

  it('should use environment config', async () => {
    // Test tool that uses env vars
  });
});
```

### Testing TypeScript Server Directly (tsx)

If you want to test without building:

```typescript
beforeAll(async () => {
  const transport = new StdioClientTransport({
    command: 'npx',
    args: ['tsx', 'src/index.ts'],
  });
  // ...
});
```

### Concurrent Tool Calls

```typescript
it('should handle concurrent calls', async () => {
  const promises = Array.from({ length: 10 }, (_, i) =>
    ctx.client.callTool({
      name: 'add',
      arguments: { a: i, b: i },
    })
  );

  const results = await Promise.all(promises);

  expect(results).toHaveLength(10);
  results.forEach((result, i) => {
    expect(getTextContent(result)).toBe(String(i + i));
  });
});
```

### Testing Resources

```typescript
describe('Resources', () => {
  it('should list resources', async () => {
    const response = await ctx.client.listResources();
    
    expect(response.resources).toBeDefined();
    const uris = response.resources.map((r) => r.uri);
    expect(uris).toContain('file://config.json');
  });

  it('should read resource content', async () => {
    const response = await ctx.client.readResource({
      uri: 'file://config.json',
    });

    expect(response.contents).toBeDefined();
    expect(response.contents[0].text).toContain('version');
  });
});
```

### Testing Prompts

```typescript
describe('Prompts', () => {
  it('should list prompts', async () => {
    const response = await ctx.client.listPrompts();
    
    expect(response.prompts).toBeDefined();
    const names = response.prompts.map((p) => p.name);
    expect(names).toContain('summarize');
  });

  it('should get prompt with arguments', async () => {
    const response = await ctx.client.getPrompt({
      name: 'summarize',
      arguments: { text: 'Hello world', style: 'brief' },
    });

    expect(response.messages).toBeDefined();
    expect(response.messages.length).toBeGreaterThan(0);
  });
});
```

## Running Tests

```bash
# Run all tests
npm test

# Run with watch mode
npm run test:watch

# Run with UI
npm run test:ui

# Run specific file
npx vitest run tests/tools.test.ts

# Run specific test
npx vitest run -t "should add positive numbers"

# Run with coverage
npx vitest run --coverage
```

## Windows-Specific Notes

On Windows, ensure:

1. **Build before testing**: Run `npm run build` first
2. **Path separators**: Use forward slashes in test paths
3. **npx commands**: Work the same on Windows
4. **tsx for development**: `npx tsx src/index.ts` works on Windows

```powershell
# Windows PowerShell
npm run build
npm test

# Or with tsx directly
npx vitest run
```

## Troubleshooting

### "Cannot find module" Errors

Ensure the server is built:
```bash
npm run build
```

### Connection Timeout

Increase timeout in `vitest.config.ts`:
```typescript
test: {
  testTimeout: 60000, // 60 seconds
}
```

### "ENOENT" Errors

Check that the command exists:
```bash
# Check node
node --version

# Check built file exists
ls build/index.js
```

### Tests Hang on Windows

Use the `forks` pool with `singleFork`:
```typescript
test: {
  pool: 'forks',
  poolOptions: {
    forks: { singleFork: true },
  },
}
```
