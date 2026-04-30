FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .

# 安装 Python 依赖
RUN pip install --no-cache-dir -e .

# 复制源码
COPY src/ src/

# 创建工作目录
RUN mkdir -p /workspace
WORKDIR /workspace

# 暴露端口
EXPOSE 8080

# 环境变量
ENV JOJO_CODE_HOST=0.0.0.0
ENV JOJO_CODE_PORT=8080
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# 启动命令
CMD ["python", "-m", "jojo_code.server.ws_server"]
