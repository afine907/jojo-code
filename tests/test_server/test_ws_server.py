"""WebSocket Server 单元测试"""

import json

import pytest
from fastapi.testclient import TestClient

from jojo_code.server.ws_server import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestHealthCheck:
    """健康检查测试"""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestWebSocketProtocol:
    """WebSocket 协议测试"""

    def test_connect_and_disconnect(self, client):
        with client.websocket_connect("/ws") as ws:
            # 连接成功即断开
            pass

    def test_invalid_json(self, client):
        with client.websocket_connect("/ws") as ws:
            ws.send_text("not json")
            response = ws.receive_text()
            data = json.loads(response)
            assert data["error"]["code"] == -32700

    def test_method_not_found(self, client):
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "nonexistent"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert data["error"]["code"] == -32601
            assert "nonexistent" in data["error"]["message"]

    def test_get_model(self, client):
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "get_model"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert data["id"] == 1
            assert "model" in data["result"]

    def test_clear(self, client):
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "clear"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert data["result"]["status"] == "ok"

    def test_get_stats(self, client):
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "get_stats"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert "messages" in data["result"]
            assert "tokens" in data["result"]

    def test_permission_mode_get(self, client):
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "permission/mode"}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            # 权限管理器未初始化时返回 error，初始化后返回 ok
            assert data["result"]["status"] in ("ok", "error")

    def test_audit_recent(self, client):
        with client.websocket_connect("/ws") as ws:
            request = {"jsonrpc": "2.0", "id": 1, "method": "audit/recent", "params": {"limit": 5}}
            ws.send_text(json.dumps(request))
            response = ws.receive_text()
            data = json.loads(response)
            assert data["result"]["status"] == "ok"
            assert "results" in data["result"]
