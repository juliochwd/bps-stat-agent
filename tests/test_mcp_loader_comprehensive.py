"""Comprehensive tests for mini_agent/tools/mcp_loader.py.

Tests MCPTool, MCPServerConnection, timeout config, load_mcp_tools_async.
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.tools.mcp_loader import (
    MCPServerConnection,
    MCPTimeoutConfig,
    MCPTool,
    get_mcp_timeout_config,
    set_mcp_timeout_config,
)


# ===================================================================
# MCPTimeoutConfig Tests
# ===================================================================

class TestMCPTimeoutConfig:
    def test_default_values(self):
        config = MCPTimeoutConfig()
        assert config.connect_timeout == 10.0
        assert config.execute_timeout == 60.0
        assert config.sse_read_timeout == 120.0

    def test_custom_values(self):
        config = MCPTimeoutConfig(connect_timeout=5.0, execute_timeout=30.0, sse_read_timeout=90.0)
        assert config.connect_timeout == 5.0
        assert config.execute_timeout == 30.0
        assert config.sse_read_timeout == 90.0


class TestSetMCPTimeoutConfig:
    def test_set_connect_timeout(self):
        original = get_mcp_timeout_config().connect_timeout
        set_mcp_timeout_config(connect_timeout=15.0)
        assert get_mcp_timeout_config().connect_timeout == 15.0
        set_mcp_timeout_config(connect_timeout=original)

    def test_set_execute_timeout(self):
        original = get_mcp_timeout_config().execute_timeout
        set_mcp_timeout_config(execute_timeout=45.0)
        assert get_mcp_timeout_config().execute_timeout == 45.0
        set_mcp_timeout_config(execute_timeout=original)

    def test_set_sse_read_timeout(self):
        original = get_mcp_timeout_config().sse_read_timeout
        set_mcp_timeout_config(sse_read_timeout=180.0)
        assert get_mcp_timeout_config().sse_read_timeout == 180.0
        set_mcp_timeout_config(sse_read_timeout=original)

    def test_set_none_does_not_change(self):
        original = get_mcp_timeout_config().connect_timeout
        set_mcp_timeout_config(connect_timeout=None)
        assert get_mcp_timeout_config().connect_timeout == original


# ===================================================================
# MCPTool Tests
# ===================================================================

class TestMCPTool:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        return session

    @pytest.fixture
    def tool(self, mock_session):
        return MCPTool(
            name="test_tool",
            description="A test MCP tool",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}},
            session=mock_session,
            execute_timeout=30.0,
        )

    def test_name(self, tool):
        assert tool.name == "test_tool"

    def test_description(self, tool):
        assert tool.description == "A test MCP tool"

    def test_parameters(self, tool):
        assert tool.parameters["type"] == "object"
        assert "query" in tool.parameters["properties"]

    @pytest.mark.asyncio
    async def test_execute_success(self, tool, mock_session):
        mock_content_item = MagicMock()
        mock_content_item.text = "Search results: found 5 items"

        mock_result = MagicMock()
        mock_result.content = [mock_content_item]
        mock_result.isError = False

        mock_session.call_tool.return_value = mock_result

        result = await tool.execute(query="inflation")
        assert result.success is True
        assert "Search results" in result.content

    @pytest.mark.asyncio
    async def test_execute_error_result(self, tool, mock_session):
        mock_content_item = MagicMock()
        mock_content_item.text = "Error: not found"

        mock_result = MagicMock()
        mock_result.content = [mock_content_item]
        mock_result.isError = True

        mock_session.call_tool.return_value = mock_result

        result = await tool.execute(query="nonexistent")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_timeout(self, tool, mock_session):
        async def slow_call(*args, **kwargs):
            await asyncio.sleep(100)

        mock_session.call_tool.side_effect = slow_call

        # Use a very short timeout
        tool._execute_timeout = 0.01
        result = await tool.execute(query="slow")
        assert result.success is False
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_exception(self, tool, mock_session):
        mock_session.call_tool.side_effect = RuntimeError("Connection lost")

        result = await tool.execute(query="test")
        assert result.success is False
        assert "Connection lost" in result.error

    @pytest.mark.asyncio
    async def test_execute_content_without_text(self, tool, mock_session):
        """Test handling content items without .text attribute."""
        mock_content_item = MagicMock()
        # Remove text attribute but keep __str__
        del mock_content_item.text
        mock_content_item.__str__ = lambda self: "raw content"

        mock_result = MagicMock()
        mock_result.content = [mock_content_item]
        mock_result.isError = False

        mock_session.call_tool.return_value = mock_result

        result = await tool.execute(query="test")
        assert result.success is True


# ===================================================================
# MCPServerConnection Tests
# ===================================================================

class TestMCPServerConnection:
    def test_init_stdio(self):
        conn = MCPServerConnection(
            name="test-server",
            connection_type="stdio",
            command="python",
            args=["-m", "my_server"],
            env={"KEY": "value"},
        )
        assert conn.name == "test-server"
        assert conn.connection_type == "stdio"
        assert conn.command == "python"
        assert conn.args == ["-m", "my_server"]
        assert conn.env == {"KEY": "value"}

    def test_init_sse(self):
        conn = MCPServerConnection(
            name="sse-server",
            connection_type="sse",
            url="http://localhost:8080/sse",
            headers={"Authorization": "Bearer token"},
        )
        assert conn.connection_type == "sse"
        assert conn.url == "http://localhost:8080/sse"
        assert conn.headers == {"Authorization": "Bearer token"}

    def test_init_http(self):
        conn = MCPServerConnection(
            name="http-server",
            connection_type="http",
            url="http://localhost:8080/mcp",
        )
        assert conn.connection_type == "http"

    def test_timeout_overrides(self):
        conn = MCPServerConnection(
            name="test",
            connection_type="stdio",
            command="test",
            connect_timeout=5.0,
            execute_timeout=20.0,
            sse_read_timeout=60.0,
        )
        assert conn._get_connect_timeout() == 5.0
        assert conn._get_execute_timeout() == 20.0
        assert conn._get_sse_read_timeout() == 60.0

    def test_default_timeouts(self):
        conn = MCPServerConnection(name="test", connection_type="stdio", command="test")
        # Should use global defaults
        assert conn._get_connect_timeout() == get_mcp_timeout_config().connect_timeout
        assert conn._get_execute_timeout() == get_mcp_timeout_config().execute_timeout

    @pytest.mark.asyncio
    async def test_connect_timeout(self):
        """Test that connection times out properly."""
        conn = MCPServerConnection(
            name="slow-server",
            connection_type="stdio",
            command="sleep",
            args=["100"],
            connect_timeout=1.0,
        )
        result = await conn.connect()
        assert result is False

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure with invalid command."""
        conn = MCPServerConnection(
            name="bad-server",
            connection_type="stdio",
            command="nonexistent_command_xyz",
            args=[],
            connect_timeout=2.0,
        )
        result = await conn.connect()
        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        conn = MCPServerConnection(name="test", connection_type="stdio", command="test")
        conn.exit_stack = AsyncMock()
        await conn.disconnect()
        # Should not raise

    @pytest.mark.asyncio
    async def test_disconnect_no_stack(self):
        """Test disconnection when not connected."""
        conn = MCPServerConnection(name="test", connection_type="stdio", command="test")
        conn.exit_stack = None
        await conn.disconnect()
        # Should not raise


