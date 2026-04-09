# Nano-Code

A mini coding agent built with LangGraph - Learn Agent architecture through practice.

一个使用 LangGraph 构建的迷你版编码 Agent，通过实践学习 Agent 核心架构。

## Features

- 🔧 **Tool System**: File read/write, code search, shell execution
- 🤖 **Agent Loop**: Thinking → Tool Call → Execute → Observe cycle
- 💾 **Memory Management**: Conversation history with auto-compression
- 🖥️ **CLI Interface**: Interactive terminal with rich output

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Agent Loop                            │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│   │Thinking │ ──▶│Execute  │ ──▶│Observe  │──┐        │
│   └─────────┘    └─────────┘    └─────────┘  │        │
│        ▲                                        │        │
│        └────────────────────────────────────────┘        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Tools                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │read_file │ │write_file│ │grep_search│ │run_cmd   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nano-code.git
cd nano-code

# Install dependencies (using uv)
uv sync

# Or install with pip
pip install -e .
```

## Usage

```bash
# Set your API key
export OPENAI_API_KEY=your-key-here
# or
export ANTHROPIC_API_KEY=your-key-here

# Run nano-code
uv run nano-code
```

### Commands

- `/help` - Show help
- `/clear` - Clear conversation memory
- `/exit` - Exit the program

## Development

### Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=src/nano_code
```

### Project Structure

```text
nano-code/
├── src/nano_code/
│   ├── agent/          # Agent core (graph, state, nodes)
│   ├── tools/          # Tool implementations
│   ├── memory/         # Conversation memory
│   ├── cli/            # CLI interface
│   └── core/           # Config and LLM client
└── tests/              # Test suite
```

## Tech Stack

- **Agent Framework**: LangGraph
- **Tool Definition**: LangChain Tools
- **LLM Client**: langchain-openai / langchain-anthropic
- **CLI**: rich + prompt-toolkit
- **Testing**: pytest

## Learning Points

This project demonstrates:

1. **Agent Loop Pattern**: How to implement the thinking-action-observation cycle
2. **LangGraph**: Building state machines for AI agents
3. **Tool Abstraction**: How to define and execute tools safely
4. **Memory Management**: Token counting and context compression
5. **TDD Development**: Test-driven development workflow

## License

MIT License

## Acknowledgments

Inspired by [Claude Code](https://claude.ai/code) - Anthropic's official CLI for Claude.
