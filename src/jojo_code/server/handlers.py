"""Agent handlers for JSON-RPC server."""

from collections.abc import Generator

from .jsonrpc import get_server

# 全局 Agent 实例
_agent = None
_conversation_memory = None
_audit_logger = None


def init_agent():
    """初始化 Agent"""
    global _agent, _conversation_memory, _audit_logger

    from jojo_code.agent.graph import get_agent_graph
    from jojo_code.memory.conversation import ConversationMemory
    from jojo_code.security.audit import AuditLogger

    _agent = get_agent_graph()
    _conversation_memory = ConversationMemory()
    _audit_logger = AuditLogger()


def get_audit_logger():
    """获取审计日志记录器"""
    global _audit_logger
    if _audit_logger is None:
        from jojo_code.security.audit import AuditLogger

        _audit_logger = AuditLogger()
    return _audit_logger


def handle_chat(message: str, stream: bool = False) -> dict | Generator:
    """处理聊天请求"""
    if _agent is None:
        init_agent()

    from jojo_code.agent.state import create_initial_state

    state = create_initial_state(message)

    if stream:
        return _stream_chat(state)
    else:
        return _sync_chat(state)


def _sync_chat(state: dict) -> dict:
    """同步聊天"""
    try:
        for chunk in _agent.stream(state):
            # chunk 格式: {'thinking': {...}} 或 {'execute': {...}}
            for node_name, node_state in chunk.items():
                if node_name == "thinking":
                    messages = node_state.get("messages", [])
                    if messages:
                        last_message = messages[-1]
                        content = last_message.get("content", "")
                        if content:
                            return {"content": content}
                    # 检查是否完成
                    if node_state.get("is_complete"):
                        return {"content": "任务完成"}

        return {"content": "No response from agent"}
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"content": f"Error: {e}"}


def _stream_chat(state: dict) -> Generator[dict, None, None]:
    """流式聊天"""
    for event in _agent.stream(state):
        # 处理不同类型的事件
        if "thinking" in event:
            yield {"type": "thinking", "text": event["thinking"]}

        if "tool_calls" in event:
            for tool_call in event["tool_calls"]:
                yield {
                    "type": "tool_call",
                    "tool_name": tool_call.get("name"),
                    "args": tool_call.get("args", {}),
                }

        if "tool_results" in event:
            for result in event["tool_results"]:
                yield {
                    "type": "tool_result",
                    "tool_name": result.get("name"),
                    "result": result.get("result"),
                }

        if "content" in event:
            yield {"type": "content", "text": event["content"]}

    yield {"type": "done"}


def handle_clear() -> dict:
    """清空对话历史"""
    global _conversation_memory
    if _conversation_memory:
        _conversation_memory.clear()
    return {"status": "ok"}


def handle_get_model() -> dict:
    """获取当前模型"""
    from jojo_code.core.config import get_settings

    settings = get_settings()
    return {"model": settings.model}


def handle_get_stats() -> dict:
    """获取会话统计"""
    if _conversation_memory is None:
        return {"messages": 0, "tokens": 0}

    return {
        "messages": len(_conversation_memory.messages),
        "tokens": _conversation_memory.total_tokens,
    }


# ========== 权限相关 Handlers ==========


def handle_permission_mode(params: dict) -> dict:
    """获取或设置权限模式

    Args:
        params: 可包含 mode 字段来设置模式

    Returns:
        当前权限模式
    """
    from jojo_code.security.manager import get_permission_manager

    pm = get_permission_manager()
    if pm is None:
        return {"status": "error", "error": "Permission manager not initialized"}

    mode = params.get("mode")
    if mode:
        try:
            pm.set_mode(mode)
            return {"status": "ok", "mode": mode}
        except ValueError as e:
            return {"status": "error", "error": str(e)}

    return {"status": "ok", "mode": pm.mode.value}


def handle_permission_confirm(params: dict) -> dict:
    """处理权限确认响应

    Args:
        params: 包含 session_id 和 approved 字段

    Returns:
        确认状态
    """
    session_id = params.get("session_id")
    approved = params.get("approved", False)
    return {"status": "ok", "session_id": session_id, "approved": approved}


def handle_audit_query(params: dict) -> dict:
    """查询审计日志

    Args:
        params: 查询参数 (start_date, end_date, tool, allowed, risk_level, limit)

    Returns:
        审计日志列表
    """
    from jojo_code.security.audit import AuditQuery

    query = AuditQuery()
    results = query.query(
        start_date=params.get("start_date"),
        end_date=params.get("end_date"),
        tool=params.get("tool"),
        allowed=params.get("allowed"),
        risk_level=params.get("risk_level"),
        limit=params.get("limit", 100),
    )
    return {"status": "ok", "results": results, "count": len(results)}


def handle_audit_stats(params: dict) -> dict:
    """获取审计统计

    Args:
        params: 可包含 date 字段

    Returns:
        统计数据
    """
    from jojo_code.security.audit import AuditQuery

    query = AuditQuery()
    stats = query.get_statistics(params.get("date"))
    return {"status": "ok", "statistics": stats}


def handle_audit_recent(params: dict) -> dict:
    """获取最近的审计事件

    Args:
        params: 可包含 limit 字段

    Returns:
        审计事件列表
    """
    from jojo_code.security.audit import AuditQuery

    query = AuditQuery()
    limit = params.get("limit", 20)
    results = query.get_recent(limit=limit)
    return {"status": "ok", "results": results}


def register_handlers():
    """注册所有处理器"""
    server = get_server()

    # Agent handlers
    server.register("chat", handle_chat)
    server.register("clear", handle_clear)
    server.register("get_model", handle_get_model)
    server.register("get_stats", handle_get_stats)

    # Permission handlers
    server.register("permission/mode", handle_permission_mode)
    server.register("permission/confirm", handle_permission_confirm)

    # Audit handlers
    server.register("audit/query", handle_audit_query)
    server.register("audit/stats", handle_audit_stats)
    server.register("audit/recent", handle_audit_recent)
