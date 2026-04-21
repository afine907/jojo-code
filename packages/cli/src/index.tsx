#!/usr/bin/env node
import React from 'react';
import { render } from 'ink';
import { App } from './app.js';

// 启动 CLI
const { waitUntilExit } = render(<App />);

// 等待退出
waitUntilExit().then(() => {
  process.exit(0);
});
