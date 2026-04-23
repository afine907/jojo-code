# 工具权限系统实现计划

## 项目路径
`/home/admin/.openclaw/workspace/jojo-code`

## 实现阶段

### Phase 1: Python 核心模块 (并发开发)

#### Task 1.1: security/modes.py (新建)
- 定义 `PermissionMode` 枚举 (YOLO/AUTO_APPROVE/INTERACTIVE/STRICT/READONLY)
- 定义 `RiskLevel` 枚举 (LOW/MEDIUM/HIGH/CRITICAL)
- 添加类型注解和文档字符串

#### Task 1.2: security/risk.py (新建)
- 实现 `assess_risk(tool_name, args)` 函数
- 定义风险模式正则表达式
- 支持工具名称和命令内容双重评估

#### Task 1.3: security/audit.py (新建)
- 实现 `AuditEvent` 数据类
- 实现 `AuditLogger` 类 (JSONL 格式日志)
- 实现 `AuditQuery` 类 (查询和统计)

#### Task 1.4: security/manager.py (增强)
- 添加 `mode` 属性 (PermissionMode)
- 增强 `check()` 方法，集成权限模式和风险评估
- 添加 `set_mode()` 方法

#### Task 1.5: security/command_guard.py (增强)
- 集成 `assess_risk()` 函数
- 在 `PermissionResult` 中添加 `risk_level` 属性

---

### Phase 2: JSON-RPC 集成

#### Task 2.1: server/handlers.py (增强)
- 添加 `handle_permission_mode()` handler
- 添加 `handle_audit_query()` handler  
- 添加 `handle_audit_stats()` handler
- 更新 `register_handlers()` 注册新 handlers

---

### Phase 3: CLI 组件

#### Task 3.1: PermissionRequest.tsx (新建)
- 实现权限请求 UI 组件
- 支持风险等级颜色显示
- 键盘快捷键 (Y/A/N)

#### Task 3.2: client/jsonrpc.ts (增强)
- 添加 `permissionMode()` 方法
- 添加 `setPermissionMode()` 方法
- 添加 `queryAudit()` 方法

---

### Phase 4: 测试和文档

#### Task 4.1: 测试文件
- tests/test_security/test_modes.py
- tests/test_security/test_risk.py
- tests/test_security/test_audit.py
- 更新 tests/test_security/test_permission.py

#### Task 4.2: 更新 __init__.py
- 导出新模块

---

## 依赖关系

```
Task 1.1 (modes.py) ──┬──► Task 1.4 (manager.py)
                      └──► Task 1.2 (risk.py)
                      
Task 1.2 (risk.py) ────► Task 1.5 (command_guard.py)

Task 1.3 (audit.py) ───► Task 1.4 (manager.py)
                      └──► Task 2.1 (handlers.py)

Task 1.4 (manager.py) ─► Task 2.1 (handlers.py)

Task 2.1 (handlers.py) ─► Task 3.2 (jsonrpc.ts)

Task 3.2 (jsonrpc.ts) ──► Task 3.1 (PermissionRequest.tsx)
```

## 并发策略

**第一批并发** (无依赖):
- Task 1.1: modes.py
- Task 1.2: risk.py  
- Task 1.3: audit.py

**第二批** (依赖第一批):
- Task 1.4: manager.py 增强
- Task 1.5: command_guard.py 增强

**第三批**:
- Task 2.1: handlers.py
- Task 3.2: jsonrpc.ts

**第四批**:
- Task 3.1: PermissionRequest.tsx

**第五批**:
- Task 4.1: 测试文件
- Task 4.2: 更新导出
