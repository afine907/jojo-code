#!/usr/bin/env python3
"""JSON-RPC Server for Nano Code CLI"""

import asyncio
import json
import signal
import sys
from typing import Any, Optional

from .protocol import JSONRPCRequest, JSONRPCResponse, JSONRPCNotification, StreamEvent


class JSONRPCServer:
    """JSON-RPC 2.0 Server over stdio"""

    def __init__(self):
        self.graph = None
        self.registry = None
        self.settings = None
        self._running = True
        self._initialize()

    def _initialize(self):
        """初始化 Agent 组件"""
        try:
            from nano_code.agent.graph import get_agent_graph
            from nano_code.tools.registry import get_tool_registry
            from nano_code.core.config import get_settings

            self.graph = get_agent_graph()
            self.registry = get_tool_registry()
            self.settings = get_settings()
        except ImportError as e:
            print(f"Warning: Could not initialize agent: {e}", file=sys.stderr)

    def _send_response(self, response: JSONRPCResponse) -> None:
        """发送响应到 stdout"""
        sys.stdout.write(json.dumps(response.to_dict()) + "\n")
        sys.stdout.flush()

    def _send_notification(self, method: str, params: dict) -> None:
        """发送通知到 stdout"""
        notification = JSONRPCNotification(method=method, params=params)
        sys.stdout.write(json.dumps(notification.to_dict()) + "\n")
        sys.stdout.flush()

    def _validate_params(
        self, params: dict, required: list[str]
    ) -> tuple[bool, Optional[str]]:
        """验证必需参数

        Returns:
            (is_valid, error_message)
        """
        for key in required:
            if key not in params:
                return False, f"Missing required parameter: {key}"
            if params[key] is None:
                return False, f"Parameter '{key}' cannot be None"
        return True, None

    async def handle_request(self, request: JSONRPCRequest) -> None:
        """处理 JSON-RPC 请求"""
        method = request.method
        params = request.params or {}

        # 方法映射
        handlers = {
            "agent.stream": self._handle_agent_stream,
            "tools.list": self._handle_tools_list,
            "tool.execute": self._handle_tool_execute,
            "config.get": self._handle_config_get,
            "config.set": self._handle_config_set,
        }

        handler = handlers.get(method)
        if not handler:
            self._send_response(
                JSONRPCResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {method}"},
                )
            )
            return

        try:
            result = await handler(params)
            # 流式方法不返回响应
            if method != "agent.stream":
                self._send_response(JSONRPCResponse(id=request.id, result=result))
        except Exception as e:
            self._send_response(
                JSONRPCResponse(id=request.id, error={"code": -32000, "message": str(e)})
            )

    async def _handle_agent_stream(self, params: dict) -> None:
        """流式对话处理"""
        # 输入验证
        is_valid, error = self._validate_params(params, ["prompt"])
        if not is_valid:
            self._send_notification(
                "stream", StreamEvent(type="error", content=error).to_dict()
            )
            return

        prompt = params.get("prompt", "")
        if not prompt.strip():
            self._send_notification(
                "stream", StreamEvent(type="error", content="Prompt cannot be empty").to_dict()
            )
            return

        mode = params.get("mode", "build")

        if not self.graph:
            self._send_notification(
                "stream", StreamEvent(type="error", content="Agent not initialized").to_dict()
            )
            return

        from nano_code.agent.state import create_initial_state

        state = create_initial_state(prompt, mode=mode)

        try:
            # 使用单独的状态跟踪处理进度
            processed_tool_calls = set()
            
            for chunk in self.graph.stream(state):
                # 检查是否应该停止
                if not self._running:
                    break
                    
                for node_name, node_output in chunk.items():
                    if node_name == "thinking":
                        # 响应内容
                        for msg in node_output.get("messages", []):
                            content = (
                                msg.get("content", "")
                                if isinstance(msg, dict)
                                else getattr(msg, "content", "")
                            )
                            if content:
                                self._send_notification(
                                    "stream", StreamEvent(type="response", content=content).to_dict()
                                )

                        # 工具调用 - 使用 ID 去重
                        for tc in node_output.get("tool_calls", []):
                            tc_id = tc.get("id", f"{tc['name']}_{id(tc['args'])}")
                            if tc_id not in processed_tool_calls:
                                processed_tool_calls.add(tc_id)
                                self._send_notification(
                                    "stream",
                                    StreamEvent(
                                        type="tool_call",
                                        content=f"Calling {tc['name']}...",
                                        metadata={"toolName": tc["name"], "toolArgs": tc["args"]},
                                    ).to_dict(),
                                )

                    elif node_name == "execute":
                        for result in node_output.get("tool_results", []):
                            self._send_notification(
                                "stream",
                                StreamEvent(
                                    type="tool_result",
                                    content=result[:500] + "..." if len(result) > 500 else result,
                                ).to_dict(),
                            )

            self._send_notification("stream", StreamEvent(type="done", content="").to_dict())

        except Exception as e:
            self._send_notification("stream", StreamEvent(type="error", content=str(e)).to_dict())

    async def _handle_tools_list(self, params: dict) -> dict:
        """获取工具列表"""
        tools = []
        if self.registry:
            for name, tool in self.registry._tools.items():
                tools.append(
                    {
                        "name": name,
                        "description": getattr(tool, "description", ""),
                        "parameters": {},
                    }
                )
        return {"tools": tools}

    async def _handle_tool_execute(self, params: dict) -> dict:
        """执行工具"""
        # 输入验证
        is_valid, error = self._validate_params(params, ["name"])
        if not is_valid:
            return {"success": False, "error": error}

        if not self.registry:
            return {"success": False, "error": "Registry not initialized"}

        name = params.get("name")
        args = params.get("args", {})

        try:
            result = self.registry.execute(name, args)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_config_get(self, params: dict) -> dict:
        """获取配置"""
        if not self.settings:
            return {"model": "gpt-4o-mini", "provider": "unknown"}
        return {
            "model": self.settings.model,
            "provider": "openai" if self.settings.openai_api_key else "unknown",
        }

    async def _handle_config_set(self, params: dict) -> dict:
        """设置配置"""
        # TODO: 实现配置持久化
        return {"success": True}

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号处理"""
        self._running = False

    async def run(self) -> None:
        """运行服务器"""
        print("Nano Code JSON-RPC Server started", file=sys.stderr)
        
        self._setup_signal_handlers()

        loop = asyncio.get_event_loop()

        while self._running:
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                request = JSONRPCRequest.from_dict(data)
                await self.handle_request(request)

            except json.JSONDecodeError:
                self._send_response(
                    JSONRPCResponse(id=None, error={"code": -32700, "message": "Parse error"})
                )
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
        
        print("Nano Code JSON-RPC Server stopped", file=sys.stderr)


def main():
    server = JSONRPCServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
