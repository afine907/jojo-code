"""jojo-code CLI 入口。

命令:
    jojo-code                  # 启动 TUI
    jojo-code server start     # 启动 WebSocket 服务（前台）
    jojo-code server start -d  # 启动 WebSocket 服务（后台守护）
    jojo-code server stop      # 停止服务
    jojo-code server status    # 查看服务状态
    jojo-code config set       # 设置配置
    jojo-code config show      # 显示配置
    jojo-code config get       # 获取单个配置
"""

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

# ========== 常量 ==========

CONFIG_DIR = Path.home() / ".jojo-code"
CONFIG_FILE = CONFIG_DIR / "config.json"
PID_FILE = CONFIG_DIR / "server.pid"
LOG_FILE = CONFIG_DIR / "server.log"

DEFAULT_CONFIG = {
    "server": "ws://localhost:8080/ws",
    "host": "0.0.0.0",
    "port": "8080",
    "model": "",
}


# ========== 配置管理 ==========


def load_config() -> dict:
    """加载配置文件"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """保存配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def get_config_value(key: str) -> str | None:
    """获取配置值"""
    config = load_config()
    return config.get(key)


# ========== 服务管理 ==========


def _read_pid() -> int | None:
    """读取 PID 文件"""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # 检查进程是否还活着
            os.kill(pid, 0)
            return pid
        except (ValueError, ProcessLookupError, PermissionError):
            # PID 文件存在但进程已死，清理
            PID_FILE.unlink(missing_ok=True)
    return None


def _write_pid(pid: int) -> None:
    """写入 PID 文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))


def _remove_pid() -> None:
    """删除 PID 文件"""
    PID_FILE.unlink(missing_ok=True)


def server_start(args):
    """启动 WebSocket 服务"""
    config = load_config()
    host = args.host or config.get("host", "0.0.0.0")
    port = args.port or config.get("port", "8080")

    # 检查是否已在运行
    existing_pid = _read_pid()
    if existing_pid is not None:
        print(f"服务已在运行 (PID: {existing_pid})")
        print("如需重启，请先执行: jojo-code server stop")
        return

    if args.daemon:
        # 后台守护模式
        _start_daemon(host, int(port))
    else:
        # 前台模式
        _start_foreground(host, int(port))


def _start_foreground(host: str, port: int):
    """前台启动服务"""
    os.environ["JOJO_CODE_HOST"] = host
    os.environ["JOJO_CODE_PORT"] = str(port)

    print("🚀 jojo-code 服务启动中...")
    print(f"   地址: ws://{host}:{port}/ws")
    print(f"   健康检查: http://{host}:{port}/health")
    print("   按 Ctrl+C 停止")
    print()

    try:
        from jojo_code.server.ws_server import main as server_main

        # 写入 PID（当前进程）
        _write_pid(os.getpid())
        server_main()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        _remove_pid()


def _start_daemon(host: str, port: int):
    """后台守护模式启动"""
    os.environ["JOJO_CODE_HOST"] = host
    os.environ["JOJO_CODE_PORT"] = str(port)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 启动子进程
    process = subprocess.Popen(
        [sys.executable, "-m", "jojo_code.server.ws_server"],
        stdout=open(LOG_FILE, "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    _write_pid(process.pid)

    print(f"🚀 服务已在后台启动 (PID: {process.pid})")
    print(f"   地址: ws://{host}:{port}/ws")
    print(f"   日志: {LOG_FILE}")
    print("   停止: jojo-code server stop")


def server_stop(args):
    """停止服务"""
    pid = _read_pid()
    if pid is None:
        print("服务未运行")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"已发送停止信号 (PID: {pid})")

        # 等待进程退出
        import time

        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break

        _remove_pid()
        print("服务已停止")
    except ProcessLookupError:
        print("进程已不存在")
        _remove_pid()
    except PermissionError:
        print(f"无权限停止进程 {pid}")


def server_status(args):
    """查看服务状态"""
    pid = _read_pid()
    if pid is None:
        print("⚪ 服务未运行")
        return

    print(f"🟢 服务运行中 (PID: {pid})")

    # 尝试健康检查
    config = load_config()
    port = config.get("port", "8080")
    try:
        import urllib.request

        req = urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2)
        data = json.loads(req.read())
        print(f"   状态: {data.get('status', 'unknown')}")
        print(f"   版本: {data.get('version', 'unknown')}")
    except Exception:
        print("   状态: 无法连接")


def config_set(args):
    """设置配置"""
    config = load_config()
    config[args.key] = args.value
    save_config(config)
    print(f"✅ {args.key} = {args.value}")


def config_show(args):
    """显示配置"""
    config = load_config()
    if not config:
        print("暂无配置")
        return

    print("当前配置:")
    for k, v in config.items():
        print(f"  {k} = {v}")


def config_get(args):
    """获取单个配置"""
    config = load_config()
    value = config.get(args.key)
    if value is None:
        print(f"配置 '{args.key}' 不存在")
    else:
        print(value)


def start_tui(args):
    """启动 Textual TUI"""
    # 从配置获取 server URL
    config = load_config()
    server_url = args.server or config.get("server", "ws://localhost:8080/ws")

    try:
        from jojo_code.cli.app import JojoCodeApp

        app = JojoCodeApp(server_url=server_url)
        app.run()
    except ImportError as e:
        print(f"错误: 缺少依赖 - {e}")
        print("请运行: pip install 'jojo-code'")
        sys.exit(1)
    except KeyboardInterrupt:
        pass


# ========== 主入口 ==========


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        prog="jojo-code",
        description="jojo-code - Python coding agent powered by LangGraph",
    )
    parser.add_argument(
        "--server",
        help="WebSocket server URL (默认从配置读取)",
        default=None,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # server 子命令
    server_parser = subparsers.add_parser("server", help="管理 WebSocket 服务")
    server_sub = server_parser.add_subparsers(dest="action")
    start_parser = server_sub.add_parser("start", help="启动服务")
    start_parser.add_argument("-d", "--daemon", action="store_true", help="后台运行")
    start_parser.add_argument("--host", help="监听地址")
    start_parser.add_argument("--port", help="监听端口")
    server_sub.add_parser("stop", help="停止服务")
    server_sub.add_parser("status", help="查看服务状态")

    # config 子命令
    config_parser = subparsers.add_parser("config", help="管理配置")
    config_sub = config_parser.add_subparsers(dest="action")
    config_set_parser = config_sub.add_parser("set", help="设置配置")
    config_set_parser.add_argument("key", help="配置项")
    config_set_parser.add_argument("value", help="配置值")
    config_sub.add_parser("show", help="显示所有配置")
    config_get_parser = config_sub.add_parser("get", help="获取配置值")
    config_get_parser.add_argument("key", help="配置项")

    args = parser.parse_args()

    if args.command is None:
        start_tui(args)
    elif args.command == "server":
        if args.action == "start":
            server_start(args)
        elif args.action == "stop":
            server_stop(args)
        elif args.action == "status":
            server_status(args)
        else:
            server_parser.print_help()
    elif args.command == "config":
        if args.action == "set":
            config_set(args)
        elif args.action == "show":
            config_show(args)
        elif args.action == "get":
            config_get(args)
        else:
            config_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
