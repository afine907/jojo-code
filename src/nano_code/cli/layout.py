"""CLI 分屏布局模块

提供终端分屏布局功能：
- 垂直分屏：上下两部分
- 水平分屏：左右两部分
- 自适应布局
- 边框和标题
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum

from rich.console import Console, ConsoleOptions, RenderResult
from rich.layout import Layout as RichLayout
from rich.panel import Panel
from rich.text import Text


class LayoutMode(Enum):
    """布局模式枚举"""

    SINGLE = "single"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class PaneConfig:
    """分屏配置"""

    title: str = ""
    border_style: str = "blue"
    min_size: int = 3


class LayoutManager:
    """布局管理器

    支持三种布局模式:
    - SINGLE: 单面板（默认）
    - HORIZONTAL: 左右分屏（对话 | 工具输出）
    - VERTICAL: 上下分屏（对话 / 工具输出）

    支持快捷键切换布局（F3 或 Ctrl+L）
    支持面板间焦点切换
    """

    def __init__(self, initial_mode: LayoutMode = LayoutMode.SINGLE) -> None:
        self._mode = initial_mode
        self._left_content: str | Text = ""
        self._right_content: str | Text = ""
        self._left_title: str = "对话"
        self._right_title: str = "工具输出"
        self._focused_pane: str = "left"
        self._console = Console()

    @property
    def mode(self) -> LayoutMode:
        """获取当前布局模式"""
        return self._mode

    @property
    def is_single(self) -> bool:
        """是否为单面板模式"""
        return self._mode == LayoutMode.SINGLE

    @property
    def is_horizontal(self) -> bool:
        """是否为水平分屏模式"""
        return self._mode == LayoutMode.HORIZONTAL

    @property
    def is_vertical(self) -> bool:
        """是否为垂直分屏模式"""
        return self._mode == LayoutMode.VERTICAL

    @property
    def focused_pane(self) -> str:
        """获取当前聚焦的面板"""
        return self._focused_pane

    def set_mode(self, mode: LayoutMode) -> None:
        """设置布局模式

        Args:
            mode: 布局模式
        """
        self._mode = mode

    def toggle_mode(self) -> LayoutMode:
        """切换布局模式

        循环切换: SINGLE -> HORIZONTAL -> VERTICAL -> SINGLE

        Returns:
            切换后的布局模式
        """
        modes = [LayoutMode.SINGLE, LayoutMode.HORIZONTAL, LayoutMode.VERTICAL]
        current_index = modes.index(self._mode)
        next_index = (current_index + 1) % len(modes)
        self._mode = modes[next_index]
        return self._mode

    def set_left_content(self, content: str | Text) -> None:
        """设置左侧/上方内容

        Args:
            content: 内容
        """
        self._left_content = content

    def set_right_content(self, content: str | Text) -> None:
        """设置右侧/下方内容

        Args:
            content: 内容
        """
        self._right_content = content

    def set_tool_output(self, content: str | Text) -> None:
        """设置工具输出内容

        Args:
            content: 内容
        """
        self._right_content = content

    def set_conversation(self, content: str | Text) -> None:
        """设置对话内容

        Args:
            content: 内容
        """
        self._left_content = content

    def get_left_content(self) -> str | Text:
        """获取左侧/上方内容"""
        return self._left_content

    def get_right_content(self) -> str | Text:
        """获取右侧/下方内容"""
        return self._right_content

    def focus_left(self) -> str:
        """聚焦左侧面板

        Returns:
            面板名称
        """
        self._focused_pane = "left"
        return self._focused_pane

    def focus_right(self) -> str:
        """聚焦右侧面板

        Returns:
            面板名称
        """
        self._focused_pane = "right"
        return self._focused_pane

    def toggle_focus(self) -> str:
        """切换面板焦点

        Returns:
            聚焦的面板名称
        """
        if self._focused_pane == "left":
            self._focused_pane = "right"
        else:
            self._focused_pane = "left"
        return self._focused_pane

    def create_layout(self) -> Layout:
        """创建布局对象

        Returns:
            Layout 实例
        """
        if self._mode == LayoutMode.SINGLE:
            return Layout(self._console)
        elif self._mode == LayoutMode.HORIZONTAL:
            return create_horizontal_layout(
                self._left_content,
                self._right_content,
                self._left_title,
                self._right_title,
                self._console,
            )
        else:
            return create_vertical_layout(
                self._left_content,
                self._right_content,
                self._left_title,
                self._right_title,
                self._console,
            )

    def __str__(self) -> str:
        return f"LayoutManager(mode={self._mode.value}, focused={self._focused_pane})"


class SplitPaneLayout:
    """分屏布局管理器"""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self._panes: list[dict] = []

    def add_pane(
        self,
        content: str | Text,
        title: str = "",
        border_style: str = "blue",
    ) -> None:
        """添加分屏

        Args:
            content: 分屏内容
            title: 分屏标题
            border_style: 边框样式
        """
        self._panes.append(
            {
                "content": content,
                "title": title,
                "border_style": border_style,
            }
        )

    def clear(self) -> None:
        """清空所有分屏"""
        self._panes.clear()

    def render_vertical(self) -> Generator[str, None, None]:
        """渲染垂直分屏（上下布局）

        Yields:
            渲染后的面板字符串
        """
        height = self.console.size.height
        pane_height = (
            max(3, (height - len(self._panes) + 1) // len(self._panes)) if self._panes else 3
        )

        for _i, pane in enumerate(self._panes):
            content = pane["content"]
            title = pane["title"]
            border = pane["border_style"]

            if isinstance(content, str):
                content = Text(content)

            yield str(
                Panel(
                    content,
                    title=title,
                    border_style=border,
                    height=pane_height,
                )
            )

    def render_horizontal(self) -> RichLayout:
        """渲染水平分屏（左右布局）

        Returns:
            RichLayout 对象
        """
        layout = RichLayoutSplit(self.console)
        layout.split_column(*[self._create_layout_pane(p) for p in self._panes])
        return layout

    def _create_layout_pane(self, pane: dict) -> LayoutPane:
        """创建布局面板"""
        return LayoutPane(
            pane["content"],
            title=pane["title"],
            border_style=pane["border_style"],
        )


class LayoutPane:
    """单个布局面板"""

    def __init__(
        self,
        content: str | Text,
        title: str = "",
        border_style: str = "blue",
    ) -> None:
        self.content = content
        self.title = title
        self.border_style = border_style

    def __rich__(self) -> Panel:
        return Panel(
            self.content,
            title=self.title,
            border_style=self.border_style,
        )


class Layout:
    """Rich Layout 包装器"""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self._layout = RichLayout(self.console)

    def split_column(self, *panes: LayoutPane) -> None:
        """垂直分屏"""
        self._layout.split_column(*[self._pane_to_rich(p) for p in panes])

    def split_row(self, *panes: LayoutPane) -> None:
        """水平分屏"""
        self._layout.split_row(*[self._pane_to_rich(p) for p in panes])

    def _pane_to_rich(self, pane: LayoutPane) -> Panel:
        return Panel(
            pane.content,
            title=pane.title,
            border_style=pane.border_style,
        )

    def __rich__(self) -> RenderResult:
        yield self._layout


def create_vertical_layout(
    top_content: str | Text,
    bottom_content: str | Text,
    top_title: str = "",
    bottom_title: str = "",
    console: Console | None = None,
) -> SplitPaneLayout:
    """创建垂直分屏布局

    Args:
        top_content: 上部内容
        bottom_content: 下部内容
        top_title: 上部标题
        bottom_title: 下部标题
        console: Console 实例

    Returns:
        SplitPaneLayout 实例
    """
    layout = SplitPaneLayout(console)
    layout.add_pane(top_content, top_title)
    layout.add_pane(bottom_content, bottom_title)
    return layout


def create_horizontal_layout(
    left_content: str | Text,
    right_content: str | Text,
    left_title: str = "",
    right_title: str = "",
    console: Console | None = None,
) -> Layout:
    """创建水平分屏布局

    Args:
        left_content: 左侧内容
        right_content: 右侧内容
        left_title: 左侧标题
        right_title: 右侧标题
        console: Console 实例

    Returns:
        Layout 实例
    """
    layout = Layout(console)
    layout.split_row(
        LayoutPane(left_content, left_title),
        LayoutPane(right_content, right_title),
    )
    return layout


class RichLayoutSplit(RichLayout):
    """简化的 Rich Layout 分屏实现"""

    def __init__(self, console: Console) -> None:
        super().__init__(console)
        self._renderable: list = []

    def split_column(self, *renderables: Panel) -> None:
        """垂直分屏"""
        self._renderable = list(renderables)

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> RenderResult:
        height = options.height
        _pane_height = max(3, (height - 1) // max(1, len(self._renderable)))

        yield from self._renderable
