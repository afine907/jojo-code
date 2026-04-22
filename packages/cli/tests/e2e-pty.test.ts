/**
 * node-pty E2E 测试
 * 
 * 注意：Ink 的 useInput 依赖 stdin raw mode，在 PTY 环境中可能无法正常工作。
 * 完整的交互测试请使用 pexpect (tests/test_e2e/test_cli.py)
 * 
 * 这个测试主要用于：
 * 1. 验证 CLI 能否启动
 * 2. 验证界面渲染是否正确
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as pty from 'node-pty';
import type { IPty } from 'node-pty';

// 仅在本地运行
const shouldRun = !process.env.CI;

describe.skipIf(!shouldRun)('CLI E2E (node-pty) - 界面渲染测试', () => {
  let ptyProcess: IPty | null = null;
  let output: string = '';

  beforeEach(() => {
    output = '';
  });

  afterEach(() => {
    if (ptyProcess) {
      try {
        ptyProcess.kill();
      } catch {}
      ptyProcess = null;
    }
  });

  function startCLI(): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('启动超时')), 15000);

      ptyProcess = pty.spawn('npx', ['tsx', 'src/index.tsx'], {
        name: 'xterm-256color',
        cols: 100,
        rows: 30,
        cwd: process.cwd(),
        env: { ...process.env, TERM: 'xterm-256color' },
      });

      ptyProcess.onData((data) => {
        output += data;
        // 检测到提示符即认为启动成功
        if (data.includes('🦞') || data.includes('📋')) {
          clearTimeout(timeout);
          resolve();
        }
      });

      ptyProcess.onExit(() => {
        clearTimeout(timeout);
        ptyProcess = null;
      });
    });
  }

  function stripAnsi(str: string): string {
    return str
      .replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '')
      .replace(/\x1b\][^\x07]*\x07/g, '')
      .replace(/\[\?[0-9;]*[a-zA-Z]/g, '')
      .replace(/\[2K/g, '')
      .replace(/\[1G/g, '')
      .replace(/\[\?25l/g, '')
      .replace(/\[\?25h/g, '');
  }

  describe('启动测试', () => {
    it('成功启动并显示提示符 🦞', async () => {
      await startCLI();
      const clean = stripAnsi(output);
      expect(clean).toContain('🦞');
    });

    it('显示帮助提示', async () => {
      await startCLI();
      const clean = stripAnsi(output);
      expect(clean).toContain('/help');
    });

    it('显示 BUILD 模式', async () => {
      await startCLI();
      const clean = stripAnsi(output);
      expect(clean).toContain('BUILD');
    });

    it('显示模型名称', async () => {
      await startCLI();
      const clean = stripAnsi(output);
      // 模型名可能从环境变量读取
      expect(clean).toMatch(/gpt-4o-mini|LongCat/);
    });

    it('显示 Tab 换行提示', async () => {
      await startCLI();
      const clean = stripAnsi(output);
      expect(clean).toContain('Tab');
    });
  });

  describe('退出测试', () => {
    // 注意：Ctrl+C 也依赖 useInput，在 PTY 中可能不工作
    // 退出功能在 pexpect 测试中验证
    it.skip('Ctrl+C 可以退出', async () => {
      await startCLI();
      
      const exitPromise = new Promise<void>((resolve) => {
        ptyProcess?.onExit(() => resolve());
      });

      ptyProcess?.write('\x03');
      
      await exitPromise;
      ptyProcess = null;
    });
  });
});

/**
 * 完整交互测试请使用 pexpect:
 * 
 * pytest tests/test_e2e/test_cli.py -v -s
 * 
 * 测试覆盖：
 * - 启动和显示
 * - /help, /mode, /clear, /exit 命令
 * - 输入和提交消息
 * - 多行输入 (Tab)
 * - Backspace, Escape 等快捷键
 */
