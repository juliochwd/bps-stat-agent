"""Tests for the edit_file fix - should only replace single occurrences."""

import pytest

from mini_agent.tools.file_tools import EditTool


@pytest.fixture
def edit_tool(tmp_path):
    return EditTool(workspace_dir=str(tmp_path))


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("def hello():\n    print('hello')\n    return True\n")
    return f


class TestEditToolFix:
    @pytest.mark.asyncio
    async def test_single_occurrence_succeeds(self, edit_tool, sample_file):
        result = await edit_tool.execute(
            path=str(sample_file),
            old_str="print('hello')",
            new_str="print('world')",
        )
        assert result.success
        assert "world" in sample_file.read_text()

    @pytest.mark.asyncio
    async def test_multiple_occurrences_fails(self, edit_tool, tmp_path):
        f = tmp_path / "dup.py"
        f.write_text("x = 1\nx = 1\nx = 1\n")
        result = await edit_tool.execute(
            path=str(f),
            old_str="x = 1",
            new_str="x = 2",
        )
        assert not result.success
        assert "3 times" in result.error
        # File should be unchanged
        assert f.read_text() == "x = 1\nx = 1\nx = 1\n"

    @pytest.mark.asyncio
    async def test_not_found_fails(self, edit_tool, sample_file):
        result = await edit_tool.execute(
            path=str(sample_file),
            old_str="nonexistent text",
            new_str="replacement",
        )
        assert not result.success
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_file_not_found(self, edit_tool, tmp_path):
        result = await edit_tool.execute(
            path=str(tmp_path / "nonexistent.py"),
            old_str="x",
            new_str="y",
        )
        assert not result.success
