"""性能监控工具 - 代码性能分析和监控"""

import ast
import io
import pstats
import time
import traceback
from pathlib import Path

from langchain_core.tools import tool


@tool
def profile_python_file(file_path: str, script_args: str | None = "") -> str:
    """对 Python 文件进行性能分析（通过 cProfile 直接执行，而非 subprocess）。

    Args:
        file_path: 要分析的 Python 文件路径
        script_args: 脚本的命令行参数

    Returns:
        性能分析结果
    """
    import cProfile

    target_file = Path(file_path)
    if not target_file.exists():
        return f"错误: 文件不存在 {file_path}"

    if target_file.suffix != ".py":
        return f"错误: {file_path} 不是 Python 文件"

    try:
        # 使用 cProfile 直接执行脚本（而非 subprocess，确保 profile 数据准确）
        pr = cProfile.Profile()

        # 设置命令行参数
        import sys

        old_argv = sys.argv
        sys.argv = [str(target_file)] + (script_args.split() if script_args else [])

        start_time = time.time()
        pr.enable()

        try:
            # 直接执行脚本
            exec_globals = {"__name__": "__main__", "__file__": str(target_file)}
            compiled = compile(target_file.read_text(encoding="utf-8"), str(target_file), "exec")
            exec(compiled, exec_globals)
        except SystemExit:
            pass  # 脚本正常退出
        except Exception as e:
            pr.disable()
            sys.argv = old_argv
            return f"脚本执行错误: {e}\n{traceback.format_exc()}"

        pr.disable()
        end_time = time.time()
        sys.argv = old_argv

        execution_time = end_time - start_time

        # 捕获分析结果
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats("cumulative")
        ps.print_stats(20)  # 显示前20个最耗时的函数

        profile_output = s.getvalue()

        # 构建结果
        result_text = f"性能分析结果: {file_path}\n"
        result_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"执行时间: {execution_time:.3f} 秒\n"
        result_text += f"\n性能分析数据:\n{profile_output}"

        return result_text

    except Exception as e:
        return f"性能分析失败: {e}"


