"""Comprehensive tests for mini_agent/llm/openai_client.py and anthropic_client.py.

Tests the generate method with mocked API calls.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.llm import AnthropicClient, OpenAIClient
from mini_agent.retry import RetryConfig
from mini_agent.schema import Message, ToolCall, FunctionCall


# ===================================================================
# OpenAIClient Tests
# ===================================================================

class TestOpenAIClientInit:
    def test_init_default(self):
        client = OpenAIClient(api_key="test-key")
        assert client.model == "MiniMax-M2.5"
        assert client.api_key == "test-key"

    def test_init_custom(self):
        client = OpenAIClient(
            api_key="key",
            api_base="https://custom.api.com/v1",
            model="gpt-4",
            retry_config=RetryConfig(enabled=True, max_retries=3),
        )
        assert client.model == "gpt-4"
        assert client.api_base == "https://custom.api.com/v1"


class TestOpenAIClientConvertTools:
    def test_convert_dict_tools_openai_format(self):
        client = OpenAIClient(api_key="test")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search for data",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]
        result = client._convert_tools(tools)
        assert len(result) == 1
        assert result[0]["type"] == "function"

    def test_convert_dict_tools_anthropic_format(self):
        client = OpenAIClient(api_key="test")
        tools = [
            {
                "name": "search",
                "description": "Search for data",
                "input_schema": {"type": "object", "properties": {}},
            }
        ]
        result = client._convert_tools(tools)
        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "search"

    def test_convert_tool_objects(self):
        client = OpenAIClient(api_key="test")
        mock_tool = MagicMock()
        mock_tool.to_openai_schema.return_value = {
            "type": "function",
            "function": {"name": "test", "description": "Test", "parameters": {}},
        }
        result = client._convert_tools([mock_tool])
        assert len(result) == 1

    def test_convert_unsupported_tool_type(self):
        client = OpenAIClient(api_key="test")
        with pytest.raises(TypeError, match="Unsupported tool type"):
            client._convert_tools([42])


class TestOpenAIClientConvertMessages:
    def test_convert_simple_messages(self):
        client = OpenAIClient(api_key="test")
        messages = [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Hello"),
        ]
        system, api_msgs = client._convert_messages(messages)
        # OpenAI format includes system in messages
        assert isinstance(api_msgs, list)

    def test_convert_with_tool_calls(self):
        client = OpenAIClient(api_key="test")
        messages = [
            Message(role="user", content="Search for inflation"),
            Message(
                role="assistant",
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        type="function",
                        function=FunctionCall(name="search", arguments={"query": "inflation"}),
                    )
                ],
            ),
            Message(role="tool", content='{"results": []}', tool_call_id="call_1"),
        ]
        system, api_msgs = client._convert_messages(messages)
        assert isinstance(api_msgs, list)


class TestOpenAIClientGenerate:
    @pytest.mark.asyncio
    async def test_generate_simple(self):
        client = OpenAIClient(api_key="test")

        # Mock the API response
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello! How can I help?"
        mock_choice.message.tool_calls = None
        mock_choice.finish_reason = "stop"
        # Mock reasoning content
        mock_choice.message.reasoning_content = None

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        with patch.object(client, "_make_api_request", new_callable=AsyncMock, return_value=mock_response):
            messages = [
                Message(role="system", content="You are helpful."),
                Message(role="user", content="Hello"),
            ]
            response = await client.generate(messages=messages)
            assert response.content == "Hello! How can I help?"
            assert response.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_with_tool_calls(self):
        client = OpenAIClient(api_key="test")

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "search"
        mock_tool_call.function.arguments = '{"query": "inflation"}'

        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_choice.message.tool_calls = [mock_tool_call]
        mock_choice.message.reasoning_content = "Let me search for that."
        mock_choice.finish_reason = "tool_calls"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 20
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 30

        with patch.object(client, "_make_api_request", new_callable=AsyncMock, return_value=mock_response):
            messages = [Message(role="user", content="Search for inflation data")]
            response = await client.generate(messages=messages)
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].function.name == "search"

    @pytest.mark.asyncio
    async def test_generate_with_reasoning(self):
        client = OpenAIClient(api_key="test")

        mock_detail = MagicMock()
        mock_detail.text = "Let me think about this..."

        mock_choice = MagicMock()
        mock_choice.message.content = "The answer is 42."
        mock_choice.message.tool_calls = None
        mock_choice.message.reasoning_details = [mock_detail]
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15
        mock_response.usage.total_tokens = 25

        with patch.object(client, "_make_api_request", new_callable=AsyncMock, return_value=mock_response):
            messages = [Message(role="user", content="What is the meaning of life?")]
            response = await client.generate(messages=messages)
            assert response.content == "The answer is 42."
            assert response.thinking == "Let me think about this..."


# ===================================================================
# AnthropicClient Tests
# ===================================================================

class TestAnthropicClientInit:
    def test_init_default(self):
        client = AnthropicClient(api_key="test-key")
        assert client.model == "MiniMax-M2.5"
        assert client.api_key == "test-key"

    def test_init_custom(self):
        client = AnthropicClient(
            api_key="key",
            api_base="https://custom.api.com/anthropic",
            model="claude-3-opus",
            retry_config=RetryConfig(enabled=True, max_retries=5),
        )
        assert client.model == "claude-3-opus"


class TestAnthropicClientConvertTools:
    def test_convert_dict_tools(self):
        client = AnthropicClient(api_key="test")
        tools = [
            {
                "name": "search",
                "description": "Search for data",
                "input_schema": {"type": "object", "properties": {}},
            }
        ]
        result = client._convert_tools(tools)
        assert len(result) == 1
        assert result[0]["name"] == "search"

    def test_convert_tool_objects(self):
        client = AnthropicClient(api_key="test")
        mock_tool = MagicMock()
        mock_tool.to_schema.return_value = {
            "name": "test",
            "description": "Test tool",
            "input_schema": {"type": "object"},
        }
        result = client._convert_tools([mock_tool])
        assert len(result) == 1

    def test_convert_unsupported_tool_type(self):
        client = AnthropicClient(api_key="test")
        with pytest.raises(TypeError, match="Unsupported tool type"):
            client._convert_tools([42])


class TestAnthropicClientConvertMessages:
    def test_convert_simple_messages(self):
        client = AnthropicClient(api_key="test")
        messages = [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Hello"),
        ]
        system, api_msgs = client._convert_messages(messages)
        assert system == "You are helpful."
        assert len(api_msgs) == 1
        assert api_msgs[0]["role"] == "user"

    def test_convert_with_tool_results(self):
        client = AnthropicClient(api_key="test")
        messages = [
            Message(role="user", content="Search"),
            Message(
                role="assistant",
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        type="function",
                        function=FunctionCall(name="search", arguments={"q": "test"}),
                    )
                ],
            ),
            Message(role="tool", content='{"result": "found"}', tool_call_id="call_1"),
        ]
        system, api_msgs = client._convert_messages(messages)
        assert isinstance(api_msgs, list)


class TestAnthropicClientGenerate:
    @pytest.mark.asyncio
    async def test_generate_simple(self):
        client = AnthropicClient(api_key="test")

        # Mock Anthropic response
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Hello! I can help with that."

        mock_response = MagicMock()
        mock_response.content = [mock_text_block]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 8

        with patch.object(client, "_make_api_request", new_callable=AsyncMock, return_value=mock_response):
            messages = [
                Message(role="system", content="You are helpful."),
                Message(role="user", content="Hello"),
            ]
            response = await client.generate(messages=messages)
            assert response.content == "Hello! I can help with that."
            assert response.finish_reason == "end_turn"

    @pytest.mark.asyncio
    async def test_generate_with_tool_use(self):
        client = AnthropicClient(api_key="test")

        mock_tool_block = MagicMock()
        mock_tool_block.type = "tool_use"
        mock_tool_block.id = "toolu_123"
        mock_tool_block.name = "search"
        mock_tool_block.input = {"query": "inflation"}

        mock_response = MagicMock()
        mock_response.content = [mock_tool_block]
        mock_response.stop_reason = "tool_use"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 20
        mock_response.usage.output_tokens = 15

        with patch.object(client, "_make_api_request", new_callable=AsyncMock, return_value=mock_response):
            messages = [Message(role="user", content="Search for inflation")]
            response = await client.generate(messages=messages)
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].function.name == "search"

    @pytest.mark.asyncio
    async def test_generate_with_thinking(self):
        client = AnthropicClient(api_key="test")

        mock_thinking_block = MagicMock()
        mock_thinking_block.type = "thinking"
        mock_thinking_block.thinking = "Let me analyze this..."

        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Based on my analysis..."

        mock_response = MagicMock()
        mock_response.content = [mock_thinking_block, mock_text_block]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 20

        with patch.object(client, "_make_api_request", new_callable=AsyncMock, return_value=mock_response):
            messages = [Message(role="user", content="Analyze this data")]
            response = await client.generate(messages=messages)
            assert response.content == "Based on my analysis..."
            assert response.thinking == "Let me analyze this..."
