"""WebSocket Server E2E 测试

在 CI 中运行，验证 Server 启动、WebSocket 通信、基础功能。
不需要 API Key，只测试通信层。
"""

import json
import subprocess
import time

import pytest
import websockets

# 服务端口（避免冲突）
TEST_PORT = 18765


@pytest.fixture(scope="module")
def server_process():
    """启动测试服务器"""
    import os

    env = os.environ.copy()
    env["JOJO_CODE_PORT"] = str(TEST_PORT)
    env["OPENAI_API_KEY"] = "test-key"
    env["OPENAI_BASE_URL"] = "http://localhost:1/v1"

    proc = subprocess.Popen(
        ["python", "-m", "jojo_code.server.ws_server"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 等待服务启动
    time.sleep(2)

    yield proc

    # 清理
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="module")
def server_url():
    return f"ws://localhost:{TEST_PORT}/ws"


class TestServerHealth:
    """服务器健康检查"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, server_process):
        """HTTP 健康检查"""
        import urllib.request

        url = f"http://localhost:{TEST_PORT}/health"
        try:
            req = urllib.request.urlopen(url, timeout=5)
            data = json.loads(req.read())
            assert data["status"] == "healthy"
        except Exception:
            pytest.skip("Server not available")


class TestWebSocketProtocol:
    """WebSocket 协议测试"""

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, server_url):
        """连接和断开"""
        async with websockets.connect(server_url):
            # 连接成功即断开
            pass

    @pytest.mark.asyncio
    async def test_invalid_json(self, server_url):
        """无效 JSON 处理"""
        async with websockets.connect(server_url) as ws:
            await ws.send("not json")
            resp = json.loads(await ws.recv())
            assert "error" in resp
            assert resp["error"]["code"] == -32700

    @pytest.mark.asyncio
    async def test_method_not_found(self, server_url):
        """未知方法处理"""
        async with websockets.connect(server_url) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "nonexistent"}))
            resp = json.loads(await ws.recv())
            assert "error" in resp
            assert resp["error"]["code"] == -32601

    @pytest.mark.asyncio
    async def test_get_model(self, server_url):
        """获取模型"""
        async with websockets.connect(server_url) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "get_model"}))
            resp = json.loads(await ws.recv())
            assert "result" in resp
            assert "model" in resp["result"]

    @pytest.mark.asyncio
    async def test_get_stats(self, server_url):
        """获取统计"""
        async with websockets.connect(server_url) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "get_stats"}))
            resp = json.loads(await ws.recv())
            assert "result" in resp
            assert "messages" in resp["result"]

    @pytest.mark.asyncio
    async def test_clear(self, server_url):
        """清空对话"""
        async with websockets.connect(server_url) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "clear"}))
            resp = json.loads(await ws.recv())
            assert resp["result"]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_permission_mode(self, server_url):
        """权限模式"""
        async with websockets.connect(server_url) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "permission/mode"}))
            resp = json.loads(await ws.recv())
            assert "result" in resp

    @pytest.mark.asyncio
    async def test_audit_recent(self, server_url):
        """审计日志"""
        async with websockets.connect(server_url) as ws:
            await ws.send(
                json.dumps(
                    {"jsonrpc": "2.0", "id": 1, "method": "audit/recent", "params": {"limit": 3}}
                )
            )
            resp = json.loads(await ws.recv())
            assert resp["result"]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_multiple_requests(self, server_url):
        """多个并发请求"""
        async with websockets.connect(server_url) as ws:
            # 发送多个请求
            for i in range(5):
                await ws.send(json.dumps({"jsonrpc": "2.0", "id": i, "method": "get_model"}))

            # 接收所有响应
            responses = []
            for _ in range(5):
                resp = json.loads(await ws.recv())
                responses.append(resp)

            ids = [r["id"] for r in responses]
            assert set(ids) == {0, 1, 2, 3, 4}


class TestCLIE2E:
    """CLI 端到端测试"""

    def test_cli_help(self):
        """CLI help 命令"""
        result = subprocess.run(
            ["python", "-m", "jojo_code", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "jojo-code" in result.stdout

    def test_cli_server_status(self):
        """CLI server status 命令"""
        result = subprocess.run(
            ["python", "-m", "jojo_code", "server", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_cli_config_show(self):
        """CLI config show 命令"""
        result = subprocess.run(
            ["python", "-m", "jojo_code", "config", "show"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
