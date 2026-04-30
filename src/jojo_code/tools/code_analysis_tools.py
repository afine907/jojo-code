"""代码分析工具 - 基于 radon 的静态分析、复杂度评估、依赖检查"""

import ast
from pathlib import Path

from langchain_core.tools import tool
from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_rank, mi_visit
from radon.raw import analyze as radon_analyze

# Python 标准库模块列表
STDLIB_MODULES = frozenset(
    [
        "abc",
        "aifc",
        "argparse",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "atexit",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "builtins",
        "bz2",
        "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "compileall",
        "concurrent",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "cProfile",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "doctest",
        "email",
        "encodings",
        "enum",
        "errno",
        "faulthandler",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "fractions",
        "ftplib",
        "functools",
        "gc",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "idlelib",
        "imaplib",
        "imghdr",
        "imp",
        "importlib",
        "intelidinspector",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "lib2to3",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "mailbox",
        "mailcap",
        "marshal",
        "math",
        "mimetypes",
        "mmap",
        "modulefinder",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "optparse",
        "os",
        "ossaudiodev",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posix",
        "posixpath",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "token",
        "tokenize",
        "tomllib",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "turtledemo",
        "types",
        "typing",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
        "_thread",
        "_io",
        "_collections_abc",
    ]
)


@tool
def analyze_python_file(path: str) -> str:
    """分析 Python 文件的复杂度、函数数量、类数量等指标（基于 radon）。

    Args:
        path: Python 文件路径

    Returns:
        代码分析结果
    """
    file_path = Path(path)
    if not file_path.exists():
        return f"错误: 文件不存在 {path}"

    if file_path.suffix != ".py":
        return f"错误: {path} 不是 Python 文件"

    try:
        code = file_path.read_text(encoding="utf-8")

        # radon 原始指标
        raw = radon_analyze(code)

        # radon 圈复杂度
        blocks = cc_visit(code)

        # radon 可维护性指数
        mi = mi_visit(code, True)
        mi_grade = mi_rank(mi)

        result = f"""文件分析结果: {path}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基本信息:
  总行数: {raw.loc}
  代码行: {raw.lloc}
  逻辑行: {raw.sloc}
  注释行: {raw.comments}
  空行: {raw.blank}

复杂度分析 (圈复杂度):
  函数/类数量: {len(blocks)}
  平均复杂度: {sum(b.complexity for b in blocks) / max(len(blocks), 1):.1f}
"""

        # 显示各函数复杂度
        if blocks:
            result += "\n  函数详情:\n"
            for b in sorted(blocks, key=lambda x: x.complexity, reverse=True)[:10]:
                rank = cc_rank(b.complexity)
                result += f"    {b.name}: 复杂度={b.complexity} ({rank}级)\n"

        # 可维护性指数
        result += f"\n可维护性指数: {mi:.1f}/100 ({mi_grade}级)"
        if mi >= 85:
            result += " ✅ 优秀"
        elif mi >= 65:
            result += " ⚠️ 一般"
        else:
            result += " ❌ 需要重构"

        return result

    except SyntaxError as e:
        return f"语法错误: {e}"
    except Exception as e:
        return f"分析失败: {e}"


@tool
def find_python_dependencies(path: str) -> str:
    """分析 Python 文件或项目的依赖关系。

    Args:
        path: Python 文件或目录路径

    Returns:
        依赖分析结果
    """
    target_path = Path(path)

    if not target_path.exists():
        return f"错误: 路径不存在 {path}"

    dependencies = set()

    if target_path.is_file() and target_path.suffix == ".py":
        try:
            content = target_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module.split(".")[0])
        except Exception as e:
            return f"分析失败: {e}"

    elif target_path.is_dir():
        for py_file in target_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.add(node.module.split(".")[0])
            except Exception:
                continue
    else:
        return f"错误: {path} 不是有效的 Python 文件或目录"

    if not dependencies:
        return f"在 {path} 中未找到依赖项"

    third_party_deps = sorted(dependencies - STDLIB_MODULES)
    stdlib_deps = sorted(dependencies & STDLIB_MODULES)

    result = f"依赖分析: {path}\n"
    result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    if third_party_deps:
        result += f"第三方依赖 ({len(third_party_deps)}):\n"
        for dep in third_party_deps:
            result += f"  - {dep}\n"

    if stdlib_deps:
        result += f"\n标准库依赖 ({len(stdlib_deps)}):\n"
        for dep in stdlib_deps:
            result += f"  - {dep}\n"

    return result


