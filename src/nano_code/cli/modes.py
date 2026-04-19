"""CLI 模式系统模块

提供 Plan/Build 两种模式的切换功能：
- AgentMode 枚举定义模式类型
- ModeManager 类管理模式状态
"""

from enum import Enum


class AgentMode(Enum):
    """Agent 模式枚举"""

    PLAN = "plan"
    BUILD = "build"

    def __str__(self) -> str:
        return self.name


class ModeManager:
    """模式管理器"""

    def __init__(self, initial_mode: AgentMode = AgentMode.BUILD) -> None:
        self._current_mode = initial_mode

    @property
    def current_mode(self) -> AgentMode:
        """获取当前模式"""
        return self._current_mode

    def set_mode(self, mode: AgentMode) -> None:
        """设置模式"""
        self._current_mode = mode

    def toggle_mode(self) -> AgentMode:
        """切换模式"""
        if self._current_mode == AgentMode.PLAN:
            self._current_mode = AgentMode.BUILD
        else:
            self._current_mode = AgentMode.PLAN
        return self._current_mode

    def is_plan_mode(self) -> bool:
        """是否 Plan 模式"""
        return self._current_mode == AgentMode.PLAN

    def is_build_mode(self) -> bool:
        """是否 Build 模式"""
        return self._current_mode == AgentMode.BUILD


_global_mode_manager = ModeManager()


def get_mode_manager() -> ModeManager:
    """获取全局模式管理器"""
    return _global_mode_manager
