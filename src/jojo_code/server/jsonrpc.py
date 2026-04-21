"""JSON-RPC Server for jojo-code CLI.

This module implements a JSON-RPC server that communicates via stdio,
allowing TypeScript CLI to interact with Python Agent core.
"""

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class JsonRpcRequest:
    """JSON-RPC 请求"""

    jsonrpc: str
    id: str | int
    method: str
    params: dict[str, Any] | None = None


@dataclass
class JsonRpcResponse:
    """JSON-RPC 响应"""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    result: Any = None
    error: dict | None = None

    def to_json(self) -> str:
        data = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error:
            data["error"] = self.error
        else:
            data["result"] = self.result
        return json.dumps(data)


class JsonRpcServer:
    """JSON-RPC Server via stdio"""

    def __init__(self):
        self.handlers: dict[str, Callable] = {}
        self._buffer = ""

    def method(self, name: str):
        """装饰器：注册方法处理器"""

        def decorator(func: Callable) -> Callable:
            self.handlers[name] = func
            return func

        return decorator

    def register(self, name: str, handler: Callable):
        """注册方法处理器"""
        self.handlers[name] = handler

    def _parse_request(self, line: str) -> JsonRpcRequest | None:
        """解析 JSON-RPC 请求"""
        try:
            data = json.loads(line)
            return JsonRpcRequest(
                jsonrpc=data.get("jsonrpc", "2.0"),
                id=data.get("id"),
                method=data["method"],
                params=data.get("params"),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def _handle_request(self, request: JsonRpcRequest) -> JsonRpcResponse:
        """处理请求"""
        handler = self.handlers.get(request.method)

        if handler is None:
            return JsonRpcResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}",
                },
            )

        try:
            params = request.params or {}
            result = handler(**params)
            return JsonRpcResponse(id=request.id, result=result)
        except Exception as e:
            return JsonRpcResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": str(e),
                },
            )

    def run(self):
        """运行服务器"""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            request = self._parse_request(line)
            if request is None:
                continue

            response = self._handle_request(request)
            print(response.to_json(), flush=True)

    def send_notification(self, method: str, params: dict[str, Any]):
        """发送通知"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        print(json.dumps(notification), flush=True)

    def send_stream_chunk(self, request_id: str | int, chunk: dict[str, Any]):
        """发送流式响应块"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": chunk,
        }
        print(json.dumps(response), flush=True)


# 全局服务器实例
_server: JsonRpcServer | None = None


def get_server() -> JsonRpcServer:
    """获取全局服务器实例"""
    global _server
    if _server is None:
        _server = JsonRpcServer()
    return _server
