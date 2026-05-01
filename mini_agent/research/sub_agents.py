"""Sub-agent dispatcher for specialized research tasks.

Manages sub-agent lifecycle and context passing. Each sub-agent is
configured with a role-specific system prompt, tool set, and model
preference. Sub-agents communicate results via files in the project
workspace, not via message passing.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from .exceptions import SubAgentError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt templates for each sub-agent role
# ---------------------------------------------------------------------------

SECTION_WRITER_PROMPT = """\
You are a specialized academic section writer for BPS (Badan Pusat Statistik) \
research papers. Your task is to write a single paper section in LaTeX format.

RULES:
- Write ONLY the assigned section — do not produce other sections.
- Use \\cite{{}} for all citations; reference the project bibliography.
- Follow the target journal's style guide strictly.
- Include cross-references to figures/tables using \\ref{{}}.
- Write in formal academic English appropriate for the target journal.
- Output the section to the designated file path.

CONTEXT:
{context}
"""

PEER_REVIEWER_PROMPT = """\
You are a simulated peer reviewer for an academic journal. Review the \
submitted manuscript section with the rigor of a real reviewer.

EVALUATE:
1. Clarity and logical flow of arguments
2. Methodological soundness
3. Proper use of citations and evidence
4. Statistical validity of claims
5. Adherence to journal style guidelines

OUTPUT FORMAT:
- Major issues (must fix before acceptance)
- Minor issues (suggestions for improvement)
- Strengths of the work
- Overall recommendation: accept / minor revision / major revision / reject

CONTEXT:
{context}
"""

STAT_VALIDATOR_PROMPT = """\
You are a statistical methods validator. Your job is to verify that all \
statistical analyses in the manuscript are correctly performed and reported.

CHECK:
1. Assumptions tested before each statistical test
2. Correct test selection for the data type and research question
3. Proper reporting of test statistics, degrees of freedom, p-values
4. Effect sizes reported where appropriate
5. Multiple comparison corrections applied when needed
6. Confidence intervals provided
7. Sample size adequacy

Flag any statistical errors or questionable practices. Reference the \
analysis scripts in the analysis/ directory.

CONTEXT:
{context}
"""

CITATION_VERIFIER_PROMPT = """\
You are a citation verification specialist. Verify every citation in the \
manuscript against the project bibliography and external databases.

VERIFY:
1. Every \\cite{{}} key exists in references.bib
2. Author names, year, title, journal match the actual publication
3. DOIs resolve correctly
4. No retracted papers are cited
5. Self-citation ratio is within acceptable bounds
6. Citation formatting matches the target journal style

Report unverified citations and suggest corrections.

CONTEXT:
{context}
"""

LIT_SYNTHESIZER_PROMPT = """\
You are a literature synthesis specialist for BPS economic research. \
Synthesize findings from multiple papers into a coherent narrative.

APPROACH:
1. Group papers by theme or methodology
2. Identify consensus findings and contradictions
3. Note methodological strengths and weaknesses across studies
4. Highlight gaps in the existing literature
5. Connect findings to the current research questions

Write the synthesis in academic prose suitable for a literature review section. \
Use \\cite{{}} for all references.

CONTEXT:
{context}
"""

DATA_EXPLORER_PROMPT = """\
You are a BPS data exploration specialist. Analyze the available datasets \
and produce descriptive statistics, visualizations, and data quality reports.

TASKS:
1. Load and inspect each dataset in the data/ directory
2. Compute descriptive statistics (mean, median, std, missing values)
3. Generate exploratory visualizations (distributions, correlations, trends)
4. Identify data quality issues (outliers, missing patterns, inconsistencies)
5. Save all outputs to the analysis/ directory

Use Python with pandas, numpy, matplotlib, and seaborn. Save figures as \
both PNG and PDF.

