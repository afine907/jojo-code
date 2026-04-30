# jojo-code 全 Python 重构计划

> 将 TypeScript CLI + Python Agent 双语言架构，重构为全 Python 单语言架构。
> CLI 使用 Textual 框架重写，Agent 层通过 WebSocket 对外提供服务。

## 一、架构总览

```
重构前:                          重构后:
┌──────────────┐                ┌──────────────┐
│ TypeScript   │  stdio JSON-RPC│ Python CLI   │  WebSocket
│ CLI (ink)    │◄──────────────►│ (Textual)    │◄─────────────►│ Python Agent │
└──────────────┘                └──────────────┘               │ (LangGraph)  │
                                                                └──────────────┘
安装: uv + pnpm                 安装: pip install jojo-code
```

## 二、分支策略

基于 `master` 创建 feature 分支，每个阶段一个分支，按顺序合并。

```
master
  └── refactor/all-python            # 总分支（所有子阶段合入）
        ├── refactor/p0-ws-server    # P0: WebSocket Server
        ├── refactor/p1-cli-entry    # P1: CLI 入口 + 配置
        ├── refactor/p2-textual-ui   # P2: Textual TUI 核心
        ├── refactor/p3-ws-client    # P3: WebSocket Client
        ├── refactor/p4-components   # P4: 权限弹窗 + 状态栏
        ├── refactor/p5-docker       # P5: Docker 支持
        └── refactor/p6-cleanup      # P6: 清理 + 集成测试
```

**流程**：每个子阶段完成后提 PR → review → 合入 `refactor/all-python` → 删除子分支

## 三、阶段详细任务

### P0：WebSocket Server（`refactor/p0-ws-server`）

**目标**：将 stdio JSON-RPC 改为 WebSocket 服务

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 0.1 | 创建 ws_server.py，FastAPI + WebSocket 端点 | `server/ws_server.py` | WebSocket 连接成功 |
| 0.2 | 实现 JSON-RPC over WebSocket 协议解析 | `server/ws_server.py` | 请求/响应格式正确 |
| 0.3 | 包装现有 handlers（chat/clear/get_model/get_stats） | `server/ws_server.py` | 所有现有方法可用 |
| 0.4 | 实现流式响应（streaming chunks） | `server/ws_server.py` | 流式输出正常 |
| 0.5 | 添加健康检查端点 `GET /health` | `server/ws_server.py` | 返回 200 |
| 0.6 | 添加 CORS 中间件 | `server/ws_server.py` | 跨域请求通过 |
| 0.7 | 配置化（host/port 从环境变量读取） | `server/ws_server.py` | 支持 JOJO_CODE_HOST/PORT |
| 0.8 | 编写单元测试 | `tests/test_server/test_ws_server.py` | 测试通过 |
| 0.9 | 更新 pyproject.toml（新增 fastapi/uvicorn/websockets 依赖） | `pyproject.toml` | `pip install -e .` 成功 |

### P1：CLI 入口 + 配置（`refactor/p1-cli-entry`）

**目标**：实现 CLI 命令行入口和配置管理

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 1.1 | 创建 cli/__init__.py | `cli/__init__.py` | 模块可导入 |
| 1.2 | 实现 CLI 入口 main.py（argparse 命令分发） | `cli/main.py` | `jojo-code --help` 正常 |
| 1.3 | 实现子命令：`server start/stop` | `cli/main.py` | 服务启动/停止 |
| 1.4 | 实现子命令：`config set/show` | `cli/config.py` | 配置读写正确 |
| 1.5 | 配置文件存储（`~/.jojo-code/config.json`） | `cli/config.py` | 持久化成功 |
| 1.6 | 默认命令 `jojo-code` 启动 TUI（占位） | `cli/main.py` | 显示"开发中"提示 |
| 1.7 | 更新 pyproject.toml `[project.scripts]` | `pyproject.toml` | `jojo-code` 命令可用 |

### P2：Textual TUI 核心（`refactor/p2-textual-ui`）

**目标**：实现 Textual 聊天界面核心

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 2.1 | 创建 Textual App 主体 | `cli/app.py` | 应用启动，显示界面 |
| 2.2 | 实现 ChatView（消息列表 + Markdown 渲染） | `cli/views/chat.py` | 消息正确渲染 |
| 2.3 | 实现 InputBox（多行输入 + 发送） | `cli/views/input_box.py` | 输入发送正常 |
| 2.4 | 实现消息气泡样式（用户/助手区分） | `cli/views/chat.py` | 样式美观 |
| 2.5 | 实现斜杠命令（/help, /clear, /mode, /exit） | `cli/app.py` | 命令响应正确 |
| 2.6 | 连接 WebSocket Client 发送消息 | 集成 ws_client | 端到端通信成功 |
| 2.7 | 实现加载状态指示器 | `cli/views/chat.py` | 加载时显示动画 |
| 2.8 | 编写 Textual 组件测试 | `tests/test_cli/` | 测试通过 |

### P3：WebSocket Client（`refactor/p3-ws-client`）

