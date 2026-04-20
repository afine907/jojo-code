/**
 * TypeScript Client 单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { AgentClient } from "../src/client/rpc.js";
import { spawn } from "child_process";
import path from "path";

// Mock child_process
vi.mock("child_process", () => ({
  spawn: vi.fn(),
}));

// 检查 Python 环境
const PYTHON_PATH = process.env.PYTHON_PATH || "/tmp/nano-code/.venv/bin/python";
const PYTHONPATH = process.env.PYTHONPATH || "/tmp/nano-code/src";
const hasPythonEnv = (() => {
  try {
    // 检查 Python 路径是否存在
    return true; // 在测试中使用 mock
  } catch {
    return false;
  }
})();

describe("AgentClient", () => {
  let client: AgentClient;
  let mockProcess: any;

  beforeEach(() => {
    client = new AgentClient();
    
    mockProcess = {
      stdin: {
        write: vi.fn(),
      },
      stdout: {
        on: vi.fn(),
      },
      stderr: {
        on: vi.fn((event, callback) => {
          if (event === "data") {
            // 模拟服务器启动消息
            setTimeout(() => {
              callback(Buffer.from("Nano Code JSON-RPC Server started\n"));
            }, 10);
          }
        }),
      },
      on: vi.fn(),
      kill: vi.fn(),
    };

    (spawn as any).mockReturnValue(mockProcess);
  });

  afterEach(() => {
    client.close();
    vi.clearAllMocks();
  });

  describe("Connection", () => {
    it("should start with disconnected state", () => {
      expect(client.connectionState).toBe("disconnected");
    });

    it("should connect successfully", async () => {
      const connectPromise = client.connect();
      
      // 触发 stderr 中的启动消息
      const stderrCallback = mockProcess.stderr.on.mock.calls.find(
        (call: any[]) => call[0] === "data"
      )?.[1];
      
      if (stderrCallback) {
        stderrCallback(Buffer.from("Nano Code JSON-RPC Server started\n"));
      }

      await connectPromise;
      expect(client.connectionState).toBe("connected");
    });

    it("should spawn python process with correct args", async () => {
      await client.connect();
      
      // 验证 spawn 被调用
      expect(spawn).toHaveBeenCalled();
      
      // 获取调用参数
      const callArgs = (spawn as any).mock.calls[0];
      expect(callArgs[1]).toEqual(["-m", "nano_code.server.rpc"]);
      expect(callArgs[2].stdio).toEqual(["pipe", "pipe", "pipe"]);
    });
  });

  describe("Request Handling", () => {
    beforeEach(async () => {
      await client.connect();
    });

    it("should send JSON-RPC request", async () => {
      // Mock response
      const requestPromise = client.sendRequest("tools.list");
      
      // 获取 stdout data callback
      const stdoutCallback = mockProcess.stdout.on.mock.calls.find(
        (call: any[]) => call[0] === "data"
      )?.[1];
      
      // 模拟响应
      if (stdoutCallback) {
        const requestId = mockProcess.stdin.write.mock.calls[0][0].match(/"id":"(\d+)"/)?.[1];
        stdoutCallback(Buffer.from(`{"jsonrpc":"2.0","id":"${requestId}","result":{"tools":[]}}\n`));
      }

      const result = await requestPromise;
      expect(result).toEqual({ tools: [] });
    });

    it("should reject on error response", async () => {
      const requestPromise = client.sendRequest("unknown.method");
      
      const stdoutCallback = mockProcess.stdout.on.mock.calls.find(
        (call: any[]) => call[0] === "data"
      )?.[1];
      
      if (stdoutCallback) {
        const requestId = mockProcess.stdin.write.mock.calls[0][0].match(/"id":"(\d+)"/)?.[1];
        stdoutCallback(
          Buffer.from(
            `{"jsonrpc":"2.0","id":"${requestId}","error":{"code":-32601,"message":"Method not found"}}\n`
          )
        );
      }

      await expect(requestPromise).rejects.toThrow("Method not found");
    });

    it("should throw error when not connected", async () => {
      client.close();
      
      await expect(client.sendRequest("tools.list")).rejects.toThrow(
        "Not connected to server"
      );
    });
  });

  describe("Stream Events", () => {
    beforeEach(async () => {
      await client.connect();
    });

    it("should emit stream events", (done) => {
      client.on("stream", (event) => {
        expect(event.type).toBe("response");
        expect(event.content).toBe("hello");
        done();
      });

      // 获取 stdout data callback
      const stdoutCallback = mockProcess.stdout.on.mock.calls.find(
        (call: any[]) => call[0] === "data"
      )?.[1];

      if (stdoutCallback) {
        stdoutCallback(
          Buffer.from('{"jsonrpc":"2.0","method":"stream","params":{"type":"response","content":"hello"}}\n')
        );
      }
    });
  });

  describe("Cleanup", () => {
    it("should kill process on close", async () => {
      await client.connect();
      client.close();

      expect(mockProcess.kill).toHaveBeenCalledWith("SIGTERM");
      expect(client.connectionState).toBe("disconnected");
    });

    it("should clear pending requests on close", async () => {
      await client.connect();
      
      // 发起请求但不响应
      const requestPromise = client.sendRequest("tools.list");
      
      // 立即关闭
      client.close();

      await expect(requestPromise).rejects.toThrow("Connection closed");
    });
  });
});
