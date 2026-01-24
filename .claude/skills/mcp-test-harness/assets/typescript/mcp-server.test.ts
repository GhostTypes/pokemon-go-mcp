/**
 * MCP Server Integration Tests Template
 * 
 * Copy this file to your tests/ directory and customize:
 * 1. Update the server command/args
 * 2. Update tool names and expected behaviors
 * 3. Replace placeholder assertions with real validations
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

// ============================================================
// Test Utilities
// ============================================================

interface TestContext {
  client: Client;
  transport: StdioClientTransport;
}

/**
 * Extract text content from a tool result.
 */
function getTextContent(result: Awaited<ReturnType<Client['callTool']>>): string {
  const textContent = result.content.find((c) => c.type === 'text');
  if (!textContent || textContent.type !== 'text') {
    throw new Error('No text content in result');
  }
  return textContent.text;
}

/**
 * Check if result indicates an error.
 */
function isError(result: Awaited<ReturnType<Client['callTool']>>): boolean {
  return result.isError === true;
}

// ============================================================
// Configuration - UPDATE THESE FOR YOUR SERVER
// ============================================================

// TODO: Update to match your server's entry point
const SERVER_COMMAND = 'node';
const SERVER_ARGS = ['build/index.js'];

// TODO: List your expected tools
const EXPECTED_TOOLS = [
  'example_tool_1',
  'example_tool_2',
];

// ============================================================
// Tests
// ============================================================

describe('MCP Server Integration Tests', () => {
  let ctx: TestContext;

  beforeAll(async () => {
    const transport = new StdioClientTransport({
      command: SERVER_COMMAND,
      args: SERVER_ARGS,
      // Uncomment to pass environment variables:
      // env: {
      //   ...process.env,
      //   API_KEY: process.env.TEST_API_KEY,
      // },
    });

    const client = new Client({
      name: 'test-client',
      version: '1.0.0',
    });

    await client.connect(transport);
    ctx = { client, transport };
  });

  afterAll(async () => {
    await ctx.client.close();
  });

  // --------------------------------------------------------
  // Tool Discovery Tests
  // --------------------------------------------------------

  describe('Tool Discovery', () => {
    it('should list all expected tools', async () => {
      const response = await ctx.client.listTools();
      const toolNames = response.tools.map((t) => t.name);

      for (const expected of EXPECTED_TOOLS) {
        expect(toolNames).toContain(expected);
      }
    });

    it('should have descriptions for all tools', async () => {
      const response = await ctx.client.listTools();

      for (const tool of response.tools) {
        expect(tool.description).toBeDefined();
        expect(tool.description!.length).toBeGreaterThan(5);
      }
    });

    it('should have input schemas for all tools', async () => {
      const response = await ctx.client.listTools();

      for (const tool of response.tools) {
        expect(tool.inputSchema).toBeDefined();
      }
    });
  });

  // --------------------------------------------------------
  // Example Tool Tests - UPDATE FOR YOUR TOOLS
  // --------------------------------------------------------

  describe('example_tool_1', () => {
    it('should execute with valid input', async () => {
      const result = await ctx.client.callTool({
        name: 'example_tool_1',
        arguments: {
          // TODO: Add your tool's expected arguments
          param1: 'value1',
        },
      });

      expect(isError(result)).toBe(false);
      
      // TODO: Update assertion to match expected output
      const text = getTextContent(result);
      expect(text).toBeDefined();
      // expect(text).toBe('expected_output');
    });

    it('should handle missing required parameters', async () => {
      const result = await ctx.client.callTool({
        name: 'example_tool_1',
        arguments: {},  // Missing required params
      });

      // Should indicate an error
      const hasError = isError(result) || 
        getTextContent(result).toLowerCase().includes('error');
      expect(hasError).toBe(true);
    });

    // Parametrized tests for various inputs
    it.each([
      // TODO: Add test cases: { input: {...}, expected: 'output' }
      { input: { param1: 'input1' }, expected: 'output1' },
      { input: { param1: 'input2' }, expected: 'output2' },
    ])('should return $expected for input $input', async ({ input, expected }) => {
      const result = await ctx.client.callTool({
        name: 'example_tool_1',
        arguments: input,
      });

      expect(getTextContent(result)).toBe(expected);
    });
  });

  // --------------------------------------------------------
  // Error Handling Tests
  // --------------------------------------------------------

  describe('Error Handling', () => {
    it('should handle non-existent tool gracefully', async () => {
      const result = await ctx.client.callTool({
        name: 'nonexistent_tool_xyz',
        arguments: {},
      });

      expect(isError(result)).toBe(true);
    });

    it('should provide actionable error messages', async () => {
      // TODO: Trigger an error in one of your tools
      const result = await ctx.client.callTool({
        name: 'example_tool_1',
        arguments: { param1: 'invalid_value_causing_error' },
      });

      if (isError(result)) {
        const errorText = getTextContent(result);
        // Error should be descriptive
        expect(errorText.length).toBeGreaterThan(10);
      }
    });
  });

  // --------------------------------------------------------
  // Resource Tests (if applicable)
  // --------------------------------------------------------

  describe('Resources', () => {
    it.skip('should list resources', async () => {
      // TODO: Remove .skip if your server exposes resources
      const response = await ctx.client.listResources();
      expect(response.resources).toBeDefined();
      
      // TODO: Check for expected resources
      // const uris = response.resources.map(r => r.uri);
      // expect(uris).toContain('file://config.json');
    });
  });

  // --------------------------------------------------------
  // Prompt Tests (if applicable)
  // --------------------------------------------------------

  describe('Prompts', () => {
    it.skip('should list prompts', async () => {
      // TODO: Remove .skip if your server exposes prompts
      const response = await ctx.client.listPrompts();
      expect(response.prompts).toBeDefined();
      
      // TODO: Check for expected prompts
      // const names = response.prompts.map(p => p.name);
      // expect(names).toContain('summarize');
    });
  });
});
