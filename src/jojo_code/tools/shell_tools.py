"""Shell 命令执行工具"""

import subprocess

from langchain_core.tools import tool

# 危险命令黑名单（防止 shell 注入）
_BLOCKED_COMMANDS = frozenset(
    [
        "rm -rf /",
        "rm -rf /*",
        ":(){:|:&};:",
        "dd if=/dev/zero of=/dev/sda",
        "mkfs",
        "> /dev/sda",
    ]
)


def _validate_command(command: str) -> str | None:
    """验证命令安全性，返回错误信息或 None（安全）。

    Args:
        command: 要验证的命令

    Returns:
        错误信息，如果命令安全则返回 None
    """
    normalized = command.strip().lower()

    # 检查危险命令
    for blocked in _BLOCKED_COMMANDS:
        if blocked in normalized:
            return f"危险命令被拒绝: {blocked}"

    # 检查管道到解释器（防止反弹 shell）
    if any(pattern in normalized for pattern in ["| sh", "| bash", "| python", "| nc "]):
        return "管道到解释器的命令被拒绝"

    return None


@tool
def run_command(
    command: str,
    timeout: int = 30,
    cwd: str | None = None,
) -> str:
    """执行 shell 命令并返回输出。

    Args:
        command: 要执行的命令
        timeout: 超时时间（秒），默认 30
        cwd: 工作目录，默认当前目录

    Returns:
        命令的标准输出，或错误信息

    Raises:
        TimeoutError: 命令执行超时
        PermissionError: 命令被安全策略拒绝
    """
    # 安全检查
    error = _validate_command(command)
    if error:
        raise PermissionError(error)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            encoding="utf-8",
            errors="replace",
        )

        # 限制输出长度（避免 OOM）
        max_output = 100_000  # 100K 字符
        output = result.stdout
        if len(output) > max_output:
            output = output[:max_output] + f"\n... (输出被截断，共 {len(result.stdout)} 字符)"

        # 合并 stdout 和 stderr
        if result.returncode != 0:
            stderr = result.stderr
            if len(stderr) > max_output:
                stderr = stderr[:max_output] + "\n... (错误输出被截断)"
            if stderr:
                output = f"Error (exit code {result.returncode}):\n{stderr}"
            elif not output:
                output = f"Error: command failed with exit code {result.returncode}"

        return output.strip() if output.strip() else "(无输出)"

    except subprocess.TimeoutExpired as e:
        raise TimeoutError(f"命令执行超时（{timeout}秒）: {command}") from e
    except Exception as e:
        return f"Error: {e}"


# 为了向后兼容，提供工具类别名
ExecuteCommandTool = run_command
RunScriptTool = run_command
