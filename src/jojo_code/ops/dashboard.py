"""AgentOps CLI 监控面板"""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .metrics import MetricsSummary, TraceMetrics
from .models import SpanStatus, SpanType, Trace


class Dashboard:
    """CLI 监控面板"""

    def __init__(self):
        self.console = Console()

    def show_current_trace(self, trace: Trace) -> None:
        """显示当前 Trace 状态"""
        self.console.clear()

        # 任务信息
        self.console.print(
            Panel(
                f"[bold]{trace.task}[/bold]",
                title="📋 当前任务",
                border_style="blue",
            )
        )

        # 执行步骤
        table = Table(title="执行步骤")
        table.add_column("#", style="dim")
        table.add_column("类型")
        table.add_column("名称")
        table.add_column("状态")
        table.add_column("耗时")

        for i, span in enumerate(trace.spans, 1):
            status_style = {
                SpanStatus.COMPLETED: "green",
                SpanStatus.FAILED: "red",
                SpanStatus.STARTED: "yellow",
            }.get(span.status, "white")

            type_icon = {
                SpanType.THINKING: "💭",
                SpanType.TOOL_CALL: "🔧",
                SpanType.OBSERVE: "👁️",
                SpanType.ERROR: "❌",
            }.get(span.type, "❓")

            table.add_row(
                str(i),
                f"{type_icon} {span.type.value}",
                span.name or "-",
                f"[{status_style}]{span.status.value}[/{status_style}]",
                f"{span.duration_ms}ms",
            )

        self.console.print(table)

        # 汇总
        self.console.print(
            Panel(
                f"[bold]思考轮数:[/bold] {trace.thinking_count}  "
                f"[bold]工具调用:[/bold] {trace.tool_call_count}  "
                f"[bold]错误:[/bold] {trace.error_count}  "
                f"[bold]耗时:[/bold] {trace.duration_ms}ms",
                title="📊 汇总",
                border_style="green",
            )
        )

    def show_metrics(self, metrics: MetricsSummary) -> None:
        """显示指标汇总"""
        # 成功率进度条
        success_bar = self._create_progress_bar(metrics.task_success_rate)
        tool_bar = self._create_progress_bar(metrics.tool_success_rate)

        self.console.print(
            Panel(
                f"""
[bold green]任务成功率[/bold green]: {success_bar} {metrics.task_success_rate:.1%}
[bold blue]工具成功率[/bold blue]: {tool_bar} {metrics.tool_success_rate:.1%}
[bold yellow]平均思考轮数[/bold yellow]: {metrics.avg_thinking_rounds:.1f}
[bold cyan]平均耗时[/bold cyan]: {metrics.avg_duration_ms:.0f}ms
[bold]总任务数[/bold]: {metrics.total_traces}
""",
                title="📊 指标汇总",
                border_style="green",
            )
        )

        # 工具使用表格
        if metrics.tool_usage:
            table = Table(title="🔧 工具使用统计")
            table.add_column("工具", style="cyan")
            table.add_column("次数", justify="right")
            table.add_column("占比", justify="right")

            total = sum(metrics.tool_usage.values())
            for tool, count in sorted(metrics.tool_usage.items(), key=lambda x: -x[1]):
                percentage = count / total * 100 if total > 0 else 0
                table.add_row(tool, str(count), f"{percentage:.1f}%")

            self.console.print(table)

        # 错误统计
        if metrics.error_types:
            error_table = Table(title="❌ 错误统计")
            error_table.add_column("错误", style="red")
            error_table.add_column("次数", justify="right")

            for error, count in sorted(metrics.error_types.items(), key=lambda x: -x[1])[:10]:
                error_table.add_row(error[:50], str(count))

            self.console.print(error_table)

    def show_trace_metrics(self, metrics: TraceMetrics) -> None:
        """显示单个 Trace 的指标"""
        status_style = {
            SpanStatus.COMPLETED: "green",
            SpanStatus.FAILED: "red",
            SpanStatus.STARTED: "yellow",
        }.get(metrics.status, "white")

        self.console.print(
            Panel(
                f"""
[bold]任务:[/bold] {metrics.task}
[bold]状态:[/bold] [{status_style}]{metrics.status.value}[/{status_style}]
[bold]思考轮数:[/bold] {metrics.thinking_rounds}
[bold]工具调用:[/bold] {metrics.tool_calls}
[bold]错误:[/bold] {metrics.errors}
[bold]耗时:[/bold] {metrics.duration_ms}ms
[bold]工具成功率:[/bold] {metrics.tool_success_rate:.1%}
[bold]使用的工具:[/bold] {", ".join(metrics.tools_used) or "-"}
""",
                title=f"📋 Trace: {metrics.trace_id}",
                border_style="blue",
            )
        )

    def show_traces_list(self, traces: list[Trace], limit: int = 10) -> None:
        """显示 Trace 列表"""
        table = Table(title=f"📋 最近 {min(limit, len(traces))} 个任务")
        table.add_column("ID", style="dim")
        table.add_column("任务")
        table.add_column("状态")
        table.add_column("思考")
        table.add_column("工具")
        table.add_column("耗时")

        for trace in traces[-limit:]:
            status_style = {
                SpanStatus.COMPLETED: "green",
                SpanStatus.FAILED: "red",
                SpanStatus.STARTED: "yellow",
            }.get(trace.status, "white")

            # 截断任务名
            task_display = trace.task[:30] + "..." if len(trace.task) > 30 else trace.task

            table.add_row(
                trace.id,
                task_display,
                f"[{status_style}]{trace.status.value}[/{status_style}]",
                str(trace.thinking_count),
                str(trace.tool_call_count),
                f"{trace.duration_ms}ms",
            )

        self.console.print(table)

    def show_summary_report(self, metrics: MetricsSummary) -> None:
        """显示完整汇总报告"""
        self.console.print("\n")

        # 标题
        self.console.print(
            Panel(
                "[bold cyan]AgentOps 汇总报告[/bold cyan]\n"
                f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                border_style="cyan",
            )
        )

        # 总体指标
        self.show_metrics(metrics)

        # 性能统计
        if metrics.total_traces > 0:
            self.console.print(
                Panel(
                    f"""
[bold]总任务:[/bold] {metrics.total_traces}
[bold]成功:[/bold] {metrics.completed_traces} ({metrics.task_success_rate:.1%})
[bold]失败:[/bold] {metrics.failed_traces}
[bold]平均思考轮数:[/bold] {metrics.avg_thinking_rounds:.1f}
[bold]平均工具调用:[/bold] {metrics.avg_tool_calls:.1f}
[bold]平均耗时:[/bold] {metrics.avg_duration_ms:.0f}ms
""",
                    title="📈 性能统计",
                    border_style="blue",
                )
            )

    def _create_progress_bar(self, value: float, width: int = 20) -> str:
        """创建进度条"""
        filled = int(value * width)
        empty = width - filled
        return "[green]█[/green]" * filled + "[dim]░[/dim]" * empty

    def print_error(self, message: str) -> None:
        """打印错误信息"""
        self.console.print(f"[bold red]❌ {message}[/bold red]")

    def print_success(self, message: str) -> None:
        """打印成功信息"""
        self.console.print(f"[bold green]✅ {message}[/bold green]")

    def print_info(self, message: str) -> None:
        """打印信息"""
        self.console.print(f"[bold blue]ℹ️ {message}[/bold blue]")

    def print_warning(self, message: str) -> None:
        """打印警告"""
        self.console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")
