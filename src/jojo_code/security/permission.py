"""权限级别和结果定义"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PermissionLevel(Enum):
    """权限级别"""

    ALLOW = "allow"  # 自动允许，无需确认
    CONFIRM = "confirm"  # 需要用户确认
    DENY = "deny"  # 禁止执行

    def __lt__(self, other: "PermissionLevel") -> bool:
        """比较权限级别严格程度: DENY > CONFIRM > ALLOW"""
        order = {PermissionLevel.ALLOW: 0, PermissionLevel.CONFIRM: 1, PermissionLevel.DENY: 2}
        return order[self] < order[other]

    def __le__(self, other: "PermissionLevel") -> bool:
        return self == other or self < other

    def __gt__(self, other: "PermissionLevel") -> bool:
        return not self <= other

    def __ge__(self, other: "PermissionLevel") -> bool:
        return self == other or self > other


@dataclass
class PermissionResult:
    """权限检查结果"""

    level: PermissionLevel
    tool_name: str
    args: dict[str, Any]
    reason: str | None = None

    @property
    def allowed(self) -> bool:
        """是否允许执行"""
        return self.level == PermissionLevel.ALLOW

    @property
    def needs_confirm(self) -> bool:
        """是否需要用户确认"""
        return self.level == PermissionLevel.CONFIRM

    @property
    def denied(self) -> bool:
        """是否被拒绝"""
        return self.level == PermissionLevel.DENY

    def __str__(self) -> str:
        if self.reason:
            return f"{self.level.value}: {self.reason}"
        return f"{self.level.value}: {self.tool_name}"
