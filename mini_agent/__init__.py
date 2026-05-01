"""BPS Stat Agent - BPS Indonesia Statistical Data Agent with 62 MCP tools + Academic Research capabilities."""

from .agent import Agent
from .bps_models import BPSResolvedResource, BPSResourceType
from .llm import LLMClient
from .schema import FunctionCall, LLMProvider, LLMResponse, Message, ToolCall

__version__ = "1.0.0"


# Lazy import for research module (only available with research-core extras)
def get_research_orchestrator():
    """Get ResearchOrchestrator (requires research-core extras)."""
    try:
        from .research.orchestrator import ResearchOrchestrator

        return ResearchOrchestrator
    except ImportError as e:
        raise ImportError(
            "Research features require extra dependencies. Install with: pip install bps-stat-agent[research-all]"
        ) from e


__all__ = [
    "Agent",
    "BPSResolvedResource",
    "BPSResourceType",
    "LLMClient",
    "LLMProvider",
    "Message",
    "LLMResponse",
    "ToolCall",
    "FunctionCall",
    "get_research_orchestrator",
]