**目标**：实现 Python WebSocket 客户端

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 3.1 | 创建 WSClient 类（连接管理） | `cli/ws_client.py` | 连接/断开正常 |
| 3.2 | 实现 request 方法（同步请求） | `cli/ws_client.py` | 请求/响应正确 |
| 3.3 | 实现 stream 方法（异步流式） | `cli/ws_client.py` | 流式接收正常 |
| 3.4 | 实现断线重连机制 | `cli/ws_client.py` | 断线后自动重连 |
| 3.5 | 实现连接状态回调 | `cli/ws_client.py` | 状态变化通知 |
| 3.6 | 编写单元测试 | `tests/test_cli/test_ws_client.py` | 测试通过 |

### P4：权限弹窗 + 状态栏（`refactor/p4-components`）

**目标**：补全交互组件

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 4.1 | 实现 PermissionModal（权限确认弹窗） | `cli/views/permission.py` | 弹窗显示/关闭 |
| 4.2 | 权限决策传递给服务端 | `cli/views/permission.py` | 允许/拒绝生效 |
| 4.3 | 实现 StatusBar（模型/模式/token/耗时） | `cli/views/status_bar.py` | 信息实时更新 |
| 4.4 | 实现工具调用状态展示 | `cli/views/chat.py` | 工具调用过程可见 |
| 4.5 | 实现会话统计面板 | `cli/views/status_bar.py` | 统计数据正确 |

### P5：Docker 支持（`refactor/p5-docker`）

**目标**：支持 Docker 部署

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 5.1 | 编写 Dockerfile | `Dockerfile` | 镜像构建成功 |
| 5.2 | 编写 docker-compose.yml | `docker-compose.yml` | `docker compose up` 启动 |
| 5.3 | 环境变量配置（API Key/Model/Port） | `Dockerfile` | 可配置 |
| 5.4 | Volume 挂载（项目目录） | `docker-compose.yml` | 文件可访问 |
| 5.5 | 编写 .dockerignore | `.dockerignore` | 镜像体积优化 |
| 5.6 | 编写 Docker 使用文档 | `docs/docker.md` | 文档完整 |

### P6：清理 + 集成测试（`refactor/p6-cleanup`）

**目标**：删除旧代码，全链路验证

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 6.1 | 删除 TypeScript CLI（packages/cli/） | `packages/cli/` | 目录删除 |
| 6.2 | 删除 Node.js 配置文件 | `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml` | 文件删除 |
| 6.3 | 更新 README.md（安装/使用文档） | `README.md` | 文档准确 |
| 6.4 | 更新 .gitignore | `.gitignore` | 无多余规则 |
| 6.5 | 全链路 E2E 测试 | `tests/test_e2e/` | CLI → Server → Agent → Tool 全通 |
| 6.6 | 清理无用的向后兼容代码 | `server/jsonrpc.py` 等 | 评估后决定保留或删除 |
| 6.7 | 更新 AGENTS.md / CLAUDE.md | 项目文档 | 与新架构一致 |

## 四、依赖关系

```
P0 (WebSocket Server)
  ↓
P1 (CLI 入口) ──→ P3 (WebSocket Client)
  ↓                    ↓
P2 (Textual UI) ←──────┘
  ↓
P4 (权限 + 状态栏)
  ↓
P5 (Docker)
  ↓
P6 (清理 + 测试)
```

**关键路径**：P0 → P1 → P3 → P2 → P4 → P5 → P6

P0 必须先完成，P1 和 P3 可部分并行，P2 依赖 P3，P4 依赖 P2。

## 五、每个 PR 的要求

### PR 格式

```
标题: refactor(P0): 添加 WebSocket Server

描述:
- 新增 FastAPI WebSocket 端点
- 实现 JSON-RPC over WebSocket 协议
- 包装现有 handlers
- 支持流式响应
- 添加单元测试

测试:
- [x] 单元测试通过
- [x] 手动测试 WebSocket 连接
```

### PR 检查清单

- [ ] 代码通过 `ruff check` 和 `ruff format --check`
- [ ] 类型检查通过 `mypy`
- [ ] 单元测试通过 `pytest`
- [ ] 不破坏现有功能（P0 阶段保留 stdio JSON-RPC）
- [ ] 有对应的测试覆盖

## 六、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Textual 组件不如 ink 丝滑 | 用户体验 | 提前做 POC 验证核心交互 |
| WebSocket 流式延迟 | 响应速度 | 使用 uvicorn + async，优化序列化 |
| Docker Volume 权限问题 | 文件操作 | 使用 `--user` 参数，文档说明 |
| 现有测试覆盖不全 | 回归风险 | P6 阶段补全 E2E 测试 |

## 七、时间估算

| 阶段 | 工作量 | 累计 |
|------|--------|------|
| P0 | 1 天 | 1 天 |
| P1 | 0.5 天 | 1.5 天 |
| P2 | 2 天 | 3.5 天 |
| P3 | 0.5 天 | 4 天 |
| P4 | 1 天 | 5 天 |
| P5 | 0.5 天 | 5.5 天 |
| P6 | 1 天 | 6.5 天 |
| **总计** | | **~6.5 天** |

## 八、最终产出

```bash
# 安装
pip install jojo-code

# 本地使用
jojo-code                  # 启动 TUI
jojo-code server start     # 启动本地服务

# Docker 使用
docker run -d -p 8080:8080 -v $(pwd):/workspace jojo-code
jojo-code --server ws://remote:8080/ws

# 配置
jojo-code config set server ws://my-server:8080/ws
jojo-code config set model gpt-4o
```
