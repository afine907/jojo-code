"""风险评估模块

根据工具名称和参数评估操作的风险等级。
"""

import re
from typing import Any

# 风险模式定义
RISK_PATTERNS = {
    "critical": [
        r"rm\s+-rf\s+/",  # rm -rf /
        r"rm\s+-rf\s+~",  # rm -rf ~
        r"rm\s+-rf\s+\*",  # rm -rf *
        r"sudo\s+",  # sudo
        r"chmod\s+777",  # chmod 777
        r">\s*/dev/sd",  # 写入磁盘设备
        r"mkfs",  # 格式化
        r"dd\s+if=",  # dd 命令
        r"fork\s*bomb",  # fork bomb
        r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;",  # fork bomb pattern
    ],
    "high": [
        r"\brm\b",  # rm 命令
        r"\bgit\s+push\s+--force\b",  # 强制推送
        r"\bgit\s+push\s+-f\b",  # 强制推送简写
        r"\bcurl\b.*\|\s*(bash|sh)",  # curl | bash
        r"\bwget\b.*\|\s*(bash|sh)",  # wget | bash
        r"\bdocker\s+run\b",  # docker run
        r"\bdocker\s+exec\b",  # docker exec
        r"\bnpm\s+publish\b",  # npm publish
        r"\bgit\s+push\b",  # git push
        r"\bgit\s+reset\s+--hard\b",  # git reset --hard
        r">\s*/etc/",  # 写入 /etc
        r">\s*/usr/",  # 写入 /usr
    ],
    "medium": [
        r"\bnpm\s+(install|add|i)\b",  # npm install
        r"\byarn\s+(add|install)\b",  # yarn add/install
        r"\bpnpm\s+(add|install)\b",  # pnpm add/install
        r"\bpip\s+install\b",  # pip install
        r"\buv\s+(install|add)\b",  # uv install
        r"\bpython\d*\b",  # python
        r"\bnode\b",  # node
        r"\bgit\s+commit\b",  # git commit
        r"\bgit\s+checkout\b",  # git checkout
        r"\bmv\s+",  # mv
        r"\bcp\s+",  # cp
        r"\btar\s+",  # tar
        r"\bunzip\s+",  # unzip
    ],
    "low": [
        r"\bread_file\b",  # 读文件
        r"\bgrep\b",  # grep
        r"\bls\b",  # ls
        r"\bcat\b",  # cat
        r"\bhead\b",  # head
        r"\btail\b",  # tail
        r"\bfind\b",  # find
        r"\bgit\s+status\b",  # git status
        r"\bgit\s+log\b",  # git log
        r"\bgit\s+diff\b",  # git diff
        r"\bgit\s+branch\b",  # git branch
        r"\bgit\s+show\b",  # git show
    ],
}

# 编译正则表达式缓存
_compiled_patterns: dict[str, list[re.Pattern]] = {}


def _get_compiled_patterns(level: str) -> list[re.Pattern]:
    """获取编译后的正则表达式列表（带缓存）"""
    if level not in _compiled_patterns:
        _compiled_patterns[level] = [
            re.compile(pattern, re.IGNORECASE) for pattern in RISK_PATTERNS.get(level, [])
        ]
    return _compiled_patterns[level]


def assess_risk(tool_name: str, args: dict[str, Any]) -> str:
    """评估操作风险等级

    根据工具名称和参数评估操作的风险等级。

    Args:
        tool_name: 工具名称
        args: 工具参数

    Returns:
        风险等级: "low" | "medium" | "high" | "critical"

    Examples:
        >>> assess_risk("read_file", {"path": "/tmp/test.txt"})
        'low'
        >>> assess_risk("run_command", {"command": "rm -rf /"})
        'critical'
        >>> assess_risk("write_file", {"path": "/etc/config"})
        'high'
    """
    # 1. 根据工具名称直接判断
    # 低风险工具：只读操作
    if tool_name in (
        "read_file",
        "list_directory",
        "grep_search",
        "glob_search",
        "git_status",
        "git_log",
        "git_diff",
        "git_blame",
        "git_info",
        "git_branch",
        "web_search",
    ):
        return "low"

    # 写文件工具
    if tool_name in ("write_file", "edit_file"):
        path = args.get("path", "")

        # 检查是否写入系统目录
        system_paths = ["/etc/", "/usr/", "/var/", "/root/", "/boot/", "/sys/", "/proc/"]
        for sys_path in system_paths:
            if path.startswith(sys_path):
                return "high"

        # 检查是否写入敏感文件
        sensitive_patterns = [".env", "credentials", "secrets", ".pem", ".key", "id_rsa"]
        for pattern in sensitive_patterns:
            if pattern in path:
                return "high"

        return "medium"

    # Shell 命令工具
    if tool_name == "run_command":
        command = args.get("command", "")

        # 从高到低检查风险模式
        for level in ["critical", "high", "medium"]:
            patterns = _get_compiled_patterns(level)
            for pattern in patterns:
                if pattern.search(command):
                    return level

        # 默认低风险
        return "low"

    # Git 写操作
    if tool_name in ("git_commit",):
        return "medium"

    # 默认中等风险
    return "medium"


def get_risk_description(risk_level: str) -> str:
    """获取风险等级的描述

    Args:
        risk_level: 风险等级

    Returns:
        风险描述
    """
    descriptions = {
        "low": "低风险 - 仅读取信息，不修改系统状态",
        "medium": "中风险 - 修改有限范围的文件或配置",
        "high": "高风险 - 修改系统关键配置或多个文件",
        "critical": "极高风险 - 可能导致数据丢失或系统不可用",
    }
    return descriptions.get(risk_level, "未知风险")


__all__ = [
    "RISK_PATTERNS",
    "assess_risk",
    "get_risk_description",
]
