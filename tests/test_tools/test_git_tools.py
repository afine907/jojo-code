"""Git 工具测试 - GitPython 版本"""

from unittest.mock import MagicMock, patch

from jojo_code.tools.git_tools import git_blame, git_branch, git_diff, git_info, git_log, git_status


class TestGitStatus:
    """git_status 工具测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_status_clean(self, mock_repo_class):
        """测试干净的工作区"""
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        mock_repo_class.return_value = mock_repo

        result = git_status.invoke({"path": "."})
        assert "工作区干净" in result

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_status_with_changes(self, mock_repo_class):
        """测试有修改的工作区"""
        mock_repo = MagicMock()
        mock_item = MagicMock()
        mock_item.change_type = "M"
        mock_item.a_path = "file.py"
        mock_repo.index.diff.return_value = [mock_item]
        mock_repo.untracked_files = ["new_file.py"]
        mock_repo_class.return_value = mock_repo

        result = git_status.invoke({"path": "."})
        assert "暂存区" in result or "未跟踪" in result

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_status_error(self, mock_repo_class):
        """测试 Git 错误"""
        from git import InvalidGitRepositoryError

        mock_repo_class.side_effect = InvalidGitRepositoryError()

        result = git_status.invoke({"path": "."})
        assert "不是 Git 仓库" in result


class TestGitDiff:
    """git_diff 工具测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_diff_no_changes(self, mock_repo_class):
        """测试没有差异"""
        mock_repo = MagicMock()
        mock_repo.git.diff.return_value = ""
        mock_repo_class.return_value = mock_repo

        result = git_diff.invoke({"path": ".", "file_path": None})
        assert "没有检测到" in result

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_diff_with_changes(self, mock_repo_class):
        """测试有差异的情况"""
        diff_content = "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,3 @@"
        mock_repo = MagicMock()
        mock_repo.git.diff.return_value = diff_content
        mock_repo_class.return_value = mock_repo

        result = git_diff.invoke({"path": ".", "file_path": None})
        assert result == diff_content


class TestGitLog:
    """git_log 工具测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_log_with_commits(self, mock_repo_class):
        """测试有提交历史的情况"""
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc1234def5678"
        mock_commit.author.name = "Alice"
        mock_commit.committed_datetime.strftime.return_value = "2026-04-30 12:00"
        mock_commit.summary = "Fix bug"

        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [mock_commit]
        mock_repo_class.return_value = mock_repo

        result = git_log.invoke({"path": ".", "limit": 5})
        assert "Fix bug" in result

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_log_no_commits(self, mock_repo_class):
        """测试没有提交历史的情况"""
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = []
        mock_repo_class.return_value = mock_repo

        result = git_log.invoke({"path": ".", "limit": 10})
        assert "没有提交历史" in result


class TestGitBlame:
    """git_blame 工具测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_blame_success(self, mock_repo_class):
        """测试成功的 blame 分析"""
        mock_commit_alice = MagicMock()
        mock_commit_alice.author.name = "Alice"
        mock_commit_bob = MagicMock()
        mock_commit_bob.author.name = "Bob"

        mock_repo = MagicMock()
        mock_repo.blame.return_value = [
            (mock_commit_alice, ["line1", "line2", "line3"]),
            (mock_commit_bob, ["line4", "line5"]),
        ]
        mock_repo_class.return_value = mock_repo

        result = git_blame.invoke({"file_path": "file.py", "path": "."})
        assert "Git Blame 分析" in result
        assert "Alice" in result
        assert "Bob" in result


class TestGitBranch:
    """git_branch 工具测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_branch_with_branches(self, mock_repo_class):
        """测试有分支的情况"""
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "main"
        mock_repo.head.is_detached = False
        mock_repo.branches = [MagicMock(name="main"), MagicMock(name="feature")]
        mock_repo.branches[0].name = "main"
        mock_repo.branches[1].name = "feature"
        mock_repo_class.return_value = mock_repo

        result = git_branch.invoke({"path": "."})
        assert "Git 分支" in result
        assert "当前分支: main" in result


class TestGitInfo:
    """git_info 工具测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_info_success(self, mock_repo_class):
        """测试成功的仓库信息获取"""
        mock_commit = MagicMock()
        mock_commit.hexsha = "abc1234def567890"
        mock_commit.author.name = "Alice"
        mock_commit.committed_datetime.strftime.return_value = "2026-04-30 12:00"
        mock_commit.summary = "Fix bug"

        mock_remote = MagicMock()
        mock_remote.name = "origin"
        mock_remote.url = "https://github.com/user/repo.git"

        mock_repo = MagicMock()
        mock_repo.head.commit = mock_commit
        mock_repo.remotes = [mock_remote]
        mock_repo.iter_commits.return_value = range(42)  # 42 commits
        mock_repo_class.return_value = mock_repo

        result = git_info.invoke({"path": "."})
        assert "Git 仓库信息" in result
        assert "Alice" in result
        assert "总提交数: 42" in result

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_info_not_repo(self, mock_repo_class):
        """测试非 Git 仓库的情况"""
        from git import InvalidGitRepositoryError

        mock_repo_class.side_effect = InvalidGitRepositoryError()

        result = git_info.invoke({"path": "."})
        assert "不是 Git 仓库" in result


class TestGitToolsErrorHandling:
    """Git 工具错误处理测试"""

    @patch("jojo_code.tools.git_tools.Repo")
    def test_git_repo_exception(self, mock_repo_class):
        """测试仓库异常"""
        mock_repo_class.side_effect = Exception("Permission denied")

        result = git_status.invoke({"path": "."})
        assert "错误" in result
