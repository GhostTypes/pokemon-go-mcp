/**
 * Vitest Configuration for MCP Server Integration Tests
 * 
 * Copy this file to your project root.
 */

import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Enable global test functions (describe, it, expect)
    globals: true,
    
    // Node environment for MCP server testing
    environment: 'node',
    
    // Timeouts for MCP operations (servers may be slow to start)
    testTimeout: 30000,    // 30 seconds per test
    hookTimeout: 30000,    // 30 seconds for beforeAll/afterAll
    
    // Test file patterns
    include: ['tests/**/*.test.ts', 'tests/**/*.spec.ts'],
    
    // Run tests sequentially to avoid subprocess conflicts
    // This is important for STDIO-based MCP testing
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true,  // Single process to avoid port conflicts
      },
    },
    
    // Reporter options
    reporters: ['verbose'],
    
    // Coverage configuration (optional)
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.spec.ts'],
    },
  },
});
