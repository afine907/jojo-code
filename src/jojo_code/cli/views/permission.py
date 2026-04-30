"""Permission Modal - 权限确认弹窗"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class PermissionModal(ModalScreen[bool]):
    """权限确认弹窗

    当 Agent 需要执行敏感操作时，弹出此窗口请求用户确认。
    """

    CSS = """
    PermissionModal {
        align: center middle;
    }

    #perm-container {
        width: 60;
        max-width: 90%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #perm-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        text-style: bold;
    }

    #perm-info {
        width: 100%;
        margin-bottom: 1;
    }

    #perm-buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    #perm-buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("y", "confirm", "允许"),
        ("n", "deny", "拒绝"),
        ("a", "always", "始终允许"),
        ("escape", "deny", "拒绝"),
    ]

    def __init__(self, tool_name: str, action: str, params: dict, **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.action = action
        self.params = params

    def compose(self) -> ComposeResult:
        with Vertical(id="perm-container"):
            yield Static("⚠️ 权限确认", id="perm-title")
            yield Static(
                f"工具: [bold]{self.tool_name}[/bold]\n操作: {self.action}\n参数: {self.params}",
                id="perm-info",
            )
            with Horizontal(id="perm-buttons"):
                yield Button("允许 (y)", variant="success", id="allow")
                yield Button("始终允许 (a)", variant="primary", id="always")
                yield Button("拒绝 (n)", variant="error", id="deny")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "allow":
            self.dismiss(True)
        elif event.button.id == "always":
            # 返回 True 并标记为 always
            self.app._always_allow = getattr(self.app, "_always_allow", set())
            self.app._always_allow.add(self.tool_name)
            self.dismiss(True)
        elif event.button.id == "deny":
            self.dismiss(False)

    def action_confirm(self) -> None:
        """键盘快捷键：允许"""
        self.dismiss(True)

    def action_deny(self) -> None:
        """键盘快捷键：拒绝"""
        self.dismiss(False)

    def action_always(self) -> None:
        """键盘快捷键：始终允许"""
        self.app._always_allow = getattr(self.app, "_always_allow", set())
        self.app._always_allow.add(self.tool_name)
        self.dismiss(True)
