"""测试风险评估模块"""

from jojo_code.security.risk import RISK_PATTERNS, assess_risk, get_risk_description


class TestRiskPatterns:
    """测试风险模式定义"""

    def test_critical_patterns_exist(self):
        """测试 critical 风险模式存在"""
        assert "critical" in RISK_PATTERNS
        assert len(RISK_PATTERNS["critical"]) > 0

    def test_high_patterns_exist(self):
        """测试 high 风险模式存在"""
        assert "high" in RISK_PATTERNS
        assert len(RISK_PATTERNS["high"]) > 0

    def test_medium_patterns_exist(self):
        """测试 medium 风险模式存在"""
        assert "medium" in RISK_PATTERNS
        assert len(RISK_PATTERNS["medium"]) > 0

    def test_low_patterns_exist(self):
        """测试 low 风险模式存在"""
        assert "low" in RISK_PATTERNS
        assert len(RISK_PATTERNS["low"]) > 0


class TestAssessRisk:
    """测试 assess_risk 函数"""

    # ─── 低风险测试 ───

    def test_read_file_low_risk(self):
        """读取文件是低风险"""
        assert assess_risk("read_file", {"path": "/tmp/test.txt"}) == "low"

    def test_list_directory_low_risk(self):
        """列出目录是低风险"""
        assert assess_risk("list_directory", {"path": "."}) == "low"

    def test_grep_search_low_risk(self):
        """grep 搜索是低风险"""
        assert assess_risk("grep_search", {"pattern": "test"}) == "low"

    def test_git_status_low_risk(self):
        """git status 是低风险"""
        assert assess_risk("git_status", {}) == "low"

    def test_git_log_low_risk(self):
        """git log 是低风险"""
        assert assess_risk("git_log", {}) == "low"

    def test_ls_command_low_risk(self):
        """ls 命令是低风险"""
        assert assess_risk("run_command", {"command": "ls -la"}) == "low"

    def test_cat_command_low_risk(self):
        """cat 命令是低风险"""
        assert assess_risk("run_command", {"command": "cat file.txt"}) == "low"

    # ─── 中等风险测试 ───

    def test_write_file_medium_risk(self):
        """写入普通文件是中等风险"""
        assert assess_risk("write_file", {"path": "src/test.py"}) == "medium"

    def test_edit_file_medium_risk(self):
        """编辑普通文件是中等风险"""
        assert assess_risk("edit_file", {"path": "config.json"}) == "medium"

    def test_npm_install_medium_risk(self):
        """npm install 是中等风险"""
        assert assess_risk("run_command", {"command": "npm install"}) == "medium"

    def test_pip_install_medium_risk(self):
        """pip install 是中等风险"""
        assert assess_risk("run_command", {"command": "pip install requests"}) == "medium"

    def test_python_command_medium_risk(self):
        """python 命令是中等风险"""
        assert assess_risk("run_command", {"command": "python script.py"}) == "medium"

    # ─── 高风险测试 ───

    def test_write_to_etc_high_risk(self):
        """写入 /etc 是高风险"""
        assert assess_risk("write_file", {"path": "/etc/config"}) == "high"

    def test_write_to_usr_high_risk(self):
        """写入 /usr 是高风险"""
        assert assess_risk("write_file", {"path": "/usr/local/bin/script"}) == "high"

    def test_write_env_file_high_risk(self):
        """写入 .env 文件是高风险"""
        assert assess_risk("write_file", {"path": ".env"}) == "high"

    def test_write_credentials_high_risk(self):
        """写入 credentials 文件是高风险"""
        assert assess_risk("write_file", {"path": "credentials.json"}) == "high"

    def test_rm_command_high_risk(self):
        """rm 命令是高风险"""
        assert assess_risk("run_command", {"command": "rm file.txt"}) == "high"

    def test_git_push_high_risk(self):
        """git push 是高风险"""
        assert assess_risk("run_command", {"command": "git push origin main"}) == "high"

    def test_docker_run_high_risk(self):
        """docker run 是高风险"""
        assert assess_risk("run_command", {"command": "docker run -it ubuntu"}) == "high"

    # ─── 极高风险测试 ───

    def test_rm_rf_root_critical(self):
        """rm -rf / 是极高风险"""
        assert assess_risk("run_command", {"command": "rm -rf /"}) == "critical"

    def test_rm_rf_home_critical(self):
        """rm -rf ~ 是极高风险"""
        assert assess_risk("run_command", {"command": "rm -rf ~"}) == "critical"

    def test_sudo_critical(self):
        """sudo 是极高风险"""
        assert assess_risk("run_command", {"command": "sudo apt update"}) == "critical"

    def test_chmod_777_critical(self):
        """chmod 777 是极高风险"""
        assert assess_risk("run_command", {"command": "chmod 777 /etc/passwd"}) == "critical"

    def test_mkfs_critical(self):
        """mkfs 是极高风险"""
        assert assess_risk("run_command", {"command": "mkfs.ext4 /dev/sda1"}) == "critical"

    # ─── 边界测试 ───

    def test_unknown_tool_default_medium(self):
        """未知工具默认中等风险"""
        assert assess_risk("unknown_tool", {}) == "medium"

    def test_empty_command(self):
        """空命令是低风险"""
        assert assess_risk("run_command", {"command": ""}) == "low"

    def test_write_file_no_path(self):
        """无路径的写入是中等风险"""
        assert assess_risk("write_file", {}) == "medium"


class TestGetRiskDescription:
    """测试 get_risk_description 函数"""

    def test_low_description(self):
        """测试低风险描述"""
        desc = get_risk_description("low")
        assert "低风险" in desc

    def test_medium_description(self):
        """测试中等风险描述"""
        desc = get_risk_description("medium")
        assert "中风险" in desc

    def test_high_description(self):
        """测试高风险描述"""
        desc = get_risk_description("high")
        assert "高风险" in desc

    def test_critical_description(self):
        """测试极高风险描述"""
        desc = get_risk_description("critical")
        assert "极高风险" in desc

    def test_unknown_description(self):
        """测试未知风险描述"""
        desc = get_risk_description("unknown")
        assert "未知" in desc
