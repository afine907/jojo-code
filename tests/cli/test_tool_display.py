"""工具调用展示测试"""

import time

from nano_code.cli.tool_display import (
    ToolCallDisplay,
    ToolCallPhase,
    display_tool_call,
    format_tool_args,
    format_tool_result,
    get_result_info,
)


class TestToolCallDisplay:
    """ToolCallDisplay 类测试"""

    def test_init(self):
        """测试初始化"""
        args = {"path": "src/main.py"}
        display = ToolCallDisplay("read_file", args)

        assert display.tool_name == "read_file"
        assert display.args == args
        assert display.start_time is None

    def test_start(self):
        """测试 start 方法"""
        args = {"path": "src/main.py"}
        display = ToolCallDisplay("read_file", args)
        display.start()

        assert display.start_time is not None

    def test_complete(self):
        """测试 complete 方法"""
        args = {"path": "src/main.py"}
        display = ToolCallDisplay("read_file", args)
        display.start_time = time.time() - 0.5
        result_content = "test result"
        display.complete(result_content)

    def test_error(self):
        """测试 error 方法"""
        args = {"path": "src/main.py"}
        display = ToolCallDisplay("read_file", args)
        display.start_time = time.time() - 0.5
        error_msg = "Permission denied"
        display.error(error_msg)


class TestFormatToolArgs:
    """format_tool_args 函数测试"""

    def test_simple_args(self):
        """测试简单参数"""
        args = {"path": "src/main.py"}
        result = format_tool_args(args)
        assert "path" in result
        assert "src/main.py" in result

    def test_long_arg_truncation(self):
        """测试长参数截断"""
        long_path = "a" * 100
        args = {"path": long_path}
        result = format_tool_args(args)
        assert len(result) <= 50

    def test_json_format(self):
        """测试 JSON 格式"""
        args = {"path": "test.py", "offset": 10}
        result = format_tool_args(args)
        assert "{" in result or "path" in result


class TestFormatToolResult:
    """format_tool_result 函数测试"""

    def test_short_result(self):
        """测试短结果"""
        result = "short result"
        assert format_tool_result(result) == result

    def test_long_result_truncation(self):
        """测试长结果截断"""
        long_result = "a" * 600
        formatted = format_tool_result(long_result)
        assert len(formatted) <= 500
        assert formatted.endswith("...")

    def test_custom_max_length(self):
        """测试自定义最大长度"""
        result = "a" * 200
        formatted = format_tool_result(result, max_length=100)
        assert len(formatted) <= 100
        assert formatted.endswith("...")


class TestGetResultInfo:
    """get_result_info 函数测试"""

    def test_short_result(self):
        """测试短结果信息"""
        result = "short result"
        info = get_result_info(result)

        assert info["length"] == len(result)
        assert info["truncated"] is False
        assert info["display"] == result

    def test_long_result(self):
        """测试长结果信息"""
        long_result = "a" * 600
        info = get_result_info(long_result)

        assert info["length"] == 600
        assert info["truncated"] is True
        assert len(info["display"]) <= 500


class TestDisplayToolCall:
    """display_tool_call 函数测试"""

    def test_phase_start(self):
        """测试开始阶段"""
        args = {"path": "test.py"}
        display_tool_call("read_file", args, ToolCallPhase.START)

    def test_phase_running(self):
        """测试运行阶段"""
        args = {"path": "test.py"}
        display_tool_call("read_file", args, ToolCallPhase.RUNNING)

    def test_phase_complete(self):
        """测试完成阶段"""
        args = {"path": "test.py"}
        display_tool_call(
            "read_file",
            args,
            ToolCallPhase.COMPLETE,
            result="result content",
            duration=0.5,
        )

    def test_phase_error(self):
        """测试错误阶段"""
        args = {"path": "test.py"}
        display_tool_call(
            "read_file",
            args,
            ToolCallPhase.ERROR,
            error="Permission denied",
            duration=0.1,
        )


class TestTruncation:
    """输出截断测试"""

    def test_args_truncation(self):
        """测试参数截断"""
        args = {"content": "x" * 200}
        result = format_tool_args(args)
        assert len(result) <= 50

    def test_result_truncation(self):
        """测试结果截断"""
        result = "y" * 1000
        formatted = format_tool_result(result)
        assert formatted.endswith("...")
        assert len(formatted) <= 503
