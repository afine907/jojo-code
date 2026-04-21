"""CLI 控制台输出测试"""

from jojo_code.cli.console import (
    SessionStats,
    print_error,
    print_help,
    print_history,
    print_model_info,
    print_session_stats,
    print_tool_call,
    print_tool_result,
    print_user,
    session_stats,
)


class TestSessionStats:
    """会话统计测试"""

    def test_default_values(self):
        """默认值测试"""
        stats = SessionStats()
        assert stats.message_count == 0
        assert stats.tool_calls == 0
        assert stats.total_tokens == 0

    def test_elapsed_time_seconds(self):
        """已用时间（秒）测试"""
        stats = SessionStats()
        stats.start_time = 1000.0
        # 测试格式
        elapsed = stats.elapsed_time()
        assert "s" in elapsed or "m" in elapsed

    def test_reset(self):
        """重置测试"""
        stats = SessionStats()
        stats.message_count = 10
        stats.tool_calls = 5
        stats.total_tokens = 1000

        stats.reset()

        assert stats.message_count == 0
        assert stats.tool_calls == 0
        assert stats.total_tokens == 0


class TestConsoleOutput:
    """控制台输出测试"""

    def test_print_user(self, capsys):
        """打印用户消息"""
        print_user("Hello")
        captured = capsys.readouterr()
        assert "You" in captured.out
        assert "Hello" in captured.out

    def test_print_error(self, capsys):
        """打印错误消息"""
        print_error("Something went wrong")
        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert "Something went wrong" in captured.out

    def test_print_tool_call(self, capsys):
        """打印工具调用"""
        print_tool_call("read_file", {"path": "/test/file.py"})
        captured = capsys.readouterr()
        assert "Tool" in captured.out
        assert "read_file" in captured.out

    def test_print_tool_result_truncated(self, capsys):
        """打印截断的工具结果"""
        long_result = "x" * 1000
        print_tool_result(long_result)
        captured = capsys.readouterr()
        assert "Result" in captured.out
        # 应该被截断
        assert "..." in captured.out

    def test_print_tool_result_with_duration(self, capsys):
        """打印带时长的工具结果"""
        print_tool_result("Success", duration=1.23)
        captured = capsys.readouterr()
        assert "Result" in captured.out
        assert "1.23" in captured.out

    def test_print_help(self, capsys):
        """打印帮助信息"""
        print_help()
        captured = capsys.readouterr()
        assert "/help" in captured.out
        assert "/clear" in captured.out
        assert "/exit" in captured.out
        assert "/stats" in captured.out

    def test_print_model_info(self, capsys):
        """打印模型信息"""
        print_model_info("gpt-4")
        captured = capsys.readouterr()
        assert "Model" in captured.out
        assert "gpt-4" in captured.out

    def test_print_history_empty(self, capsys):
        """打印空历史"""
        print_history([])
        captured = capsys.readouterr()
        assert "No messages" in captured.out

    def test_print_history_with_messages(self, capsys):
        """打印消息历史"""
        from langchain_core.messages import AIMessage, HumanMessage

        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
        print_history(messages)
        captured = capsys.readouterr()
        assert "Hello" in captured.out
        assert "Hi there" in captured.out

    def test_print_session_stats(self, capsys):
        """打印会话统计"""
        # 使用全局 session_stats 并设置值
        global_stats = session_stats

        global_stats.message_count = 5
        global_stats.tool_calls = 3
        global_stats.total_tokens = 1000

        print_session_stats("gpt-4")
        captured = capsys.readouterr()
        assert "gpt-4" in captured.out
        assert "5" in captured.out
        assert "3" in captured.out

        # 重置
        global_stats.reset()


class TestGlobalSessionStats:
    """全局会话统计测试"""

    def test_global_instance_exists(self):
        """全局实例存在"""
        assert session_stats is not None
        assert isinstance(session_stats, SessionStats)
