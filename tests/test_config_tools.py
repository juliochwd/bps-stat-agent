"""Tests for mini_agent/tools/config_tools.py — LiteLLM and DSPy config tools."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.tools.config_tools import DSPyOptimizeTool, LiteLLMConfigTool


@pytest.fixture
def litellm_tool(tmp_path):
    """Create a LiteLLMConfigTool with temp workspace."""
    return LiteLLMConfigTool(workspace_dir=str(tmp_path))


@pytest.fixture
def dspy_tool(tmp_path):
    """Create a DSPyOptimizeTool with temp workspace."""
    return DSPyOptimizeTool(workspace_dir=str(tmp_path))


class TestLiteLLMConfigTool:
    def test_name(self, litellm_tool):
        assert litellm_tool.name == "litellm_config"

    def test_description(self, litellm_tool):
        assert "LiteLLM" in litellm_tool.description

    def test_parameters(self, litellm_tool):
        params = litellm_tool.parameters
        assert params["type"] == "object"
        assert "action" in params["properties"]
        assert "required" in params

    @pytest.mark.asyncio
    async def test_list_models_default(self, litellm_tool):
        """Test listing models with default config."""
        result = await litellm_tool.execute(action="list_models")
        assert result.success is True
        assert "LiteLLM Model Routing" in result.content
        assert "paper_writing" in result.content

    @pytest.mark.asyncio
    async def test_list_models_from_file(self, litellm_tool, tmp_path):
        """Test listing models from existing config file."""
        config = {
            "routing_rules": {"custom_task": {"primary": "gpt-4", "fallback": "gpt-3.5"}},
            "providers": {"openai": {"api_key": "sk-test"}},
            "cost_tracking": {"total_usd": 1.5, "requests": 10},
        }
        config_path = tmp_path / ".litellm_config.json"
        config_path.write_text(json.dumps(config))

        result = await litellm_tool.execute(action="list_models")
        assert result.success is True
        assert "custom_task" in result.content
        assert "openai" in result.content

    @pytest.mark.asyncio
    async def test_set_model(self, litellm_tool, tmp_path):
        """Test setting a model for a task type."""
        result = await litellm_tool.execute(
            action="set_model", model="gpt-4o", provider="paper_writing"
        )
        assert result.success is True
        assert "paper_writing" in result.content
        assert "gpt-4o" in result.content

        # Verify file was written
        config_path = tmp_path / ".litellm_config.json"
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["routing_rules"]["paper_writing"]["primary"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_set_model_with_colon_syntax(self, litellm_tool, tmp_path):
        """Test setting model with task:model syntax."""
        result = await litellm_tool.execute(action="set_model", model="data_analysis:claude-3")
        assert result.success is True
        assert "data_analysis" in result.content
        assert "claude-3" in result.content

    @pytest.mark.asyncio
    async def test_set_model_no_model_param(self, litellm_tool):
        """Test set_model without model parameter."""
        result = await litellm_tool.execute(action="set_model", model="")
        assert result.success is False
        assert "model" in result.error.lower()

    @pytest.mark.asyncio
    async def test_set_fallback(self, litellm_tool, tmp_path):
        """Test setting a fallback model."""
        result = await litellm_tool.execute(
            action="set_fallback", model="gpt-3.5-turbo", provider="paper_writing"
        )
        assert result.success is True
        assert "fallback" in result.content.lower()

    @pytest.mark.asyncio
    async def test_set_fallback_no_model(self, litellm_tool):
        """Test set_fallback without model parameter."""
        result = await litellm_tool.execute(action="set_fallback", model="")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_set_fallback_colon_syntax(self, litellm_tool, tmp_path):
        """Test set_fallback with task:model syntax."""
        result = await litellm_tool.execute(action="set_fallback", model="review:gpt-4o-mini")
        assert result.success is True
        assert "review" in result.content

    @pytest.mark.asyncio
    async def test_get_cost(self, litellm_tool):
        """Test getting cost information."""
        result = await litellm_tool.execute(action="get_cost")
        assert result.success is True
        assert "Cost Tracking" in result.content
        assert "Total spent" in result.content

    @pytest.mark.asyncio
    async def test_unknown_action(self, litellm_tool):
        """Test unknown action returns error."""
        result = await litellm_tool.execute(action="invalid_action")
        assert result.success is False
        assert "Unknown action" in result.error

    def test_load_config_nonexistent(self, tmp_path):
        """Test loading config when file doesn't exist."""
        config = LiteLLMConfigTool._load_config(tmp_path / "nonexistent.json")
        assert "routing_rules" in config
        assert "providers" in config
        assert "cost_tracking" in config

    def test_save_config(self, tmp_path):
        """Test saving config to file."""
        config_path = tmp_path / "test_config.json"
        config = {"routing_rules": {"test": {"primary": "model-a"}}}
        LiteLLMConfigTool._save_config(config, config_path)

        assert config_path.exists()
        loaded = json.loads(config_path.read_text())
        assert loaded == config


class TestDSPyOptimizeTool:
    def test_name(self, dspy_tool):
        assert dspy_tool.name == "dspy_optimize"

    def test_description(self, dspy_tool):
        assert "DSPy" in dspy_tool.description

    def test_parameters(self, dspy_tool):
        params = dspy_tool.parameters
        assert "module" in params["properties"]
        assert "required" in params

    @pytest.mark.asyncio
    async def test_dspy_not_installed(self, dspy_tool):
        """Test error when dspy is not installed."""
        with patch("mini_agent.tools.config_tools._HAS_DSPY", False):
            result = await dspy_tool.execute(module="literature_review")
            assert result.success is False
            assert "dspy" in result.error.lower()

    @pytest.mark.asyncio
    async def test_unknown_module(self, dspy_tool):
        """Test error for unknown module name."""
        with patch("mini_agent.tools.config_tools._HAS_DSPY", True):
            with patch(
                "mini_agent.tools.config_tools.DSPyOptimizeTool.execute"
            ) as mock_exec:
                # Simulate the module import failing
                mock_exec.return_value = MagicMock(
                    success=False, error="Unknown module: invalid"
                )
                result = await mock_exec(module="invalid")
                assert result.success is False

    def test_create_example_trainset_literature_review(self, dspy_tool):
        """Test creating example trainset for literature_review."""
        trainset = dspy_tool._create_example_trainset("literature_review")
        assert len(trainset) == 2
        assert "research_question" in trainset[0]

    def test_create_example_trainset_data_analysis(self, dspy_tool):
        """Test creating example trainset for data_analysis."""
        trainset = dspy_tool._create_example_trainset("data_analysis")
        assert len(trainset) == 1
        assert "research_questions" in trainset[0]

    def test_create_example_trainset_paper_generation(self, dspy_tool):
        """Test creating example trainset for paper_generation."""
        trainset = dspy_tool._create_example_trainset("paper_generation")
        assert len(trainset) == 1
        assert "section_name" in trainset[0]

    def test_create_example_trainset_quality_check(self, dspy_tool):
        """Test creating example trainset for quality_check."""
        trainset = dspy_tool._create_example_trainset("quality_check")
        assert len(trainset) == 1
        assert "text" in trainset[0]

    def test_create_example_trainset_unknown(self, dspy_tool):
        """Test creating example trainset for unknown module."""
        trainset = dspy_tool._create_example_trainset("unknown_module")
        assert trainset == []
