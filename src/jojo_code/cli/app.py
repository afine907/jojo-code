"""jojo-code Textual App

主应用入口，整合所有视图组件。
"""

import asyncio
import logging

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from jojo_code.cli.views.chat import ChatView
from jojo_code.cli.views.input_box import InputBox, NewMessage
from jojo_code.cli.views.status_bar import StatusBar

logger = logging.getLogger(__name__)


class JojoCodeApp(App):
    """jojo-code TUI 应用"""

    TITLE = "jojo-code"
    SUB_TITLE = "Python Coding Agent"

    CSS = """
    #chat {
        height: 1fr;
        border: solid $primary;
        margin: 0 1;
    }

    #input-box {
        height: 3;
        margin: 0 1;
    }

    #status-bar {
        height: 1;
        dock: bottom;
        background: $primary-background-lighten-2;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "退出"),
        Binding("ctrl+l", "clear", "清空"),
        Binding("ctrl+p", "toggle_mode", "切换模式"),
    ]

    def __init__(self, server_url: str = "ws://localhost:8080/ws", **kwargs):
        super().__init__(**kwargs)
        self.server_url = server_url
        self._ws_client = None
        self._mode = "build"

    def compose(self) -> ComposeResult:
        yield Header()
        yield ChatView(id="chat")
        yield InputBox(id="input-box")
        yield StatusBar(id="status-bar")
        yield Footer()

    async def on_mount(self) -> None:
        """应用启动时连接 WebSocket"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_connection(False)

        try:
            from jojo_code.cli.ws_client import WSClient

            self._ws_client = WSClient(self.server_url)
            await self._ws_client.connect()
            status_bar.update_connection(True)

            # 获取模型信息
            model = await self._ws_client.get_model()
            status_bar.update_model(model)

            # 获取统计信息
            stats = await self._ws_client.get_stats()
            status_bar.update_stats(
                stats.get("messages", 0),
                stats.get("tokens", 0),
            )
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            chat = self.query_one("#chat", ChatView)
            chat.add_assistant_message(
                f"⚠️ 无法连接到服务: {e}\n请确保服务已启动: jojo-code server start"
            )

    def on_new_message(self, event: NewMessage) -> None:
        """处理新消息"""
        content = event.content

        # 处理斜杠命令
        if content.startswith("/"):
            self._handle_command(content)
            return

        # 发送消息
        asyncio.create_task(self._send_message(content))

    def _handle_command(self, cmd: str) -> None:
        """处理斜杠命令"""
        parts = cmd.strip().split()
        command = parts[0].lower()
        chat = self.query_one("#chat", ChatView)

        if command == "/help":
            help_text = (
                "可用命令:\n"
                "  /mode [plan|build]  - 切换模式\n"
                "  /clear              - 清空对话\n"
                "  /quit, /exit        - 退出"
            )
            chat.add_assistant_message(help_text)

        elif command == "/clear":
            self.action_clear()

        elif command == "/mode":
            if len(parts) > 1:
                self._mode = parts[1] if parts[1] in ("plan", "build") else "build"
            else:
                self._mode = "plan" if self._mode == "build" else "build"
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.update_mode(self._mode)
            chat.add_assistant_message(f"模式已切换为: {self._mode}")

        elif command in ("/quit", "/exit"):
            self.exit()

        else:
            chat.add_assistant_message(f"未知命令: {command}")

    async def _send_message(self, message: str) -> None:
        """发送消息到服务端"""
        chat = self.query_one("#chat", ChatView)
        input_box = self.query_one("#input-box", InputBox)
        status_bar = self.query_one("#status-bar", StatusBar)

        # 显示用户消息
        chat.add_user_message(message)

        # 禁用输入
        input_box.disable()

        # 显示加载状态
        chat.add_loading()

        try:
            if self._ws_client is None:
                from jojo_code.cli.ws_client import WSClient

                self._ws_client = WSClient(self.server_url)
                await self._ws_client.connect()
                status_bar.update_connection(True)

            # 流式接收响应
            full_response = ""
            async for chunk in self._ws_client.stream("chat", {"message": message, "stream": True}):
                if chunk.type == "thinking":
                    pass  # 思考过程不显示

                elif chunk.type == "tool_call":
                    chat.add_tool_call(chunk.tool_name, "running")

                elif chunk.type == "tool_result":
                    chat.update_tool_status(chunk.tool_name, "completed")

                elif chunk.type == "content":
                    full_response += chunk.text

                elif chunk.type == "done":
                    break

            # 移除加载状态，显示完整响应
            chat.remove_loading()
            if full_response:
                chat.add_assistant_message(full_response)

            # 更新统计
            stats = await self._ws_client.get_stats()
            status_bar.update_stats(
                stats.get("messages", 0),
                stats.get("tokens", 0),
            )

        except Exception as e:
            chat.remove_loading()
            chat.add_assistant_message(f"❌ 错误: {e}")
            status_bar.update_connection(False)

        finally:
            input_box.enable()

    def action_clear(self) -> None:
        """清空对话"""
        chat = self.query_one("#chat", ChatView)
        chat.clear_messages()
        if self._ws_client:
            asyncio.create_task(self._ws_client.clear())

    def action_toggle_mode(self) -> None:
        """切换模式"""
        self._mode = "plan" if self._mode == "build" else "build"
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_mode(self._mode)
