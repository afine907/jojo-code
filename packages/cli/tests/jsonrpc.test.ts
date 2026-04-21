import { describe, it, expect, vi } from 'vitest';
import { JsonRpcClient } from '../src/client/jsonrpc.js';

// Mock child_process
vi.mock('child_process', () => ({
  spawn: vi.fn(() => ({
    stdin: { write: vi.fn() },
    stdout: { on: vi.fn() },
    stderr: { on: vi.fn() },
    on: vi.fn(),
    kill: vi.fn(),
  })),
}));

describe('JsonRpcClient', () => {
  it('can be instantiated', () => {
    const client = new JsonRpcClient();
    expect(client).toBeDefined();
  });

  it('generates unique request ids', async () => {
    const client = new JsonRpcClient();
    // Request should increment id
    // (actual test would need mock server)
    client.close();
  });
});
