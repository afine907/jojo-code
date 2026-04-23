"""测试审计日志系统"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

from jojo_code.security.audit import AuditEvent, AuditLogger, AuditQuery


class TestAuditEvent:
    """测试 AuditEvent 数据类"""

    def test_create_event(self):
        """测试创建审计事件"""
        event = AuditEvent(
            id="test_001",
            timestamp="2026-04-23T00:00:00Z",
            session_id="sess_001",
            event_type="tool_call",
            tool="run_command",
            action="execute",
            params={"command": "ls"},
            allowed=True,
            mode="interactive",
            reason="test",
            risk_level="low",
        )

        assert event.id == "test_001"
        assert event.tool == "run_command"
        assert event.allowed is True
        assert event.risk_level == "low"

    def test_event_to_dict(self):
        """测试事件转换为字典"""
        from dataclasses import asdict

        event = AuditEvent(
            id="test_002",
            timestamp="2026-04-23T00:00:00Z",
            session_id="sess_001",
            event_type="tool_call",
            tool="read_file",
            action="read",
            params={"path": "/tmp/test.txt"},
            allowed=True,
            mode="interactive",
            reason="",
            risk_level="low",
        )

        d = asdict(event)
        assert d["id"] == "test_002"
        assert d["tool"] == "read_file"
        assert d["params"]["path"] == "/tmp/test.txt"


class TestAuditLogger:
    """测试 AuditLogger 类"""

    def test_init_with_default_path(self):
        """测试默认路径初始化"""
        logger = AuditLogger()
        assert logger.log_dir.name == "audit"
        assert logger.session_id is not None

    def test_init_with_custom_path(self):
        """测试自定义路径初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            logger = AuditLogger(log_dir=log_dir, session_id="test_session")

            assert logger.log_dir == log_dir
            assert logger.session_id == "test_session"

    def test_log_event(self):
        """测试记录事件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit"
            logger = AuditLogger(log_dir=log_dir)

            event = AuditEvent(
                id="test_001",
                timestamp="2026-04-23T00:00:00Z",
                session_id=logger.session_id,
                event_type="tool_call",
                tool="run_command",
                action="execute",
                params={"command": "ls"},
                allowed=True,
                mode="interactive",
                reason="",
                risk_level="low",
            )

            logger.log_event(event)
            logger.close()

            # 验证文件存在
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"{today}.jsonl"
            assert log_file.exists()

            # 验证内容
            with open(log_file) as f:
                line = f.readline()
                data = json.loads(line)
                assert data["id"] == "test_001"
                assert data["tool"] == "run_command"

    def test_log_tool_call(self):
        """测试便捷方法 log_tool_call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit"
            logger = AuditLogger(log_dir=log_dir)

            event_id = logger.log_tool_call(
                tool="run_command",
                action="execute",
                params={"command": "npm install"},
                decision={
                    "allowed": True,
                    "mode": "interactive",
                    "reason": "User confirmed",
                    "risk_level": "medium",
                },
                execution={
                    "status": "success",
                    "duration_ms": 1234,
                    "exit_code": 0,
                },
            )

            assert event_id.startswith("audit_")
            logger.close()


class TestAuditQuery:
    """测试 AuditQuery 类"""

    def test_query_empty(self):
        """测试查询空日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit"
            query = AuditQuery(log_dir=log_dir)

            results = query.query()
            assert results == []

    def test_query_with_events(self):
        """测试查询有事件的日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit"
            log_dir.mkdir(parents=True, exist_ok=True)

            # 创建测试日志
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"{today}.jsonl"

            events = [
                {
                    "id": "audit_001",
                    "timestamp": "2026-04-23T08:00:00Z",
                    "session_id": "sess_001",
                    "event_type": "tool_call",
                    "tool": "run_command",
                    "action": "execute",
                    "params": {"command": "ls"},
                    "allowed": True,
                    "mode": "interactive",
                    "reason": "",
                    "risk_level": "low",
                },
                {
                    "id": "audit_002",
                    "timestamp": "2026-04-23T08:01:00Z",
                    "session_id": "sess_001",
                    "event_type": "tool_call",
                    "tool": "write_file",
                    "action": "write",
                    "params": {"path": "test.txt"},
                    "allowed": True,
                    "mode": "interactive",
                    "reason": "User confirmed",
                    "risk_level": "medium",
                },
                {
                    "id": "audit_003",
                    "timestamp": "2026-04-23T08:02:00Z",
                    "session_id": "sess_001",
                    "event_type": "tool_call",
                    "tool": "run_command",
                    "action": "execute",
                    "params": {"command": "rm -rf /"},
                    "allowed": False,
                    "mode": "interactive",
                    "reason": "Dangerous command",
                    "risk_level": "critical",
                },
            ]

            with open(log_file, "w") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")

            # 测试查询所有
            query = AuditQuery(log_dir=log_dir)
            results = query.query()
            assert len(results) == 3

            # 测试按工具过滤
            results = query.query(tool="run_command")
            assert len(results) == 2

            # 测试按允许状态过滤
            results = query.query(allowed=True)
            assert len(results) == 2

            results = query.query(allowed=False)
            assert len(results) == 1

            # 测试按风险等级过滤
            results = query.query(risk_level="critical")
            assert len(results) == 1

            # 测试 limit
            results = query.query(limit=2)
            assert len(results) == 2

    def test_get_statistics(self):
        """测试获取统计数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit"
            log_dir.mkdir(parents=True, exist_ok=True)

            today = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"{today}.jsonl"

            events = [
                {
                    "id": f"audit_{i}",
                    "timestamp": "2026-04-23T08:00:00Z",
                    "session_id": "sess_001",
                    "event_type": "tool_call",
                    "tool": "run_command" if i % 2 == 0 else "write_file",
                    "action": "execute",
                    "params": {},
                    "allowed": i < 4,
                    "mode": "interactive",
                    "reason": "",
                    "risk_level": ["low", "medium", "high", "critical", "low"][i],
                }
                for i in range(5)
            ]

            with open(log_file, "w") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")

            query = AuditQuery(log_dir=log_dir)
            stats = query.get_statistics()

            assert stats["total_calls"] == 5
            assert stats["allowed"] == 4
            assert stats["denied"] == 1
            assert "run_command" in stats["by_tool"]
            assert "write_file" in stats["by_tool"]

    def test_get_recent(self):
        """测试获取最近事件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "audit"
            log_dir.mkdir(parents=True, exist_ok=True)

            today = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"{today}.jsonl"

            for i in range(10):
                event = {
                    "id": f"audit_{i}",
                    "timestamp": "2026-04-23T08:00:00Z",
                    "session_id": "sess_001",
                    "event_type": "tool_call",
                    "tool": "run_command",
                    "action": "execute",
                    "params": {},
                    "allowed": True,
                    "mode": "interactive",
                    "reason": "",
                    "risk_level": "low",
                }
                with open(log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")

            query = AuditQuery(log_dir=log_dir)
            results = query.get_recent(limit=5)

            assert len(results) == 5
