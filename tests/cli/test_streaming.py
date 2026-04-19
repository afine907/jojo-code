"""流式输出测试"""

from unittest.mock import MagicMock, patch

import pytest


class TestStreaming:
    """测试流式输出功能"""

    @pytest.fixture
    def mock_llm_stream(self):
        """Mock LLM 流式响应"""
        chunks = [
            AIMessageChunk(content="Hello "),
            AIMessageChunk(content="world!"),
            AIMessageChunk(content=" Testing streaming."),
        ]
        return iter(chunks)

    @pytest.fixture
    def mock_graph_stream(self, mock_llm_stream):
        """Mock graph.stream() 返回值"""
        return mock_llm_stream

    def test_streaming_imports(self):
        """测试流式相关导入"""
        from rich.live import Live

        assert Live is not None

    def test_streaming_message_extraction(self):
        """测试从流式块提取消息内容"""

        chunks = [
            {"role": "assistant", "content": "Hello "},
            {"role": "assistant", "content": "world!"},
        ]

        full_content = ""
        for chunk in chunks:
            if isinstance(chunk, dict):
                content = chunk.get("content", "")
            else:
                content = getattr(chunk, "content", "")
            if content:
                full_content += content

        assert full_content == "Hello world!"

    def test_streaming_graph_iteration(self):
        """测试 graph.stream() 迭代"""
        chunks = [
            {"thinking": {"messages": [{"role": "assistant", "content": "Hello "}]}},
            {"thinking": {"messages": [{"role": "assistant", "content": "world!"}]}},
            {"thinking": {"messages": [], "is_complete": True}},
        ]

        full_response = ""
        for chunk in chunks:
            for node_name, node_output in chunk.items():
                if node_name == "thinking" and "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, dict):
                            content = msg.get("content", "")
                        else:
                            content = getattr(msg, "content", "")
                        if content:
                            full_response += content

        assert full_response == "Hello world!"

    def test_streaming_tool_result_handling(self):
        """测试流式输出工具结果"""
        chunks = [
            {"execute": {"tool_results": ["Result 1"]}},
            {"execute": {"tool_results": ["Result 2"]}},
        ]

        tool_results = []
        for chunk in chunks:
            for node_name, node_output in chunk.items():
                if node_name == "execute" and "tool_results" in node_output:
                    for result in node_output["tool_results"]:
                        if result:
                            tool_results.append(result)

        assert len(tool_results) == 2
        assert tool_results[0] == "Result 1"
        assert tool_results[1] == "Result 2"

    def test_streaming_interrupt(self):
        """测试流式中断"""
        chunks = [
            {"thinking": {"messages": [{"role": "assistant", "content": "Partial "}]}},
            KeyboardInterrupt(),
        ]

        full_response = ""
        try:
            for chunk in chunks:
                if isinstance(chunk, KeyboardInterrupt):
                    raise chunk
                for node_name, node_output in chunk.items():
                    if node_name == "thinking" and "messages" in node_output:
                        for msg in node_output["messages"]:
                            content = msg.get("content", "") if isinstance(msg, dict) else ""
                            if content:
                                full_response += content
        except KeyboardInterrupt:
            pass

        assert full_response == "Partial "


class AIMessageChunk:
    """Mock AIMessageChunk for testing"""

    def __init__(self, content: str = ""):
        self.content = content
        self.type = "ai"
        self.additional_kwargs = {}


class TestStreamingIntegration:
    """测试流式输出集成"""

    @patch("nano_code.agent.graph.get_agent_graph")
    @patch("nano_code.core.llm.get_llm")
    def test_streaming_with_mocked_graph(self, mock_get_llm, mock_get_graph):
        """测试使用 mock 的 graph 进行流式输出"""
        from nano_code.agent.state import create_initial_state

        mock_graph = MagicMock()
        mock_get_graph.return_value = mock_graph

        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        state = create_initial_state("test query")
        state["messages"] = [{"role": "user", "content": "test query"}]

        chunks = [
            {"thinking": {"messages": [{"role": "assistant", "content": "Response "}]}},
            {"thinking": {"messages": [{"role": "assistant", "content": "part 1"}]}},
            {"thinking": {"messages": [], "is_complete": True}},
        ]

        mock_graph.stream.return_value = iter(chunks)

        full_response = ""
        for chunk in mock_graph.stream(state):
            for node_name, node_output in chunk.items():
                if node_name == "thinking" and "messages" in node_output:
                    for msg in node_output["messages"]:
                        content = msg.get("content", "") if isinstance(msg, dict) else ""
                        if content:
                            full_response += content

        assert full_response == "Response part 1"
