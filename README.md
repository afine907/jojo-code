<div align="center">

# 🤖 jojo-Code

**A coding agent powered by LangGraph - Python CLI + WebSocket Server**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3%2B-green?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Textual](https://img.shields.io/badge/Textual-0.40%2B-blueviolet?logo=python&logoColor=white)](https://github.com/Textualize/textual)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*全 Python 编码 Agent：Textual TUI + WebSocket Server + LangGraph*

</div>

---

## ✨ 特色

- 🔧 **20+ 工具** - 文件读写、代码搜索、Shell 执行、Git 操作、Web 搜索
- 🧠 **Agent 循环** - LangGraph 状态机：Thinking → Tool Call → Execute → Observe
- 💾 **智能记忆** - 自动 Token 计数与上下文压缩
- 🖥️ **现代 TUI** - Textual 框架终端界面，流式输出
- 🌐 **WebSocket 服务** - CLI 与 Server 分离，支持远程部署
- 🐳 **Docker 支持** - 一键部署，环境变量配置
- 🧪 **TDD 驱动** - 350+ 测试覆盖

---

## 🚀 快速开始

### 安装

```bash
pip install jojo-code
```

### 配置

```bash
# 设置 API Key
export OPENAI_API_KEY=your-api-key

# 或使用 OpenAI 兼容 API
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.longcat.chat/openai/v1
export JOJO_CODE_MODEL=LongCat-Flash-Chat
```

### 使用

```bash
# 启动 TUI（自动连接本地服务）
jojo-code

# 或手动启动服务
jojo-code server start
jojo-code
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
