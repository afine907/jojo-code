"""审计日志系统

记录所有工具调用和权限决策，支持查询和统计。
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """审计事件"""

    id: str
    timestamp: str
    session_id: str

    # 事件详情
    event_type: str  # tool_call | permission_change | mode_change
    tool: str
    action: str
    params: dict[str, Any]

    # 权限决策
    allowed: bool
    mode: str
    reason: str
    risk_level: str
    matched_rule: str | None = None

    # 用户交互
    prompt_shown: bool = False
    user_response: str | None = None
    response_time_ms: int | None = None

    # 执行结果
    execution_status: str | None = None
    duration_ms: int | None = None
    exit_code: int | None = None
    error_message: str | None = None

    # 上下文
    agent_task: str | None = None
    working_directory: str | None = None


class AuditLogger:
    """审计日志记录器

    将审计事件记录到 JSONL 格式的日志文件中，按日期分文件存储。
    """

    def __init__(
        self,
        log_dir: Path | None = None,
        session_id: str | None = None,
    ):
        """初始化审计日志记录器

        Args:
            log_dir: 日志存储目录，默认 ~/.local/share/jojo-code/audit/
            session_id: 会话 ID，默认自动生成
        """
        self.log_dir = log_dir or Path.home() / ".local/share/jojo-code/audit"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self._current_file: Path | None = None
        self._file_handle = None

    def _get_log_file(self) -> Path:
        """获取当天日志文件路径"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"{today}.jsonl"

    def _ensure_file_open(self):
        """确保日志文件打开"""
        log_file = self._get_log_file()
        if self._current_file != log_file:
            if self._file_handle:
                self._file_handle.close()
            self._file_handle = open(log_file, "a", encoding="utf-8")
            self._current_file = log_file

    def log_event(self, event: AuditEvent):
        """记录审计事件

        Args:
            event: 审计事件
        """
        self._ensure_file_open()

        line = json.dumps(asdict(event), ensure_ascii=False)
        self._file_handle.write(line + "\n")
        self._file_handle.flush()

        logger.debug(f"Audit event logged: {event.id}")

    def log_tool_call(
        self,
        tool: str,
        action: str,
        params: dict,
        decision: dict,
        execution: dict | None = None,
        context: dict | None = None,
    ) -> str:
        """记录工具调用（便捷方法）

        Args:
            tool: 工具名称
            action: 操作名称
            params: 工具参数
            decision: 权限决策
            execution: 执行结果
            context: 上下文信息

        Returns:
            事件 ID
        """
        event_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        event = AuditEvent(
            id=event_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            session_id=self.session_id,
            event_type="tool_call",
            tool=tool,
            action=action,
            params=params,
            allowed=decision.get("allowed", False),
            mode=decision.get("mode", "unknown"),
            reason=decision.get("reason", ""),
            risk_level=decision.get("risk_level", "unknown"),
            matched_rule=decision.get("matched_rule"),
            prompt_shown=decision.get("prompt_shown", False),
            user_response=decision.get("user_response"),
            response_time_ms=decision.get("response_time_ms"),
            execution_status=execution.get("status") if execution else None,
            duration_ms=execution.get("duration_ms") if execution else None,
            exit_code=execution.get("exit_code") if execution else None,
            error_message=execution.get("error") if execution else None,
            agent_task=context.get("task") if context else None,
            working_directory=context.get("cwd") if context else None,
        )

        self.log_event(event)
        return event_id

    def close(self):
        """关闭日志文件"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None


class AuditQuery:
    """审计日志查询器

    支持按日期、工具、权限状态等条件查询审计日志。
    """

    def __init__(self, log_dir: Path | None = None):
        """初始化查询器

        Args:
            log_dir: 日志存储目录
        """
        self.log_dir = log_dir or Path.home() / ".local/share/jojo-code/audit"

    def query(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        tool: str | None = None,
        allowed: bool | None = None,
        risk_level: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """查询审计日志

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            tool: 过滤工具名称
            allowed: 过滤是否允许
            risk_level: 过滤风险等级
            limit: 最大返回数量

        Returns:
            审计事件列表
        """
        results = []

        # 确定查询的日期范围
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # 生成日期列表
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # 遍历日志文件
        for date in dates:
            log_file = self.log_dir / f"{date}.jsonl"
            if not log_file.exists():
                continue

            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # 应用过滤条件
                    if tool and event.get("tool") != tool:
                        continue
                    if allowed is not None and event.get("allowed") != allowed:
                        continue
                    if risk_level and event.get("risk_level") != risk_level:
                        continue

                    results.append(event)

                    if len(results) >= limit:
                        return results

        return results

    def get_statistics(self, date: str | None = None) -> dict:
        """获取统计数据

        Args:
            date: 统计日期，默认今天

        Returns:
            统计数据字典
        """
        date = date or datetime.now().strftime("%Y-%m-%d")
        events = self.query(start_date=date, end_date=date, limit=10000)

        stats = {
            "total_calls": len(events),
            "allowed": sum(1 for e in events if e.get("allowed")),
            "denied": sum(1 for e in events if not e.get("allowed")),
            "by_tool": self._count_by(events, "tool"),
            "by_risk": self._count_by(events, "risk_level"),
            "by_mode": self._count_by(events, "mode"),
        }

        return stats

    def _count_by(self, events: list[dict], key: str) -> dict:
        """按字段统计"""
        counts = {}
        for event in events:
            value = event.get(key, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def get_recent(self, limit: int = 20) -> list[dict]:
        """获取最近的审计事件

        Args:
            limit: 最大返回数量

        Returns:
            审计事件列表
        """
        return self.query(limit=limit)


__all__ = [
    "AuditEvent",
    "AuditLogger",
    "AuditQuery",
]