# ===================================================================
# load_mcp_tools_async Tests
# ===================================================================

class TestLoadMCPToolsAsync:
    @pytest.mark.asyncio
    async def test_load_nonexistent_config(self):
        from mini_agent.tools.mcp_loader import load_mcp_tools_async
        result = await load_mcp_tools_async("/nonexistent/mcp.json")
        assert result == []

    @pytest.mark.asyncio
    async def test_load_empty_config(self, tmp_path):
        from mini_agent.tools.mcp_loader import load_mcp_tools_async
        config_file = tmp_path / "mcp.json"
        config_file.write_text("{}")
        result = await load_mcp_tools_async(str(config_file))
        assert result == []

    @pytest.mark.asyncio
    async def test_load_invalid_json(self, tmp_path):
        from mini_agent.tools.mcp_loader import load_mcp_tools_async
        config_file = tmp_path / "mcp.json"
        config_file.write_text("not valid json")
        result = await load_mcp_tools_async(str(config_file))
        assert result == []

    @pytest.mark.asyncio
    async def test_load_with_servers(self, tmp_path):
        from mini_agent.tools.mcp_loader import load_mcp_tools_async
        config = {
            "mcpServers": {
                "test-server": {
                    "command": "nonexistent_server_binary",
                    "args": [],
                }
            }
        }
        config_file = tmp_path / "mcp.json"
        config_file.write_text(json.dumps(config))
        # Will fail to connect but should not crash
        result = await load_mcp_tools_async(str(config_file))
        assert isinstance(result, list)
