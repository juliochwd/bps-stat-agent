"""Extended tests for mini_agent/tools/citation_tools.py — citation management tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.citation_tools import *


# Discover available classes
import mini_agent.tools.citation_tools as ct_module


class TestCitationToolsModule:
    """Test citation tools module structure."""

    def test_module_importable(self):
        assert ct_module is not None

    def test_has_tool_classes(self):
        """Module should have Tool subclasses."""
        from mini_agent.tools.base import Tool
        tool_classes = [
            obj for name, obj in vars(ct_module).items()
            if isinstance(obj, type) and issubclass(obj, Tool) and obj is not Tool
        ]
        assert len(tool_classes) >= 1

    def test_tool_properties(self):
        """All tools should have name, description, parameters."""
        from mini_agent.tools.base import Tool
        tool_classes = [
            obj for name, obj in vars(ct_module).items()
            if isinstance(obj, type) and issubclass(obj, Tool) and obj is not Tool
        ]
        for cls in tool_classes:
            try:
                instance = cls(workspace_dir="/tmp")
            except TypeError:
                instance = cls()
            assert isinstance(instance.name, str)
            assert isinstance(instance.description, str)
            assert isinstance(instance.parameters, dict)
