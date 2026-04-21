"""工具调用展示模块

提供工具调用的可视化显示功能，包括：
- 工具调用进度显示（开始、执行中、完成）
- 工具参数格式化（JSON格式）
- 工具结果格式化（截断长输出）
- 错误情况显示
- 执行时间显示
"""

import json
import time
from typing import Any

from rich.console import Console
from rich.status import Status

console = Console()

MAX_RESULT_LENGTH = 500
MAX_ARG_LENGTH = 50

ToolCallPhases = Any


class ToolCallPhase:
    """工具调用阶段"""

    START = "start"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class ToolCallDisplay:
    """工具调用显示类

    提供工具调用各阶段的进度显示。
    """

    def __init__(self, tool_name: str, args: dict[str, Any]) -> None:
        """初始化工具调用显示

        Args:
            tool_name: 工具名称
            args: 工具参数
        """
        self.tool_name = tool_name
        self.args = args
        self.start_time: float | None = None
        self._status: Status | None = None

    def start(self) -> None:
        """显示工具调用开始"""
        self.start_time = time.time()
        args_formatted = format_tool_args(self.args)
        console.print(f"\n🔧 执行工具: {self.tool_name}")
        console.print(f"   参数: {args_formatted}")

    def running(self) -> Status:
        """显示工具执行中状态，返回 Status 用于上下文管理"""
        self._status = console.status("   ⏳ 执行中...", spinner="dots")
        self._status.start()
        return self._status

    def complete(self, result: str) -> None:
        """显示工具执行完成

        Args:
            result: 工具执行结果
        """
        if self._status is not None:
            self._status.stop()

        duration = 0.0
        if self.start_time is not None:
            duration = time.time() - self.start_time

        result_formatted = format_tool_result(result)
        console.print(f"   ✅ 完成 ({duration:.2f}s)")
        console.print(f"   结果: {result_formatted}")

    def error(self, error_message: str) -> None:
        """显示工具执行错误

        Args:
            error_message: 错误信息
        """
        if self._status is not None:
            self._status.stop()

        duration = 0.0
        if self.start_time is not None:
            duration = time.time() - self.start_time

        console.print(f"   ❌ 错误 ({duration:.2f}s): {error_message}")


def format_tool_args(args: dict[str, Any]) -> str:
    """格式化工具参数

    Args:
        args: 工具参数字典

    Returns:
        格式化后的参数字符串
    """
    try:
        args_json = json.dumps(args)
    except (TypeError, ValueError):
        args_json = str(args)

    if len(args_json) > MAX_ARG_LENGTH:
        args_json = args_json[: MAX_ARG_LENGTH - 3] + "..."

    return args_json


def format_tool_result(result: str, max_length: int = MAX_RESULT_LENGTH) -> str:
    """格式化工具结果

    截断过长的结果以便显示。

    Args:
        result: 工具执行结果
        max_length: 最大显示长度

    Returns:
        格式化后的结果字符串
    """
    if len(result) <= max_length:
        return result

    truncated = result[: max_length - 3] + "..."
    return truncated


def get_result_info(result: str) -> dict[str, Any]:
    """获取结果的元信息

    Args:
        result: 工具执行结果

    Returns:
        包含结果信息的字典
    """
    info: dict[str, Any] = {
        "length": len(result),
        "truncated": len(result) > MAX_RESULT_LENGTH,
    }

    if len(result) > MAX_RESULT_LENGTH:
        info["display"] = format_tool_result(result)
    else:
        info["display"] = result

    return info


def display_tool_call(
    tool_name: str,
    args: dict[str, Any],
    phase: str = ToolCallPhase.START,
    result: str | None = None,
    error: str | None = None,
    duration: float | None = None,
) -> None:
    """显示工具调用的统一接口

    根据不同阶段显示相应的信息。

    Args:
        tool_name: 工具名称
        args: 工具参数
        phase: 当前阶段 (start/running/complete/error)
        result: 执行结果（仅在 complete 阶段使用）
        error: 错误信息（仅在 error 阶段使用）
        duration: 执行耗时（秒）
    """
    if phase == ToolCallPhase.START:
        console.print(f"\n🔧 执行工具: {tool_name}")
        console.print(f"   参数: {format_tool_args(args)}")

    elif phase == ToolCallPhase.RUNNING:
        console.print("   ⏳ 执行中...")

    elif phase == ToolCallPhase.COMPLETE:
        duration_str = f" ({duration:.2f}s)" if duration is not None else ""
        result_formatted = format_tool_result(result or "")
        console.print(f"   ✅ 完成{duration_str}")
        console.print(f"   结果: {result_formatted}")

    elif phase == ToolCallPhase.ERROR:
        duration_str = f" ({duration:.2f}s)" if duration is not None else ""
        console.print(f"   ❌ 错误{duration_str}: {error}")
