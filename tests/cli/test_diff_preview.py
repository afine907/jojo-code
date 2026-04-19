"""CLI Diff Preview 模块测试"""

import pytest

from nano_code.cli.diff_preview import (
    DiffFile,
    DiffLine,
    DiffPreview,
    DiffStats,
    compute_diff_stats,
    create_inline_diff,
    format_diff,
    generate_diff,
    parse_unified_diff,
    render_diff_summary,
)


class TestDiffLine:
    """测试 DiffLine 数据类"""

    def test_context_line(self):
        """测试上下文行"""
        line = DiffLine(type="context", content="print('hello')", old_line_num=1, new_line_num=1)
        assert line.type == "context"
        assert line.content == "print('hello')"
        assert line.old_line_num == 1
        assert line.new_line_num == 1

    def test_added_line(self):
        """测试新增行"""
        line = DiffLine(type="added", content="new_function()", new_line_num=5)
        assert line.type == "added"
        assert line.content == "new_function()"
        assert line.new_line_num == 5

    def test_removed_line(self):
        """测试删除行"""
        line = DiffLine(type="removed", content="old_function()", old_line_num=3)
        assert line.type == "removed"
        assert line.content == "old_function()"
        assert line.old_line_num == 3


class TestDiffFile:
    """测试 DiffFile 数据类"""

    def test_diff_file_defaults(self):
        """测试默认统计"""
        diff_file = DiffFile(old_path="a.py", new_path="b.py", lines=[])
        assert diff_file.additions == 0
        assert diff_file.deletions == 0


class TestDiffStats:
    """测试 DiffStats 数据类"""

    def test_diff_stats_defaults(self):
        """测试默认统计"""
        stats = DiffStats()
        assert stats.files_changed == 0
        assert stats.insertions == 0
        assert stats.deletions == 0


class TestParseUnifiedDiff:
    """测试 parse_unified_diff 函数"""

    def test_parse_simple_diff(self):
        """测试解析简单 diff"""
        diff_text = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 line1
-line2
+new_line2
 line3
+line4
"""
        files = parse_unified_diff(diff_text)
        assert len(files) == 1
        assert files[0].additions == 2
        assert files[0].deletions == 1

    def test_parse_empty_diff(self):
        """测试解析空 diff"""
        files = parse_unified_diff("")
        assert len(files) == 0


class TestComputeDiffStats:
    """测试 compute_diff_stats 函数"""

    def test_compute_stats_simple(self):
        """测试计算简单 diff 统计"""
        diff_text = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
+added_line
-removed_line
 context
"""
        stats = compute_diff_stats(diff_text)
        assert stats.insertions == 1
        assert stats.deletions == 2  # includes --- line


class TestGenerateDiff:
    """测试 generate_diff 函数"""

    def test_generate_diff_simple(self):
        """测试生成简单 diff"""
        old = "line1\nline2\nline3\n"
        new = "line1\nmodified\nline3\n"
        diff = generate_diff(old, new, "a.txt", "b.txt")
        assert "--- a.txt" in diff
        assert "+++ b.txt" in diff
        assert "-line2" in diff
        assert "+modified" in diff

    def test_generate_diff_empty_old(self):
        """测试旧内容为空时生成 diff"""
        old = ""
        new = "new line\n"
        diff = generate_diff(old, new, "a.txt", "b.txt")
        assert "+new line" in diff

    def test_generate_diff_empty_new(self):
        """测试新内容为空时生成 diff"""
        old = "old line\n"
        new = ""
        diff = generate_diff(old, new, "a.txt", "b.txt")
        assert "-old line" in diff

    def test_generate_diff_both_empty(self):
        """测试两个内容都为空"""
        diff = generate_diff("", "", "a.txt", "b.txt")
        assert diff == ""

    def test_generate_diff_no_changes(self):
        """测试无变化"""
        content = "same line\n"
        diff = generate_diff(content, content, "a.txt", "b.txt")
        assert diff == ""

    def test_generate_diff_multiple_lines(self):
        """测试多行 diff"""
        old = "line1\nline2\nline3\n"
        new = "line1\nline2 modified\nline3 modified\nline4\n"
        diff = generate_diff(old, new, "a.txt", "b.txt")
        assert "+line2 modified" in diff
        assert "+line3 modified" in diff
        assert "+line4" in diff


class TestFormatDiff:
    """测试 format_diff 函数"""

    def test_format_diff_simple(self):
        """测试格式化简单 diff"""
        diff_text = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,2 @@
-old
+new
"""
        result = format_diff(diff_text)
        assert "Diff:" in result
        assert "+1/-" in result  # -1 plus --- line

    def test_format_diff_empty(self):
        """测试格式化空 diff"""
        result = format_diff("")
        assert "No changes" in result

    def test_format_diff_with_color(self):
        """测试带颜色的格式化"""
        diff_text = """--- a/test.py
