"""jojo-code CLI 入口。

命令:
    jojo-code                  # 启动 TUI
    jojo-code server start     # 启动 WebSocket 服务
    jojo-code server stop      # 停止服务
    jojo-code config set       # 设置配置
    jojo-code config show      # 显示配置
"""

import argparse
import sys


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        prog="jojo-code",
        description="jojo-code - Python coding agent powered by LangGraph",
    )
    parser.add_argument("--server", help="WebSocket server URL", default="ws://localhost:8080/ws")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # server 子命令
    server_parser = subparsers.add_parser("server", help="管理 WebSocket 服务")
    server_sub = server_parser.add_subparsers(dest="action")
    server_sub.add_parser("start", help="启动服务")
    server_sub.add_parser("stop", help="停止服务")

    # config 子命令
    config_parser = subparsers.add_parser("config", help="管理配置")
    config_sub = config_parser.add_subparsers(dest="action")
    config_set = config_sub.add_parser("set", help="设置配置")
    config_set.add_argument("key", help="配置项")
    config_set.add_argument("value", help="配置值")
    config_sub.add_parser("show", help="显示配置")

    args = parser.parse_args()

    if args.command is None:
        # 默认启动 TUI
        _start_tui(args.server)
    elif args.command == "server":
        _handle_server(args)
    elif args.command == "config":
        _handle_config(args)


def _start_tui(server_url: str):
    """启动 Textual TUI"""
    try:
        from jojo_code.cli.app import JojoCodeApp

        app = JojoCodeApp(server_url=server_url)
        app.run()
    except ImportError as e:
        print(f"错误: 缺少依赖 - {e}")
        print("请运行: pip install 'jojo-code[all]'")
        sys.exit(1)


def _handle_server(args):
    """处理 server 子命令"""
    if args.action == "start":
        print("启动 WebSocket 服务...")
        try:
            import uvicorn
            from jojo_code.server.ws_server import app

            uvicorn.run(app, host="0.0.0.0", port=8080)
        except ImportError as e:
            print(f"错误: 缺少依赖 - {e}")
            sys.exit(1)
    elif args.action == "stop":
        print("停止服务 - 功能开发中")
    else:
        print("请指定操作: start 或 stop")


def _handle_config(args):
    """处理 config 子命令"""
    from pathlib import Path

    config_dir = Path.home() / ".jojo-code"
    config_file = config_dir / "config.json"

    if args.action == "set":
        import json

        config_dir.mkdir(parents=True, exist_ok=True)
        config = {}
        if config_file.exists():
            config = json.loads(config_file.read_text())
        config[args.key] = args.value
        config_file.write_text(json.dumps(config, indent=2))
        print(f"已设置 {args.key} = {args.value}")
    elif args.action == "show":
        import json

        if config_file.exists():
            config = json.loads(config_file.read_text())
            for k, v in config.items():
                print(f"  {k} = {v}")
        else:
            print("暂无配置")
    else:
        print("请指定操作: set 或 show")


if __name__ == "__main__":
    main()
