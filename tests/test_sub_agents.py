"""Tests for mini_agent.research.sub_agents — sub-agent dispatcher."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from mini_agent.research.sub_agents import (
    SubAgentConfig,
    SubAgentDispatcher,
    SubAgentResult,
)


class TestSubAgentConfig:
    def test_default_values(self):
        cfg = SubAgentConfig(role="test", system_prompt="You are a test agent.")
        assert cfg.role == "test"
        assert cfg.max_steps == 30
        assert cfg.temperature == 0.3
        assert cfg.tool_names == []

    def test_custom_values(self):
        cfg = SubAgentConfig(
            role="writer",
            system_prompt="Write sections.",
            tool_names=["write_file", "read_file"],
            model_preference="gpt-4o",
            max_steps=15,
            temperature=0.4,
        )
        assert cfg.role == "writer"
        assert cfg.tool_names == ["write_file", "read_file"]
        assert cfg.model_preference == "gpt-4o"


class TestSubAgentResult:
    def test_default_values(self):
        result = SubAgentResult(role="test", task="do something")
        assert result.success is True
        assert result.output == ""
        assert result.error is None
        assert result.steps_taken == 0

    def test_failed_result(self):
        result = SubAgentResult(
            role="test",
            task="do something",
            success=False,
            error="Something went wrong",
        )
        assert result.success is False
        assert result.error == "Something went wrong"


class TestSubAgentDispatcher:
    def test_init(self):
        dispatcher = SubAgentDispatcher(tool_registry=MagicMock())
        assert dispatcher is not None

    def test_agent_configs_exist(self):
        dispatcher = SubAgentDispatcher(tool_registry=MagicMock())
        assert hasattr(dispatcher, "AGENT_CONFIGS") or hasattr(dispatcher, "_configs")

    def test_build_task_message(self):
        dispatcher = SubAgentDispatcher(tool_registry=MagicMock())
        msg = dispatcher._build_task_message(
            task="Write the introduction section",
            context={"topic": "fiscal decentralization"},
        )
        assert "introduction" in msg.lower()
        assert "fiscal" in msg.lower()

    def test_build_task_message_no_context(self):
        dispatcher = SubAgentDispatcher(tool_registry=MagicMock())
        msg = dispatcher._build_task_message(
            task="Analyze the data",
            context=None,
        )
        assert "Analyze" in msg

    async def test_dispatch_creates_agent(self):
        mock_registry = MagicMock()
        mock_registry.get_tools_for_phase.return_value = []
        mock_registry.get_all_tools.return_value = []
        mock_registry.get_tool_by_name.return_value = None

        dispatcher = SubAgentDispatcher(tool_registry=mock_registry)

        with patch.object(dispatcher, "_create_agent") as mock_create:
            mock_agent = AsyncMock()
            mock_agent.add_user_message = MagicMock()  # sync method
            mock_agent.run.return_value = "Section written successfully"
            mock_create.return_value = mock_agent

            result = await dispatcher.dispatch(
                agent_type="section_writer",
                task="Write the introduction",
                context={"topic": "test"},
            )
            assert mock_create.called or result is not None
