"""测试权限模式和风险等级"""

import pytest

from jojo_code.security.modes import PermissionMode, RiskLevel


class TestPermissionMode:
    """测试 PermissionMode 枚举"""

    def test_all_modes_exist(self):
        """测试所有模式都存在"""
        assert PermissionMode.YOLO.value == "yolo"
        assert PermissionMode.AUTO_APPROVE.value == "auto_approve"
        assert PermissionMode.INTERACTIVE.value == "interactive"
        assert PermissionMode.STRICT.value == "strict"
        assert PermissionMode.READONLY.value == "readonly"

    def test_allows_write(self):
        """测试写操作权限"""
        assert PermissionMode.YOLO.allows_write() is True
        assert PermissionMode.AUTO_APPROVE.allows_write() is True
        assert PermissionMode.INTERACTIVE.allows_write() is True
        assert PermissionMode.STRICT.allows_write() is True
        assert PermissionMode.READONLY.allows_write() is False

    def test_requires_confirmation_yolo(self):
        """YOLO 模式永远不需要确认"""
        assert PermissionMode.YOLO.requires_confirmation(RiskLevel.LOW) is False
        assert PermissionMode.YOLO.requires_confirmation(RiskLevel.MEDIUM) is False
        assert PermissionMode.YOLO.requires_confirmation(RiskLevel.HIGH) is False
        assert PermissionMode.YOLO.requires_confirmation(RiskLevel.CRITICAL) is False

    def test_requires_confirmation_auto_approve(self):
        """AUTO_APPROVE 模式只有高风险需要确认"""
        assert PermissionMode.AUTO_APPROVE.requires_confirmation(RiskLevel.LOW) is False
        assert PermissionMode.AUTO_APPROVE.requires_confirmation(RiskLevel.MEDIUM) is False
        assert PermissionMode.AUTO_APPROVE.requires_confirmation(RiskLevel.HIGH) is True
        assert PermissionMode.AUTO_APPROVE.requires_confirmation(RiskLevel.CRITICAL) is True

    def test_requires_confirmation_interactive(self):
        """INTERACTIVE 模式中等以上风险需要确认"""
        assert PermissionMode.INTERACTIVE.requires_confirmation(RiskLevel.LOW) is False
        assert PermissionMode.INTERACTIVE.requires_confirmation(RiskLevel.MEDIUM) is True
        assert PermissionMode.INTERACTIVE.requires_confirmation(RiskLevel.HIGH) is True
        assert PermissionMode.INTERACTIVE.requires_confirmation(RiskLevel.CRITICAL) is True

    def test_requires_confirmation_strict(self):
        """STRICT 模式所有操作都需要确认"""
        assert PermissionMode.STRICT.requires_confirmation(RiskLevel.LOW) is True
        assert PermissionMode.STRICT.requires_confirmation(RiskLevel.MEDIUM) is True
        assert PermissionMode.STRICT.requires_confirmation(RiskLevel.HIGH) is True
        assert PermissionMode.STRICT.requires_confirmation(RiskLevel.CRITICAL) is True

    def test_requires_confirmation_readonly(self):
        """READONLY 模式所有操作都需要确认（实际会被拒绝）"""
        assert PermissionMode.READONLY.requires_confirmation(RiskLevel.LOW) is True
        assert PermissionMode.READONLY.requires_confirmation(RiskLevel.MEDIUM) is True

    def test_from_string_valid(self):
        """测试从字符串解析有效模式"""
        assert PermissionMode.from_string("yolo") == PermissionMode.YOLO
        assert PermissionMode.from_string("interactive") == PermissionMode.INTERACTIVE
        assert PermissionMode.from_string("strict") == PermissionMode.STRICT

    def test_from_string_invalid(self):
        """测试从字符串解析无效模式"""
        with pytest.raises(ValueError, match="无效的权限模式"):
            PermissionMode.from_string("invalid_mode")


class TestRiskLevel:
    """测试 RiskLevel 枚举"""

    def test_all_levels_exist(self):
        """测试所有风险等级都存在"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_comparison_less_than(self):
        """测试风险等级小于比较"""
        assert RiskLevel.LOW < RiskLevel.MEDIUM
        assert RiskLevel.LOW < RiskLevel.HIGH
        assert RiskLevel.LOW < RiskLevel.CRITICAL
        assert RiskLevel.MEDIUM < RiskLevel.HIGH
        assert RiskLevel.MEDIUM < RiskLevel.CRITICAL
        assert RiskLevel.HIGH < RiskLevel.CRITICAL

    def test_comparison_greater_than(self):
        """测试风险等级大于比较"""
        assert RiskLevel.CRITICAL > RiskLevel.HIGH
        assert RiskLevel.CRITICAL > RiskLevel.MEDIUM
        assert RiskLevel.CRITICAL > RiskLevel.LOW
        assert RiskLevel.HIGH > RiskLevel.MEDIUM
        assert RiskLevel.HIGH > RiskLevel.LOW
        assert RiskLevel.MEDIUM > RiskLevel.LOW

    def test_comparison_equal(self):
        """测试风险等级等于比较"""
        assert RiskLevel.LOW == RiskLevel.LOW
        assert RiskLevel.LOW <= RiskLevel.LOW
        assert RiskLevel.LOW >= RiskLevel.LOW

    def test_comparison_less_equal(self):
        """测试风险等级小于等于比较"""
        assert RiskLevel.LOW <= RiskLevel.MEDIUM
        assert RiskLevel.LOW <= RiskLevel.LOW
        assert RiskLevel.MEDIUM <= RiskLevel.HIGH

    def test_comparison_greater_equal(self):
        """测试风险等级大于等于比较"""
        assert RiskLevel.CRITICAL >= RiskLevel.HIGH
        assert RiskLevel.CRITICAL >= RiskLevel.CRITICAL
        assert RiskLevel.HIGH >= RiskLevel.MEDIUM

    def test_from_string_valid(self):
        """测试从字符串解析有效风险等级"""
        assert RiskLevel.from_string("low") == RiskLevel.LOW
        assert RiskLevel.from_string("medium") == RiskLevel.MEDIUM
        assert RiskLevel.from_string("high") == RiskLevel.HIGH
        assert RiskLevel.from_string("critical") == RiskLevel.CRITICAL

    def test_from_string_invalid(self):
        """测试从字符串解析无效风险等级"""
        with pytest.raises(ValueError, match="无效的风险等级"):
            RiskLevel.from_string("extreme")
