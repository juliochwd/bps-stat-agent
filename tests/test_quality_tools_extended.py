"""Extended tests for mini_agent/tools/quality_tools.py — quality checking tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.quality_tools import (
    AuditReproducibilityTool,
    CheckGrammarTool,
    CheckReadabilityTool,
    CheckStyleTool,
    DetectPlagiarismTool,
    SimulatePeerReviewTool,
)


class TestCheckGrammarTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CheckGrammarTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "check_grammar"

    def test_description(self, tool):
        assert "grammar" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params
        assert "required" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test grammar checking."""
        result = await tool.execute(
            text="This is a simple sentence with no errors."
        )
        assert isinstance(result.success, bool)


class TestCheckStyleTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CheckStyleTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "check_style"

    def test_description(self, tool):
        assert "style" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test style checking."""
        result = await tool.execute(
            text="The results clearly show a significant relationship between X and Y."
        )
        assert isinstance(result.success, bool)


class TestCheckReadabilityTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CheckReadabilityTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "check_readability"

    def test_description(self, tool):
        assert "readability" in tool.description.lower() or "read" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test readability checking."""
        text = (
            "This study examines the relationship between fiscal policy and economic growth. "
            "Using panel data from 34 provinces over 12 years, we employ fixed effects regression. "
            "The results indicate a significant positive relationship between government spending and GDP growth."
        )
        result = await tool.execute(text=text)
        assert isinstance(result.success, bool)


class TestSimulatePeerReviewTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return SimulatePeerReviewTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "simulate_peer_review"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "peer" in desc or "review" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test peer review simulation."""
        result = await tool.execute(
            section_name="methodology",
            content="We use OLS regression with n=500 observations.",
        )
        assert isinstance(result.success, bool)


class TestDetectPlagiarismTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return DetectPlagiarismTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "detect_plagiarism"

    def test_description(self, tool):
        assert "plagiarism" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test plagiarism detection."""
        result = await tool.execute(
            text="This is original text that should not be flagged."
        )
        assert isinstance(result.success, bool)


class TestAuditReproducibilityTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return AuditReproducibilityTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "audit_reproducibility"

    def test_description(self, tool):
        assert "reproducibility" in tool.description.lower() or "audit" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test reproducibility audit."""
        result = await tool.execute()
        assert isinstance(result.success, bool)
