"""Comprehensive coverage tests for mini_agent/agent.py.

Tests Agent class: initialization, add_user_message, run loop,
token counting, summarization, cancellation.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.agent import Agent
from mini_agent.schema import FunctionCall, LLMResponse, Message, TokenUsage, ToolCall
from mini_agent.tools.base import Tool, ToolResult


# ===========================================================================
# Fixtures
# ===========================================================================


class MockTool(Tool):
    """A simple mock tool for testing."""

    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "A mock tool for testing"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input text"},
            },
            "required": ["input"],
        }

    async def execute(self, input: str = "", **kwargs) -> ToolResult:
        return ToolResult(success=True, content=f"Processed: {input}")


class FailingTool(Tool):
    """A tool that always fails."""

    @property
    def name(self) -> str:
        return "failing_tool"

    @property
    def description(self) -> str:
        return "A tool that always fails"

    @property
    def parameters(self) -> dict:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> ToolResult:
        raise RuntimeError("Tool execution crashed!")


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.provider = "test"
    llm.model = "test-model"
    return llm


@pytest.fixture
def agent(mock_llm, tmp_path):
    """Create an Agent with mock LLM and tools."""
    tools = [MockTool(), FailingTool()]
    return Agent(
        llm_client=mock_llm,
        system_prompt="You are a test agent.",
        tools=tools,
        max_steps=5,
        workspace_dir=str(tmp_path),
    )


# ===========================================================================
# Initialization tests
# ===========================================================================


class TestAgentInit:
    """Test Agent initialization."""

    def test_basic_init(self, mock_llm, tmp_path):
        agent = Agent(
            llm_client=mock_llm,
            system_prompt="Test prompt",
            tools=[MockTool()],
            workspace_dir=str(tmp_path),
        )
        assert len(agent.tools) == 1
        assert "mock_tool" in agent.tools
        assert agent.max_steps == 50  # default
        assert agent.token_limit == 80000  # default

    def test_workspace_info_injected(self, mock_llm, tmp_path):
        agent = Agent(
            llm_client=mock_llm,
            system_prompt="Simple prompt",
            tools=[],
            workspace_dir=str(tmp_path),
        )
        assert "Current Workspace" in agent.system_prompt

    def test_workspace_info_not_duplicated(self, mock_llm, tmp_path):
        agent = Agent(
            llm_client=mock_llm,
            system_prompt="Prompt with Current Workspace already",
            tools=[],
            workspace_dir=str(tmp_path),
        )
        # Should not add workspace info again
        assert agent.system_prompt.count("Current Workspace") == 1

    def test_workspace_created(self, mock_llm, tmp_path):
        ws = tmp_path / "new_ws"
        Agent(
            llm_client=mock_llm,
            system_prompt="Test",
            tools=[],
            workspace_dir=str(ws),
        )
        assert ws.exists()

    def test_messages_initialized(self, agent):
        assert len(agent.messages) == 1
        assert agent.messages[0].role == "system"


# ===========================================================================
# add_user_message tests
# ===========================================================================


class TestAddUserMessage:
    """Test add_user_message."""

    def test_adds_message(self, agent):
        agent.add_user_message("Hello")
        assert len(agent.messages) == 2
        assert agent.messages[1].role == "user"
        assert agent.messages[1].content == "Hello"

    def test_multiple_messages(self, agent):
        agent.add_user_message("First")
        agent.add_user_message("Second")
        assert len(agent.messages) == 3
        assert agent.messages[2].content == "Second"


# ===========================================================================
# Token estimation tests
# ===========================================================================


class TestTokenEstimation:
    """Test token estimation methods."""

    def test_estimate_tokens(self, agent):
        agent.add_user_message("Hello world, this is a test message.")
        tokens = agent._estimate_tokens()
        assert tokens > 0

    def test_estimate_tokens_fallback(self, agent):
        agent._encoding = None  # Force fallback
        agent.add_user_message("Hello world")
        tokens = agent._estimate_tokens_fallback()
        assert tokens > 0

    def test_estimate_tokens_with_tool_calls(self, agent):
        tc = ToolCall(
            id="call_1",
            type="function",
            function=FunctionCall(name="mock_tool", arguments={"input": "test"}),
        )
        msg = Message(
            role="assistant",
            content="I'll help you.",
            tool_calls=[tc],
        )
        agent.messages.append(msg)
        tokens = agent._estimate_tokens()
        assert tokens > 0


# ===========================================================================
# run() tests
# ===========================================================================


class TestAgentRun:
    """Test Agent.run() method."""

    @pytest.mark.asyncio
    async def test_simple_response_no_tools(self, agent, mock_llm):
        """Test agent completes when LLM returns no tool calls."""
        response = LLMResponse(
            content="Here is my answer.",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=100, prompt_tokens=80, completion_tokens=20),
        )

        mock_llm.generate = AsyncMock(return_value=response)

        agent.add_user_message("What is 2+2?")
        result = await agent.run()
        assert result == "Here is my answer."

    @pytest.mark.asyncio
    async def test_tool_call_and_response(self, agent, mock_llm):
        """Test agent calls a tool then gets final response."""
        # First response: tool call
        tc = ToolCall(
            id="call_123",
            type="function",
            function=FunctionCall(name="mock_tool", arguments={"input": "test data"}),
        )

        response1 = LLMResponse(
            content="Let me use a tool.",
            thinking=None,
            tool_calls=[tc],
            finish_reason="tool_calls",
            usage=TokenUsage(total_tokens=150, prompt_tokens=100, completion_tokens=50),
        )

        # Second response: final answer
        response2 = LLMResponse(
            content="The tool returned: Processed: test data",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=200, prompt_tokens=150, completion_tokens=50),
        )

        mock_llm.generate = AsyncMock(side_effect=[response1, response2])

        agent.add_user_message("Process this data")
        result = await agent.run()
        assert "Processed" in result or "tool returned" in result.lower()

    @pytest.mark.asyncio
    async def test_unknown_tool(self, agent, mock_llm):
        """Test agent handles unknown tool gracefully."""
        tc = ToolCall(
            id="call_456",
            type="function",
            function=FunctionCall(name="nonexistent_tool", arguments={}),
        )

        response1 = LLMResponse(
            content="Using tool.",
            thinking=None,
            tool_calls=[tc],
            finish_reason="tool_calls",
            usage=TokenUsage(total_tokens=100, prompt_tokens=80, completion_tokens=20),
        )

        response2 = LLMResponse(
            content="Tool not found, sorry.",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=150, prompt_tokens=100, completion_tokens=50),
        )

        mock_llm.generate = AsyncMock(side_effect=[response1, response2])

        agent.add_user_message("Use unknown tool")
        result = await agent.run()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_tool_execution_exception(self, agent, mock_llm):
        """Test agent handles tool execution exceptions."""
        tc = ToolCall(
            id="call_789",
            type="function",
            function=FunctionCall(name="failing_tool", arguments={}),
        )

        response1 = LLMResponse(
            content="Using failing tool.",
            thinking=None,
            tool_calls=[tc],
            finish_reason="tool_calls",
            usage=TokenUsage(total_tokens=100, prompt_tokens=80, completion_tokens=20),
        )

        response2 = LLMResponse(
            content="Tool failed, I'll try another approach.",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=150, prompt_tokens=100, completion_tokens=50),
        )

        mock_llm.generate = AsyncMock(side_effect=[response1, response2])

        agent.add_user_message("Use failing tool")
        result = await agent.run()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_max_steps_reached(self, agent, mock_llm):
        """Test agent stops after max_steps."""
        tc = ToolCall(
            id="call_loop",
            type="function",
            function=FunctionCall(name="mock_tool", arguments={"input": "loop"}),
        )

        response = LLMResponse(
            content="Calling tool again.",
            thinking=None,
            tool_calls=[tc],
            finish_reason="tool_calls",
            usage=TokenUsage(total_tokens=100, prompt_tokens=80, completion_tokens=20),
        )

        mock_llm.generate = AsyncMock(return_value=response)

        agent.add_user_message("Loop forever")
        result = await agent.run()
        assert "couldn't be completed" in result.lower() or "max" in result.lower()

    @pytest.mark.asyncio
    async def test_llm_error(self, agent, mock_llm):
        """Test agent handles LLM errors."""
        mock_llm.generate = AsyncMock(side_effect=Exception("API error"))

        agent.add_user_message("Test")
        result = await agent.run()
        assert "failed" in result.lower() or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_thinking_displayed(self, agent, mock_llm, capsys):
        """Test that thinking content is handled."""
        response = LLMResponse(
            content="Final answer.",
            thinking="Let me think about this...",
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=100, prompt_tokens=80, completion_tokens=20),
        )

        mock_llm.generate = AsyncMock(return_value=response)

        agent.add_user_message("Think about this")
        result = await agent.run()
        assert result == "Final answer."


# ===========================================================================
# Cancellation tests
# ===========================================================================


class TestAgentCancellation:
    """Test Agent cancellation via cancel_event."""

    @pytest.mark.asyncio
    async def test_cancel_at_start(self, agent, mock_llm):
        """Test cancellation before first step."""
        cancel_event = asyncio.Event()
        cancel_event.set()  # Already cancelled

        agent.add_user_message("Do something")
        result = await agent.run(cancel_event=cancel_event)
        assert "cancelled" in result.lower()

    @pytest.mark.asyncio
    async def test_cancel_via_agent_attribute(self, agent, mock_llm):
        """Test cancellation via agent.cancel_event."""
        cancel_event = asyncio.Event()
        cancel_event.set()
        agent.cancel_event = cancel_event

        agent.add_user_message("Do something")
        result = await agent.run()
        assert "cancelled" in result.lower()

    @pytest.mark.asyncio
    async def test_cancel_after_tool_call(self, agent, mock_llm):
        """Test cancellation after a tool executes."""
        tc = ToolCall(
            id="call_cancel",
            type="function",
            function=FunctionCall(name="mock_tool", arguments={"input": "data"}),
        )

        response = LLMResponse(
            content="Using tool.",
            thinking=None,
            tool_calls=[tc],
            finish_reason="tool_calls",
            usage=TokenUsage(total_tokens=100, prompt_tokens=80, completion_tokens=20),
        )

        mock_llm.generate = AsyncMock(return_value=response)

        cancel_event = asyncio.Event()
        agent.add_user_message("Process")

        # Cancel after first tool execution
        original_execute = MockTool.execute

        async def cancel_after_execute(self_tool, **kwargs):
            result = await original_execute(self_tool, **kwargs)
            cancel_event.set()
            return result

        with patch.object(MockTool, "execute", cancel_after_execute):
            result = await agent.run(cancel_event=cancel_event)
            assert "cancelled" in result.lower()


# ===========================================================================
# Message cleanup tests
# ===========================================================================


class TestMessageCleanup:
    """Test _cleanup_incomplete_messages."""

    def test_cleanup_removes_incomplete(self, agent):
        from mini_agent.schema import Message
        agent.messages.append(Message(role="user", content="Hello"))
        agent.messages.append(Message(role="assistant", content="Working..."))
        agent.messages.append(Message(role="tool", content="result", tool_call_id="x", name="t"))

        agent._cleanup_incomplete_messages()
        # Should remove the assistant and tool messages
        assert agent.messages[-1].role == "user"

    def test_cleanup_no_assistant(self, agent):
        """No cleanup needed if no assistant message."""
        original_len = len(agent.messages)
        agent._cleanup_incomplete_messages()
        assert len(agent.messages) == original_len


# ===========================================================================
# get_history tests
# ===========================================================================


class TestGetHistory:
    """Test get_history."""

    def test_returns_copy(self, agent):
        history = agent.get_history()
        assert history == agent.messages
        # Should be a copy
        history.append(MagicMock())
        assert len(history) != len(agent.messages)
