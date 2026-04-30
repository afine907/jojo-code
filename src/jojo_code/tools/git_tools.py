"""Git 集成工具 - 基本的 Git 操作支持"""

import subprocess

from langchain_core.tools import tool


def _run_git(args: list[str], path: str = ".", timeout: int = 10) -> tuple[bool, str]:
    """执行 git 命令的通用辅助函数。

    Args:
        args: git 命令参数列表
        path: 仓库路径
        timeout: 超时时间

    Returns:
        (成功, 输出) 元组
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "错误: Git 命令执行超时"
    except FileNotFoundError:
        return False, "错误: Git 未安装或不在 PATH 中"
    except Exception as e:
        return False, f"错误: {e}"


@tool
def git_status(path: str = ".") -> str:
    """查看 Git 仓库状态。

    Args:
        path: 仓库路径，默认为当前目录

    Returns:
        Git 状态信息
    """
    ok, output = _run_git(["status", "--porcelain"], path)
    if not ok:
        return f"Git 错误: {output}"

    if not output:
        return "工作区干净，没有修改"

    # 解析状态输出
    lines = output.split("\n")
    staged = []
    unstaged = []
    untracked = []

    for line in lines:
        if not line.strip():
            continue

        status_code = line[:2]
        filename = line[3:]

        if status_code.startswith("??"):
            untracked.append(filename)
        elif status_code[0] in "MADRC":
            staged.append(f"{status_code} {filename}")
        elif status_code[1] in "MADRC":
            unstaged.append(f"{status_code} {filename}")

    result = "Git 状态:\n"
    result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    if staged:
        result += f"暂存区 ({len(staged)} 个文件):\n"
        result += "\n".join([f"  {item}" for item in staged]) + "\n"

    if unstaged:
        result += f"未暂存 ({len(unstaged)} 个文件):\n"
        result += "\n".join([f"  {item}" for item in unstaged]) + "\n"

    if untracked:
        result += f"未跟踪 ({len(untracked)} 个文件):\n"
        result += "\n".join([f"  {item}" for item in untracked]) + "\n"

    return result


@tool
def git_diff(path: str = ".", file_path: str | None = None) -> str:
    """查看 Git 差异。

    Args:
        path: 仓库路径，默认为当前目录
        file_path: 特定文件路径，如果提供则只显示该文件的差异

    Returns:
        Git 差异信息
    """
    args = ["diff"]
    if file_path:
        args.append(file_path)

    ok, output = _run_git(args, path)
    if not ok:
        return f"Git 错误: {output}"

    if not output:
        target = file_path or "工作区"
        return f"没有检测到 {target} 的差异"

    # 限制输出长度，避免过长
    lines = output.split("\n")
    if len(lines) > 50:
        output = "\n".join(lines[:50]) + f"\n... (还有 {len(lines) - 50} 行)\n"

    return output


@tool
def git_log(path: str = ".", limit: int = 10) -> str:
    """查看 Git 提交历史。

    Args:
        path: 仓库路径，默认为当前目录
        limit: 显示最近几条提交，默认为 10

    Returns:
        Git 提交历史
    """
    ok, output = _run_git(["log", f"-{limit}", "--oneline", "--graph"], path)
    if not ok:
        return f"Git 错误: {output}"

    if not output:
        return "没有提交历史"

    return f"最近 {limit} 条提交:\n{output}"


@tool
def git_blame(file_path: str, path: str = ".") -> str:
    """查看文件的 Git blame 信息。

    Args:
        file_path: 要查看的文件路径
        path: 仓库路径，默认为当前目录

    Returns:
        Git blame 信息
    """
    ok, output = _run_git(["blame", "--line-porcelain", file_path], path)
    if not ok:
        return f"Git 错误: {output}"

    if not output:
        return f"无法获取 {file_path} 的 blame 信息"

    # 解析 porcelain 格式，提取关键信息
    lines = output.split("\n")
    authors = {}
    total_code_lines = 0

    for line in lines:
        if line.startswith("author "):
            author = line[7:]
            authors[author] = authors.get(author, 0) + 1
        elif line.startswith("lineno "):
            total_code_lines += 1  # 每个 lineno 行代表一行真实代码

    result = f"Git Blame 分析: {file_path}\n"
    result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    if authors:
        result += "主要作者:\n"
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
        for author, count in sorted_authors[:5]:
            pct = count / max(total_code_lines, 1) * 100
            result += f"  {author}: {count} 行 ({pct:.0f}%)\n"

    result += f"\n总行数: {total_code_lines}"

    return result


@tool
def git_branch(path: str = ".") -> str:
    """查看 Git 分支信息。

    Args:
        path: 仓库路径，默认为当前目录

    Returns:
        Git 分支信息
    """
    # 一次性获取分支和远程分支信息
    ok, output = _run_git(["branch", "-a", "--list"], path)
    if not ok:
        return f"Git 错误: {output}"

    if not output:
        return "没有找到分支"

    branches = output.split("\n")
    current_branch = None
    local_branches = []
    remote_branches = []

    for branch in branches:
        branch = branch.strip()
        if not branch:
            continue
        if branch.startswith("* "):
            current_branch = branch[2:]
            local_branches.append(f"*{current_branch}")
        elif branch.startswith("remotes/"):
            remote_branches.append(branch)
        else:
            local_branches.append(branch)

    result = "Git 分支:\n"
    result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    result += f"当前分支: {current_branch or '未知'}\n\n"
    result += "所有分支:\n"
    result += "\n".join([f"  {branch}" for branch in local_branches])

    if remote_branches:
        result += f"\n\n远程分支 ({len(remote_branches)}):\n"
        result += "\n".join([f"  {branch}" for branch in remote_branches[:10]])

    return result


@tool
def git_info(path: str = ".") -> str:
    """获取 Git 仓库的基本信息。

    Args:
        path: 仓库路径，默认为当前目录

    Returns:
        Git 仓库信息
    """
    # 先检查是否在 Git 仓库中
    ok, output = _run_git(["rev-parse", "--git-dir"], path)
    if not ok:
        return "错误: 当前目录不是 Git 仓库"

    info = "Git 仓库信息:\n"
    info += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    # 一次性获取所有信息（减少 subprocess 调用）
    ok, multi_output = _run_git(
        ["log", "-1", "--format=remote:%D%ncommit:%H%nauthor:%an%ndate:%ar%nmessage:%s"],
        path,
    )
    if ok and multi_output:
        for line in multi_output.split("\n"):
            if line.startswith("remote:"):
                info += f"分支/标签: {line[7:]}\n"
            elif line.startswith("commit:"):
                info += f"最新提交: {line[7:14]}\n"
            elif line.startswith("author:"):
                info += f"作者: {line[7:]}\n"
            elif line.startswith("date:"):
                info += f"时间: {line[5:]}\n"
            elif line.startswith("message:"):
                info += f"信息: {line[8:]}\n"

    # 获取远程仓库
    ok, remote_output = _run_git(["remote", "-v"], path)
    if ok and remote_output:
        remotes = remote_output.split("\n")
        info += "\n远程仓库:\n"
        for remote in remotes[:3]:
            info += f"  {remote}\n"

    # 获取提交统计（单次调用）
    ok, count_output = _run_git(["rev-list", "--count", "HEAD"], path)
    if ok and count_output:
        info += f"\n总提交数: {count_output}\n"

    return info


# 为了向后兼容
GitStatusTool = git_status
GitDiffTool = git_diff
GitLogTool = git_log
GitBlameTool = git_blame
