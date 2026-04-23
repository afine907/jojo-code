import React, { useState, useCallback } from 'react';
import { Box, Text, useApp } from 'ink';
import { ChatView } from './components/ChatView.js';
import { InputBox } from './components/InputBox.js';
import { PermissionRequest } from './components/PermissionRequest.js';
import { useAgent } from './hooks/useAgent.js';

export type Mode = 'plan' | 'build';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: string;
}

export function App() {
  const { exit } = useApp();
  const [mode, setMode] = useState<Mode>('build');
  
  const {
    messages,
    isLoading,
    model,
    toolCalls,
    permissionRequest,
    sendMessage,
    clearHistory,
    handlePermissionDecision,
    getPermissionMode,
    setPermissionMode,
  } = useAgent();

  const handleSubmit = useCallback(async (input: string) => {
    if (input.startsWith('/')) {
      handleCommand(input);
      return;
    }
    await sendMessage(input);
  }, [sendMessage]);

  const handleCommand = (cmd: string) => {
    const parts = cmd.trim().split(/\s+/);
    const command = parts[0].toLowerCase();
    
    switch (command) {
      case '/help':
        console.log(`
可用命令:
  /mode [plan|build]  - 切换模式 (默认: build)
  /permission [mode]  - 查看/设置权限模式 (yolo|auto_approve|interactive|strict|readonly)
  /audit              - 查看最近审计日志
  /clear              - 清空对话
  /exit, /quit        - 退出
        `);
        break;
      case '/clear':
        clearHistory();
        break;
      case '/mode':
        if (parts[1]) {
          setMode(parts[1] === 'plan' ? 'plan' : 'build');
        } else {
          setMode(m => m === 'plan' ? 'build' : 'plan');
        }
        break;
      case '/permission':
        if (parts[1]) {
          setPermissionMode(parts[1]).then(() => {
            console.log(`权限模式已切换为: ${parts[1]}`);
          }).catch((err) => {
            console.log(`设置失败: ${err.message}`);
          });
        } else {
          getPermissionMode().then((mode) => {
            console.log(`当前权限模式: ${mode}`);
          }).catch(() => {
            console.log('获取权限模式失败');
          });
        }
        break;
      case '/audit':
        // TODO: 显示审计日志
        console.log('审计日志功能开发中...');
        break;
      case '/exit':
      case '/quit':
        exit();
        break;
      default:
        console.log(`未知命令: ${command}`);
    }
  };

  const toggleMode = useCallback(() => {
    setMode(m => m === 'plan' ? 'build' : 'plan');
  }, []);

  return (
    <Box flexDirection="column" minHeight={20}>
      {/* 聊天区域 */}
      <Box flexGrow={1} flexDirection="column">
        <ChatView messages={messages} isLoading={isLoading} />
      </Box>
      
      {/* 权限请求对话框 */}
      {permissionRequest && (
        <PermissionRequest
          tool={permissionRequest.tool}
          action={permissionRequest.action}
          params={permissionRequest.params}
          riskLevel={permissionRequest.riskLevel}
          reason={permissionRequest.reason}
          onDecision={handlePermissionDecision}
        />
      )}
      
      {/* 工具执行状态 - 简洁版 */}
      {toolCalls.length > 0 && (
        <Box paddingX={1}>
          <Text dimColor>
            ⏳ {toolCalls.map(t => t.name).join(', ')}
          </Text>
        </Box>
      )}
      
      {/* 输入框 */}
      <InputBox 
        onSubmit={handleSubmit} 
        disabled={isLoading || permissionRequest !== null}
        mode={mode}
        onToggleMode={toggleMode}
        model={model}
      />
    </Box>
  );
}
