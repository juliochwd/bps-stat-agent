"""Tests for mini_agent/tools/file_tools.py — file operation tools."""

import pytest

from mini_agent.tools.file_tools import EditTool, ReadTool, WriteTool, truncate_text_by_tokens


class TestTruncateTextByTokens:
    """Tests for truncate_text_by_tokens."""

    def test_short_text_unchanged(self):
        text = "Hello world"
        result = truncate_text_by_tokens(text, max_tokens=100)
        assert result == text

    def test_long_text_truncated(self):
        text = "word " * 50000  # Very long text
        result = truncate_text_by_tokens(text, max_tokens=100)
        assert len(result) < len(text)
        assert "truncated" in result.lower()

    def test_truncation_preserves_head_and_tail(self):
        text = "START " + "middle " * 50000 + " END"
        result = truncate_text_by_tokens(text, max_tokens=200)
        assert result.startswith("START")
        # Tail should be preserved
        assert "END" in result


class TestReadTool:
    """Tests for ReadTool."""

    @pytest.fixture
    def read_tool(self, tmp_path):
        return ReadTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_read_existing_file(self, read_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n")

        result = await read_tool.execute(path=str(test_file))
        assert result.success is True
        assert "line1" in result.content
        assert "line2" in result.content
        assert "line3" in result.content

    @pytest.mark.asyncio
    async def test_read_with_line_numbers(self, read_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("first\nsecond\nthird\n")

        result = await read_tool.execute(path=str(test_file))
        assert result.success is True
        assert "1|first" in result.content
        assert "2|second" in result.content

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, read_tool):
        result = await read_tool.execute(path="nonexistent.txt")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_read_with_offset(self, read_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n")

        result = await read_tool.execute(path=str(test_file), offset=3)
        assert result.success is True
        assert "line3" in result.content
        assert "line1" not in result.content

    @pytest.mark.asyncio
    async def test_read_with_limit(self, read_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n")

        result = await read_tool.execute(path=str(test_file), limit=2)
        assert result.success is True
        assert "line1" in result.content
        assert "line2" in result.content
        assert "line3" not in result.content

    @pytest.mark.asyncio
    async def test_read_with_offset_and_limit(self, read_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n")

        result = await read_tool.execute(path=str(test_file), offset=2, limit=2)
        assert result.success is True
        assert "line2" in result.content
        assert "line3" in result.content
        assert "line1" not in result.content
        assert "line4" not in result.content

    @pytest.mark.asyncio
    async def test_read_relative_path(self, read_tool, tmp_path):
        test_file = tmp_path / "subdir" / "test.txt"
        test_file.parent.mkdir()
        test_file.write_text("content")

        result = await read_tool.execute(path="subdir/test.txt")
        assert result.success is True
        assert "content" in result.content

    @pytest.mark.asyncio
    async def test_read_path_traversal_blocked(self, read_tool, tmp_path):
        # Create a file outside workspace
        outside = tmp_path.parent / "outside.txt"
        outside.write_text("secret")

        result = await read_tool.execute(path="../outside.txt")
        assert result.success is False
        assert "access denied" in result.error.lower()

    def test_properties(self, read_tool):
        assert read_tool.name == "read_file"
        assert "Read" in read_tool.description
        assert "path" in read_tool.parameters["properties"]


class TestWriteTool:
    """Tests for WriteTool."""

    @pytest.fixture
    def write_tool(self, tmp_path):
        return WriteTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_write_new_file(self, write_tool, tmp_path):
        result = await write_tool.execute(path="new_file.txt", content="Hello World")
        assert result.success is True

        written = (tmp_path / "new_file.txt").read_text()
        assert written == "Hello World"

    @pytest.mark.asyncio
    async def test_write_creates_directories(self, write_tool, tmp_path):
        result = await write_tool.execute(path="deep/nested/file.txt", content="content")
        assert result.success is True
        assert (tmp_path / "deep" / "nested" / "file.txt").exists()

    @pytest.mark.asyncio
    async def test_write_overwrites_existing(self, write_tool, tmp_path):
        test_file = tmp_path / "existing.txt"
        test_file.write_text("old content")

        result = await write_tool.execute(path="existing.txt", content="new content")
        assert result.success is True
        assert test_file.read_text() == "new content"

    @pytest.mark.asyncio
    async def test_write_path_traversal_blocked(self, write_tool):
        result = await write_tool.execute(path="../outside.txt", content="hack")
        assert result.success is False
        assert "access denied" in result.error.lower()

    def test_properties(self, write_tool):
        assert write_tool.name == "write_file"
        assert "Write" in write_tool.description


class TestEditTool:
    """Tests for EditTool."""

    @pytest.fixture
    def edit_tool(self, tmp_path):
        return EditTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_edit_success(self, edit_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        result = await edit_tool.execute(
            path="test.txt", old_str="World", new_str="Python"
        )
        assert result.success is True
        assert test_file.read_text() == "Hello Python"

    @pytest.mark.asyncio
    async def test_edit_text_not_found(self, edit_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        result = await edit_tool.execute(
            path="test.txt", old_str="NotHere", new_str="Replacement"
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_edit_multiple_occurrences(self, edit_tool, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar foo baz foo")

        result = await edit_tool.execute(
            path="test.txt", old_str="foo", new_str="qux"
        )
        assert result.success is False
        assert "3 times" in result.error

    @pytest.mark.asyncio
    async def test_edit_file_not_found(self, edit_tool):
        result = await edit_tool.execute(
            path="nonexistent.txt", old_str="a", new_str="b"
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_edit_path_traversal_blocked(self, edit_tool):
        result = await edit_tool.execute(
            path="../outside.txt", old_str="a", new_str="b"
        )
        assert result.success is False
        assert "access denied" in result.error.lower()

    def test_properties(self, edit_tool):
        assert edit_tool.name == "edit_file"
        assert "replacement" in edit_tool.description.lower()
