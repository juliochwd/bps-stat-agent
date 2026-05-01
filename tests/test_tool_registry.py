"""Tests for mini_agent.research.tool_registry."""

from __future__ import annotations

import pytest

from mini_agent.research.tool_registry import ToolRegistry
from mini_agent.tools.base import Tool, ToolResult


class _Stub(Tool):
    def __init__(self, n):
        self._name = n

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return f"Stub: {self._name}"

    @property
    def parameters(self):
        return {"type": "object", "properties": {}}

    async def execute(self, **kw):
        return ToolResult(success=True, content="ok")


@pytest.fixture
def reg():
    return ToolRegistry()


class TestRegister:
    def test_adds(self, reg):
        reg.register(_Stub("p"), phases=["plan"])
        assert reg.tool_count == 1

    def test_core_when_no_phases(self, reg):
        reg.register(_Stub("c"))
        assert reg.get_tool_by_name("c") is not None
        assert "c" in reg.list_all()["core"]

    def test_multi_phases(self, reg):
        reg.register(_Stub("p"), phases=["plan", "collect"])
        assert any(t.name == "p" for t in reg.get_tools_for_phase("plan"))
        assert any(t.name == "p" for t in reg.get_tools_for_phase("collect"))


class TestCore:
    def test_always_available(self, reg):
        reg.register(_Stub("c"))
        reg.register(_Stub("p"), phases=["plan"])
        for ph in ["plan", "collect", "analyze", "write", "review"]:
            assert "c" in [t.name for t in reg.get_tools_for_phase(ph)]

    def test_first(self, reg):
        reg.register(_Stub("c"))
        reg.register(_Stub("p"), phases=["plan"])
        assert reg.get_tools_for_phase("plan")[0].name == "c"


class TestPhaseTools:
    def test_correct(self, reg):
        reg.register(_Stub("p"), phases=["plan"])
        reg.register(_Stub("a"), phases=["analyze"])
        assert len(reg.get_tools_for_phase("plan")) == 1

    def test_no_dupes(self, reg):
        reg.register(_Stub("c"))
        reg.register(_Stub("c"), phases=["plan"])
        assert [t.name for t in reg.get_tools_for_phase("plan")].count("c") == 1

    def test_empty(self, reg):
        assert reg.get_tools_for_phase("review") == []


class TestGetTool:
    def test_found(self, reg):
        t = _Stub("p")
        reg.register(t, phases=["plan"])
        assert reg.get_tool_by_name("p") is t

    def test_not_found(self, reg):
        assert reg.get_tool_by_name("x") is None


class TestUnregister:
    def test_removes(self, reg):
        reg.register(_Stub("p"), phases=["plan"])
        reg.unregister("p")
        assert reg.get_tool_by_name("p") is None and reg.tool_count == 0

    def test_safe(self, reg):
        reg.unregister("x")


class TestLoadUnload:
    def test_load(self, reg):
        reg.register(_Stub("p"), phases=["plan"])
        assert len(reg.load_phase("plan")) == 1

    def test_unload(self, reg):
        reg.unload_phase("plan")


class TestIntrospection:
    def test_list_all(self, reg):
        reg.register(_Stub("c"))
        reg.register(_Stub("p"), phases=["plan"])
        result = reg.list_all()
        assert "c" in result["core"] and "p" in result["plan"]

    def test_count(self, reg):
        reg.register(_Stub("c"))
        reg.register(_Stub("p"), phases=["plan"])
        reg.register(_Stub("a"), phases=["analyze"])
        assert reg.tool_count == 3

    def test_phase_count(self, reg):
        reg.register(_Stub("c"))
        reg.register(_Stub("p"), phases=["plan"])
        assert reg.get_phase_tool_count("plan") == 2
