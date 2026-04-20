"""JSON-RPC Server 单元测试"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock

from nano_code.server.protocol import JSONRPCRequest, JSONRPCResponse, JSONRPCNotification, StreamEvent
from nano_code.server.rpc import JSONRPCServer


class TestProtocol:
    """协议类测试"""

    def test_request_from_dict(self):
        """测试请求解析"""
        data = {"jsonrpc": "2.0", "id": "1", "method": "test", "params": {"a": 1}}
        request = JSONRPCRequest.from_dict(data)
        assert request.jsonrpc == "2.0"
        assert request.id == "1"
        assert request.method == "test"
        assert request.params == {"a": 1}

    def test_request_from_dict_minimal(self):
        """测试最小请求"""
        data = {"method": "test"}
        request = JSONRPCRequest.from_dict(data)
        assert request.jsonrpc == "2.0"
        assert request.id is None
        assert request.method == "test"
        assert request.params == {}

    def test_response_to_dict_with_result(self):
        """测试成功响应"""
        response = JSONRPCResponse(id="1", result={"status": "ok"})
        data = response.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "1"
        assert data["result"] == {"status": "ok"}
        assert "error" not in data

    def test_response_to_dict_with_error(self):
        """测试错误响应"""
        response = JSONRPCResponse(id="1", error={"code": -32000, "message": "Error"})
        data = response.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert "error" in data
        assert "result" not in data
        assert data["error"]["code"] == -32000

    def test_notification_to_dict(self):
        """测试通知"""
        notification = JSONRPCNotification(method="stream", params={"type": "response"})
        data = notification.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "stream"
        assert data["params"]["type"] == "response"
        assert "id" not in data

    def test_stream_event_basic(self):
        """测试流式事件"""
        event = StreamEvent(type="response", content="hello")
        data = event.to_dict()
        assert data["type"] == "response"
        assert data["content"] == "hello"
        assert "metadata" not in data

    def test_stream_event_with_metadata(self):
        """测试带元数据的流式事件"""
        event = StreamEvent(
            type="tool_call",
            content="Calling tool...",
            metadata={"toolName": "read_file", "toolArgs": {"path": "/test"}}
        )
        data = event.to_dict()
        assert data["metadata"]["toolName"] == "read_file"


class TestJSONRPCServerValidation:
    """JSON-RPC Server 参数验证测试"""

    def test_validate_params_success(self):
        """测试参数验证成功"""
        server = JSONRPCServer()
        is_valid, error = server._validate_params({"prompt": "hello"}, ["prompt"])
        assert is_valid is True
        assert error is None

    def test_validate_params_missing(self):
        """测试参数验证失败 - 缺失参数"""
        server = JSONRPCServer()
        is_valid, error = server._validate_params({}, ["prompt"])
        assert is_valid is False
        assert "Missing required parameter" in error

    def test_validate_params_none(self):
        """测试参数验证失败 - 参数为 None"""
        server = JSONRPCServer()
        is_valid, error = server._validate_params({"prompt": None}, ["prompt"])
        assert is_valid is False
        assert "cannot be None" in error

    def test_validate_params_multiple(self):
        """测试多参数验证"""
        server = JSONRPCServer()
        is_valid, error = server._validate_params(
            {"name": "test", "args": {}},
            ["name", "args"]
        )
        assert is_valid is True


class TestJSONRPCServerHandlers:
    """JSON-RPC Server 处理器测试"""

    def test_handle_tools_list_empty(self):
        """测试空工具列表"""
        server = JSONRPCServer()
        server.registry = None
        
        result = asyncio.run(server._handle_tools_list({}))
        assert result["tools"] == []

    def test_handle_tools_list_with_tools(self):
        """测试工具列表"""
        server = JSONRPCServer()
        server.registry = Mock()
        server.registry._tools = {
            "read_file": Mock(description="Read a file"),
            "write_file": Mock(description="Write a file"),
        }
        
        result = asyncio.run(server._handle_tools_list({}))
        assert "tools" in result
        assert len(result["tools"]) == 2

    def test_handle_tool_execute_missing_name(self):
        """测试工具执行失败 - 缺少名称"""
        server = JSONRPCServer()
        
        result = asyncio.run(server._handle_tool_execute({"args": {}}))
        assert result["success"] is False
        assert "Missing required parameter" in result["error"]

    def test_handle_tool_execute_no_registry(self):
        """测试工具执行失败 - 无注册表"""
        server = JSONRPCServer()
        server.registry = None
        
        result = asyncio.run(server._handle_tool_execute({"name": "read_file"}))
        assert result["success"] is False
        assert "Registry not initialized" in result["error"]

    def test_handle_tool_execute_success(self):
        """测试工具执行成功"""
        server = JSONRPCServer()
        server.registry = Mock()
        server.registry.execute = Mock(return_value="file content")
        
        result = asyncio.run(server._handle_tool_execute({"name": "read_file", "args": {"path": "/test"}}))
        assert result["success"] is True
        assert result["result"] == "file content"

    def test_handle_config_get_no_settings(self):
        """测试配置获取 - 无设置"""
        server = JSONRPCServer()
        server.settings = None
        
        result = asyncio.run(server._handle_config_get({}))
        assert result["model"] == "gpt-4o-mini"
        assert result["provider"] == "unknown"

    def test_handle_config_get_with_settings(self):
        """测试配置获取 - 有设置"""
        server = JSONRPCServer()
        server.settings = Mock()
        server.settings.model = "gpt-4o"
        server.settings.openai_api_key = "test-key"
        
        result = asyncio.run(server._handle_config_get({}))
        assert result["model"] == "gpt-4o"
        assert result["provider"] == "openai"


class TestStreamEvents:
    """流式事件测试"""

    def test_handle_agent_stream_no_graph(self):
        """测试流式对话 - 无图"""
        server = JSONRPCServer()
        server.graph = None
        
        notifications = []
        def mock_notification(method, params):
            notifications.append(params)
        
        server._send_notification = mock_notification
        
        asyncio.run(server._handle_agent_stream({"prompt": "hello"}))
        
        assert len(notifications) == 1
        assert notifications[0]["type"] == "error"

    def test_handle_agent_stream_empty_prompt(self):
        """测试流式对话 - 空提示"""
        server = JSONRPCServer()
        
        notifications = []
        def mock_notification(method, params):
            notifications.append(params)
        
        server._send_notification = mock_notification
        
        asyncio.run(server._handle_agent_stream({"prompt": ""}))
        
        assert len(notifications) == 1
        assert notifications[0]["type"] == "error"
        assert "cannot be empty" in notifications[0]["content"]

    def test_handle_agent_stream_missing_prompt(self):
        """测试流式对话 - 缺少提示"""
        server = JSONRPCServer()
        
        notifications = []
        def mock_notification(method, params):
            notifications.append(params)
        
        server._send_notification = mock_notification
        
        asyncio.run(server._handle_agent_stream({}))
        
        assert len(notifications) == 1
        assert notifications[0]["type"] == "error"


class TestMethodHandling:
    """方法处理测试"""

    def test_handle_request_unknown_method(self):
        """测试未知方法"""
        server = JSONRPCServer()
        
        responses = []
        def mock_response(resp):
            responses.append(resp)
        
        server._send_response = mock_response
        
        request = JSONRPCRequest(id="1", method="unknown_method")
        asyncio.run(server.handle_request(request))
        
        assert len(responses) == 1
        assert responses[0].error is not None
        assert responses[0].error["code"] == -32601


class TestSignalHandling:
    """信号处理测试"""

    def test_signal_handler(self):
        """测试信号处理"""
        server = JSONRPCServer()
        assert server._running is True
        
        # 模拟信号
        server._signal_handler(2, None)  # SIGINT
        
        assert server._running is False