@tool
def check_code_style(path: str, rules: str = "basic") -> str:
    """检查代码风格问题（调用 ruff）。

    Args:
        path: Python 文件路径
        rules: 检查规则，可选 'basic', 'strict'

    Returns:
        代码风格检查结果
    """
    import subprocess

    file_path = Path(path)
    if not file_path.exists():
        return f"错误: 文件不存在 {path}"

    if file_path.suffix != ".py":
        return f"错误: {path} 不是 Python 文件"

    try:
        cmd = ["ruff", "check", "--output-format=text"]
        if rules == "strict":
            cmd.append("--select=ALL")
        cmd.append(str(file_path))

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return f"✅ 代码风格检查通过: {path} (ruff)"

        output = result.stdout.strip()
        if output:
            lines = output.split("\n")
            if len(lines) > 15:
                output = "\n".join(lines[:15]) + f"\n... (共 {len(lines)} 个问题)"
            return f"代码风格问题 (ruff):\n{output}"

        return f"代码风格检查通过: {path} (ruff)"

    except FileNotFoundError:
        return _check_code_style_basic(file_path, rules)
    except subprocess.TimeoutExpired:
        return "错误: 代码风格检查超时"
    except Exception as e:
        return f"检查失败: {e}"


def _check_code_style_basic(file_path: Path, rules: str = "basic") -> str:
    """基本的代码风格检查（ruff 不可用时的后备方案）。"""
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        issues = []

        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"第 {i} 行: 行长度超过 120 字符 ({len(line)})")
            if line.rstrip() != line:
                issues.append(f"第 {i} 行: 存在尾随空格")
            if "\t" in line:
                issues.append(f"第 {i} 行: 使用制表符而不是空格")

        if lines and lines[-1].strip() != "":
            issues.append("文件末尾缺少空行")

        if not issues:
            return f"代码风格检查通过: {file_path} (基本规则)"

        result = f"代码风格问题 ({len(issues)} 个):\n"
        result += "\n".join(issues[:10])
        if len(issues) > 10:
            result += f"\n... 还有 {len(issues) - 10} 个问题"
        return result

    except Exception as e:
        return f"检查失败: {e}"


@tool
def suggest_refactoring(path: str) -> str:
    """分析代码并提供重构建议（基于 radon 复杂度指标）。

    Args:
        path: Python 文件路径

    Returns:
        重构建议
    """
    file_path = Path(path)
    if not file_path.exists():
        return f"错误: 文件不存在 {path}"

    if file_path.suffix != ".py":
        return f"错误: {path} 不是 Python 文件"

    try:
        code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(code)
        suggestions = []

        # 使用 radon 获取复杂度数据
        blocks = cc_visit(code)

        # 高复杂度函数
        for block in blocks:
            if block.complexity >= 10:
                suggestions.append(
                    f"{block.name}: 复杂度={block.complexity} ({cc_rank(block.complexity)}级),"
                    "建议拆分为更小的函数"
                )

        # 可维护性指数低
        mi = mi_visit(code, True)
        if mi < 65:
            suggestions.append(f"文件可维护性指数 {mi:.1f}/100 ({mi_rank(mi)}级)，建议重构")

        # AST 分析：函数参数过多
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
                suggestions.append(
                    f"函数 '{node.name}' 参数过多 ({len(node.args.args)} 个)，考虑使用参数对象"
                )

        # AST 分析：类方法过多
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                if len(methods) > 10:
                    suggestions.append(
                        f"类 '{node.name}' 方法过多 ({len(methods)} 个)，考虑职责分离"
                    )

        # AST 分析：重复字符串常量
        string_constants: dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if len(node.value) > 10:
                    string_constants[node.value] = string_constants.get(node.value, 0) + 1

        for const, count in string_constants.items():
            if count > 1:
                suggestions.append(
                    f"字符串常量 '{const[:30]}...' 重复使用 {count} 次，考虑定义为常量"
                )

        if not suggestions:
            return f"重构建议: {path}\n代码结构良好，暂无明显重构需求"

        result = f"重构建议 ({len(suggestions)} 项):\n"
        result += "\n".join([f"• {sugg}" for sugg in suggestions[:5]])

        if len(suggestions) > 5:
            result += f"\n... 还有 {len(suggestions) - 5} 个建议"

        return result

    except SyntaxError as e:
        return f"语法错误: {e}"
    except Exception as e:
        return f"分析失败: {e}"
