"""CLI 布局模块测试"""

import pytest

from jojo_code.cli.layout import Layout, LayoutManager, LayoutMode, SplitPaneLayout


class TestLayoutMode:
    """测试 LayoutMode 枚举"""

    def test_single_mode_value(self):
        """测试 SINGLE 模式值"""
        assert LayoutMode.SINGLE.value == "single"

    def test_horizontal_mode_value(self):
        """测试 HORIZONTAL 模式值"""
        assert LayoutMode.HORIZONTAL.value == "horizontal"

    def test_vertical_mode_value(self):
        """测试 VERTICAL 模式值"""
        assert LayoutMode.VERTICAL.value == "vertical"

    def test_mode_names(self):
        """测试模式名称"""
        assert LayoutMode.SINGLE.name == "SINGLE"
        assert LayoutMode.HORIZONTAL.name == "HORIZONTAL"
        assert LayoutMode.VERTICAL.name == "VERTICAL"

    def test_str_method(self):
        """测试 __str__ 方法"""
        assert str(LayoutMode.SINGLE) == "LayoutMode.SINGLE"
        assert str(LayoutMode.HORIZONTAL) == "LayoutMode.HORIZONTAL"
        assert str(LayoutMode.VERTICAL) == "LayoutMode.VERTICAL"


