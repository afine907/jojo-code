# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

jojo-Code is a mini coding agent built with LangGraph, designed for learning AI Agent architecture. It implements the classic "Thinking → Tool Call → Execute → Observe" agent loop pattern.

## Commands

```bash
# Run the CLI
uv run jojo-code

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_agent.py -v

# Run with coverage
uv run pytest tests/ -v --cov=src/jojo_code --cov-report=html

# Linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/

# Build package
uv build
```

## Architecture

The codebase follows a three-layer architecture:

```
CLI Layer (cli/) → Agent Loop (agent/) → Tool Layer (tools/)
```

**Agent Loop (LangGraph State Machine):**
- `thinking_node` → `execute_node` → loop back or END
- State managed via `AgentState` TypedDict with messages, tool_calls, tool_results
- Maximum 50 iterations per session

**Key Files:**
- [agent/graph.py](src/jojo_code/agent/graph.py) - LangGraph state machine definition
- [agent/nodes.py](src/jojo_code/agent/nodes.py) - thinking/execute node implementations
- [agent/state.py](src/jojo_code/agent/state.py) - AgentState TypedDict
- [tools/registry.py](src/jojo_code/tools/registry.py) - Tool registration and execution
- [core/llm.py](src/jojo_code/core/llm.py) - LLM client (OpenAI/Anthropic/compatible APIs)

**Tool System:**
Tools are LangChain `BaseTool` instances. Register new tools in `ToolRegistry._register_default_tools()`.

**Memory Management:**
`ConversationMemory` handles message history with automatic token counting (tiktoken) and compression when exceeding `max_tokens`.

## Configuration

Create `.env` file (see `.env.example`). Supports:
1. OpenAI-compatible APIs (LongCat, DeepSeek) - set `OPENAI_BASE_URL`
2. Anthropic Claude - set `ANTHROPIC_API_KEY`
3. OpenAI default - set `OPENAI_API_KEY`

## Testing

Tests use pytest with `pytest-asyncio`. Markers:
- `@pytest.mark.e2e` - real API calls
- `@pytest.mark.longcat` - LongCat API tests
- `@pytest.mark.slow` - slow tests

## Code Style

- Line length: 100 characters
- Python 3.11+ with type hints
- Ruff for linting/formatting, mypy for type checking
