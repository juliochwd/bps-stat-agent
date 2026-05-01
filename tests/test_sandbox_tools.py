"""Tests for sandbox tools."""

from __future__ import annotations

import pytest

try:
    from mini_agent.tools.analysis_tools import PythonReplTool

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

pytestmark = pytest.mark.skipif(not HAS_NUMPY, reason="numpy/pandas not installed (research extras)")


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "analysis" / "sandbox_output").mkdir(parents=True, exist_ok=True)
    return str(tmp_path)


class TestExecution:
    async def test_print(self, workspace):
        assert "hello" in (await PythonReplTool(workspace_dir=workspace).execute(code="print('hello')")).content

    async def test_math(self, workspace):
        assert "21" in (await PythonReplTool(workspace_dir=workspace).execute(code="print(3 * 7)")).content

    async def test_multiline(self, workspace):
        r = await PythonReplTool(workspace_dir=workspace).execute(code="x=10\ny=20\nprint(x+y)")
        assert r.success is True and "30" in r.content

    async def test_list_comp(self, workspace):
        r = await PythonReplTool(workspace_dir=workspace).execute(code="print([i**2 for i in range(5)])")
        assert "[0, 1, 4, 9, 16]" in r.content


class TestErrors:
    async def test_syntax(self, workspace):
        r = await PythonReplTool(workspace_dir=workspace).execute(code="def foo(")
        assert r.success is False or "error" in (r.content + (r.error or "")).lower()

    async def test_runtime(self, workspace):
        r = await PythonReplTool(workspace_dir=workspace).execute(code="1/0")
        assert r.success is False or "error" in (r.content + (r.error or "")).lower()

    async def test_name(self, workspace):
        r = await PythonReplTool(workspace_dir=workspace).execute(code="print(undefined_var)")
        assert r.success is False or "error" in (r.content + (r.error or "")).lower()


class TestTimeout:
    async def test_accepts(self, workspace):
        assert (await PythonReplTool(workspace_dir=workspace).execute(code="print('q')", timeout=5)).success is True
