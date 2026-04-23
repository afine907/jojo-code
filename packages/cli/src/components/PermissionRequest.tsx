import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

export interface PermissionRequestProps {
  /** 工具名称 */
  tool: string;
  /** 操作名称 */
  action: string;
  /** 工具参数 */
  params: Record<string, any>;
  /** 风险等级 */
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  /** 原因说明 */
  reason: string;
  /** 用户决策回调 */
  onDecision: (decision: 'allow' | 'deny' | 'always') => void;
}

const riskColors = {
  low: 'green',
  medium: 'yellow',
  high: 'orange',
  critical: 'red',
};

const riskLabels = {
  low: '🟢 Low',
  medium: '🟡 Medium',
  high: '🟠 High',
  critical: '🔴 Critical',
};

const riskDescriptions = {
  low: '低风险 - 仅读取信息，不修改系统状态',
  medium: '中风险 - 修改有限范围的文件或配置',
  high: '高风险 - 修改系统关键配置或多个文件',
  critical: '极高风险 - 可能导致数据丢失或系统不可用',
};

/**
 * 权限请求组件
 *
 * 显示权限请求对话框，让用户决定是否允许操作。
 */
export function PermissionRequest({
  tool,
  action,
  params,
  riskLevel,
  reason,
  onDecision,
}: PermissionRequestProps) {
  const [selected, setSelected] = useState(0);
  const options = [
    { key: 'y', label: 'Yes, allow', action: 'allow' as const },
    { key: 'a', label: 'Always allow for this tool', action: 'always' as const },
    { key: 'n', label: 'No, deny', action: 'deny' as const },
  ];

  useInput((input, key) => {
    // 快捷键
    if (input === 'y') {
      onDecision('allow');
    } else if (input === 'a') {
      onDecision('always');
    } else if (input === 'n') {
      onDecision('deny');
    }
    // 方向键选择
    else if (key.leftArrow || key.upArrow) {
      setSelected(Math.max(0, selected - 1));
    } else if (key.rightArrow || key.downArrow) {
      setSelected(Math.min(options.length - 1, selected + 1));
    }
    // 回车确认选择
    else if (key.return) {
      onDecision(options[selected].action);
    }
  });

  return (
    <Box flexDirection="column" padding={1}>
      <Box
        flexDirection="column"
        borderStyle="round"
        borderColor={riskColors[riskLevel]}
        padding={1}
      >
        {/* 标题 */}
        <Box marginBottom={1}>
          <Text bold color={riskColors[riskLevel]}>
            🔒 Permission Request
          </Text>
        </Box>

        {/* 基本信息 */}
        <Box>
          <Text bold>Tool: </Text>
          <Text>{tool}</Text>
        </Box>

        <Box>
          <Text bold>Action: </Text>
          <Text>{action}</Text>
        </Box>

        <Box>
          <Text bold>Risk: </Text>
          <Text color={riskColors[riskLevel]}>{riskLabels[riskLevel]}</Text>
        </Box>

        {/* 命令预览 */}
        {params.command && (
          <Box flexDirection="column" marginTop={1}>
            <Text bold>Command:</Text>
            <Box marginLeft={2}>
              <Text dimColor>$ {params.command}</Text>
            </Box>
          </Box>
        )}

        {/* 文件路径预览 */}
        {params.path && (
          <Box marginTop={1}>
            <Text bold>Path: </Text>
            <Text dimColor>{params.path}</Text>
          </Box>
        )}

        {/* 原因 */}
        <Box marginTop={1}>
          <Text dimColor>Reason: {reason}</Text>
        </Box>

        {/* 风险描述 */}
        <Box marginTop={1}>
          <Text dimColor italic>
            {riskDescriptions[riskLevel]}
          </Text>
        </Box>

        {/* 分隔线 */}
        <Box marginY={1}>
          <Text dimColor>────────────────────────────────────────</Text>
        </Box>

        {/* 选项 */}
        <Box>
          {options.map((opt, i) => (
            <Box key={opt.key} marginRight={2}>
              <Text
                color={selected === i ? 'cyan' : 'gray'}
                bold={selected === i}
                inverse={selected === i}
              >
                {' '}
                [{opt.key}] {opt.label}{' '}
              </Text>
            </Box>
          ))}
        </Box>

        {/* 提示 */}
        <Box marginTop={1}>
          <Text dimColor>
            Press Y/A/N or use arrow keys and Enter
          </Text>
        </Box>
      </Box>
    </Box>
  );
}

/**
 * 权限请求确认对话框（简化版，只有 Yes/No）
 */
export function PermissionConfirm({
  message,
  riskLevel,
  onConfirm,
  onCancel,
}: {
  message: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  onConfirm: () => void;
  onCancel: () => void;
}) {
  useInput((input) => {
    if (input === 'y') {
      onConfirm();
    } else if (input === 'n') {
      onCancel();
    }
  });

  return (
    <Box
      flexDirection="column"
      borderStyle="round"
      borderColor={riskColors[riskLevel]}
      padding={1}
    >
      <Text color={riskColors[riskLevel]} bold>
        ⚠️ {message}
      </Text>
      <Box marginTop={1}>
        <Text>[Y] Yes, continue  </Text>
        <Text>[N] No, cancel</Text>
      </Box>
    </Box>
  );
}

export default PermissionRequest;
