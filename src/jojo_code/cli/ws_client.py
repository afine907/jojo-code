"""WebSocket Client for jojo-code CLI.

通过 WebSocket 连接 jojo-code Server，发送 JSON-RPC 请求并接收响应。
支持同步请求和流式响应。

用法:
    async with WSClient("ws://localhost:8080/ws") as client:
        result = await client.request("get_model")
        async for chunk in client.stream("chat", {"message": "hello"}):
            print(chunk)
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

import websockets
import websockets.exceptions

logger = logging.getLogger(__name__)


@dataclass
class StreamChunk:
    """流式响应块"""

    type: str  # thinking, tool_call, tool_result, content, done, error
    text: str = ""
    tool_name: str = ""
    args: dict = field(default_factory=dict)
    result: str = ""
    message: str = ""


class WSClient:
    """WebSocket JSON-RPC 客户端"""

    def __init__(self, url: str = "ws://localhost:8080/ws"):
        """初始化客户端

        Args:
            url: WebSocket 服务地址
        """
        self.url = url
        self._ws = None
        self._request_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._stream_queues: dict[str, asyncio.Queue] = {}
        self._receive_task = None
        self._connected = False

    async def connect(self) -> None:
        """建立 WebSocket 连接"""
        if self._connected:
            return

        try:
            self._ws = await websockets.connect(self.url)
            self._connected = True
            # 启动接收循环
            self._receive_task = asyncio.create_task(self._receive_loop())
            logger.info(f"Connected to {self.url}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        """断开连接"""
        self._connected = False
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        if self._ws:
            await self._ws.close()
            self._ws = None
        logger.info("Disconnected")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

    async def _receive_loop(self):
        """接收消息循环"""
        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {message}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed")
            self._connected = False
        except asyncio.CancelledError:
            pass

    async def _handle_message(self, data: dict):
        """处理接收到的消息"""
        req_id = data.get("id")

        # 检查是否是流式响应
        result = data.get("result", {})
        if isinstance(result, dict):
            # 流式响应：放入对应的队列
            if req_id in self._stream_queues:
                await self._stream_queues[req_id].put(result)
                return

        # 普通响应：放入 pending 队列
        if req_id in self._pending:
            future = self._pending.pop(req_id)
            if not future.done():
                future.set_result(data)

    def _next_id(self) -> int:
        """生成下一个请求 ID"""
        self._request_id += 1
        return self._request_id

    async def request(self, method: str, params: dict[str, Any] | None = None) -> dict:
        """发送同步 JSON-RPC 请求

        Args:
            method: 方法名
            params: 参数

        Returns:
            响应结果
        """
        if not self._connected:
            await self.connect()

        req_id = self._next_id()
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        # 创建 Future
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._pending[req_id] = future

        # 发送请求
        await self._ws.send(json.dumps(request))

        # 等待响应（超时 300 秒，Agent 可能需要较长时间）
        try:
            response = await asyncio.wait_for(future, timeout=300)
        except TimeoutError:
            self._pending.pop(req_id, None)
            raise TimeoutError(f"Request timed out: {method}") from None

        # 检查错误
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"RPC error {error.get('code')}: {error.get('message')}")

        return response.get("result", {})

    async def stream(
        self, method: str, params: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """发送流式 JSON-RPC 请求

        Args:
            method: 方法名
            params: 参数

        Yields:
            流式响应块
        """
        if not self._connected:
            await self.connect()

        req_id = self._next_id()
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": {**(params or {}), "stream": True},
        }

        # 创建流式队列
        queue: asyncio.Queue = asyncio.Queue()
        self._stream_queues[req_id] = queue

        # 发送请求
        await self._ws.send(json.dumps(request))

        try:
            while True:
                chunk = await queue.get()

                msg_type = chunk.get("type", "")
                if msg_type == "done":
                    break

                if msg_type == "error":
                    raise RuntimeError(chunk.get("message", "Stream error"))

                yield StreamChunk(
                    type=msg_type,
                    text=chunk.get("text", ""),
                    tool_name=chunk.get("tool_name", ""),
                    args=chunk.get("args", {}),
                    result=chunk.get("result", ""),
                    message=chunk.get("message", ""),
                )
        finally:
            self._stream_queues.pop(req_id, None)

    async def chat(self, message: str, stream: bool = False) -> dict | AsyncGenerator:
        """聊天快捷方法

        Args:
            message: 用户消息
            stream: 是否流式

        Returns:
            非流式返回结果 dict，流式返回 AsyncGenerator
        """
        if stream:
            return self.stream("chat", {"message": message})
        return await self.request("chat", {"message": message})

    async def clear(self) -> dict:
        """清空对话历史"""
        return await self.request("clear")

    async def get_model(self) -> str:
        """获取当前模型"""
        result = await self.request("get_model")
        return result.get("model", "unknown")

    async def get_stats(self) -> dict:
        """获取会话统计"""
        return await self.request("get_stats")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # HTTP 健康检查（非 WebSocket）
            import aiohttp

            http_url = self.url.replace("ws://", "http://").replace("/ws", "/health")
            async with aiohttp.ClientSession() as session:
                async with session.get(http_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception:
            return False
