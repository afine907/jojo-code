"""Chat View - 消息列表显示组件"""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static


class MessageBubble(Static):
    """单条消息气泡"""

    def __init__(self, role: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.content = content

    def render(self) -> str:
        if self.role == "user":
            return f"[bold cyan]👤 {self.content}[/bold cyan]"
        else:
            return f"[white]{self.content}[/white]"


class ToolCallIndicator(Static):
    """工具调用状态指示器"""

    def __init__(self, tool_name: str, status: str = "running", **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.status = status

    def render(self) -> str:
        icons = {"pending": "○", "running": "◐", "completed": "●", "error": "✗"}
        icon = icons.get(self.status, "?")
        return f"[dim]{icon} {self.tool_name}[/dim]"


class ChatView(VerticalScroll):
    """聊天消息列表视图"""

    def compose(self) -> ComposeResult:
        yield Static(
            "[dim]输入问题开始对话，/help 查看命令[/dim]",
            id="placeholder",
        )

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        # 移除占位符
        placeholder = self.query_one("#placeholder", Static)
        if placeholder:
            placeholder.remove()

        bubble = MessageBubble("user", content)
        self.mount(bubble)
        self.scroll_end(animate=False)

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        bubble = MessageBubble("assistant", content)
        self.mount(bubble)
        self.scroll_end(animate=False)

    def add_tool_call(self, tool_name: str, status: str = "running") -> ToolCallIndicator:
        """添加工具调用指示器"""
        indicator = ToolCallIndicator(tool_name, status)
        self.mount(indicator)
        self.scroll_end(animate=False)
        return indicator

    def update_tool_status(self, tool_name: str, status: str) -> None:
        """更新工具调用状态"""
        for indicator in self.query(ToolCallIndicator):
            if indicator.tool_name == tool_name:
                indicator.status = status
                indicator.refresh()
                break

    def add_loading(self) -> Static:
        """添加加载指示器"""
        loading = Static("[dim]  ○[/dim]", id="loading")
        self.mount(loading)
        self.scroll_end(animate=False)
        return loading

    def remove_loading(self) -> None:
        """移除加载指示器"""
        loading = self.query_one("#loading", Static)
        if loading:
            loading.remove()

    def clear_messages(self) -> None:
        """清空所有消息"""
        self.remove_children()
        self.mount(
            Static(
                "[dim]输入问题开始对话，/help 查看命令[/dim]",
                id="placeholder",
            )
        )
