"""CLI 模式系统测试"""

import pytest

from nano_code.cli.modes import AgentMode, ModeManager, get_mode_manager


class TestAgentMode:
    """测试 AgentMode 枚举"""

    def test_plan_mode_value(self):
        """测试 PLAN 模式值"""
        assert AgentMode.PLAN.value == "plan"

    def test_build_mode_value(self):
        """测试 BUILD 模式值"""
        assert AgentMode.BUILD.value == "build"

    def test_mode_names(self):
        """测试模式名称"""
        assert AgentMode.PLAN.name == "PLAN"
        assert AgentMode.BUILD.name == "BUILD"

    def test_str_method(self):
        """测试 __str__ 方法"""
        assert str(AgentMode.PLAN) == "PLAN"
        assert str(AgentMode.BUILD) == "BUILD"

    def test_mode_equality(self):
        """测试模式相等性"""
        assert AgentMode.PLAN == AgentMode.PLAN
        assert AgentMode.BUILD == AgentMode.BUILD
        assert AgentMode.PLAN != AgentMode.BUILD


class TestModeManager:
    """测试 ModeManager 类"""

    @pytest.fixture
    def manager(self):
        """创建 ModeManager 实例"""
        return ModeManager()

    @pytest.fixture
    def plan_manager(self):
        """创建 PLAN 模式的 ModeManager 实例"""
        return ModeManager(initial_mode=AgentMode.PLAN)

    def test_default_initial_mode(self, manager):
        """测试默认初始模式为 BUILD"""
        assert manager.current_mode == AgentMode.BUILD

    def test_custom_initial_mode(self, plan_manager):
        """测试自定义初始模式"""
        assert plan_manager.current_mode == AgentMode.PLAN

    def test_set_mode_to_plan(self, manager):
        """测试设置模式为 PLAN"""
        manager.set_mode(AgentMode.PLAN)
        assert manager.current_mode == AgentMode.PLAN

    def test_set_mode_to_build(self, plan_manager):
        """测试设置模式为 BUILD"""
        plan_manager.set_mode(AgentMode.BUILD)
        assert plan_manager.current_mode == AgentMode.BUILD

    def test_toggle_mode_from_build_to_plan(self, manager):
        """测试从 BUILD 切换到 PLAN"""
        result = manager.toggle_mode()
        assert result == AgentMode.PLAN
        assert manager.current_mode == AgentMode.PLAN

    def test_toggle_mode_from_plan_to_build(self, plan_manager):
        """测试从 PLAN 切换到 BUILD"""
        result = plan_manager.toggle_mode()
        assert result == AgentMode.BUILD
        assert plan_manager.current_mode == AgentMode.BUILD

    def test_toggle_mode_multiple_times(self, manager):
        """测试多次切换模式"""
        assert manager.current_mode == AgentMode.BUILD

        manager.toggle_mode()
        assert manager.current_mode == AgentMode.PLAN

        manager.toggle_mode()
        assert manager.current_mode == AgentMode.BUILD

        manager.toggle_mode()
        assert manager.current_mode == AgentMode.PLAN

    def test_is_plan_mode_true(self, plan_manager):
        """测试 is_plan_mode 返回 True"""
        assert plan_manager.is_plan_mode() is True

    def test_is_plan_mode_false(self, manager):
        """测试 is_plan_mode 返回 False"""
        assert manager.is_plan_mode() is False

    def test_is_build_mode_true(self, manager):
        """测试 is_build_mode 返回 True"""
        assert manager.is_build_mode() is True

    def test_is_build_mode_false(self, plan_manager):
        """测试 is_build_mode 返回 False"""
        assert plan_manager.is_build_mode() is False


class TestModeManagerIntegration:
    """测试 ModeManager 集成功能"""

    def test_toggle_reflects_in_is_methods(self):
        """测试 toggle 后的结果正确反映在 is_ 方法中"""
        manager = ModeManager()

        manager.set_mode(AgentMode.PLAN)
        assert manager.is_plan_mode() is True
        assert manager.is_build_mode() is False

        manager.set_mode(AgentMode.BUILD)
        assert manager.is_plan_mode() is False
        assert manager.is_build_mode() is True

    def test_get_mode_manager_returns_singleton(self):
        """测试 get_mode_manager 返回全局单例"""
        manager1 = get_mode_manager()
        manager2 = get_mode_manager()
        assert manager1 is manager2

    def test_global_manager_default_mode(self):
        """测试全局管理器默认模式"""
        manager = get_mode_manager()
        manager.set_mode(AgentMode.BUILD)
        assert manager.current_mode == AgentMode.BUILD
