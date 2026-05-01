<div align="center">

# 🤖 jojo-Code

**轻量级 AI 编码助手 - 全 Python 实现，易于定制和扩展**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3%2B-green?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Textual](https://img.shields.io/badge/Textual-0.40%2B-blueviolet?logo=python&logoColor=white)](https://github.com/Textualize/textual)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/afine907/jojo-code?style=social)](https://github.com/afine907/jojo-code/stargazers)

*终端 TUI + WebSocket Server + LangGraph Agent - 可自托管、可扩展的编码助手*

**[English](README_EN.md)** | 中文文档

</div>

---

## 🎯 为什么选择 jojo-Code？

| 特性 | jojo-Code | Claude Code | Cursor | Aider |
|------|-----------|-------------|--------|-------|
| **开源免费** | ✅ 完全开源 | ❌ 商业产品 | ❌ 商业产品 | ✅ 开源 |
| **自托管** | ✅ 完全本地 | ❌ 云端 | ❌ 云端 | ✅ 本地 |
| **终端 TUI** | ✅ Textual | ✅ 终端 | ❌ IDE 插件 | ✅ 终端 |
| **Python 原生** | ✅ 100% Python | ❌ TypeScript | ❌ TypeScript | ✅ Python |
| **易于定制** | ✅ 插件式工具 | ❌ 封闭 | ⚠️ 有限 | ✅ 可定制 |
| **LangGraph** | ✅ 可视化调试 | ❌ | ❌ | ❌ |
| **远程部署** | ✅ WebSocket | ❌ | ❌ | ❌ |

**jojo-Code 的独特价值**：
- 🎓 **学习友好**：清晰的 LangGraph 架构，适合学习 Agent 开发
- 🔧 **易于扩展**：插件式工具系统，20 行代码添加新工具
- 🌐 **灵活部署**：本地 CLI 或远程 WebSocket Server
- 💰 **成本可控**：支持任意 OpenAI 兼容 API（LongCat、DeepSeek、Moonshot...）

---

## ✨ 核心功能

- 🔧 **20+ 工具** - 文件读写、代码搜索、Shell 执行、Git 操作、Web 搜索
- 🧠 **LangGraph Agent** - 状态机驱动：Thinking → Tool Call → Execute → Observe
- 💾 **智能记忆** - 自动 Token 计数与上下文压缩
- 🖥️ **现代 TUI** - Textual 终端界面，流式输出，类似 Claude Code
- 🌐 **WebSocket 服务** - CLI 与 Server 分离，支持远程部署
- 🔐 **权限控制** - 敏感操作需要用户确认
- 🐳 **Docker 支持** - 一键部署，环境变量配置
- 🧪 **高测试覆盖** - 350+ 测试，TDD 开发

---

## 📸 截图

> TUI 界面截图（待补充）

---

## 🚀 快速开始

### 安装

```bash
# 从 PyPI 安装（即将发布）
pip install jojo-code

# 或从源码安装
git clone https://github.com/afine907/jojo-code.git
cd jojo-code
uv sync
```

### 配置

```bash
# 设置 API Key（支持任意 OpenAI 兼容 API）
export OPENAI_API_KEY=your-api-key

# 可选：使用其他 API
export OPENAI_BASE_URL=https://api.longcat.chat/openai/v1
export JOJO_CODE_MODEL=LongCat-Flash-Chat
```

### 使用

```bash
# 启动 TUI
jojo-code

# 或先启动服务，再连接
jojo-code server start -d  # 后台启动
jojo-code                  # 连接服务
```

---

## 💡 使用场景

### 1. 日常编码

```
你: 帮我在 user 模块添加一个登录函数

jojo: 
[Reading] src/user/__init__.py
[Reading] src/auth/session.py
[Writing] src/user/login.py
✅ 已创建 login.py，包含 login() 函数
```

### 2. 代码重构

```
你: 把 authenticate 函数拆分成多个小函数

jojo:
[Reading] src/auth/authenticate.py
[Editing] src/auth/authenticate.py
✅ 已拆分为：validate_credentials(), check_permission(), create_session()
```

### 3. Bug 修复

```
你: 修复 login 函数中的 SQL 注入漏洞

jojo:
[Reading] src/user/login.py
[Editing] src/user/login.py
✅ 已使用参数化查询替换字符串拼接
```

### 4. 学习 LangGraph

jojo-Code 的清晰架构适合学习 Agent 开发：

```python
# src/jojo_code/agent/graph.py
from langgraph.graph import StateGraph

# 定义状态
class AgentState(TypedDict):
    messages: list[BaseMessage]
    tool_calls: list[ToolCall]

# 定义节点
def thinking(state: AgentState) -> AgentState:
    """LLM 思考，决定是否调用工具"""
    ...

def execute(state: AgentState) -> AgentState:
    """执行工具调用"""
    ...

# 构建图
graph = StateGraph(AgentState)
graph.add_node("thinking", thinking)
graph.add_node("execute", execute)
graph.add_edge("thinking", "execute")
```

---

## 🏗️ 架构

```
┌──────────────────────┐            ┌─────────────────────────┐
│ pip install jojo-code│            │ Docker / pip install    │
│                      │  WebSocket │                         │
│  Textual CLI (Python)│◄──────────►│  FastAPI + WebSocket    │
│  流式输出 + TUI      │            │  LangGraph Agent        │
│                      │            │  20+ Tools              │
└──────────────────────┘            └─────────────────────────┘
```

### 目录结构

```text
src/jojo_code/
├── cli/                # Textual TUI
│   ├── app.py          # 主应用
│   ├── main.py         # CLI 入口
│   ├── ws_client.py    # WebSocket 客户端
│   └── views/          # UI 组件
│       ├── chat.py     # 消息列表
│       ├── input_box.py
│       ├── permission.py
│       └── status_bar.py
│
├── server/             # WebSocket Server
│   ├── ws_server.py    # FastAPI WebSocket
│   ├── handlers.py     # JSON-RPC handlers
│   └── jsonrpc.py      # 兼容旧协议
│
├── agent/              # LangGraph Agent
│   ├── graph.py        # 状态图定义
│   ├── nodes.py        # thinking/execute 节点
│   └── state.py        # 状态结构
│
├── tools/              # 20+ 工具
│   ├── file_tools.py
│   ├── shell_tools.py
│   ├── git_tools.py
│   ├── search_tools.py
│   └── ...
│
├── security/           # 权限系统
├── memory/             # 对话记忆
└── core/               # 配置 & LLM 客户端
```

---

## 📖 命令

```bash
# TUI
jojo-code                        # 启动终端界面

# 服务管理
jojo-code server start           # 前台启动服务
jojo-code server start -d        # 后台守护模式
jojo-code server status          # 查看服务状态
jojo-code server stop            # 停止服务

# 配置
jojo-code config set server ws://localhost:8080/ws
jojo-code config set model gpt-4o
jojo-code config show
jojo-code config get server
```

---

## 🐳 Docker

```bash
# 启动
docker compose up -d

# 验证
curl http://localhost:8080/health

# 远程连接
jojo-code config set server ws://your-server:8080/ws
jojo-code
```

详见 [Docker 部署指南](docs/docker.md)

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| Agent 框架 | LangGraph |
| 工具定义 | LangChain Tools |
| LLM 客户端 | langchain-openai / langchain-anthropic |
| CLI 框架 | Textual |
| WebSocket | FastAPI + websockets |
| 测试 | pytest + pytest-asyncio |
| 包管理 | uv |

---

## 🧪 开发

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest tests/ -v

# 代码检查
uv run ruff check src/
uv run ruff format --check src/
```

---

## 🤝 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

Made with ❤️ for learning Agent architecture

</div>
