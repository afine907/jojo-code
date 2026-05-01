"""性能监控工具 - 代码性能分析和监控（基于 radon）"""

import ast
import cProfile
import io
import pstats
import time
from pathlib import Path

from langchain_core.tools import tool
from radon.complexity import cc_rank, cc_visit


@tool
def profile_python_file(file_path: str, script_args: str | None = "") -> str:
    """对 Python 文件进行性能分析（通过 cProfile 直接执行）。

    Args:
        file_path: 要分析的 Python 文件路径
        script_args: 脚本的命令行参数

    Returns:
        性能分析结果
    """
    target_file = Path(file_path)
    if not target_file.exists():
        return f"错误: 文件不存在 {file_path}"

    if target_file.suffix != ".py":
        return f"错误: {file_path} 不是 Python 文件"

    try:
        pr = cProfile.Profile()

        import sys

        old_argv = sys.argv
        sys.argv = [str(target_file)] + (script_args.split() if script_args else [])

        start_time = time.time()
        pr.enable()

        try:
            exec_globals = {"__name__": "__main__", "__file__": str(target_file)}
            compiled = compile(target_file.read_text(encoding="utf-8"), str(target_file), "exec")
            exec(compiled, exec_globals)
        except SystemExit:
            pass
        except Exception as e:
            pr.disable()
            sys.argv = old_argv
            return f"脚本执行错误: {e}"

        pr.disable()
        end_time = time.time()
        sys.argv = old_argv

        execution_time = end_time - start_time

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats("cumulative")
        ps.print_stats(20)

        profile_output = s.getvalue()

        result_text = f"性能分析结果: {file_path}\n"
        result_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"执行时间: {execution_time:.3f} 秒\n"
        result_text += f"\n性能分析数据:\n{profile_output}"

        return result_text

    except Exception as e:
        return f"性能分析失败: {e}"


@tool
def analyze_function_complexity(file_path: str) -> str:
    """分析 Python 文件中函数的复杂度（基于 radon 圈复杂度）。

    Args:
        file_path: Python 文件路径

    Returns:
        函数复杂度分析结果
    """
    target_file = Path(file_path)
    if not target_file.exists():
        return f"错误: 文件不存在 {file_path}"

    if target_file.suffix != ".py":
        return f"错误: {file_path} 不是 Python 文件"

    try:
        code = target_file.read_text(encoding="utf-8")
        blocks = cc_visit(code)

        if not blocks:
            return f"在 {file_path} 中未找到函数定义"

        # 按复杂度排序
        blocks.sort(key=lambda x: x.complexity, reverse=True)

        result = f"函数复杂度分析: {file_path}\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        for block in blocks:
            rank = cc_rank(block.complexity)
            result += f"函数: {block.name} (第 {block.lineno} 行)\n"
            result += f"  复杂度: {block.complexity} ({rank}级)\n"
            result += f"  类型: {block.letter}\n\n"

        # 总体建议
        high_complexity = [b for b in blocks if b.complexity > 10]
        if high_complexity:
            result += f"⚠️  发现 {len(high_complexity)} 个高复杂度函数，建议重构:\n"
            for b in high_complexity[:3]:
                result += f"  • {b.name} (复杂度: {b.complexity}, {cc_rank(b.complexity)}级)\n"

        return result

    except SyntaxError as e:
        return f"语法错误: {e}"
    except Exception as e:
        return f"分析失败: {e}"


@tool
def suggest_performance_optimizations(file_path: str) -> str:
    """分析代码并提供性能优化建议（基于 radon + AST）。

    Args:
        file_path: Python 文件路径

    Returns:
        性能优化建议
    """
    target_file = Path(file_path)
    if not target_file.exists():
        return f"错误: 文件不存在 {file_path}"

    if target_file.suffix != ".py":
        return f"错误: {file_path} 不是 Python 文件"

    try:
        code = target_file.read_text(encoding="utf-8")
        tree = ast.parse(code)
        suggestions = []

        # radon 圈复杂度分析
        blocks = cc_visit(code)
        for block in blocks:
            if block.complexity > 15:
                suggestions.append(
                    f"{block.name}: 复杂度={block.complexity} ({cc_rank(block.complexity)}级),"
                    "强烈建议重构"
                )
            elif block.complexity > 10:
                suggestions.append(f"函数 '{block.name}' 圈复杂度 {block.complexity}，建议优化")

        # radon 可维护性指数
        mi = mi_visit_wrapper(code)
        if mi < 40:
            suggestions.append(f"文件可维护性指数 {mi:.1f}/100，整体需要重构")

        # AST: 嵌套循环
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child is not node:
                        suggestions.append(f"第 {node.lineno} 行: 检测到嵌套循环")
                        break

        # AST: 字符串拼接
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    suggestions.append(f"第 {node.lineno} 行: 字符串拼接，考虑使用 join()")

        # AST: 全局变量
        global_vars = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                global_vars.extend(node.names)
        if global_vars:
            suggestions.append(f"使用全局变量: {', '.join(global_vars)}")

        if not suggestions:
            return f"性能分析: {file_path}\n代码性能良好，暂无明显优化建议"

        result = f"性能优化建议 ({len(suggestions)} 项):\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += "\n".join([f"• {sugg}" for sugg in suggestions[:5]])

        if len(suggestions) > 5:
            result += f"\n... 还有 {len(suggestions) - 5} 个建议"

        return result

    except SyntaxError as e:
        return f"语法错误: {e}"
    except Exception as e:
        return f"分析失败: {e}"


def mi_visit_wrapper(code: str) -> float:
    """安全调用 radon 的 mi_visit 函数。"""
    try:
        from radon.metrics import mi_visit

        return mi_visit(code, True)
    except Exception:
        return 100.0  # 默认值


@tool
def benchmark_code_snippet(code: str, iterations: int = 1000) -> str:
    """对代码片段进行基准测试（使用 timeit）。

    Args:
        code: 要测试的 Python 代码片段
        iterations: 执行次数，默认为 1000

    Returns:
        基准测试结果
    """
    import timeit

    try:
        # 安全检查
        dangerous_patterns = ["import os", "subprocess", "open(", "__import__", "eval(", "exec("]
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                return f"安全拒绝: 代码包含潜在危险操作 '{pattern}'"

        timer = timeit.Timer(code)
        total_time = timer.timeit(number=iterations)
        avg_time = total_time / iterations

        result = "代码基准测试结果:\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"代码片段:\n{code}\n\n"
        result += f"执行次数: {iterations}\n"
        result += f"总时间: {total_time:.6f} 秒\n"
        result += f"平均时间: {avg_time:.6f} 秒\n"
        result += f"每秒执行: {1 / avg_time:.0f} 次\n"

        if avg_time < 0.001:
            performance = "非常快 ⚡"
        elif avg_time < 0.01:
            performance = "快速 ✅"
        elif avg_time < 0.1:
            performance = "中等 ⏱️"
        else:
            performance = "较慢 🐌"

        result += f"\n性能评估: {performance}"

        return result

    except Exception as e:
        return f"基准测试失败: {e}"
