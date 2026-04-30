"""WebSocket Client 单元测试"""

import json

import pytest
from fastapi.testclient import TestClient

from jojo_code.server.ws_server import app


@pytest.fixture
def server_url():
    """测试服务器 URL"""
    return "ws://testserver/ws"


@pytest.fixture
def client():
    """创建 FastAPI 测试客户端"""
    return TestClient(app)


class TestWSClientProtocol:
    """WebSocket 客户端协议测试"""

    def test_connect_and_disconnect(self, client):
        """测试连接和断开"""
        with client.websocket_connect("/ws") as ws:
            # 发送一个简单请求
            request = {"jsonrpc": "2.0", "id": 1, "method": "get_model"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert data["id"] == 1
            assert "model" in data["result"]

    def test_multiple_requests(self, client):
        """测试多个请求"""
        with client.websocket_connect("/ws") as ws:
            # 发送多个请求
            for i in range(3):
                request = {"jsonrpc": "2.0", "id": i, "method": "get_model"}
                ws.send_text(json.dumps(request))

            # 接收所有响应
            responses = []
            for _ in range(3):
                response = ws.receive_text()
                responses.append(json.loads(response))

            ids = [r["id"] for r in responses]
            assert set(ids) == {0, 1, 2}

    def test_error_handling(self, client):
        """测试错误处理"""
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "nonexistent"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert "error" in data
            assert data["error"]["code"] == -32601
