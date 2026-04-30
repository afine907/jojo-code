# Docker 部署指南

## 快速开始

### 1. 构建镜像

```bash
docker build -t jojo-code .
```

### 2. 启动服务

```bash
# 使用 docker-compose（推荐）
docker compose up -d

# 或使用 docker run
docker run -d \
  --name jojo-code \
  -p 8080:8080 \
  -v $(pwd):/workspace \
  -e OPENAI_API_KEY=your-api-key \
  jojo-code
```

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8080/health

# 查看日志
docker logs jojo-code
```

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 | - |
| `ANTHROPIC_API_KEY` | Anthropic API Key | - |
| `JOJO_CODE_MODEL` | 模型名称 | gpt-4o-mini |
| `JOJO_CODE_PORT` | 服务端口 | 8080 |

### 挂载目录

```bash
# 挂载你的项目目录
docker run -d \
  -p 8080:8080 \
  -v /path/to/your/project:/workspace \
  -e OPENAI_API_KEY=xxx \
  jojo-code
```

## 远程连接

启动 Docker 服务后，用 CLI 连接：

```bash
# 设置远程服务器地址
jojo-code config set server ws://your-server:8080/ws

# 启动 TUI
jojo-code
```

## 停止服务

```bash
docker compose down
# 或
docker stop jojo-code
```
