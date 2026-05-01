"""Tests for mini_agent/llm/litellm_client.py — LiteLLM provider client."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.schema.schema import (
    FunctionCall,
    LLMResponse,
    Message,
    TokenUsage,
    ToolCall,
)


class TestLiteLLMClientImport:
    """Test import and initialization."""

    def test_import(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        assert LiteLLMClient is not None

    def test_init_defaults(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        assert client.model == "claude-sonnet-4-20250514"
        assert client.fallback_models == []
        assert client.budget_limit == 50.0
        assert client.total_cost == 0.0
        assert client.call_count == 0

    def test_init_custom(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(
            model="gpt-4o",
            api_key="sk-test",
            api_base="https://api.test.com",
            fallback_models=["gpt-3.5-turbo"],
            budget_limit=10.0,
        )
        assert client.model == "gpt-4o"
        assert client.api_key == "sk-test"
        assert client.api_base == "https://api.test.com"
        assert client.fallback_models == ["gpt-3.5-turbo"]
        assert client.budget_limit == 10.0


class TestLiteLLMClientEnsure:
    """Test lazy import of litellm."""

    def test_ensure_litellm_not_installed(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        client._litellm = None

        with patch.dict("sys.modules", {"litellm": None}):
            with patch("builtins.__import__", side_effect=ImportError("no litellm")):
                with pytest.raises(ImportError, match="LiteLLM is not installed"):
                    client._ensure_litellm()

    def test_ensure_litellm_installed(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        client._litellm = None

        mock_litellm = MagicMock()
        with patch("builtins.__import__", return_value=mock_litellm):
            with patch.dict("sys.modules", {"litellm": mock_litellm}):
                result = client._ensure_litellm()
                assert result is not None


class TestLiteLLMClientGenerate:
    """Test the generate method."""

    @pytest.mark.asyncio
    async def test_generate_success(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(model="gpt-4o")

        # Mock litellm
        mock_litellm = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_litellm.acompletion = AsyncMock(return_value=mock_response)
        mock_litellm.completion_cost = MagicMock(return_value=0.001)
        client._litellm = mock_litellm

        messages = [Message(role="user", content="Hi")]
        result = await client.generate(messages)

        assert isinstance(result, LLMResponse)
        assert result.content == "Hello!"
        assert result.finish_reason == "stop"
        assert client.call_count == 1
        assert client.total_cost == 0.001

    @pytest.mark.asyncio
    async def test_generate_budget_exceeded(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(budget_limit=1.0)
        client.total_cost = 1.5  # Already over budget
        # Mock _ensure_litellm to avoid import error
        mock_litellm = MagicMock()
        client._litellm = mock_litellm

        messages = [Message(role="user", content="Hi")]
        with pytest.raises(RuntimeError, match="Budget limit reached"):
            await client.generate(messages)

    @pytest.mark.asyncio
    async def test_generate_fallback(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(model="primary-model", fallback_models=["fallback-model"])

        mock_litellm = MagicMock()
        call_count = [0]

        async def mock_acompletion(**kwargs):
            call_count[0] += 1
            if kwargs["model"] == "primary-model":
                raise Exception("Primary failed")
            # Fallback succeeds
            resp = MagicMock()
            resp.choices = [MagicMock()]
            resp.choices[0].message.content = "Fallback response"
            resp.choices[0].message.tool_calls = None
            resp.choices[0].finish_reason = "stop"
            resp.usage = MagicMock()
            resp.usage.prompt_tokens = 5
            resp.usage.completion_tokens = 3
            resp.usage.total_tokens = 8
            return resp

        mock_litellm.acompletion = mock_acompletion
        mock_litellm.completion_cost = MagicMock(return_value=0.0)
        client._litellm = mock_litellm

        messages = [Message(role="user", content="Hi")]
        result = await client.generate(messages)

        assert result.content == "Fallback response"
        assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_generate_all_models_fail(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(model="model-a", fallback_models=["model-b"])

        mock_litellm = MagicMock()
        mock_litellm.acompletion = AsyncMock(side_effect=Exception("All fail"))
        mock_litellm.completion_cost = MagicMock(return_value=0.0)
        client._litellm = mock_litellm

        messages = [Message(role="user", content="Hi")]
        with pytest.raises(RuntimeError, match="All LiteLLM models failed"):
            await client.generate(messages)

    @pytest.mark.asyncio
    async def test_generate_with_tool_calls(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(model="gpt-4o")

        mock_litellm = MagicMock()
        mock_tc = MagicMock()
        mock_tc.id = "call_123"
        mock_tc.function.name = "read_file"
        mock_tc.function.arguments = '{"path": "test.txt"}'

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_response.choices[0].message.tool_calls = [mock_tc]
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 20
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 30

        mock_litellm.acompletion = AsyncMock(return_value=mock_response)
        mock_litellm.completion_cost = MagicMock(return_value=0.002)
        client._litellm = mock_litellm

        messages = [Message(role="user", content="Read test.txt")]
        result = await client.generate(messages)

        assert result.finish_reason == "tool_use"
        assert result.tool_calls is not None
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].function.name == "read_file"


class TestLiteLLMClientConvertMessages:
    """Test message conversion."""

    def test_convert_system_message(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hi"),
        ]
        system_msg, api_msgs = client._convert_messages(messages)
        assert system_msg == "You are helpful"
        assert len(api_msgs) == 1
        assert api_msgs[0]["role"] == "user"

    def test_convert_system_message_list_content(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        messages = [
            Message(
                role="system",
                content=[{"type": "text", "text": "Part 1"}, {"type": "text", "text": "Part 2"}],
            ),
        ]
        system_msg, api_msgs = client._convert_messages(messages)
        assert system_msg == "Part 1 Part 2"

    def test_convert_tool_message(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        messages = [
            Message(role="tool", content="result data", tool_call_id="call_123"),
        ]
        _, api_msgs = client._convert_messages(messages)
        assert api_msgs[0]["tool_call_id"] == "call_123"

    def test_convert_assistant_with_tool_calls(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        messages = [
            Message(
                role="assistant",
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        type="function",
                        function=FunctionCall(name="test", arguments={"a": 1}),
                    )
                ],
            ),
        ]
        _, api_msgs = client._convert_messages(messages)
        assert "tool_calls" in api_msgs[0]
        assert api_msgs[0]["tool_calls"][0]["id"] == "call_1"


class TestLiteLLMClientPrepareRequest:
    """Test request preparation."""

    def test_prepare_request_basic(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(model="gpt-4o", api_key="sk-test", api_base="https://api.test.com")
        messages = [Message(role="user", content="Hello")]
        request = client._prepare_request(messages)

        assert request["model"] == "gpt-4o"
        assert request["api_key"] == "sk-test"
        assert request["api_base"] == "https://api.test.com"

    def test_prepare_request_with_tools(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient()
        messages = [Message(role="user", content="Hello")]

        # Tool as dict
        tool_dict = {
            "type": "function",
            "function": {"name": "test", "parameters": {}},
        }
        request = client._prepare_request(messages, tools=[tool_dict])
        assert "tools" in request
        assert request["tools"][0] == tool_dict

    def test_prepare_request_no_api_key(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(api_key=None)
        messages = [Message(role="user", content="Hello")]
        request = client._prepare_request(messages)
        assert "api_key" not in request


class TestLiteLLMClientCostReport:
    """Test cost reporting."""

    def test_get_cost_report(self):
        from mini_agent.llm.litellm_client import LiteLLMClient

        client = LiteLLMClient(budget_limit=25.0)
        client.total_cost = 5.0
        client.call_count = 10
        client.call_costs = [{"model": "gpt-4o", "cost": 0.5}] * 10

        report = client.get_cost_report()
        assert report["total_cost_usd"] == 5.0
        assert report["call_count"] == 10
        assert report["budget_limit_usd"] == 25.0
        assert report["budget_remaining_usd"] == 20.0
        assert len(report["recent_calls"]) == 10


class TestSafeJsonHelpers:
    """Test _safe_json_dumps and _safe_json_loads."""

    def test_safe_json_dumps_string(self):
        from mini_agent.llm.litellm_client import _safe_json_dumps

        assert _safe_json_dumps("already a string") == "already a string"

    def test_safe_json_dumps_dict(self):
        from mini_agent.llm.litellm_client import _safe_json_dumps

        result = _safe_json_dumps({"key": "value"})
        assert json.loads(result) == {"key": "value"}

    def test_safe_json_dumps_non_serializable(self):
        from mini_agent.llm.litellm_client import _safe_json_dumps

        result = _safe_json_dumps(object())
        assert isinstance(result, str)

    def test_safe_json_loads_dict(self):
        from mini_agent.llm.litellm_client import _safe_json_loads

        assert _safe_json_loads({"key": "value"}) == {"key": "value"}

    def test_safe_json_loads_string(self):
        from mini_agent.llm.litellm_client import _safe_json_loads

        assert _safe_json_loads('{"key": "value"}') == {"key": "value"}

    def test_safe_json_loads_invalid(self):
        from mini_agent.llm.litellm_client import _safe_json_loads

        result = _safe_json_loads("not json")
        assert result == {"raw": "not json"}
