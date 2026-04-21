import React, { useState, useCallback } from 'react';
import { Box, Text, useInput } from 'ink';
import type { Mode } from '../app.js';

interface InputBoxProps {
  onSubmit: (input: string) => void;
  disabled: boolean;
  mode: Mode;
}

export function InputBox({ onSubmit, disabled, mode }: InputBoxProps) {
  const [input, setInput] = useState('');
  const [multiline, setMultiline] = useState(false);
  const [lines, setLines] = useState<string[]>([]);

  useInput((char, key) => {
    if (disabled) return;

    // Tab 切换多行模式
    if (key.tab) {
      if (multiline) {
        setLines([...lines, input]);
        setInput('');
      } else {
        setMultiline(true);
      }
      return;
    }

    // Enter 提交
    if (key.return) {
      console.log('[DEBUG] Enter pressed, multiline:', multiline, 'input:', input);
      if (multiline && input) {
        // 多行模式下，Enter 换行
        setLines([...lines, input]);
        setInput('');
      } else {
        // 提交
        const finalInput = multiline 
          ? [...lines, input].join('\n')
          : input;
        console.log('[DEBUG] finalInput:', finalInput);
        if (finalInput.trim()) {
          console.log('[DEBUG] Calling onSubmit');
          onSubmit(finalInput.trim());
          setInput('');
          setLines([]);
          setMultiline(false);
        }
      }
      return;
    }

    // Backspace
    if (key.backspace || key.delete) {
      setInput(prev => prev.slice(0, -1));
      return;
    }

    // 普通字符
    if (char && !key.ctrl && !key.meta) {
      setInput(prev => prev + char);
    }
  });

  const promptIcon = mode === 'plan' ? '📋' : '🦞';
  const placeholder = multiline 
    ? '(多行模式 - Enter 换行，Tab 完成)'
    : '(Tab 切换多行模式)';

  return (
    <Box flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1}>
      {/* 显示已输入的多行内容 */}
      {lines.length > 0 && (
        <Box flexDirection="column">
          {lines.map((line, i) => (
            <Text key={i} dimColor>{`> ${line}`}</Text>
          ))}
        </Box>
      )}
      
      {/* 当前输入行 */}
      <Box>
        <Text bold color="cyan">{promptIcon} </Text>
        <Text>{input}</Text>
        {!input && <Text dimColor>{placeholder}</Text>}
        <Text backgroundColor="cyan"> </Text>
      </Box>
      
      {disabled && (
        <Text dimColor>处理中...</Text>
      )}
    </Box>
  );
}