@tool
def analyze_function_complexity(file_path: str) -> str:
    """分析 Python 文件中函数的复杂度。

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
        content = target_file.read_text(encoding="utf-8")
        tree = ast.parse(content)

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数复杂度
                complexity = _calculate_function_complexity(node)

                # 获取函数信息（单次遍历）
                has_return = False
                has_loops = False
                has_conditionals = False

                for n in ast.walk(node):
                    if isinstance(n, ast.Return):
                        has_return = True
                    elif isinstance(n, (ast.For, ast.While)):
                        has_loops = True
                    elif isinstance(n, ast.If):
                        has_conditionals = True

                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "complexity": complexity,
                    "params": len(node.args.args),
                    "has_return": has_return,
                    "has_loops": has_loops,
                    "has_conditionals": has_conditionals,
                }

                functions.append(func_info)

        if not functions:
            return f"在 {file_path} 中未找到函数定义"

        # 按复杂度排序
        functions.sort(key=lambda x: x["complexity"], reverse=True)

        result = f"函数复杂度分析: {file_path}\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        for func in functions:
            complexity_level = _get_complexity_level(func["complexity"])
            result += f"函数: {func['name']} (第 {func['line']} 行)\n"
            result += f"  复杂度: {func['complexity']} ({complexity_level})\n"
            result += f"  参数数量: {func['params']}\n"
            result += f"  特性: {', '.join(_get_function_features(func))}\n\n"

        # 提供总体建议
        high_complexity_funcs = [f for f in functions if f["complexity"] > 10]
        if high_complexity_funcs:
            result += f"⚠️  发现 {len(high_complexity_funcs)} 个高复杂度函数，建议重构:\n"
            for func in high_complexity_funcs[:3]:
                result += f"  • {func['name']} (复杂度: {func['complexity']})\n"

        return result

    except SyntaxError as e:
        return f"语法错误: {e}"
    except Exception as e:
        return f"分析失败: {e}"


def _calculate_function_complexity(node: ast.FunctionDef) -> int:
    """计算函数复杂度（圈复杂度）"""
    complexity = 1  # 基础复杂度

    for n in ast.walk(node):
        if isinstance(n, ast.If):
            complexity += 1
        elif isinstance(n, (ast.For, ast.While)):
            complexity += 2
        elif isinstance(n, ast.Try):
            complexity += len(n.handlers)
        elif isinstance(n, ast.With):
            complexity += 1
        elif isinstance(n, ast.BoolOp):
            complexity += len(n.values) - 1
        elif isinstance(n, ast.Compare):
            complexity += len(n.ops) - 1

    return complexity


def _get_complexity_level(complexity: int) -> str:
    """获取复杂度等级描述"""
    if complexity <= 5:
        return "简单"
    elif complexity <= 10:
        return "中等"
    elif complexity <= 20:
        return "复杂"
    else:
        return "非常复杂"


def _get_function_features(func_info: dict) -> list:
    """获取函数特性列表"""
    features = []
    if func_info["has_return"]:
        features.append("有返回值")
    if func_info["has_loops"]:
        features.append("包含循环")
    if func_info["has_conditionals"]:
        features.append("包含条件语句")
    if func_info["params"] > 3:
        features.append("多参数")

    return features if features else ["简单函数"]


@tool
def suggest_performance_optimizations(file_path: str) -> str:
    """分析代码并提供性能优化建议（单次 AST 遍历）。

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
        content = target_file.read_text(encoding="utf-8")
        tree = ast.parse(content)
        suggestions = []

        # 单次 AST 遍历收集所有信息
        # 跟踪属性访问
        attr_access_count: dict[str, int] = {}
        # 全局变量
        global_vars: list[str] = []

        for node in ast.walk(tree):
            # 检查嵌套循环
            if isinstance(node, (ast.For, ast.While)):
                # 检查父节点是否也是循环
                for parent in ast.walk(tree):
                    if isinstance(parent, (ast.For, ast.While)) and parent != node:
                        # 检查 node 是否在 parent 内
                        for child in ast.walk(parent):
                            if child is node:
                                suggestions.append(
                                    f"第 {node.lineno} 行: 检测到嵌套循环，考虑优化算法复杂度"
                                )
                                break
                        break

            # 检查属性访问次数
            elif isinstance(node, ast.Attribute):
                try:
                    attr_name = f"{ast.unparse(node.value)}.{node.attr}"
                    attr_access_count[attr_name] = attr_access_count.get(attr_name, 0) + 1
                except (TypeError, ValueError):
                    pass

            # 检查字符串拼接
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    suggestions.append(f"第 {node.lineno} 行: 字符串拼接，考虑使用 join() 方法")

            # 检查全局变量
            elif isinstance(node, ast.Global):
                global_vars.extend(node.names)

            # 检查大列表
            elif isinstance(node, ast.List) and len(node.elts) > 100:
                suggestions.append(f"第 {node.lineno} 行: 创建大型列表，考虑使用生成器")

        # 添加高频属性访问建议
        for attr_name, count in attr_access_count.items():
            if count > 3:
                suggestions.append(f"属性 '{attr_name}' 访问 {count} 次，考虑缓存到变量")

        # 添加全局变量建议
        if global_vars:
            suggestions.append(f"使用全局变量: {', '.join(global_vars)}，考虑使用参数传递")

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


@tool
def benchmark_code_snippet(code: str, iterations: int = 1000) -> str:
    """对代码片段进行简单的基准测试（使用 timeit 而非 exec 循环）。

    Args:
        code: 要测试的 Python 代码片段
        iterations: 执行次数，默认为 1000

    Returns:
        基准测试结果
    """
    import timeit

    try:
        # 安全检查：禁止危险操作
        dangerous_patterns = ["import os", "subprocess", "open(", "__import__", "eval(", "exec("]
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                return f"安全拒绝: 代码包含潜在危险操作 '{pattern}'"

        # 使用 timeit 进行精确计时
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

        # 提供简单的性能评估
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
