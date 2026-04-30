"""Git 集成工具 - 基于 GitPython 的 Git 操作支持"""

from git import InvalidGitRepositoryError, Repo
from langchain_core.tools import tool


def _get_repo(path: str = ".") -> tuple[Repo | None, str | None]:
    """获取 Git 仓库实例。

    Args:
        path: 仓库路径

    Returns:
        (Repo 实例, 错误信息) 元组
    """
    try:
        repo = Repo(path, search_parent_directories=True)
        return repo, None
    except InvalidGitRepositoryError:
        return None, "错误: 当前目录不是 Git 仓库"
    except Exception as e:
        return None, f"错误: {e}"


@tool
def git_status(path: str = ".") -> str:
    """查看 Git 仓库状态。

    Args:
        path: 仓库路径，默认为当前目录

    Returns:
        Git 状态信息
    """
    repo, error = _get_repo(path)
    if error:
        return error

    try:
        # 获取工作区变更
        changed_files = repo.index.diff(None)
        staged_files = repo.index.diff("HEAD")
        untracked_files = repo.untracked_files

        staged = []
        unstaged = []
        untracked = list(untracked_files) if untracked_files else []

        for item in staged_files:
            staged.append(f"{item.change_type} {item.a_path}")

        for item in changed_files:
            if item.a_path not in [s.split(" ")[1] for s in staged]:
                unstaged.append(f"{item.change_type} {item.a_path}")

        if not staged and not unstaged and not untracked:
            return "工作区干净，没有修改"

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
            result += "\n".join([f"  {item}" for item in untracked[:20]]) + "\n"

        return result

    except Exception as e:
        return f"错误: {e}"


@tool
def git_diff(path: str = ".", file_path: str | None = None) -> str:
    """查看 Git 差异。

    Args:
        path: 仓库路径，默认为当前目录
        file_path: 特定文件路径，如果提供则只显示该文件的差异

    Returns:
        Git 差异信息
    """
    repo, error = _get_repo(path)
    if error:
        return error

    try:
        if file_path:
            diff_output = repo.git.diff(file_path)
        else:
            diff_output = repo.git.diff()

        if not diff_output:
            target = file_path or "工作区"
            return f"没有检测到 {target} 的差异"

        # 限制输出长度
        lines = diff_output.split("\n")
        if len(lines) > 50:
            diff_output = "\n".join(lines[:50]) + f"\n... (还有 {len(lines) - 50} 行)\n"

        return diff_output

    except Exception as e:
        return f"错误: {e}"


@tool
def git_log(path: str = ".", limit: int = 10) -> str:
    """查看 Git 提交历史。

    Args:
        path: 仓库路径，默认为当前目录
        limit: 显示最近几条提交，默认为 10

    Returns:
        Git 提交历史
    """
    repo, error = _get_repo(path)
    if error:
        return error

    try:
        commits = list(repo.iter_commits(max_count=limit))

        if not commits:
            return "没有提交历史"

        result = f"最近 {len(commits)} 条提交:\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        for commit in commits:
            sha = commit.hexsha[:7]
            author = commit.author.name
            date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M")
            message = commit.summary
            result += f"  {sha} {author} {date} {message}\n"

        return result

    except Exception as e:
        return f"错误: {e}"


@tool
def git_blame(file_path: str, path: str = ".") -> str:
    """查看文件的 Git blame 信息。

    Args:
        file_path: 要查看的文件路径
        path: 仓库路径，默认为当前目录

    Returns:
        Git blame 信息
    """
    repo, error = _get_repo(path)
    if error:
        return error

    try:
        # 获取 blame 信息
        blame = repo.blame("HEAD", file_path)

        authors = {}
        total_lines = 0

        for commit, lines in blame:
            author = commit.author.name
            line_count = len(lines)
            authors[author] = authors.get(author, 0) + line_count
            total_lines += line_count

        result = f"Git Blame 分析: {file_path}\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        if authors:
            result += "主要作者:\n"
            sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
            for author, count in sorted_authors[:5]:
                pct = count / max(total_lines, 1) * 100
                result += f"  {author}: {count} 行 ({pct:.0f}%)\n"

        result += f"\n总行数: {total_lines}"

        return result

    except Exception as e:
        return f"错误: {e}"


@tool
def git_branch(path: str = ".") -> str:
    """查看 Git 分支信息。

    Args:
        path: 仓库路径，默认为当前目录

    Returns:
        Git 分支信息
    """
    repo, error = _get_repo(path)
    if error:
        return error

    try:
        current = (
            repo.active_branch.name if not repo.head.is_detached else repo.head.commit.hexsha[:7]
        )
        branches = [b.name for b in repo.branches]
        remote_branches = [r.name for r in repo.remotes[0].refs] if repo.remotes else []

        result = "Git 分支:\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"当前分支: {current}\n\n"
        result += "所有分支:\n"
        result += "\n".join([f"  {'*' if b == current else ' '} {b}" for b in branches])

        if remote_branches:
            result += f"\n\n远程分支 ({len(remote_branches)}):\n"
            result += "\n".join([f"  {b}" for b in remote_branches[:10]])

        return result

    except Exception as e:
        return f"错误: {e}"


@tool
def git_info(path: str = ".") -> str:
    """获取 Git 仓库的基本信息。

    Args:
        path: 仓库路径，默认为当前目录

    Returns:
        Git 仓库信息
    """
    repo, error = _get_repo(path)
    if error:
        return error

    try:
        info = "Git 仓库信息:\n"
        info += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        # 当前 HEAD 信息
        head = repo.head.commit
        info += f"最新提交: {head.hexsha[:7]}\n"
        info += f"作者: {head.author.name}\n"
        info += f"时间: {head.committed_datetime.strftime('%Y-%m-%d %H:%M')}\n"
        info += f"信息: {head.summary}\n"

        # 远程仓库
        if repo.remotes:
            info += "\n远程仓库:\n"
            for remote in repo.remotes[:3]:
                info += f"  {remote.name}: {remote.url}\n"

        # 提交统计
        commit_count = sum(1 for _ in repo.iter_commits())
        info += f"\n总提交数: {commit_count}\n"

        return info

    except Exception as e:
        return f"错误: {e}"


# 为了向后兼容
GitStatusTool = git_status
GitDiffTool = git_diff
GitLogTool = git_log
GitBlameTool = git_blame
