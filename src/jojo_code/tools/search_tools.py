"""代码搜索工具 - grep 搜索和 glob 文件匹配"""

import re
from pathlib import Path

from langchain_core.tools import tool

# 搜索结果最大行数
MAX_RESULTS = 500
# 单文件最大读取大小（5MB）
MAX_FILE_SIZE = 5 * 1024 * 1024


@tool
def grep_search(
    pattern: str,
    path: str,
    file_pattern: str = "*",
    case_sensitive: bool = True,
    max_results: int = MAX_RESULTS,
) -> str:
    """在文件中搜索匹配正则表达式的内容。

    Args:
        pattern: 正则表达式模式
        path: 搜索路径（文件或目录）
        file_pattern: 文件名模式，默认 "*" 匹配所有文件
        case_sensitive: 是否区分大小写，默认 True
        max_results: 最大返回结果数，默认 500

    Returns:
        匹配结果，包含文件名、行号和匹配行
    """
    search_path = Path(path)
    if not search_path.exists():
        return f"错误: 路径不存在 {path}"

    # 编译正则表达式
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return f"错误: 无效的正则表达式 - {e}"

    results = []
    truncated = False

    # 确定要搜索的文件
    if search_path.is_file():
        files = [search_path]
    else:
        files = [f for f in search_path.rglob(file_pattern) if f.is_file()]

    # 搜索每个文件
    for file_path in files:
        if len(results) >= max_results:
            truncated = True
            break

        # 跳过大文件
        try:
            if file_path.stat().st_size > MAX_FILE_SIZE:
                continue
        except OSError:
            continue

        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        try:
                            display_path = file_path.relative_to(search_path.parent)
                        except ValueError:
                            display_path = file_path

                        results.append(f"{display_path}:{line_num}: {line.rstrip()}")

                        if len(results) >= max_results:
                            truncated = True
                            break
        except (PermissionError, OSError):
            continue

    if not results:
        return ""

    output = "\n".join(results)
    if truncated:
        output += f"\n... (结果已截断，显示前 {max_results} 条)"

    return output


@tool
def glob_search(pattern: str, path: str) -> str:
    """使用 glob 模式匹配查找文件。

    Args:
        pattern: glob 模式，如 "*.py", "**/*.txt"
        path: 搜索起始路径

    Returns:
        匹配的文件路径列表
    """
    search_path = Path(path)
    if not search_path.exists():
        return f"错误: 路径不存在 {path}"

    # 使用 glob 或 rglob（根据是否包含 **）
    if "**" in pattern:
        matches = list(search_path.glob(pattern))
    else:
        matches = list(search_path.glob(pattern))

    if not matches:
        return ""

    # 返回相对路径（限制数量）
    results = []
    for match in sorted(matches)[:500]:
        if match.is_file():
            try:
                rel_path = match.relative_to(search_path)
                results.append(str(rel_path))
            except ValueError:
                results.append(str(match))

    return "\n".join(results) if results else ""


# 为了向后兼容，提供工具类别名
GrepTool = grep_search
WebSearchTool = None  # 未实现
