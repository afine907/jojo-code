import React from 'react';
import { Box, Text } from 'ink';
import type { Message, ToolCall } from '../app.js';

interface ChatViewProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatView({ messages, isLoading }: ChatViewProps) {
  if (messages.length === 0 && !isLoading) {
    return (
      <Box flexDirection="column" padding={1}>
        <Text dimColor>
          输入你的问题，/help 查看命令，Ctrl+D 退出
        </Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" paddingX={1}>
      {messages.map(msg => (
        <MessageItem key={msg.id} message={msg} />
      ))}
      {isLoading && (
        <Box>
          <Text color="cyan">⠋ AI 思考中...</Text>
        </Box>
      )}
    </Box>
  );
}

function MessageItem({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  
  return (
    <Box flexDirection="column" marginY={1}>
      <Box>
        <Text bold color={isUser ? 'green' : 'blue'}>
          {isUser ? '👤 You: ' : '🤖 AI: '}
        </Text>
      </Box>
      <Box paddingLeft={2}>
        <Text>{message.content}</Text>
      </Box>
      {message.toolCalls && message.toolCalls.length > 0 && (
        <Box paddingLeft={2} flexDirection="column">
          {message.toolCalls.map((tool, i) => (
            <ToolCallItem key={i} tool={tool} />
          ))}
        </Box>
      )}
    </Box>
  );
}

function ToolCallItem({ tool }: { tool: ToolCall }) {
  const statusIcon = {
    pending: '⏳',
    running: '⚡',
    completed: '✅',
    error: '❌',
  }[tool.status];

  return (
    <Box>
      <Text dimColor>
        {statusIcon} {tool.name}
      </Text>
    </Box>
  );
}
