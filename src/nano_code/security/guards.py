"""权限守卫基类"""

from abc import ABC, abstractmethod
from typing import Any

from nano_code.security.permission import PermissionResult


class BaseGuard(ABC):
    """权限守卫基类

    所有权限守卫必须继承此类并实现 check 方法。
    """

    @abstractmethod
    def check(self, tool_name: str, args: dict[str, Any]) -> PermissionResult:
        """检查工具调用权限

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            权限检查结果
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """守卫名称"""
        pass
