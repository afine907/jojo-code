# Code Review Report

## 1. Python Server (rpc.py)

### 🔴 Critical Issues

1. **State Mutation Bug** (Line 76-102)
   - `state` 变量在 `graph.stream(state)` 后被修改，但后续迭代使用的是修改后的 state
   - 可能导致重复处理或遗漏处理

2. **Missing Input Validation**
   - `_handle_agent_stream`: `prompt` 可能为空字符串
   - `_handle_tool_execute`: `name` 可能为 None
   - 应该验证必需参数

3. **No Graceful Shutdown**
   - `run()` 方法的无限循环没有优雅退出机制
   - 应该处理 SIGTERM/SIGINT 信号

### 🟡 Medium Issues

4. **Hardcoded Truncation** (Line 101)
   - `result[:500]` 硬编码截断长度
   - 应该可配置

5. **Missing Error Context**
   - 错误响应只包含 message，没有 stack trace 或上下文
   - 应该在开发模式下提供更多信息

6. **No Request Timeout**
   - 长时间运行的请求没有超时机制
   - 可能导致请求堆积

### 🟢 Suggestions

7. **Add Logging**
   - 添加结构化日志记录请求和响应

8. **Type Hints Missing**
   - 部分方法缺少返回类型注解

---

## 2. TypeScript Client (rpc.ts)

### 🔴 Critical Issues

1. **Unreliable Connection Delay** (Line 37)
   ```typescript
   setTimeout(resolve, 100);  // 硬编码 100ms
   ```
   - 应该等待服务器实际就绪，而不是固定延迟

2. **Silent JSON Parse Errors** (Line 62)
   - JSON 解析错误被静默忽略
   - 应该记录或发出错误事件

3. **No Process Cleanup on Error**
   - `close()` 方法调用 `process.kill()` 但没有等待进程退出
   - 可能导致僵尸进程

### 🟡 Medium Issues

4. **Singleton Pattern Issues** (Line 165-171)
   - 全局单例 `_client` 使测试困难
   - 应该使用依赖注入

5. **No Reconnection Logic**
   - 连接断开后没有自动重连
   - 应该实现指数退避重连

6. **Memory Leak Potential**
   - `pendingRequests` Map 在超时后只删除不清理
   - 应该定期清理过期的 pending 请求

### 🟢 Suggestions

7. **Add Connection State**
   - 应该暴露连接状态 (connecting, connected, disconnected)

8. **Better Error Types**
   - 应该定义自定义错误类型 (ConnectionError, TimeoutError, etc.)

---

## 3. React Hook (useAgent.ts)

### 🔴 Critical Issues

1. **Stale Closure Bug** (Line 38)
   ```typescript
   client.on("stream", handleStreamEvent);
   ```
   - `handleStreamEvent` 在 useEffect 依赖数组中缺失
   - 可能导致 stale closure 问题

2. **Missing Cleanup for Streaming**
   - 组件卸载时如果有正在进行的流式请求，没有取消
   - 应该使用 AbortController

### 🟡 Medium Issues

3. **Race Condition**
   - `currentResponseRef` 在多个事件处理器中被修改
   - 应该使用 useReducer 或更安全的状态管理

4. **No Error Recovery**
   - 错误发生后用户只能手动 reconnect
   - 应该提供自动恢复选项

5. **Memory Leak in Effect**
   - useEffect 返回的 cleanup 函数只关闭 client
   - 应该也清理事件监听器

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 5 |
| 🟡 Medium | 9 |
| 🟢 Suggestions | 5 |

## Priority Fix Order

1. Fix state mutation bug in Python Server
2. Add input validation in Python Server
3. Fix stale closure in useAgent hook
4. Implement reliable connection in TypeScript Client
5. Add proper cleanup and error handling
