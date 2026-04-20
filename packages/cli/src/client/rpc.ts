/**
 * JSON-RPC Client for Nano Code
 *
 * 通过 stdio 与 Python Server 通信
 */

import { spawn, ChildProcess } from "child_process";
import { EventEmitter } from "events";
import type { StreamEvent, Tool, Config } from "./types.js";

interface JSONRPCRequest {
  jsonrpc: "2.0";
  id: string;
  method: string;
  params?: Record<string, unknown>;
}

interface PendingRequest {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
  timeout: NodeJS.Timeout;
}

export type ConnectionState = "disconnected" | "connecting" | "connected" | "error";

export class AgentClient extends EventEmitter {
  private process: ChildProcess | null = null;
  private requestId = 0;
  private pendingRequests = new Map<string, PendingRequest>();
  private buffer = "";
  private _connectionState: ConnectionState = "disconnected";
  private connectionTimeout = 5000; // 5 seconds
  private requestTimeout = 60000; // 60 seconds

  /**
   * 获取连接状态
   */
  get connectionState(): ConnectionState {
    return this._connectionState;
  }

  /**
   * 连接到 Python Server
   */
  async connect(): Promise<void> {
    if (this._connectionState === "connected") {
      return;
    }

    this._connectionState = "connecting";

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error("Connection timeout"));
        this._connectionState = "error";
        this.process?.kill();
      }, this.connectionTimeout);

      // 启动 Python Server
      this.process = spawn("python", ["-m", "nano_code.server.rpc"], {
        stdio: ["pipe", "pipe", "pipe"],
      });

      // 处理 stdout
      this.process.stdout?.on("data", (data: Buffer) => {
        this.buffer += data.toString();
        this.processBuffer();
      });

      // 处理 stderr (日志)
      this.process.stderr?.on("data", (data: Buffer) => {
        const message = data.toString().trim();
        console.error("[Server]", message);
        
        // 检测服务器就绪
        if (message.includes("started")) {
          clearTimeout(timeoutId);
          this._connectionState = "connected";
          resolve();
        }
      });

      // 处理错误
      this.process.on("error", (error: Error) => {
        clearTimeout(timeoutId);
        this._connectionState = "error";
        this.emit("error", error);
        reject(error);
      });

      // 处理退出
      this.process.on("exit", (code) => {
        this._connectionState = "disconnected";
        this.emit("disconnected", code);
        if (code !== 0 && code !== null) {
          console.error(`Server exited with code ${code}`);
        }
      });
    });
  }

  /**
   * 处理响应缓冲区
   */
  private processBuffer(): void {
    const lines = this.buffer.split("\n");
    this.buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const response = JSON.parse(line);

        // 流式通知
        if (response.method === "stream") {
          this.emit("stream", response.params as StreamEvent);
        }
        // 请求响应
        else if (response.id) {
          const pending = this.pendingRequests.get(response.id);
          if (pending) {
            clearTimeout(pending.timeout);
            this.pendingRequests.delete(response.id);
            if (response.error) {
              pending.reject(new Error(response.error.message));
            } else {
              pending.resolve(response.result);
            }
          }
        }
      } catch (e) {
        // 记录解析错误
        console.error("[Client] Failed to parse response:", line, e);
      }
    }
  }

  /**
   * 发送 JSON-RPC 请求
   */
  async sendRequest<T = unknown>(
    method: string,
    params: Record<string, unknown> = {}
  ): Promise<T> {
    if (this._connectionState !== "connected") {
      throw new Error("Not connected to server");
    }

    return new Promise((resolve, reject) => {
      const id = String(++this.requestId);
      const request: JSONRPCRequest = {
        jsonrpc: "2.0",
        id,
        method,
        params,
      };

      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, this.requestTimeout);

      this.pendingRequests.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
        timeout,
      });

      this.process?.stdin?.write(JSON.stringify(request) + "\n");
    });
  }

  /**
   * 流式对话
   */
  async stream(prompt: string, mode: "build" | "plan" = "build"): Promise<void> {
    await this.sendRequest("agent.stream", { prompt, mode });
  }

  /**
   * 获取工具列表
   */
  async getTools(): Promise<Tool[]> {
    const result = await this.sendRequest<{ tools: Tool[] }>("tools.list");
    return result.tools;
  }

  /**
   * 执行工具
   */
  async executeTool(name: string, args: Record<string, unknown>): Promise<string> {
    const result = await this.sendRequest<
      { success: boolean; result?: string; error?: string }
    >("tool.execute", { name, args });
    if (!result.success) {
      throw new Error(result.error || "Tool execution failed");
    }
    return result.result || "";
  }

  /**
   * 获取配置
   */
  async getConfig(): Promise<Config> {
    return this.sendRequest<Config>("config.get");
  }

  /**
   * 设置配置
   */
  async setConfig(config: Partial<Config>): Promise<void> {
    await this.sendRequest("config.set", config);
  }

  /**
   * 关闭连接
   */
  close(): void {
    // 清理所有 pending 请求
    for (const [id, pending] of this.pendingRequests) {
      clearTimeout(pending.timeout);
      pending.reject(new Error("Connection closed"));
    }
    this.pendingRequests.clear();
    
    // 清理 buffer
    this.buffer = "";
    
    // 终止进程
    if (this.process) {
      this.process.kill("SIGTERM");
      this.process = null;
    }
    
    this._connectionState = "disconnected";
    this.removeAllListeners();
  }
}
