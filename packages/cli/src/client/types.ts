// JSON-RPC 类型定义

export interface JsonRpcRequest {
  jsonrpc: '2.0';
  id: string | number;
  method: string;
  params?: Record<string, unknown>;
}

export interface JsonRpcResponse<T = unknown> {
  jsonrpc: '2.0';
  id: string | number;
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export interface JsonRpcNotification {
  jsonrpc: '2.0';
  method: string;
  params?: Record<string, unknown>;
}

// Agent 相关类型

export interface AgentState {
  messages: AgentMessage[];
  current_tool_calls: ToolCallInfo[];
  iteration_count: number;
  max_iterations: number;
  mode: 'plan' | 'build';
}

export interface AgentMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: ToolCallInfo[];
}

export interface ToolCallInfo {
  id: string;
  name: string;
  args: Record<string, unknown>;
  result?: string;
}

// 流式响应类型

export type StreamChunk = 
  | { type: 'content'; text: string }
  | { type: 'tool_call'; tool_name: string; args: Record<string, unknown> }
  | { type: 'tool_result'; tool_name: string; result: string }
  | { type: 'thinking'; text: string }
  | { type: 'done' }
  | { type: 'error'; message: string };