+++ b/test.py
+added
-removed
"""
        result = format_diff(diff_text, colorize=True)
        assert "[green]" in result
        assert "[red]" in result

    def test_format_diff_without_color(self):
        """测试不带颜色的格式化"""
        diff_text = """--- a/test.py
+++ b/test.py
+added
-removed
"""
        result = format_diff(diff_text, colorize=False)
        assert "+added" in result
        assert "-removed" in result

    def test_format_diff_max_lines(self):
        """测试最大行数限制"""
        diff_lines = ["--- a/test.py\n", "+++ b/test.py\n"]
        diff_lines += [f"@@ -{i},{i} +{i},{i} @@\n" for i in range(60)]
        diff_lines += ["+line\n" for _ in range(60)]
        diff_text = "".join(diff_lines)

        result = format_diff(diff_text, max_lines=50)
        assert "more lines" in result

    def test_format_diff_no_line_numbers(self):
        """测试不显示行号"""
        diff_text = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,2 @@
-old
+new
"""
        result = format_diff(diff_text, show_line_numbers=False)
        assert "Diff:" in result


class TestDiffPreview:
    """测试 DiffPreview 类"""

    @pytest.fixture
    def preview(self):
        """创建 DiffPreview 实例"""
        return DiffPreview()

    def test_render_simple(self, preview):
        """测试渲染简单 diff"""
        diff_text = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,2 @@
-old
+new
"""
        result = preview.render(diff_text)
        assert "Files:" in result
        assert "+1" in result or "-1" in result

    def test_render_empty(self, preview):
        """测试渲染空 diff"""
        result = preview.render("")
        assert result == ""

    def test_get_line_prefix(self, preview):
        """测试获取行前缀"""
        assert "+" in preview._get_line_prefix("added")
        assert "-" in preview._get_line_prefix("removed")
        assert "@@" in preview._get_line_prefix("header")
        assert " " in preview._get_line_prefix("context")

    def test_format_line_nums(self, preview):
        """测试格式化行号"""
        line = DiffLine(type="context", content="test", old_line_num=5, new_line_num=6)
        result = preview._format_line_nums(line)
        assert "5" in result
        assert "6" in result

    def test_render_side_by_side(self, preview):
        """测试并排渲染"""
        old = "line1\nline2\n"
        new = "line1\nmodified\n"
        result = preview.render_side_by_side(old, new)
        assert "Old" in result
        assert "New" in result


class TestCreateInlineDiff:
    """测试 create_inline_diff 函数"""

    def test_unchanged_lines(self):
        """测试未改变的行"""
        old = "line1\nline2\n"
        new = "line1\nline2\n"
        diff = create_inline_diff(old, new)
        assert len(diff) == 2
        assert diff[0]["type"] == "unchanged"
        assert diff[1]["type"] == "unchanged"

    def test_added_lines(self):
        """测试新增的行"""
        old = "line1\n"
        new = "line1\nline2\n"
        diff = create_inline_diff(old, new)
        assert len(diff) == 2
        assert diff[1]["type"] == "added"
        assert diff[1]["content"] == "line2"

    def test_removed_lines(self):
        """测试删除的行"""
        old = "line1\nline2\n"
        new = "line1\n"
        diff = create_inline_diff(old, new)
        assert len(diff) == 2
        assert diff[1]["type"] == "removed"
        assert diff[1]["content"] == "line2"

    def test_modified_lines(self):
        """测试修改的行"""
        old = "old\n"
        new = "new\n"
        diff = create_inline_diff(old, new)
        assert len(diff) == 2
        assert diff[0]["type"] == "removed"
        assert diff[1]["type"] == "added"


class TestRenderDiffSummary:
    """测试 render_diff_summary 函数"""

    def test_render_summary(self):
        """测试渲染摘要"""
        diff_text = """--- a/test.py
+++ b/test.py
+added
-removed
"""
        result = render_diff_summary(diff_text)
        assert "Changed:" in result
        assert "files" in result


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_files(self):
        """测试空文件 diff"""
        diff = generate_diff("", "", "a.txt", "b.txt")
        assert diff == ""

    def test_large_file_truncation(self):
        """测试大文件截断"""
        old_lines = ["line\n" for _ in range(300)]
        new_lines = ["line\n" for _ in range(300)]
        for i in range(0, 300, 3):
            new_lines[i] = f"modified{i}\n"

        diff = generate_diff("".join(old_lines), "".join(new_lines), "a.txt", "b.txt")
        result = format_diff(diff, max_lines=10)
        assert "more lines" in result

    def test_very_long_lines(self):
        """测试非常长的行"""
        long_line = "x" * 10000
        diff = generate_diff(long_line, long_line + "y", "a.txt", "b.txt")
        assert "+" in diff

    def test_binary_like_content(self):
        """测试二进制内容"""
        old = "\x00\x01\x02\n"
        new = "\x00\x01\x03\n"
        diff = generate_diff(old, new, "a.bin", "b.bin")
        assert "---" in diff
        assert "+++" in diff
