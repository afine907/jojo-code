"""权限系统测试"""

from pathlib import Path

import pytest

from nano_code.security.command_guard import CommandGuard
from nano_code.security.manager import PermissionConfig, PermissionManager
from nano_code.security.path_guard import PathGuard
from nano_code.security.permission import PermissionLevel, PermissionResult


class TestPermissionLevel:
    """测试权限级别"""

    def test_level_comparison(self):
        """测试权限级别比较"""
        assert PermissionLevel.ALLOW < PermissionLevel.CONFIRM
        assert PermissionLevel.CONFIRM < PermissionLevel.DENY
        assert PermissionLevel.DENY > PermissionLevel.ALLOW

    def test_level_properties(self):
        """测试权限级别属性"""
        allow = PermissionResult(PermissionLevel.ALLOW, "test", {})
        confirm = PermissionResult(PermissionLevel.CONFIRM, "test", {})
        deny = PermissionResult(PermissionLevel.DENY, "test", {})

        assert allow.allowed
        assert not allow.needs_confirm
        assert not allow.denied

        assert not confirm.allowed
        assert confirm.needs_confirm
        assert not confirm.denied

        assert not deny.allowed
        assert not deny.needs_confirm
        assert deny.denied


class TestPathGuard:
    """测试路径守卫"""

    @pytest.fixture
    def workspace(self, tmp_path: Path) -> Path:
        """创建测试工作空间"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / ".env").write_text("SECRET=123")
        (tmp_path / "secrets").mkdir()
        (tmp_path / "secrets" / "key.pem").write_text("private key")
        return tmp_path

    def test_allow_read_in_workspace(self, workspace: Path):
        """测试允许读取工作空间内文件"""
        guard = PathGuard(workspace_root=workspace)
        result = guard.check("read_file", {"path": str(workspace / "src" / "main.py")})

        assert result.allowed

    def test_deny_outside_workspace(self, workspace: Path):
        """测试拒绝访问工作空间外文件"""
        guard = PathGuard(workspace_root=workspace, allow_outside=False)
        result = guard.check("read_file", {"path": "/etc/passwd"})

        assert result.denied
        assert result.reason is not None and "工作空间外" in result.reason

    def test_deny_blacklisted_path(self, workspace: Path):
        """测试拒绝黑名单路径"""
        guard = PathGuard(
            workspace_root=workspace,
            denied_patterns=[".env", "secrets/**"],
        )
        result = guard.check("read_file", {"path": str(workspace / ".env")})

        assert result.denied
        assert result.reason is not None and "禁止模式" in result.reason

    def test_confirm_on_write(self, workspace: Path):
        """测试写入操作需要确认"""
        guard = PathGuard(
            workspace_root=workspace,
            confirm_patterns=["src/**"],
        )
        result = guard.check("write_file", {"path": str(workspace / "src" / "main.py")})

        assert result.needs_confirm
        assert result.reason is not None and "需要确认" in result.reason

    def test_allow_non_file_tools(self, workspace: Path):
        """测试非文件工具自动允许"""
        guard = PathGuard(workspace_root=workspace)
        result = guard.check("run_command", {"command": "ls"})

        assert result.allowed


class TestCommandGuard:
    """测试命令守卫"""

    def test_allow_whitelisted_command(self):
        """测试允许白名单命令"""
        guard = CommandGuard(allowed_commands=["ls", "cat"])
        result = guard.check("run_command", {"command": "ls -la"})

        assert result.allowed

    def test_deny_blacklisted_command(self):
        """测试拒绝黑名单命令"""
        guard = CommandGuard(denied_commands=["rm -rf /", "sudo"])
        result = guard.check("run_command", {"command": "sudo rm -rf /"})

        assert result.denied

    def test_deny_network_command(self):
        """测试拒绝网络命令"""
        guard = CommandGuard(allow_network=False)
        result = guard.check("run_command", {"command": "curl http://example.com"})

        assert result.denied
        assert result.reason is not None and "网络命令" in result.reason

    def test_deny_excessive_timeout(self):
        """测试拒绝超长超时"""
        guard = CommandGuard(max_timeout=60)
        result = guard.check("run_command", {"command": "ls", "timeout": 120})

        assert result.denied
        assert result.reason is not None and "超时" in result.reason

    def test_disabled_shell(self):
        """测试禁用 shell"""
        guard = CommandGuard(enabled=False)
        result = guard.check("run_command", {"command": "ls"})

        assert result.denied
        assert result.reason is not None and "已被禁用" in result.reason

    def test_default_confirm(self):
        """测试默认需要确认"""
        guard = CommandGuard(
            allowed_commands=[],
            default=PermissionLevel.CONFIRM,
        )
        result = guard.check("run_command", {"command": "python script.py"})

        assert result.needs_confirm

    def test_non_command_tools(self):
        """测试非命令工具自动允许"""
        guard = CommandGuard()
        result = guard.check("read_file", {"path": "test.py"})

        assert result.allowed


class TestPermissionManager:
    """测试权限管理器"""

    @pytest.fixture
    def manager(self, tmp_path: Path) -> PermissionManager:
        """创建测试权限管理器"""
        config = PermissionConfig(
            workspace_root=tmp_path,
            denied_paths=[".env"],
            denied_commands=["sudo"],
            audit_log=False,
        )
        return PermissionManager(config)

    def test_check_file_tool(self, manager: PermissionManager, tmp_path: Path):
        """测试文件工具权限检查"""
        (tmp_path / "test.py").write_text("print('test')")

        result = manager.check("read_file", {"path": str(tmp_path / "test.py")})
        assert result.allowed

    def test_check_command_tool(self, manager: PermissionManager):
        """测试命令工具权限检查"""
        result = manager.check("run_command", {"command": "sudo ls"})
        assert result.denied

    def test_audit_log(self, tmp_path: Path):
        """测试审计日志"""
        log_path = tmp_path / "audit.log"
        config = PermissionConfig(
            workspace_root=tmp_path,
            audit_log=True,
            audit_log_path=log_path,
        )
        manager = PermissionManager(config)

        # 执行多次调用，触发缓冲区刷新
        for i in range(manager.LOG_BUFFER_SIZE + 2):
            manager.check("read_file", {"path": str(tmp_path / f"test{i}.py")})

        # 手动刷新确保写入
        manager.flush()

        assert log_path.exists()
        content = log_path.read_text()
        assert "read_file" in content

    def test_max_tool_calls(self, tmp_path: Path):
        """测试最大调用次数限制"""
        config = PermissionConfig(
            workspace_root=tmp_path,
            max_tool_calls=2,
            audit_log=False,
        )
        manager = PermissionManager(config)

        # 在工作空间内创建文件
        (tmp_path / "test1.py").write_text("test")
        (tmp_path / "test2.py").write_text("test")
        (tmp_path / "test3.py").write_text("test")

        # 前两次应该成功
        result1 = manager.check("read_file", {"path": str(tmp_path / "test1.py")})
        result2 = manager.check("read_file", {"path": str(tmp_path / "test2.py")})

        assert result1.allowed
        assert result2.allowed

        # 第三次应该被拒绝
        result3 = manager.check("read_file", {"path": str(tmp_path / "test3.py")})
        assert result3.denied
        assert result3.reason is not None and "最大调用次数" in result3.reason


class TestPermissionConfig:
    """测试权限配置"""

    def test_development_config(self):
        """测试开发模式配置"""
        config = PermissionConfig.development()

        assert config.shell_enabled
        assert "sudo" in config.denied_commands

    def test_production_config(self):
        """测试生产模式配置"""
        config = PermissionConfig.production()

        assert not config.allow_network
        assert config.audit_log
