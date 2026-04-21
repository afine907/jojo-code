import React from 'react';
import { Box, Text } from 'ink';
import type { Mode } from '../app.js';

interface StatusBarProps {
  mode: Mode;
  model: string;
  messages: number;
  tools: number;
  duration: number;
}

export function StatusBar({ mode, model, messages, tools, duration }: StatusBarProps) {
  const modeLabel = mode === 'plan' ? 'PLAN' : 'BUILD';
  const modeColor = mode === 'plan' ? 'magenta' : 'green';
  
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <Box 
      borderStyle="single" 
      borderColor="gray"
      justifyContent="space-between"
      paddingX={1}
    >
      <Box>
        <Text bold color={modeColor}>
          [{modeLabel}]
        </Text>
        <Text> │ </Text>
        <Text color="cyan">{model}</Text>
      </Box>
      
      <Box>
        <Text dimColor>
          Msgs: {messages} │ Tools: {tools} │ {formatDuration(duration)}
        </Text>
      </Box>
    </Box>
  );
}
