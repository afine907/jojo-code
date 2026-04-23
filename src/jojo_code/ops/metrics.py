"""AgentOps 指标计算引擎"""

from dataclasses import dataclass, field
from datetime import datetime

from .models import SpanStatus, SpanType, Trace


@dataclass
class MetricsSummary:
    """指标汇总"""

    total_traces: int = 0
    completed_traces: int = 0
    failed_traces: int = 0

    avg_thinking_rounds: float = 0.0
    avg_tool_calls: float = 0.0
    avg_duration_ms: float = 0.0

    tool_success_rate: float = 0.0
    task_success_rate: float = 0.0

    tool_usage: dict[str, int] = field(default_factory=dict)
    error_types: dict[str, int] = field(default_factory=dict)

    # 时间范围
    start_time: datetime | None = None
    end_time: datetime | None = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "total_traces": self.total_traces,
            "completed_traces": self.completed_traces,
            "failed_traces": self.failed_traces,
            "avg_thinking_rounds": round(self.avg_thinking_rounds, 2),
            "avg_tool_calls": round(self.avg_tool_calls, 2),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "tool_success_rate": round(self.tool_success_rate, 4),
            "task_success_rate": round(self.task_success_rate, 4),
            "tool_usage": self.tool_usage,
            "error_types": self.error_types,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class TraceMetrics:
    """单个 Trace 的指标"""

    trace_id: str
    task: str
    status: SpanStatus

    thinking_rounds: int = 0
    tool_calls: int = 0
    errors: int = 0

    duration_ms: int = 0
    tool_success_rate: float = 1.0

    tools_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "task": self.task,
            "status": self.status.value,
            "thinking_rounds": self.thinking_rounds,
            "tool_calls": self.tool_calls,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "tool_success_rate": round(self.tool_success_rate, 4),
            "tools_used": self.tools_used,
        }


class MetricsEngine:
    """指标计算引擎"""

    def __init__(self, traces: list[Trace]):
        self.traces = traces

    def calculate(self) -> MetricsSummary:
        """计算所有指标"""
        if not self.traces:
            return MetricsSummary()

        completed = [t for t in self.traces if t.status == SpanStatus.COMPLETED]
        failed = [t for t in self.traces if t.status == SpanStatus.FAILED]

        total_thinking = sum(t.thinking_count for t in self.traces)
        total_tool_calls = sum(t.tool_call_count for t in self.traces)
        total_duration = sum(t.duration_ms for t in self.traces)

        # 工具使用统计
        tool_usage: dict[str, int] = {}
        for trace in self.traces:
            for span in trace.spans:
                if span.type == SpanType.TOOL_CALL:
                    tool_usage[span.name] = tool_usage.get(span.name, 0) + 1

        # 错误类型统计
        error_types: dict[str, int] = {}
        for trace in self.traces:
            for span in trace.spans:
                if span.error:
                    # 简单分类：取错误信息前 50 字符
                    error_key = span.error[:50]
                    error_types[error_key] = error_types.get(error_key, 0) + 1

        # 计算平均工具成功率
        tool_rates = [t.tool_success_rate for t in self.traces]
        avg_tool_rate = sum(tool_rates) / len(tool_rates) if tool_rates else 1.0

        # 时间范围
        start_time = min(t.start_time for t in self.traces)
        end_time = max(t.end_time for t in self.traces if t.end_time) or start_time

        return MetricsSummary(
            total_traces=len(self.traces),
            completed_traces=len(completed),
            failed_traces=len(failed),
            avg_thinking_rounds=total_thinking / len(self.traces),
            avg_tool_calls=total_tool_calls / len(self.traces),
            avg_duration_ms=total_duration / len(self.traces),
            tool_success_rate=avg_tool_rate,
            task_success_rate=len(completed) / len(self.traces),
            tool_usage=tool_usage,
            error_types=error_types,
            start_time=start_time,
            end_time=end_time,
        )

    def calculate_trace_metrics(self, trace: Trace) -> TraceMetrics:
        """计算单个 Trace 的指标"""
        tools_used = [span.name for span in trace.spans if span.type == SpanType.TOOL_CALL]

        return TraceMetrics(
            trace_id=trace.id,
            task=trace.task,
            status=trace.status,
            thinking_rounds=trace.thinking_count,
            tool_calls=trace.tool_call_count,
            errors=trace.error_count,
            duration_ms=trace.duration_ms,
            tool_success_rate=trace.tool_success_rate,
            tools_used=tools_used,
        )

    def filter_by_time(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> list[Trace]:
        """按时间范围过滤"""
        filtered = self.traces
        if start:
            filtered = [t for t in filtered if t.start_time >= start]
        if end:
            filtered = [t for t in filtered if t.start_time <= end]
        return filtered

    def filter_by_session(self, session_id: str) -> list[Trace]:
        """按会话过滤"""
        return [t for t in self.traces if t.session_id == session_id]

    def filter_by_status(self, status: SpanStatus) -> list[Trace]:
        """按状态过滤"""
        return [t for t in self.traces if t.status == status]

    def get_tool_usage_ranking(self, limit: int = 10) -> list[tuple[str, int]]:
        """获取工具使用排名"""
        tool_usage: dict[str, int] = {}
        for trace in self.traces:
            for span in trace.spans:
                if span.type == SpanType.TOOL_CALL:
                    tool_usage[span.name] = tool_usage.get(span.name, 0) + 1

        return sorted(tool_usage.items(), key=lambda x: -x[1])[:limit]

    def get_error_distribution(self) -> dict[str, int]:
        """获取错误分布"""
        error_types: dict[str, int] = {}
        for trace in self.traces:
            for span in trace.spans:
                if span.error:
                    error_key = span.error[:50]
                    error_types[error_key] = error_types.get(error_key, 0) + 1
        return error_types

    def get_performance_stats(self) -> dict:
        """获取性能统计"""
        if not self.traces:
            return {
                "min_duration_ms": 0,
                "max_duration_ms": 0,
                "median_duration_ms": 0,
                "p95_duration_ms": 0,
            }

        durations = sorted([t.duration_ms for t in self.traces])
        n = len(durations)

        return {
            "min_duration_ms": durations[0],
            "max_duration_ms": durations[-1],
            "median_duration_ms": durations[n // 2],
            "p95_duration_ms": durations[int(n * 0.95)] if n > 1 else durations[-1],
        }
