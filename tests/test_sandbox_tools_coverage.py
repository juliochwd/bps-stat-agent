"""Comprehensive coverage tests for mini_agent/tools/sandbox_tools.py.

Tests PythonREPLTool with local execution, Docker error paths, E2B error paths.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.tools.sandbox_tools import PythonREPLTool


# ===========================================================================
# PythonREPLTool - Properties
# ===========================================================================


class TestPythonREPLToolProperties:
    """Test tool properties."""

    def test_name(self, tmp_path):
        tool = PythonREPLTool(workspace_dir=str(tmp_path))
        assert tool.name == "python_repl"

    def test_description(self, tmp_path):
        tool = PythonREPLTool(workspace_dir=str(tmp_path))
        assert "python" in tool.description.lower() or "execute" in tool.description.lower()

    def test_parameters(self, tmp_path):
        tool = PythonREPLTool(workspace_dir=str(tmp_path))
        params = tool.parameters
        assert "code" in params["properties"]
        assert "timeout" in params["properties"]
        assert "sandbox_type" in params["properties"]


# ===========================================================================
# PythonREPLTool - Local execution
# ===========================================================================


class TestPythonREPLToolLocal:
    """Test local subprocess execution."""

    @pytest.fixture
    def tool(self, tmp_path):
        return PythonREPLTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_empty_code(self, tool):
        result = await tool.execute(code="")
        assert result.success is False
        assert "no code" in result.error.lower()

    @pytest.mark.asyncio
    async def test_whitespace_only(self, tool):
        result = await tool.execute(code="   ")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_simple_print(self, tool):
        result = await tool.execute(code="print('hello world')")
        assert result.success is True
        assert "hello world" in result.content

    @pytest.mark.asyncio
    async def test_math_computation(self, tool):
        result = await tool.execute(code="print(2 + 3 * 4)")
        assert result.success is True
        assert "14" in result.content

    @pytest.mark.asyncio
    async def test_multiline_code(self, tool):
        code = """
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""
        result = await tool.execute(code=code)
        assert result.success is True
        assert "30" in result.content

    @pytest.mark.asyncio
    async def test_import_stdlib(self, tool):
        code = "import math\nprint(math.pi)"
        result = await tool.execute(code=code)
        assert result.success is True
        assert "3.14" in result.content

    @pytest.mark.asyncio
    async def test_syntax_error(self, tool):
        result = await tool.execute(code="def foo(")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_runtime_error(self, tool):
        result = await tool.execute(code="1/0")
        assert result.success is False
        assert "ZeroDivision" in (result.content + (result.error or ""))

    @pytest.mark.asyncio
    async def test_name_error(self, tool):
        result = await tool.execute(code="print(undefined_variable)")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_timeout(self, tool):
        code = "import time\ntime.sleep(10)"
        result = await tool.execute(code=code, timeout=1)
        assert result.success is False
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_file_generation(self, tool, tmp_path):
        code = """
import json
with open('output.json', 'w') as f:
    json.dump({"key": "value"}, f)
print("File written")
"""
        result = await tool.execute(code=code)
        assert result.success is True
        assert "File written" in result.content

    @pytest.mark.asyncio
    async def test_stderr_output(self, tool):
        code = "import sys\nsys.stderr.write('warning message\\n')\nprint('done')"
        result = await tool.execute(code=code)
        assert result.success is True
        assert "done" in result.content

    @pytest.mark.asyncio
    async def test_workspace_created(self, tmp_path):
        ws = tmp_path / "new_workspace"
        tool = PythonREPLTool(workspace_dir=str(ws))
        result = await tool.execute(code="print('ok')")
        assert result.success is True
        assert ws.exists()


# ===========================================================================
# PythonREPLTool - Docker execution
# ===========================================================================


class TestPythonREPLToolDocker:
    """Test Docker execution paths."""

    @pytest.fixture
    def tool(self, tmp_path):
        return PythonREPLTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_docker_not_installed(self, tool):
        with patch("mini_agent.tools.sandbox_tools._HAS_DOCKER", False):
            result = await tool.execute(code="print('hi')", sandbox_type="docker")
            assert result.success is False
            assert "docker" in result.error.lower()

    @pytest.mark.asyncio
    async def test_docker_execution_mocked(self, tool, tmp_path):
        """Test Docker execution with mocked docker client."""
        mock_container = MagicMock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.side_effect = [b"hello output", b""]
        mock_container.remove = MagicMock()

        mock_client = MagicMock()
        mock_client.containers.run.return_value = mock_container

        mock_docker_module = MagicMock()
        mock_docker_module.from_env.return_value = mock_client
        mock_docker_module.errors.DockerException = Exception

        with patch("mini_agent.tools.sandbox_tools._HAS_DOCKER", True), \
             patch.dict("sys.modules", {"docker": mock_docker_module}):
            result = await tool.execute(code="print('hello')", sandbox_type="docker")
            assert result.success is True
            assert "hello output" in result.content

    @pytest.mark.asyncio
    async def test_docker_execution_error(self, tool, tmp_path):
        """Test Docker execution failure."""
        mock_docker_module = MagicMock()
        mock_docker_module.errors.DockerException = Exception
        mock_docker_module.from_env.side_effect = Exception("Docker error")

        with patch("mini_agent.tools.sandbox_tools._HAS_DOCKER", True), \
             patch.dict("sys.modules", {"docker": mock_docker_module}):
            result = await tool.execute(code="print('hi')", sandbox_type="docker")
            assert result.success is False


# ===========================================================================
# PythonREPLTool - E2B execution
# ===========================================================================


class TestPythonREPLToolE2B:
    """Test E2B execution paths."""

    @pytest.fixture
    def tool(self, tmp_path):
        return PythonREPLTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_e2b_not_installed(self, tool):
        with patch("mini_agent.tools.sandbox_tools._HAS_E2B", False):
            result = await tool.execute(code="print('hi')", sandbox_type="e2b")
            assert result.success is False
            assert "e2b" in result.error.lower()

    @pytest.mark.asyncio
    async def test_e2b_no_api_key(self, tool):
        mock_e2b = MagicMock()
        with patch("mini_agent.tools.sandbox_tools._HAS_E2B", True), \
             patch.dict("sys.modules", {"e2b_code_interpreter": mock_e2b}), \
             patch.dict("os.environ", {"E2B_API_KEY": ""}, clear=False):
            result = await tool.execute(code="print('hi')", sandbox_type="e2b")
            assert result.success is False
            assert "E2B_API_KEY" in result.error
