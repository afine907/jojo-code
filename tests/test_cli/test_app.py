"""Textual App 单元测试"""

from jojo_code.cli.app import JojoCodeApp
from jojo_code.cli.views.chat import ChatView, MessageBubble, ToolCallIndicator
from jojo_code.cli.views.status_bar import StatusBar


class TestChatView:
    """ChatView 测试"""

    def test_chat_view_compose(self):
        """测试 ChatView 组成"""
        chat = ChatView()
        assert chat is not None

    def test_message_bubble_render_user(self):
        """测试用户消息渲染"""
        bubble = MessageBubble("user", "Hello")
        assert bubble.role == "user"
        assert bubble.content == "Hello"

    def test_message_bubble_render_assistant(self):
        """测试助手消息渲染"""
        bubble = MessageBubble("assistant", "Hi there")
        assert bubble.role == "assistant"
        assert bubble.content == "Hi there"

    def test_tool_call_indicator(self):
        """测试工具调用指示器"""
        indicator = ToolCallIndicator("read_file", "running")
        assert indicator.tool_name == "read_file"
        assert indicator.status == "running"


class TestStatusBar:
    """StatusBar 测试"""

    def test_status_bar_init(self):
        """测试状态栏初始化"""
        status = StatusBar()
        assert status.model == "unknown"
        assert status.mode == "build"
        assert status.connected is False

    def test_update_model(self):
        """测试更新模型"""
        status = StatusBar()
        status.update_model("gpt-4o")
        assert status.model == "gpt-4o"

    def test_update_connection(self):
        """测试更新连接状态"""
        status = StatusBar()
        status.update_connection(True)
        assert status.connected is True


class TestJojoCodeApp:
    """JojoCodeApp 测试"""

    def test_app_init(self):
        """测试应用初始化"""
        app = JojoCodeApp(server_url="ws://test:8080/ws")
        assert app.server_url == "ws://test:8080/ws"
        assert app._mode == "build"
