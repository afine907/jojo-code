import { useState, useEffect, useCallback } from 'react';
import type { Message, ToolCall } from '../app.js';
import { JsonRpcClient } from '../client/jsonrpc.js';

export interface PermissionRequest {
  tool: string;
  action: string;
  params: Record<string, unknown>;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  reason: string;
}

interface UseAgentReturn {
  messages: Message[];
  isLoading: boolean;
  model: string;
  toolCalls: ToolCall[];
  sessionStats: {
    duration: number;
    totalToolCalls: number;
  };
  permissionRequest: PermissionRequest | null;
  sendMessage: (input: string) => Promise<void>;
  clearHistory: () => void;
  handlePermissionDecision: (decision: 'allow' | 'deny' | 'always') => void;
  getPermissionMode: () => Promise<string>;
  setPermissionMode: (mode: string) => Promise<void>;
}

export function useAgent(): UseAgentReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [model, setModel] = useState('gpt-4o-mini');
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [startTime] = useState(Date.now());
  const [permissionRequest, setPermissionRequest] = useState<PermissionRequest | null>(null);
  
  const client = useState(() => new JsonRpcClient())[0];

  // 获取当前模型
  useEffect(() => {
    client.request<{ model: string }>('get_model', {}).then(result => {
      if (result && result.model) setModel(result.model);
    }).catch(() => {
      // 使用默认模型
    });
  }, [client]);

  const sendMessage = useCallback(async (input: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setToolCalls([]);

    try {
      const result = await client.request<{ content: string }>('chat', { message: input });
      
      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: result?.content || 'No response',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: `msg-${Date.now() + 2}`,
        role: 'assistant',
        content: `❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setToolCalls([]);
    }
  }, [client]);

  const clearHistory = useCallback(() => {
    setMessages([]);
    client.request('clear', {}).catch(() => {});
  }, [client]);

  const handlePermissionDecision = useCallback(async (decision: 'allow' | 'deny' | 'always') => {
    if (!permissionRequest) return;
    
    try {
      await client.permissionConfirm('session', decision !== 'deny');
      
      if (decision === 'always') {
        // 将工具添加到临时允许列表
        console.log(`Always allow ${permissionRequest.tool}`);
      }
    } catch (error) {
      console.error('Permission confirm error:', error);
    } finally {
      setPermissionRequest(null);
    }
  }, [client, permissionRequest]);

  const getPermissionMode = useCallback(async () => {
    return client.getPermissionMode();
  }, [client]);

  const setPermissionMode = useCallback(async (mode: string) => {
    await client.setPermissionMode(mode);
  }, [client]);

  const duration = Math.floor((Date.now() - startTime) / 1000);

  return {
    messages,
    isLoading,
    model,
    toolCalls,
    sessionStats: {
      duration,
      totalToolCalls: messages.reduce(
        (sum, m) => sum + (m.toolCalls?.length || 0),
        0
      ),
    },
    permissionRequest,
    sendMessage,
    clearHistory,
    handlePermissionDecision,
    getPermissionMode,
    setPermissionMode,
  };
}