class TestLayoutManager:
    """测试 LayoutManager 类"""

    @pytest.fixture
    def manager(self):
        """创建 LayoutManager 实例"""
        return LayoutManager()

    @pytest.fixture
    def horizontal_manager(self):
        """创建 HORIZONTAL 模式的 LayoutManager 实例"""
        return LayoutManager(initial_mode=LayoutMode.HORIZONTAL)

    @pytest.fixture
    def vertical_manager(self):
        """创建 VERTICAL 模式的 LayoutManager 实例"""
        return LayoutManager(initial_mode=LayoutMode.VERTICAL)

    def test_default_mode_is_single(self, manager):
        """测试默认初始模式为 SINGLE"""
        assert manager.mode == LayoutMode.SINGLE

    def test_custom_initial_mode(self, horizontal_manager):
        """测试自定义初始模式"""
        assert horizontal_manager.mode == LayoutMode.HORIZONTAL

    def test_set_mode_to_horizontal(self, manager):
        """测试设置模式为 HORIZONTAL"""
        manager.set_mode(LayoutMode.HORIZONTAL)
        assert manager.mode == LayoutMode.HORIZONTAL

    def test_set_mode_to_vertical(self, manager):
        """测试设置模式为 VERTICAL"""
        manager.set_mode(LayoutMode.VERTICAL)
        assert manager.mode == LayoutMode.VERTICAL

    def test_set_mode_to_single(self, horizontal_manager):
        """测试设置模式为 SINGLE"""
        horizontal_manager.set_mode(LayoutMode.SINGLE)
        assert horizontal_manager.mode == LayoutMode.SINGLE

    def test_toggle_mode_from_single_to_horizontal(self, manager):
        """测试从 SINGLE 切换到 HORIZONTAL"""
        result = manager.toggle_mode()
        assert result == LayoutMode.HORIZONTAL
        assert manager.mode == LayoutMode.HORIZONTAL

    def test_toggle_mode_from_horizontal_to_vertical(self, horizontal_manager):
        """测试从 HORIZONTAL 切换到 VERTICAL"""
        result = horizontal_manager.toggle_mode()
        assert result == LayoutMode.VERTICAL
        assert horizontal_manager.mode == LayoutMode.VERTICAL

    def test_toggle_mode_from_vertical_to_single(self, vertical_manager):
        """测试从 VERTICAL 切换到 SINGLE"""
        result = vertical_manager.toggle_mode()
        assert result == LayoutMode.SINGLE
        assert vertical_manager.mode == LayoutMode.SINGLE

    def test_toggle_mode_multiple_times(self, manager):
        """测试多次切换模式"""
        assert manager.mode == LayoutMode.SINGLE

        manager.toggle_mode()
        assert manager.mode == LayoutMode.HORIZONTAL

        manager.toggle_mode()
        assert manager.mode == LayoutMode.VERTICAL

        manager.toggle_mode()
        assert manager.mode == LayoutMode.SINGLE

    def test_is_single_true(self, manager):
        """测试 is_single 返回 True"""
        assert manager.is_single is True

    def test_is_single_false(self, horizontal_manager):
        """测试 is_single 返回 False"""
        assert horizontal_manager.is_single is False

    def test_is_horizontal_true(self, horizontal_manager):
        """测试 is_horizontal 返回 True"""
        assert horizontal_manager.is_horizontal is True

    def test_is_horizontal_false(self, manager):
        """测试 is_horizontal 返回 False"""
        assert manager.is_horizontal is False

    def test_is_vertical_true(self, vertical_manager):
        """测试 is_vertical 返回 True"""
        assert vertical_manager.is_vertical is True

    def test_is_vertical_false(self, manager):
        """测试 is_vertical 返回 False"""
        assert manager.is_vertical is False

    def test_default_focused_pane_is_left(self, manager):
        """测试默认聚焦左侧面板"""
        assert manager.focused_pane == "left"

    def test_focus_left(self, manager):
        """测试聚焦左侧面板"""
        manager.focus_right()
        result = manager.focus_left()
        assert result == "left"
        assert manager.focused_pane == "left"

    def test_focus_right(self, manager):
        """测试聚焦右侧面板"""
        result = manager.focus_right()
        assert result == "right"
        assert manager.focused_pane == "right"

    def test_toggle_focus_from_left_to_right(self, manager):
        """测试从左侧切换到右侧"""
        result = manager.toggle_focus()
        assert result == "right"
        assert manager.focused_pane == "right"

    def test_toggle_focus_from_right_to_left(self, manager):
        """测试从右侧切换到左侧"""
        manager.focus_right()
        result = manager.toggle_focus()
        assert result == "left"
        assert manager.focused_pane == "left"

    def test_set_left_content(self, manager):
        """测试设置左侧内容"""
        manager.set_left_content("Hello")
        assert manager.get_left_content() == "Hello"

    def test_set_right_content(self, manager):
        """测试设置右侧内容"""
        manager.set_right_content("World")
        assert manager.get_right_content() == "World"

    def test_set_tool_output(self, manager):
        """测试设置工具输出"""
        manager.set_tool_output("Tool output")
        assert manager.get_right_content() == "Tool output"

    def test_set_conversation(self, manager):
        """测试设置对话内容"""
        manager.set_conversation("User message")
        assert manager.get_left_content() == "User message"

    def test_create_layout_returns_layout_object(self, manager):
        """测试 create_layout 返回 Layout 对象"""
        layout = manager.create_layout()
        assert isinstance(layout, Layout)

    def test_create_horizontal_layout(self, horizontal_manager):
        """测试创建水平布局"""
        horizontal_manager.set_left_content("Left")
        horizontal_manager.set_right_content("Right")
        layout = horizontal_manager.create_layout()
        assert isinstance(layout, Layout)

    def test_create_vertical_layout(self, vertical_manager):
        """测试创建垂直布局"""
        vertical_manager.set_left_content("Top")
        vertical_manager.set_right_content("Bottom")
        layout = vertical_manager.create_layout()
        assert isinstance(layout, (Layout, SplitPaneLayout))

    def test_str_representation(self, manager):
        """测试字符串表示"""
        result = str(manager)
        assert "LayoutManager" in result
        assert "single" in result
        assert "left" in result


class TestLayoutManagerIntegration:
    """测试 LayoutManager 集成功能"""

    def test_toggle_reflects_in_is_methods(self):
        """测试 toggle 后的结果正确反映在 is_ 方法中"""
        manager = LayoutManager()

        manager.set_mode(LayoutMode.HORIZONTAL)
        assert manager.is_horizontal is True
        assert manager.is_single is False
        assert manager.is_vertical is False

        manager.set_mode(LayoutMode.VERTICAL)
        assert manager.is_horizontal is False
        assert manager.is_single is False
        assert manager.is_vertical is True

        manager.set_mode(LayoutMode.SINGLE)
        assert manager.is_horizontal is False
        assert manager.is_single is True
        assert manager.is_vertical is False

    def test_focus_and_content_integration(self):
        """测试焦点和内容设置的集成"""
        manager = LayoutManager()

        manager.set_left_content("Conversation content")
        manager.set_tool_output("Tool result")
        assert manager.get_left_content() == "Conversation content"
        assert manager.get_right_content() == "Tool result"

        manager.focus_right()
        assert manager.focused_pane == "right"

        manager.toggle_focus()
        assert manager.focused_pane == "left"
