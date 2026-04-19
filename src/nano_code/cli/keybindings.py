"""CLI 快捷键系统模块

提供键盘快捷键功能：
- 快捷键绑定定义
- 快捷键处理
- 默认快捷键配置
- 提示信息显示
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from rich.console import Console
from rich.text import Text

KeyType = Literal["ctrl", "alt", "shift", "key"]


@dataclass
class KeyBinding:
    """快捷键绑定"""

    keys: str
    description: str
    handler: Callable[[], None] | None = None
    category: str = "general"
    hidden: bool = False


@dataclass
class KeyBindingGroup:
    """快捷键组"""

    name: str
    description: str
    bindings: list[KeyBinding] = field(default_factory=list)


class KeyBindingManager:
    """快捷键管理器"""

    def __init__(self) -> None:
        self._bindings: dict[str, KeyBinding] = {}
        self._groups: list[KeyBindingGroup] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        """注册默认快捷键"""
        general = KeyBindingGroup(
            name="General",
            description="General commands",
            bindings=[
                KeyBinding("ctrl+c", "Interrupt current operation", category="general"),
                KeyBinding("ctrl+d", "Exit program", category="general"),
                KeyBinding("ctrl+l", "Clear screen", category="general"),
                KeyBinding("ctrl+r", "Reset session", category="general"),
                KeyBinding("ctrl+s", "Save session", category="general"),
                KeyBinding("f1", "Show help", category="general"),
                KeyBinding("f2", "Toggle mode (Plan/Build)", category="general"),
                KeyBinding("f3", "Toggle layout", category="general"),
                KeyBinding("tab", "New line / complete", category="general"),
                KeyBinding("?", "Show help", category="general"),
                KeyBinding("ctrl+u", "Clear input", category="edit"),
                KeyBinding("ctrl+a", "Go to line start", category="edit"),
                KeyBinding("ctrl+e", "Go to line end", category="edit"),
            ],
        )

        navigation = KeyBindingGroup(
            name="Navigation",
            description="Navigation",
            bindings=[
                KeyBinding("ctrl+p", "Previous", category="nav"),
                KeyBinding("ctrl+n", "Next", category="nav"),
                KeyBinding("ctrl+b", "Page up", category="nav"),
                KeyBinding("ctrl+f", "Page down", category="nav"),
                KeyBinding("home", "Go to start", category="nav"),
                KeyBinding("end", "Go to end", category="nav"),
            ],
        )

        diff = KeyBindingGroup(
            name="Diff",
            description="File diff",
            bindings=[
                KeyBinding("ctrl+shift+d", "Previous diff", category="diff"),
                KeyBinding("ctrl+o", "Open file", category="diff"),
            ],
        )

        self._groups = [general, navigation, diff]

        for group in self._groups:
            for binding in group.bindings:
                self._bindings[binding.keys.lower()] = binding

    def register(self, binding: KeyBinding) -> None:
        """注册快捷键

        Args:
            binding: 快捷键绑定
        """
        self._bindings[binding.keys.lower()] = binding

    def unregister(self, keys: str) -> None:
        """注销快捷键

        Args:
            keys: 快捷键
        """
        self._bindings.pop(keys.lower(), None)

    def get(self, keys: str) -> KeyBinding | None:
        """获取快捷键

        Args:
            keys: 快捷键

        Returns:
            KeyBinding 或 None
        """
        return self._bindings.get(keys.lower())

    def get_bindings(self, category: str | None = None) -> list[KeyBinding]:
        """获取快捷键列表

        Args:
            category: 分类过滤

        Returns:
            KeyBinding 列表
        """
        if category:
            return [b for b in self._bindings.values() if b.category == category]
        return list(self._bindings.values())

    def get_groups(self) -> list[KeyBindingGroup]:
        """获取快捷键组

        Returns:
            KeyBindingGroup 列表
        """
        return self._groups


_default_bindings = KeyBindingManager()


def get_keybindings() -> KeyBindingManager:
    """获取默认快捷键管理器"""
    return _default_bindings


def get_default_bindings() -> KeyBindingManager:
    """获取默认快捷键管理器（已弃用，请使用 get_keybindings）"""
    return _default_bindings


def show_keybindings(
    category: str | None = None,
    console: Console | None = None,
) -> None:
    """显示快捷键帮助

    Args:
        category: 分类过滤
        console: Console 实例
    """
    console = console or Console()
    bindings = _default_bindings.get_bindings(category)

    if not bindings:
        console.print("[dim]No keybindings found[/dim]")
        return

    grouped: dict[str, list[KeyBinding]] = {}
    for b in bindings:
        if b.category not in grouped:
            grouped[b.category] = []
        grouped[b.category].append(b)

    for cat, binds in grouped.items():
        console.print(f"\n[bold]{cat.upper()}:[/bold]")
        for b in binds:
            console.print(f"  [cyan]{b.keys:20}[/cyan] {b.description}")


def format_keybinding(key: str) -> str:
    """格式化快捷键显示

    Args:
        key: 快捷键

    Returns:
        格式化的字符串
    """
    key = key.lower()
    replacements = {
        "ctrl": "^",
        "shift": "Shift+",
        "alt": "Alt+",
    }

    result = key
    for old, new in replacements.items():
        if result.startswith(old + "+"):
            result = new + result[len(old) + 1 :]
        result = result.replace(old + "+", new)

    return result


def is_matching(
    pressed: str,
    binding: str,
) -> bool:
    """检查按键是否匹配

    Args:
        pressed: 按下的键
        binding: 绑定的键

    Returns:
        是否匹配
    """
    return pressed.lower() == binding.lower()


class KeyHint:
    """快捷键提示"""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self._hints: list[tuple[str, str]] = []

    def add(self, key: str, description: str) -> None:
        """添加提示

        Args:
            key: 快捷键
            description: 描述
        """
        self._hints.append((key, description))

    def render(self) -> Text:
        """渲染提示"""
        text = Text()
        for i, (key, desc) in enumerate(self._hints):
            if i > 0:
                text.append("  ")
            text.append(f"[dim]{format_keybinding(key)}[/dim]: {desc}")
        return text

    def clear(self) -> None:
        """清空提示"""
        self._hints.clear()

    def __rich__(self) -> Text:
        return self.render()


# 全局快捷键提示实例
default_hint = KeyHint()


def get_key_hint() -> KeyHint:
    """获取快捷键提示实例"""
    return default_hint