CONTEXT:
{context}
"""


# ---------------------------------------------------------------------------
# Configuration model
# ---------------------------------------------------------------------------


class SubAgentConfig(BaseModel):
    """Configuration for a sub-agent instance.

    Attributes:
        role: The sub-agent's role identifier.
        system_prompt: System prompt template (with ``{context}`` placeholder).
        tool_names: List of tool names this sub-agent may use.
        model_preference: Preferred LLM model for this agent's task type.
        max_steps: Maximum agentic loop iterations.
        temperature: Sampling temperature for this agent's outputs.
    """

    role: str
    system_prompt: str
    tool_names: list[str] = Field(default_factory=list)
    model_preference: str = "claude-sonnet-4-20250514"
    max_steps: int = 30
    temperature: float = 0.3


class SubAgentResult(BaseModel):
    """Result from a sub-agent execution.

    Attributes:
        role: The sub-agent role that produced this result.
        task: The task description that was dispatched.
        output: The text output from the sub-agent.
        success: Whether the sub-agent completed successfully.
        steps_taken: Number of agentic loop steps used.
        error: Error message if the sub-agent failed.
    """

    role: str
    task: str
    output: str = ""
    success: bool = True
    steps_taken: int = 0
    error: str | None = None


# ---------------------------------------------------------------------------
# Sub-agent dispatcher
# ---------------------------------------------------------------------------


class SubAgentDispatcher:
    """Dispatches and manages specialized sub-agents for research tasks.

    Each sub-agent is configured with a role-specific system prompt,
    tool set, and model preference. Sub-agents communicate results
    via files in the project workspace, not via message passing.

    Example::

        dispatcher = SubAgentDispatcher(tool_registry=registry)
        result = await dispatcher.dispatch(
            agent_type="section_writer",
            task="Write the methodology section",
            context={"outline": "...", "template": "elsevier"},
        )
    """

    AGENT_CONFIGS: dict[str, SubAgentConfig] = {
        "section_writer": SubAgentConfig(
            role="section_writer",
            system_prompt=SECTION_WRITER_PROMPT,
            tool_names=[
                "read_file",
                "write_file",
                "edit_file",
                "citation_manager",
                "latex_compile",
            ],
            model_preference="claude-sonnet-4-20250514",
            max_steps=25,
            temperature=0.4,
        ),
        "peer_reviewer": SubAgentConfig(
            role="peer_reviewer",
            system_prompt=PEER_REVIEWER_PROMPT,
            tool_names=[
                "read_file",
                "write_file",
                "check_statistical_validity",
                "verify_citations",
            ],
            model_preference="claude-sonnet-4-20250514",
            max_steps=20,
            temperature=0.2,
        ),
        "stat_validator": SubAgentConfig(
            role="stat_validator",
            system_prompt=STAT_VALIDATOR_PROMPT,
            tool_names=[
                "read_file",
                "write_file",
                "python_repl",
                "descriptive_stats",
                "hypothesis_test",
            ],
            model_preference="gpt-4o",
            max_steps=20,
            temperature=0.1,
        ),
        "citation_verifier": SubAgentConfig(
            role="citation_verifier",
            system_prompt=CITATION_VERIFIER_PROMPT,
            tool_names=[
                "read_file",
                "write_file",
                "verify_citations",
                "citation_manager",
            ],
            model_preference="gpt-4o-mini",
            max_steps=15,
            temperature=0.1,
        ),
        "lit_synthesizer": SubAgentConfig(
            role="lit_synthesizer",
            system_prompt=LIT_SYNTHESIZER_PROMPT,
            tool_names=[
                "read_file",
                "write_file",
                "literature_search",
                "citation_manager",
                "vector_search",
                "paper_qa",
            ],
            model_preference="claude-sonnet-4-20250514",
            max_steps=25,
            temperature=0.4,
        ),
        "data_explorer": SubAgentConfig(
            role="data_explorer",
            system_prompt=DATA_EXPLORER_PROMPT,
            tool_names=[
                "read_file",
                "write_file",
                "python_repl",
                "descriptive_stats",
                "create_visualization",
            ],
            model_preference="gpt-4o",
            max_steps=30,
            temperature=0.2,
        ),
    }

    def __init__(
        self,
        tool_registry: Any = None,
        llm_gateway: Any = None,
    ) -> None:
        """Initialize the sub-agent dispatcher.

        Args:
            tool_registry: A ToolRegistry instance for resolving tool names
                to Tool objects. If None, tools are resolved lazily.
            llm_gateway: An LLMGateway instance for model routing.
                If None, a default LLMClient is created per agent.
        """
        self._tool_registry = tool_registry
        self._llm_gateway = llm_gateway

    async def dispatch(
        self,
        agent_type: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Dispatch a sub-agent to perform a specialized task.

        The sub-agent runs within the project workspace and writes its
        outputs to files. The dispatcher collects the output after the
        agent completes.

        Args:
            agent_type: Key into ``AGENT_CONFIGS`` (e.g. ``"section_writer"``).
            task: Natural-language task description for the sub-agent.
            context: Additional context dict passed to the system prompt.

        Returns:
            The sub-agent's text output.

        Raises:
            SubAgentError: If the agent type is unknown or execution fails.
        """
        config = self.AGENT_CONFIGS.get(agent_type)
        if config is None:
            available = ", ".join(sorted(self.AGENT_CONFIGS.keys()))
            raise SubAgentError(
                f"Unknown agent type: '{agent_type}'. Available: {available}",
            )

        formatted_context = self._build_task_message(task, context)
        system_prompt = config.system_prompt.format(context=formatted_context)

        logger.info(
            "Dispatching sub-agent '%s' — task: %.80s...",
            agent_type,
            task,
        )

        try:
            agent = self._create_agent(config, system_prompt)
            agent.add_user_message(task)
            output = await agent.run()
            return output

        except ImportError as exc:
            logger.warning(
                "Sub-agent dispatch requires full agent stack: %s. Returning stub result.",
                exc,
            )
            return (
                f"[Sub-agent '{agent_type}' could not be dispatched: "
                f"missing dependency — {exc}]\n\n"
                f"Task was: {task}\n"
                f"Context: {formatted_context}"
            )
        except Exception as exc:
            raise SubAgentError(
                f"Sub-agent '{agent_type}' failed: {exc}",
            ) from exc

    def _create_agent(self, config: SubAgentConfig, system_prompt: str) -> Any:
        """Create a plain Agent instance from a SubAgentConfig.

        Args:
            config: The sub-agent configuration.
            system_prompt: The fully formatted system prompt.

        Returns:
            An Agent instance ready to run.
        """
        from ..agent import Agent
        from ..llm import LLMClient

        llm_client = LLMClient(
            model=config.model_preference,
            temperature=config.temperature,
        )

        # Resolve tools from registry
        tools = []
        if self._tool_registry is not None:
            for tool_name in config.tool_names:
                tool = self._tool_registry.get_tool(tool_name)
                if tool is not None:
                    tools.append(tool)

        agent = Agent(
            llm_client=llm_client,
            system_prompt=system_prompt,
            tools=tools,
            max_steps=config.max_steps,
        )

        return agent

    @staticmethod
    def _build_task_message(task: str, context: dict[str, Any] | None) -> str:
        """Build a formatted task message from task description and context.

        Args:
            task: The task description.
            context: Optional context dict with additional information.

        Returns:
            Formatted context string for system prompt injection.
        """
        if not context:
            return f"Task: {task}"

        lines: list[str] = [f"Task: {task}", ""]
        for key, value in context.items():
            if isinstance(value, list):
                items = "\n".join(f"  - {item}" for item in value)
                lines.append(f"**{key}:**\n{items}")
            elif isinstance(value, dict):
                lines.append(f"**{key}:** {json.dumps(value, indent=2)}")
            else:
                lines.append(f"**{key}:** {value}")

        return "\n".join(lines)
