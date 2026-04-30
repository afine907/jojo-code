"""Permission Modal 单元测试"""

from jojo_code.cli.views.permission import PermissionModal


class TestPermissionModal:
    """PermissionModal 测试"""

    def test_modal_init(self):
        """测试弹窗初始化"""
        modal = PermissionModal(
            tool_name="run_command",
            action="execute",
            params={"command": "ls"},
        )
        assert modal.tool_name == "run_command"
        assert modal.action == "execute"
        assert modal.params == {"command": "ls"}

    def test_modal_init_read_file(self):
        """测试读文件弹窗"""
        modal = PermissionModal(
            tool_name="read_file",
            action="read",
            params={"path": "/etc/passwd"},
        )
        assert modal.tool_name == "read_file"
