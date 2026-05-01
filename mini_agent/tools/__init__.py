"""Tools module — All available tools for the BPS Stat Agent."""

from .base import Tool, ToolResult
from .bash_tool import BashTool
from .file_tools import EditTool, ReadTool, WriteTool
from .note_tool import RecallNoteTool, SessionNoteTool

# Research tools — lazy imports to avoid requiring research-core extras
# These modules only depend on stdlib + pydantic (already in base deps)
try:
    from .research_tools import ProjectInitTool, ProjectStatusTool, SwitchPhaseTool
except ImportError:
    ProjectInitTool = None  # type: ignore[assignment,misc]
    ProjectStatusTool = None  # type: ignore[assignment,misc]
    SwitchPhaseTool = None  # type: ignore[assignment,misc]

# Statistics tools — require numpy/pandas/scipy (research-core extras)
# Lazy-loaded to preserve backward compatibility for base install
try:
    from .statistics_tools import (
        BayesianAnalysisTool,
        CausalInferenceTool,
        DescriptiveStatsTool,
        HypothesisTestTool,
        NonparametricTestTool,
        RegressionAnalysisTool,
        SurvivalAnalysisTool,
        TimeSeriesAnalysisTool,
    )
except ImportError:
    DescriptiveStatsTool = None  # type: ignore[assignment,misc]
    RegressionAnalysisTool = None  # type: ignore[assignment,misc]
    HypothesisTestTool = None  # type: ignore[assignment,misc]
    TimeSeriesAnalysisTool = None  # type: ignore[assignment,misc]
    BayesianAnalysisTool = None  # type: ignore[assignment,misc]
    CausalInferenceTool = None  # type: ignore[assignment,misc]
    SurvivalAnalysisTool = None  # type: ignore[assignment,misc]
    NonparametricTestTool = None  # type: ignore[assignment,misc]

# Citation tools — require requests (already in base deps)
try:
    from .citation_tools import (
        CitationManagerTool,
        LiteratureSearchTool,
        VerifyCitationsTool,
    )
except ImportError:
    LiteratureSearchTool = None  # type: ignore[assignment,misc]
    CitationManagerTool = None  # type: ignore[assignment,misc]
    VerifyCitationsTool = None  # type: ignore[assignment,misc]

__all__ = [
    # Base
    "Tool",
    "ToolResult",
    # File tools
    "ReadTool",
    "WriteTool",
    "EditTool",
    "BashTool",
    # Note tools
    "SessionNoteTool",
    "RecallNoteTool",
    # Research tools (available when research extras installed)
    "ProjectInitTool",
    "ProjectStatusTool",
    "SwitchPhaseTool",
    # Statistics tools (available when research-core extras installed)
    "DescriptiveStatsTool",
    "RegressionAnalysisTool",
    "HypothesisTestTool",
    "TimeSeriesAnalysisTool",
    "BayesianAnalysisTool",
    "CausalInferenceTool",
    "SurvivalAnalysisTool",
    "NonparametricTestTool",
    # Citation tools (available when research extras installed)
    "LiteratureSearchTool",
    "CitationManagerTool",
    "VerifyCitationsTool",
]
