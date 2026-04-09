"""CLI 主入口"""
import sys

from langchain_core.messages import HumanMessage
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.markdown import Markdown

from nano_code.agent.graph import get_agent_graph
from nano_code.agent.state import create_initial_state
from nano_code.cli.console import (
    console,
    print_assistant,
    print_error,
    print_tool_call,
    print_tool_result,
    print_user,
    print_welcome,
)
from nano_code.core.config import get_settings
from nano_code.memory.conversation import ConversationMemory


def run_interactive():
    """运行交互式会话"""
    print_welcome()

    # 初始化记忆
    settings = get_settings()
    storage_path = settings.storage_path / "sessions" / "default.json"
    memory = ConversationMemory(storage_path=storage_path, auto_save=True)

    # 初始化 Agent
    graph = get_agent_graph()

    # 初始化 prompt session
    session = PromptSession(
        history=FileHistory(str(settings.storage_path / "history.txt")),
        multiline=True,
        mouse_support=True,
    )

    console.print("\n[dim]提示: 输入多行内容时，按 Tab 换行，Enter 发送[/dim]\n")

    while True:
        try:
            # 获取用户输入
            user_input = session.prompt("\n> ", multiline=False)

            if not user_input.strip():
                continue

            # 处理命令
            if user_input.startswith("/"):
                handle_command(user_input, memory)
                continue

            # 打印用户消息
            print_user(user_input)

            # 添加到记忆
            memory.add_message(HumanMessage(content=user_input))

            # 运行 Agent
            state = create_initial_state(user_input)
            state["messages"] = memory.get_context()

            # 执行图
            result = graph.invoke(state)

            # 提取响应
            if result.get("messages"):
                last_msg = result["messages"][-1]
                if isinstance(last_msg, dict):
                    response = last_msg.get("content", "")
                else:
                    response = getattr(last_msg, "content", "")

                if response:
                    # 尝试渲染 Markdown
                    try:
                        print_assistant("")
                        console.print(Markdown(response))
                    except Exception:
                        print_assistant(response)

                    # 添加到记忆
                    from langchain_core.messages import AIMessage

                    memory.add_message(AIMessage(content=response))

        except KeyboardInterrupt:
            console.print("\n[yellow]已取消[/yellow]")
            continue
        except EOFError:
            console.print("\n[blue]再见！[/blue]")
            break
        except Exception as e:
            print_error(str(e))


def handle_command(command: str, memory: ConversationMemory):
    """处理命令

    Args:
        command: 命令字符串
        memory: 记忆管理器
    """
    cmd = command.strip().lower()

    if cmd in ("/exit", "/quit", "/q"):
        console.print("[blue]再见！[/blue]")
        sys.exit(0)

    elif cmd == "/clear":
        memory.clear()
        console.print("[green]已清空记忆[/green]")

    elif cmd == "/help":
        console.print(
            """
[bold]命令列表:[/bold]
  /help    - 显示帮助
  /clear   - 清空记忆
  /exit    - 退出程序
"""
        )

    else:
        console.print(f"[yellow]未知命令: {command}[/yellow]")


def main():
    """主入口"""
    try:
        run_interactive()
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
