"""权限模式和风险等级定义"""

from enum import StrEnum
from typing import Self


class PermissionMode(StrEnum):
    """权限模式 - 控制工具执行的权限级别

    YOLO: 完全信任模式，允许执行所有操作，无任何限制
    AUTO_APPROVE: 自动批准模式，自动批准低风险操作，高风险操作需要确认
    INTERACTIVE: 交互模式，所有写操作都需要用户确认
    STRICT: 严格模式，所有操作都需要用户确认
    READONLY: 只读模式，只允许读操作，拒绝所有写操作
    """

    YOLO = "yolo"
    AUTO_APPROVE = "auto_approve"
    INTERACTIVE = "interactive"
    STRICT = "strict"
    READONLY = "readonly"

    def allows_write(self) -> bool:
        """是否允许写操作"""
        return self not in (PermissionMode.READONLY,)

    def requires_confirmation(self, risk_level: "RiskLevel") -> bool:
        """给定风险等级是否需要确认

        Args:
            risk_level: 操作的风险等级

        Returns:
            是否需要用户确认
        """
        if self == PermissionMode.YOLO:
            return False
        if self == PermissionMode.AUTO_APPROVE:
            # AUTO_APPROVE: MEDIUM 及以下自动批准，HIGH 及以上需要确认
            return risk_level >= RiskLevel.HIGH
        if self == PermissionMode.INTERACTIVE:
            # INTERACTIVE: LOW 自动批准，MEDIUM 及以上需要确认
            return risk_level > RiskLevel.LOW
        if self == PermissionMode.STRICT:
            return True
        if self == PermissionMode.READONLY:
            return True
        return True

    @classmethod
    def from_string(cls, value: str) -> Self:
        """从字符串解析权限模式

        Args:
            value: 字符串值

        Returns:
            对应的 PermissionMode

        Raises:
            ValueError: 无效的模式字符串
        """
        try:
            return cls(value)
        except ValueError:
            valid_modes = [m.value for m in cls]
            raise ValueError(f"无效的权限模式: {value}, 有效值: {valid_modes}") from None


class RiskLevel(StrEnum):
    """风险等级 - 评估操作的风险程度

    LOW: 低风险，仅读取信息，不修改系统状态
    MEDIUM: 中风险，修改有限范围的文件或配置
    HIGH: 高风险，修改系统关键配置或多个文件
    CRITICAL: 极高风险，可能导致数据丢失或系统不可用
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other: Self) -> bool:
        """比较风险等级严格程度: LOW < MEDIUM < HIGH < CRITICAL"""
        order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3,
        }
        return order[self] < order[other]

    def __le__(self, other: Self) -> bool:
        return self == other or self < other

    def __gt__(self, other: Self) -> bool:
        return not self <= other

    def __ge__(self, other: Self) -> bool:
        return self == other or self > other

    @classmethod
    def from_string(cls, value: str) -> Self:
        """从字符串解析风险等级

        Args:
            value: 字符串值

        Returns:
            对应的 RiskLevel

        Raises:
            ValueError: 无效的风险等级字符串
        """
        try:
            return cls(value)
        except ValueError:
            valid_levels = [level.value for level in cls]
            raise ValueError(f"无效的风险等级: {value}, 有效值: {valid_levels}") from None


__all__ = [
    "PermissionMode",
    "RiskLevel",
]
