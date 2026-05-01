# IMPLEMENTATION GUIDE: BPS Stat Agent → Academic Research Agent

> **Document Version**: 1.0  
> **Last Updated**: 2025-01-30  
> **Target Audience**: Developers implementing the Academic Research Agent extension  
> **Prerequisite Reading**: ARCHITECTURE.md, RESEARCH-WORKFLOW.md

---

## Table of Contents

1. [Overview](#section-1-overview)
2. [New Package Structure](#section-2-new-package-structure)
3. [ResearchOrchestrator Implementation](#section-3-researchorchestrator-implementation)
4. [PhaseManager Implementation](#section-4-phasemanager-implementation)
5. [ProjectState Implementation](#section-5-projectstate-implementation)
6. [LiteLLM Integration](#section-6-litellm-integration)
7. [DSPy Integration](#section-7-dspy-integration)
8. [New Tool Implementations](#section-8-new-tool-implementations)
9. [CLI Extension](#section-9-cli-extension)
10. [Configuration Extension](#section-10-configuration-extension)
11. [Step-by-Step Implementation Order](#section-11-step-by-step-implementation-order)

---

## Section 1: Overview

### What Changes, What Stays the Same

| Component | Status | Details |
|-----------|--------|---------|
| `mini_agent/agent.py` (567 lines) | **UNCHANGED** | Core `Agent` class remains the base class — `ResearchOrchestrator` inherits from it |
| `mini_agent/cli.py` (881 lines) | **EXTENDED** | Add `research` subcommand via new `subparsers.add_parser()` — no existing code modified |
| `mini_agent/config.py` (279 lines) | **EXTENDED** | Add optional `research:` section to `Config` — backward compatible, defaults to `None` |
| `mini_agent/tools/base.py` (55 lines) | **UNCHANGED** | `Tool` ABC and `ToolResult` stay identical — all new tools implement this interface |
| `mini_agent/tools/*.py` | **UNCHANGED** | bash_tool, file_tools, note_tool, skill_tool, mcp_loader all preserved |
| `mini_agent/llm/llm_wrapper.py` (132 lines) | **EXTENDED** | Add `LITELLM` provider option — existing Anthropic/OpenAI paths untouched |
| `mini_agent/llm/base.py` (84 lines) | **UNCHANGED** | `LLMClientBase` ABC stays identical |
| `mini_agent/schema/schema.py` (55 lines) | **EXTENDED** | Add `LITELLM = "litellm"` to `LLMProvider` enum |
| `mini_agent/bps_*.py` (8 files) | **UNCHANGED** | All BPS functionality fully preserved |
| `mini_agent/skills/` | **UNCHANGED** | Skills system preserved |
| `mini_agent/research/` | **NEW** | Entire research package — new directory tree |

### Backward Compatibility Guarantee

```
RULE 1: Running `bpsagent` (without subcommand) MUST behave identically to today.
RULE 2: All existing tests MUST pass without modification.
RULE 3: The `bpsagent research` subcommand is the ONLY entry point to new functionality.
RULE 4: LiteLLM wrapper MUST expose the same LLMClient.generate() signature.
RULE 5: No existing import paths change — `from mini_agent.agent import Agent` still works.
RULE 6: config.yaml without a `research:` section loads and runs exactly as before.
```

### Architecture Principle

The existing `Agent` class (in `agent.py`) is a **general-purpose agent loop** with:
- Message history management (`self.messages: list[Message]`)
- Tool registry (`self.tools: dict[str, Tool]`)
- LLM interaction (`self.llm.generate(messages, tools)`)
- Token management and summarization (`_summarize_messages()`)
- Cancellation support (`cancel_event`)

The `ResearchOrchestrator` **extends** it via inheritance to add:
- Phase-aware tool loading (different tools per research phase)
- Sub-agent delegation (specialist agents for statistics, writing, etc.)
- Project state persistence (YAML file survives across sessions)
- Cross-session continuity (resume where you left off)
- Quality gates (must pass criteria before advancing phases)

```
Agent (existing, agent.py line 29)
  └── ResearchOrchestrator (new, extends Agent)
        ├── PhaseManager       — controls which tools are active per phase
        ├── ProjectState       — Pydantic model persisted as project.yaml
        ├── ResearchWorkspace  — directory structure management
        ├── SessionResumeManager — cross-session continuity
        ├── QualityGateEvaluator — phase transition gates
        └── Specialist sub-agents (each is a plain Agent instance)
```

### Key Design Decisions

1. **Inheritance over composition** for `ResearchOrchestrator(Agent)` — this lets us reuse the entire agent loop (`run()`, `_summarize_messages()`, cancellation) without reimplementing it.

2. **Tool swapping via `self.tools` dict** — the parent `Agent.__init__()` stores tools as `self.tools = {tool.name: tool for tool in tools}` (agent.py line 42). We swap this dict when changing phases.

3. **System prompt replacement via `self.messages[0]`** — the parent stores the system prompt as `self.messages[0]` (agent.py line 60). We replace it when changing phases.

4. **Sub-agents are plain `Agent` instances** — no special class needed. Each specialist gets a role-specific prompt and tool subset.

---

## Section 2: New Package Structure

### Complete File Tree (new files only)

```
mini_agent/
├── (ALL EXISTING FILES — DO NOT MODIFY unless specified in this guide)
│
├── research/                           # NEW: Research agent package
│   ├── __init__.py                     # Package exports
│   ├── orchestrator.py                 # ResearchOrchestrator(Agent) — ~350 lines
│   ├── phase_manager.py               # PhaseManager — tool loading per phase — ~300 lines
│   ├── project_state.py               # ProjectState — Pydantic model + YAML — ~250 lines
│   ├── workspace.py                   # Workspace scaffolding — ~120 lines
│   ├── session_resume.py              # Cross-session continuity — ~200 lines
│   ├── quality_gate.py                # Quality gate evaluation — ~150 lines
│   │
│   ├── prompts/                        # Phase-specific system prompts
│   │   ├── __init__.py
│   │   ├── orchestrator_system.md      # Main orchestrator system prompt
│   │   ├── plan_phase.md              # Planning phase prompt
│   │   ├── collect_phase.md           # Collection phase prompt
│   │   ├── analyze_phase.md           # Analysis phase prompt
│   │   ├── write_phase.md             # Writing phase prompt
│   │   └── review_phase.md            # Review phase prompt
│   │
│   ├── tools/                          # Research-specific tools
│   │   ├── __init__.py
│   │   ├── python_repl.py            # PythonREPLTool (E2B/Docker/local)
│   │   ├── literature_search.py       # LiteratureSearchTool (Semantic Scholar + OpenAlex)
│   │   ├── citation_manager.py        # CitationManagerTool (BibTeX management)
│   │   ├── statistical_analysis.py    # StatisticalAnalysisTool
│   │   ├── visualization.py           # VisualizationTool
│   │   ├── paper_writer.py            # PaperWriterTool (LaTeX/Markdown)
│   │   ├── quality_gate_tool.py       # QualityGateTool (agent-callable)
│   │   └── data_loader.py            # DataLoaderTool (CSV/Excel/API)
│   │
│   ├── dspy_modules/                   # DSPy optimization modules
│   │   ├── __init__.py
│   │   ├── signatures.py             # DSPy Signature definitions
│   │   ├── research_question.py       # RQ generation module
│   │   ├── literature_synthesis.py    # Literature synthesis module
│   │   ├── methodology_design.py      # Methodology design module
│   │   ├── results_interpretation.py  # Results interpretation module
│   │   └── optimizer.py              # DSPy optimization workflow (offline)
│   │
│   └── config/                         # Research-specific configuration
│       ├── __init__.py
│       ├── research_config.py         # ResearchConfig Pydantic model
│       └── defaults.yaml              # Default research configuration
│
├── llm/
│   ├── (existing files — UNCHANGED)
│   └── litellm_client.py              # NEW: LiteLLM-based client
│
└── config/
    └── research_mcp.json              # NEW: MCP config for research tool servers
```

### `mini_agent/research/__init__.py`

```python
"""Academic Research Agent — extends Mini-Agent with research workflow capabilities."""

from .orchestrator import ResearchOrchestrator
from .phase_manager import PhaseManager, ResearchPhase
from .project_state import ProjectState
from .workspace import ResearchWorkspace

__all__ = [
    "ResearchOrchestrator",
    "PhaseManager",
    "ResearchPhase",
    "ProjectState",
    "ResearchWorkspace",
]
```

---

## Section 3: ResearchOrchestrator Implementation

### File: `mini_agent/research/orchestrator.py`

This is the central class. It extends `Agent` (from `agent.py` line 29) by overriding `__init__` and `run()`, and adding phase management methods.

**Key integration points with existing code:**
- Calls `super().__init__()` which sets up `self.llm`, `self.tools`, `self.messages`, `self.workspace_dir` (agent.py lines 32-63)
- Calls `super().run()` which executes the full agent loop (agent.py lines 312-563)
- Swaps `self.tools` dict to change available tools per phase
- Replaces `self.messages[0]` to change the system prompt per phase

```python
"""Research Orchestrator — extends Agent with phase management and sub-agent delegation."""

import asyncio
from pathlib import Path
from typing import Any

from ..agent import Agent
from ..llm import LLMClient
from ..schema import Message
from ..tools.base import Tool
from .phase_manager import PhaseManager, ResearchPhase
from .project_state import ProjectState
from .quality_gate import QualityGateEvaluator
from .session_resume import SessionResumeManager
from .workspace import ResearchWorkspace


class ResearchOrchestrator(Agent):
    """Extends Agent with research phase management and sub-agent delegation.

    The orchestrator manages the overall research workflow:
    1. Maintains project state across sessions (project.yaml)
    2. Loads phase-appropriate tools (different tools per phase)
    3. Delegates specialized tasks to sub-agents (statistician, writer, etc.)
    4. Enforces quality gates between phases
    5. Handles cross-session continuity (resume where you left off)

    Inheritance from Agent gives us:
    - The full agent loop (run method with tool execution)
    - Token management and message summarization
    - Cancellation support
    - Logging and metrics
    """

    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        tools: list[Tool],
        project_dir: str,
        max_steps: int = 100,
        token_limit: int = 120000,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the Research Orchestrator.

        Args:
            llm_client: LLM client for generation (same interface as existing)
            system_prompt: Base system prompt (will be augmented with phase context)
            tools: Base tools available in ALL phases (file ops, bash, notes)
            project_dir: Root directory for the research project
            max_steps: Maximum agent steps per session (higher than default 50)
            token_limit: Token limit before summarization (higher for research)
            config: Research-specific configuration dict
        """
        # Step 1: Initialize workspace (creates directory structure)
        self.workspace = ResearchWorkspace(project_dir)
        self.workspace.ensure_structure()

        # Step 2: Load or create project state from project.yaml
        self.project_state = ProjectState.load_or_create(
            self.workspace.state_file
        )

        # Step 3: Initialize phase manager (controls tool availability per phase)
        self.phase_manager = PhaseManager(
            base_tools=tools,
            workspace=self.workspace,
            config=config or {},
        )

        # Step 4: Quality gate evaluator
        self.quality_gate = QualityGateEvaluator(
            llm_client=llm_client,
            project_state=self.project_state,
        )

        # Step 5: Session resume manager
        self.session_resume = SessionResumeManager(
            workspace=self.workspace,
            project_state=self.project_state,
        )

        # Step 6: Get phase-appropriate tools for current phase
        current_phase = self.project_state.phase.current
        phase_tools = self.phase_manager.get_active_tools(current_phase)

        # Step 7: Augment system prompt with phase context
        augmented_prompt = self._build_phase_prompt(system_prompt, current_phase)

        # Step 8: Initialize parent Agent with phase-appropriate tools
        # This calls Agent.__init__() which sets up:
        #   self.llm, self.tools, self.messages, self.workspace_dir
        #   self.max_steps, self.token_limit, self.logger
        super().__init__(
            llm_client=llm_client,
            system_prompt=augmented_prompt,
            tools=phase_tools,
            max_steps=max_steps,
            workspace_dir=project_dir,
            token_limit=token_limit,
        )

        # Store references for sub-agent creation and phase transitions
        self._config = config or {}
        self._llm_client = llm_client
        self._base_system_prompt = system_prompt

        # Sub-agent registry (created on demand)
        self._specialist_agents: dict[str, Agent] = {}

    # ─── Phase Prompt Building ───────────────────────────────────────────

    def _build_phase_prompt(self, base_prompt: str, phase: str) -> str:
        """Build phase-augmented system prompt.

        Combines the base system prompt with:
        - Current phase context and objectives
        - Project state summary
        - Session continuity context (if resuming)
        """
        phase_prompt = self.phase_manager.get_phase_prompt(phase)
        state_summary = self.project_state.get_summary()
        resume_context = self.session_resume.get_resume_context()

        return f"""{base_prompt}

## Current Research Phase: {phase.upper()}

{phase_prompt}

## Project State Summary
{state_summary}

## Session Context
{resume_context}

## Phase Transition Rules
- You may ONLY transition to the next phase after passing the quality gate.
- Call the `quality_gate` tool to evaluate readiness for the next phase.
- If the gate fails, address the feedback before retrying.
- Available phase sequence: plan -> collect -> analyze -> write -> review
- Backward transitions are allowed (e.g., analyze -> collect if more data needed).
"""

    # ─── Phase Transitions ───────────────────────────────────────────────

    async def enter_phase(self, phase: ResearchPhase) -> bool:
        """Transition to a new research phase.

        This method:
        1. Validates the transition is allowed
        2. Runs the quality gate for the current phase
        3. Updates project state
        4. Reloads tools for the new phase
        5. Updates the system prompt

        Args:
            phase: Target phase to enter

        Returns:
            True if transition successful, False if quality gate failed
        """
        current = self.project_state.phase.current

        # Validate transition is allowed
        if not self.phase_manager.can_transition(current, phase.value):
            return False

        # Run quality gate for current phase
        gate_result = await self.quality_gate.evaluate(current)
        if not gate_result.passed:
            self.project_state.phase.gate_feedback = gate_result.feedback
            self.project_state.save()
            return False

        # Record transition in project state
        self.project_state.phase.current = phase.value
        self.project_state.phase.history.append({
            "from": current,
            "to": phase.value,
            "timestamp": self.project_state.get_timestamp(),
        })
        self.project_state.phase.started_at[phase.value] = (
            self.project_state.get_timestamp()
        )
        self.project_state.quality.gates_passed.append(current)
        self.project_state.save()

        # Reload tools for new phase
        new_tools = self.phase_manager.get_active_tools(phase.value)
        self.tools = {tool.name: tool for tool in new_tools}

        # Update system prompt (replace messages[0])
        self.system_prompt = self._build_phase_prompt(
            self._base_system_prompt, phase.value
        )
        self.messages[0] = Message(role="system", content=self.system_prompt)

        return True

    # ─── Sub-Agent Delegation ────────────────────────────────────────────

    async def delegate_to_specialist(
        self,
        role: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Delegate a task to a specialist sub-agent.

        Creates (or reuses) a specialist agent with role-specific tools and prompts.
        The specialist runs independently and returns its result.

        Args:
            role: Specialist role — one of:
                  "statistician", "literature_reviewer", "writer",
                  "methodology_expert", "data_analyst"
            task: Task description for the specialist
            context: Additional context to inject into the specialist's prompt

        Returns:
            The specialist's final response string
        """
        if role not in self._specialist_agents:
            specialist = self._create_specialist(role)
            self._specialist_agents[role] = specialist
        else:
            specialist = self._specialist_agents[role]

        task_message = self._build_specialist_task(task, context)
        specialist.add_user_message(task_message)

        result = await specialist.run()

        # Record delegation in project state for audit trail
        self.project_state.record_delegation(role, task, result)

        return result

    def _create_specialist(self, role: str) -> Agent:
        """Create a specialist sub-agent for a specific role.

        Each specialist gets:
        - Role-specific system prompt
        - Subset of tools relevant to their role
        - Shared workspace access
        - Lower max_steps (specialists should be focused)
        """
        specialist_prompts = {
            "statistician": (
                "You are a research statistician specialist. Your role is to:\n"
                "- Design appropriate statistical tests for research questions\n"
                "- Execute statistical analyses using Python (scipy, statsmodels, sklearn)\n"
                "- Interpret results with proper effect sizes and confidence intervals\n"
                "- Flag potential issues (multicollinearity, non-normality, small samples)\n"
                "- Report results in APA format\n\n"
                "Always show your work: state hypotheses, check assumptions, run tests, interpret."
            ),
            "literature_reviewer": (
                "You are a systematic literature reviewer. Your role is to:\n"
                "- Search for relevant papers using structured queries\n"
                "- Evaluate paper quality and relevance\n"
                "- Extract key findings, methods, and gaps\n"
                "- Synthesize findings into coherent themes\n"
                "- Identify research gaps that motivate new work\n"
                "- Manage citations properly (author, year, DOI)\n\n"
                "Follow PRISMA guidelines for systematic reviews when applicable."
            ),
            "writer": (
                "You are an academic paper writer. Your role is to:\n"
                "- Write clear, concise academic prose\n"
                "- Follow the target journal's style guide\n"
                "- Structure arguments logically with proper transitions\n"
                "- Integrate citations naturally into the text\n"
                "- Maintain consistent terminology throughout\n\n"
                "Output in LaTeX or Markdown as specified. Always cite sources."
            ),
            "methodology_expert": (
                "You are a research methodology expert. Your role is to:\n"
                "- Design rigorous research methodologies\n"
                "- Select appropriate sampling strategies\n"
                "- Define valid measurement instruments\n"
                "- Identify and address threats to validity\n"
                "- Recommend appropriate analytical frameworks\n\n"
                "Always justify methodological choices with references."
            ),
            "data_analyst": (
                "You are a data analysis specialist. Your role is to:\n"
                "- Load and clean datasets (handle missing values, outliers, encoding)\n"
                "- Perform exploratory data analysis (distributions, correlations)\n"
                "- Create publication-quality visualizations\n"
                "- Transform and engineer features as needed\n"
                "- Document all data processing steps for reproducibility\n\n"
                "Always use pandas, numpy, matplotlib/seaborn. Show code and explain."
            ),
        }

        specialist_tool_names = {
            "statistician": ["python_repl", "statistical_analysis", "visualization"],
            "literature_reviewer": ["literature_search", "citation_manager", "record_note"],
            "writer": ["paper_writer", "citation_manager", "read_file", "write_file"],
            "methodology_expert": ["python_repl", "statistical_analysis", "literature_search"],
            "data_analyst": ["python_repl", "data_loader", "visualization", "statistical_analysis"],
        }

        prompt = specialist_prompts.get(role, f"You are a research specialist in {role}.")
        tool_names = specialist_tool_names.get(role, [])

        available_tools = self.phase_manager.get_all_tools()
        role_tools = [t for t in available_tools if t.name in tool_names]

        return Agent(
            llm_client=self._llm_client,
            system_prompt=prompt,
            tools=role_tools,
            max_steps=30,
            workspace_dir=str(self.workspace.root),
            token_limit=80000,
        )

    def _build_specialist_task(self, task: str, context: dict | None) -> str:
        """Build a task message for a specialist with relevant context."""
        parts = [f"## Task\n{task}"]

        if context:
            parts.append("\n## Context")
            for key, value in context.items():
                parts.append(f"- **{key}**: {value}")

        parts.append("\n## Project Info")
        parts.append(f"- Topic: {self.project_state.project.topic}")
        parts.append(f"- Phase: {self.project_state.phase.current}")

        if self.project_state.research_questions:
            parts.append("\n## Research Questions")
            for rq in self.project_state.research_questions:
                parts.append(f"- {rq.id}: {rq.question}")

        return "\n".join(parts)

    # ─── Overridden run() ────────────────────────────────────────────────

    async def run(self, cancel_event: asyncio.Event | None = None) -> str:
        """Override run() to add session persistence and resume.

        Wraps the parent Agent.run() with:
        - Session resume context injection (if continuing from previous session)
        - Automatic state saving on completion
        - Session checkpoint creation for future resumption
        """
        # Inject resume context if this is a continuation session
        if self.session_resume.has_previous_session():
            resume_msg = self.session_resume.get_resume_message()
            if resume_msg and len(self.messages) == 1:  # Only system prompt exists
                self.messages.append(Message(role="user", content=resume_msg))

        try:
            # Call parent Agent.run() — this executes the full agent loop
            result = await super().run(cancel_event=cancel_event)
        finally:
            # Always save state and create checkpoint, even on cancellation
            self.project_state.save()
            self.session_resume.create_checkpoint(
                messages=self.messages,
                phase=self.project_state.phase.current,
            )

        return result
```

---

## Section 4: PhaseManager Implementation

### File: `mini_agent/research/phase_manager.py`

The PhaseManager controls which tools are available in each research phase. It lazy-loads research tools on first access and provides phase-specific system prompt fragments.

**Key integration with existing code:**
- Returns `list[Tool]` instances that implement the same `Tool` ABC from `tools/base.py`
- The orchestrator passes these to `Agent.__init__()` which stores them as `self.tools = {tool.name: tool for tool in tools}`

```python
"""Phase Manager — controls tool availability and transitions per research phase."""

from enum import Enum
from pathlib import Path
from typing import Any

from ..tools.base import Tool


class ResearchPhase(str, Enum):
    """Research workflow phases."""
    PLAN = "plan"
    COLLECT = "collect"
    ANALYZE = "analyze"
    WRITE = "write"
    REVIEW = "review"


# Valid phase transitions (directed graph)
# Forward transitions require quality gate passage
# Backward transitions are always allowed (for iteration)
PHASE_TRANSITIONS: dict[str, list[str]] = {
    "plan": ["collect"],
    "collect": ["analyze", "plan"],        # Can go back to plan if scope changes
    "analyze": ["write", "collect"],        # Can go back to collect if more data needed
    "write": ["review", "analyze"],         # Can go back to analyze if results need rework
    "review": ["write", "plan"],            # Can go back to write for revisions
}


class PhaseManager:
    """Manages tool loading and availability per research phase.

    Each phase has:
    - A set of phase-specific tools (loaded on demand)
    - A set of always-available base tools (file ops, bash, notes)
    - A phase-specific system prompt fragment
    - Quality gate criteria that must be met before advancing

    Tool Loading Strategy:
    - Base tools (from cli.py initialization) are ALWAYS available
    - Research tools are lazy-loaded on first access
    - Phase determines which research tools are exposed to the LLM
    """

    # Tool names available in each phase
    # Base tools (file ops, bash, notes) are ALWAYS available — not listed here
    PHASE_TOOLS: dict[str, list[str]] = {
        "plan": [
            "literature_search",      # Search for related work to inform planning
            "citation_manager",       # Start building bibliography
            "record_note",            # Record decisions and rationale
            "recall_notes",           # Recall previous notes
            "quality_gate",           # Check if ready to proceed
        ],
        "collect": [
            "literature_search",      # Systematic literature search
            "citation_manager",       # Manage references
            "data_loader",            # Load datasets from files/APIs
            "python_repl",            # Data exploration and cleaning
            "record_note",
            "recall_notes",
            "quality_gate",
        ],
        "analyze": [
            "python_repl",            # Statistical analysis execution
            "statistical_analysis",   # High-level statistical operations
            "visualization",          # Create publication-quality figures
            "data_loader",            # Load additional data if needed
            "record_note",
            "recall_notes",
            "quality_gate",
        ],
        "write": [
            "paper_writer",           # LaTeX/Markdown paper generation
            "citation_manager",       # Insert citations
            "visualization",          # Regenerate/refine figures
            "python_repl",            # Generate tables, verify numbers
            "literature_search",      # Fill citation gaps
            "record_note",
            "recall_notes",
            "quality_gate",
        ],
        "review": [
            "paper_writer",           # Make revisions
            "citation_manager",       # Fix citation issues
            "python_repl",            # Verify calculations
            "statistical_analysis",   # Re-check analyses
            "quality_gate",           # Final quality check
            "record_note",
            "recall_notes",
        ],
    }

    # Quality gate criteria per phase — must ALL be met to advance
    GATE_CRITERIA: dict[str, list[str]] = {
        "plan": [
            "At least 1 research question defined",
            "Methodology approach selected",
            "Data sources identified",
            "Timeline/scope defined",
        ],
        "collect": [
            "Minimum 10 relevant papers found and cataloged",
            "Primary data source loaded and validated",
            "Data quality assessment completed",
            "Literature gaps identified",
        ],
        "analyze": [
            "All research questions addressed with statistical tests",
            "Results tables generated",
            "Key figures created",
            "Effect sizes and confidence intervals reported",
            "Assumptions checked and documented",
        ],
        "write": [
            "All sections drafted (intro, methods, results, discussion)",
            "All figures and tables referenced in text",
            "All claims supported by citations or data",
            "Word count within target range",
        ],
        "review": [
            "No placeholder text remaining",
            "Citation format consistent",
            "Statistical reporting follows APA guidelines",
            "Abstract accurately summarizes paper",
            "Limitations section present and honest",
        ],
    }

    def __init__(
        self,
        base_tools: list[Tool],
        workspace: "ResearchWorkspace",
        config: dict[str, Any],
    ):
        """Initialize PhaseManager.

        Args:
            base_tools: Tools available in ALL phases (from cli.py initialization:
                        BashTool, ReadTool, WriteTool, EditTool, SessionNoteTool, etc.)
            workspace: Research workspace for tool initialization paths
            config: Research configuration dict (from config.yaml research section)
        """
        self.base_tools = base_tools
        self.workspace = workspace
        self.config = config

        # Registry of all research tools (lazy-loaded)
        self._tool_registry: dict[str, Tool] = {}
        self._tools_initialized = False

    def _ensure_tools_initialized(self):
        """Lazy-initialize research tools on first access.

        This avoids importing heavy dependencies (scipy, pandas, etc.)
        until they're actually needed.
        """
        if self._tools_initialized:
            return

        from .tools import (
            CitationManagerTool,
            DataLoaderTool,
            LiteratureSearchTool,
            PaperWriterTool,
            PythonREPLTool,
            QualityGateTool,
            StatisticalAnalysisTool,
            VisualizationTool,
        )

        workspace_dir = str(self.workspace.root)

        tool_instances: list[Tool] = [
            PythonREPLTool(
                workspace_dir=workspace_dir,
                sandbox_type=self.config.get("sandbox_type", "local"),
            ),
            LiteratureSearchTool(workspace_dir=workspace_dir),
            CitationManagerTool(
                workspace_dir=workspace_dir,
                bibliography_file=str(self.workspace.root / "references.bib"),
            ),
            StatisticalAnalysisTool(workspace_dir=workspace_dir),
            VisualizationTool(
                workspace_dir=workspace_dir,
                output_dir=str(self.workspace.figures_dir),
            ),
            PaperWriterTool(
                workspace_dir=workspace_dir,
                output_dir=str(self.workspace.paper_dir),
            ),
            QualityGateTool(gate_criteria=self.GATE_CRITERIA),
            DataLoaderTool(
                workspace_dir=workspace_dir,
                data_dir=str(self.workspace.data_dir),
            ),
        ]

        for tool in tool_instances:
            self._tool_registry[tool.name] = tool

        self._tools_initialized = True

    def get_active_tools(self, phase: str) -> list[Tool]:
        """Get the complete tool list for a given phase.

        Returns base tools + phase-specific research tools.
        """
        self._ensure_tools_initialized()

        active_tools = list(self.base_tools)

        phase_tool_names = self.PHASE_TOOLS.get(phase, [])
        for tool_name in phase_tool_names:
            if tool_name in self._tool_registry:
                active_tools.append(self._tool_registry[tool_name])

        return active_tools

    def get_all_tools(self) -> list[Tool]:
        """Get ALL tools (base + all research tools).

        Used for specialist agents that may need any tool regardless of phase.
        """
        self._ensure_tools_initialized()
        all_tools = list(self.base_tools)
        all_tools.extend(self._tool_registry.values())
        return all_tools

    def get_phase_prompt(self, phase: str) -> str:
        """Get the system prompt fragment for a specific phase.

        Tries to load from prompts/ directory first, falls back to built-in prompts.
        """
        prompts_dir = Path(__file__).parent / "prompts"
        prompt_file = prompts_dir / f"{phase}_phase.md"

        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")

        # Fallback built-in prompts
        fallback_prompts = {
            "plan": (
                "## Planning Phase Objectives\n"
                "- Define clear, testable research questions\n"
                "- Identify appropriate methodology\n"
                "- Locate data sources and assess feasibility\n"
                "- Create a research timeline\n"
                "- Review related work to position your contribution\n\n"
                "### Available Actions\n"
                "- Search literature to understand the field\n"
                "- Define research questions (use record_note to save them)\n"
                "- Outline methodology approach\n"
                "- When ready, call quality_gate to check if you can proceed"
            ),
            "collect": (
                "## Collection Phase Objectives\n"
                "- Conduct systematic literature search\n"
                "- Download and organize relevant papers\n"
                "- Load and validate primary datasets\n"
                "- Assess data quality and completeness\n"
                "- Document data provenance\n\n"
                "### Available Actions\n"
                "- Search for papers using structured queries\n"
                "- Load datasets from files or APIs\n"
                "- Clean and validate data using Python\n"
                "- Catalog all sources with proper citations\n"
                "- When ready, call quality_gate to proceed to analysis"
            ),
            "analyze": (
                "## Analysis Phase Objectives\n"
                "- Execute statistical analyses for each research question\n"
                "- Generate publication-quality figures\n"
                "- Create results tables\n"
                "- Check statistical assumptions\n"
                "- Document all analytical decisions\n\n"
                "### Available Actions\n"
                "- Run Python code for statistical analysis\n"
                "- Use statistical_analysis for common tests\n"
                "- Create visualizations with proper labels and legends\n"
                "- Record findings and interpretations\n"
                "- When ready, call quality_gate to proceed to writing"
            ),
            "write": (
                "## Writing Phase Objectives\n"
                "- Draft all paper sections (Introduction, Methods, Results, Discussion)\n"
                "- Integrate figures and tables into the narrative\n"
                "- Ensure all claims are supported by evidence\n"
                "- Maintain consistent citation style\n"
                "- Meet target word count\n\n"
                "### Available Actions\n"
                "- Use paper_writer to generate/edit sections\n"
                "- Insert citations from your bibliography\n"
                "- Reference figures and tables\n"
                "- Search for additional citations if needed\n"
                "- When ready, call quality_gate to proceed to review"
            ),
            "review": (
                "## Review Phase Objectives\n"
                "- Check for completeness and consistency\n"
                "- Verify all statistical claims match analysis outputs\n"
                "- Ensure citation format is correct throughout\n"
                "- Check for placeholder text or TODOs\n"
                "- Verify abstract matches content\n"
                "- Assess limitations honestly\n\n"
                "### Available Actions\n"
                "- Re-run analyses to verify numbers\n"
                "- Fix citation formatting issues\n"
                "- Edit paper sections for clarity\n"
                "- Run final quality gate for submission readiness"
            ),
        }

        return fallback_prompts.get(phase, f"You are in the {phase} phase.")

    def can_transition(self, from_phase: str, to_phase: str) -> bool:
        """Check if a phase transition is valid."""
        allowed = PHASE_TRANSITIONS.get(from_phase, [])
        return to_phase in allowed

    def get_gate_criteria(self, phase: str) -> list[str]:
        """Get quality gate criteria for a phase."""
        return self.GATE_CRITERIA.get(phase, [])
```

---

## Section 5: ProjectState Implementation

### File: `mini_agent/research/project_state.py`

The ProjectState is a Pydantic model that persists as `project.yaml` in the workspace root. It is the single source of truth for the research project across sessions.

```python
"""Project State — Pydantic model with YAML persistence for research project tracking."""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProjectMetadata(BaseModel):
    """Core project metadata."""
    topic: str = ""
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    institution: str = ""
    target_journal: str = ""
    created_at: str = ""
    updated_at: str = ""
    tags: list[str] = Field(default_factory=list)


class ResearchQuestion(BaseModel):
    """A single research question with tracking."""
    id: str                                    # e.g., "RQ1", "RQ2"
    question: str                              # The actual question text
    hypothesis: str = ""                       # Associated hypothesis
    status: str = "pending"                    # pending | investigating | answered | revised
    answer_summary: str = ""                   # Summary of the answer found
    evidence: list[str] = Field(default_factory=list)


class DataSource(BaseModel):
    """A data source in the project inventory."""
    id: str                                    # e.g., "DS1"
    name: str                                  # Human-readable name
    type: str                                  # "file" | "api" | "database" | "manual"
    path_or_url: str = ""
    format: str = ""                           # "csv" | "excel" | "json" | "stata" | "spss"
    rows: int | None = None
    columns: int | None = None
    variables: list[str] = Field(default_factory=list)
    quality_notes: str = ""
    loaded: bool = False


class PaperReference(BaseModel):
    """A literature reference."""
    id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    journal: str = ""
    doi: str = ""
    abstract: str = ""
    relevance: str = ""                        # "high" | "medium" | "low"
    key_findings: list[str] = Field(default_factory=list)
    cited_in_sections: list[str] = Field(default_factory=list)


class LiteratureState(BaseModel):
    """State of literature review."""
    search_queries: list[dict[str, Any]] = Field(default_factory=list)
    references: list[PaperReference] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    total_papers_screened: int = 0
    total_papers_included: int = 0


class AnalysisResult(BaseModel):
    """A single analysis result."""
    id: str
    research_question_id: str                  # Links to ResearchQuestion.id
    test_name: str                             # e.g., "linear_regression", "t_test"
    description: str = ""
    result_summary: str = ""
    p_value: float | None = None
    effect_size: float | None = None
    confidence_interval: list[float] = Field(default_factory=list)
    assumptions_met: bool = True
    assumptions_notes: str = ""
    figure_paths: list[str] = Field(default_factory=list)
    table_data: dict[str, Any] = Field(default_factory=dict)


class PaperSection(BaseModel):
    """A section of the paper."""
    name: str                                  # "abstract" | "introduction" | "methods" | etc.
    status: str = "not_started"                # not_started | drafting | drafted | revising | final
    word_count: int = 0
    file_path: str = ""
    last_edited: str = ""


class PaperState(BaseModel):
    """State of the paper writing."""
    format: str = "latex"                      # "latex" or "markdown"
    template: str = ""
    sections: list[PaperSection] = Field(default_factory=list)
    total_word_count: int = 0
    target_word_count: int = 8000
    figures: list[dict[str, str]] = Field(default_factory=list)
    tables: list[dict[str, str]] = Field(default_factory=list)


class QualityState(BaseModel):
    """Quality tracking across phases."""
    gates_passed: list[str] = Field(default_factory=list)
    current_gate_feedback: str = ""
    issues: list[dict[str, str]] = Field(default_factory=list)
    review_checklist: dict[str, bool] = Field(default_factory=dict)


class PhaseState(BaseModel):
    """Phase tracking."""
    current: str = "plan"
    history: list[dict[str, Any]] = Field(default_factory=list)
    gate_feedback: str = ""
    started_at: dict[str, str] = Field(default_factory=dict)


class DelegationRecord(BaseModel):
    """Record of a sub-agent delegation."""
    role: str
    task: str
    result_summary: str
    timestamp: str
    phase: str


class ProjectState(BaseModel):
    """Complete project state — persisted as project.yaml.

    This is the single source of truth for the research project.
    It is loaded at session start and saved after every significant action.

    Example project.yaml:
        project:
          topic: "Impact of remote work on productivity"
          title: "Remote Work and Productivity: A Mixed-Methods Analysis"
          authors: ["Jane Doe"]
          target_journal: "Journal of Organizational Behavior"
        phase:
          current: "analyze"
        research_questions:
          - id: RQ1
            question: "Does remote work frequency correlate with self-reported productivity?"
            status: investigating
        data_inventory:
          - id: DS1
            name: "Survey responses"
            type: file
            path_or_url: data/raw/survey_2024.csv
            rows: 1247
            loaded: true
    """
    project: ProjectMetadata = Field(default_factory=ProjectMetadata)
    phase: PhaseState = Field(default_factory=PhaseState)
    research_questions: list[ResearchQuestion] = Field(default_factory=list)
    data_inventory: list[DataSource] = Field(default_factory=list)
    literature: LiteratureState = Field(default_factory=LiteratureState)
    analyses: list[AnalysisResult] = Field(default_factory=list)
    paper: PaperState = Field(default_factory=PaperState)
    quality: QualityState = Field(default_factory=QualityState)
    delegations: list[DelegationRecord] = Field(default_factory=list)

    # Internal: file path for persistence (excluded from serialization)
    _state_file: Path | None = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def load_or_create(cls, state_file: Path) -> "ProjectState":
        """Load existing state from YAML or create new."""
        if state_file.exists():
            with open(state_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            state = cls.model_validate(data)
        else:
            state = cls()
            state.project.created_at = cls._get_timestamp()

        state._state_file = state_file
        return state

    def save(self):
        """Persist current state to YAML file."""
        if self._state_file is None:
            raise ValueError("No state file path set. Use load_or_create() first.")

        self.project.updated_at = self._get_timestamp()
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(exclude_none=True)

        with open(self._state_file, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )

    def get_summary(self) -> str:
        """Generate a human-readable summary of current project state."""
        lines = []

        if self.project.topic:
            lines.append(f"**Topic**: {self.project.topic}")
        if self.project.title:
            lines.append(f"**Title**: {self.project.title}")

        lines.append(f"**Phase**: {self.phase.current}")
        lines.append(f"**Research Questions**: {len(self.research_questions)} defined")

        rq_status: dict[str, int] = {}
        for rq in self.research_questions:
            rq_status[rq.status] = rq_status.get(rq.status, 0) + 1
        if rq_status:
            lines.append(f"  Status breakdown: {rq_status}")

        lines.append(f"**Data Sources**: {len(self.data_inventory)} registered")
        lines.append(f"**Literature**: {self.literature.total_papers_included} papers included")
        lines.append(f"**Analyses**: {len(self.analyses)} completed")

        if self.paper.sections:
            drafted = sum(1 for s in self.paper.sections if s.status in ("drafted", "final"))
            lines.append(
                f"**Paper**: {drafted}/{len(self.paper.sections)} sections drafted "
                f"({self.paper.total_word_count} words)"
            )

        lines.append(
            f"**Quality Gates Passed**: {', '.join(self.quality.gates_passed) or 'none'}"
        )

        return "\n".join(lines)

    def record_delegation(self, role: str, task: str, result: str):
        """Record a sub-agent delegation for audit trail."""
        self.delegations.append(DelegationRecord(
            role=role,
            task=task,
            result_summary=result[:500] if len(result) > 500 else result,
            timestamp=self._get_timestamp(),
            phase=self.phase.current,
        ))
        self.save()

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def get_timestamp() -> str:
        return datetime.now().isoformat(timespec="seconds")
```

### File: `mini_agent/research/workspace.py`

```python
"""Research Workspace — directory structure management."""

from pathlib import Path


class ResearchWorkspace:
    """Manages the research project directory structure.

    Standard layout:
        project_root/
        +-- project.yaml          # Project state
        +-- data/raw/             # Raw data files
        +-- data/processed/       # Cleaned data
        +-- literature/papers/    # Downloaded papers
        +-- literature/notes/     # Reading notes
        +-- analysis/scripts/     # Analysis code
        +-- analysis/outputs/     # Analysis results
        +-- figures/              # Publication figures
        +-- paper/sections/       # Paper section drafts
        +-- review/               # Review artifacts
        +-- .sessions/            # Session checkpoints
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    @property
    def state_file(self) -> Path:
        return self.root / "project.yaml"

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def raw_data_dir(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def processed_data_dir(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def literature_dir(self) -> Path:
        return self.root / "literature"

    @property
    def papers_dir(self) -> Path:
        return self.root / "literature" / "papers"

    @property
    def lit_notes_dir(self) -> Path:
        return self.root / "literature" / "notes"

    @property
    def analysis_dir(self) -> Path:
        return self.root / "analysis"

    @property
    def scripts_dir(self) -> Path:
        return self.root / "analysis" / "scripts"

    @property
    def outputs_dir(self) -> Path:
        return self.root / "analysis" / "outputs"

    @property
    def figures_dir(self) -> Path:
        return self.root / "figures"

    @property
    def paper_dir(self) -> Path:
        return self.root / "paper"

    @property
    def sections_dir(self) -> Path:
        return self.root / "paper" / "sections"

    @property
    def review_dir(self) -> Path:
        return self.root / "review"

    @property
    def sessions_dir(self) -> Path:
        return self.root / ".sessions"

    def ensure_structure(self):
        """Create the full directory structure if it doesn't exist."""
        directories = [
            self.root, self.raw_data_dir, self.processed_data_dir,
            self.papers_dir, self.lit_notes_dir,
            self.scripts_dir, self.outputs_dir,
            self.figures_dir, self.sections_dir,
            self.review_dir, self.sessions_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_relative_path(self, absolute_path: Path) -> str:
        """Get path relative to workspace root."""
        try:
            return str(absolute_path.relative_to(self.root))
        except ValueError:
            return str(absolute_path)
```

---

## Section 6: LiteLLM Integration

### Strategy

Add LiteLLM as a **third provider option** alongside the existing Anthropic and OpenAI clients. The existing clients remain untouched for backward compatibility. Research mode uses LiteLLM by default for its cost tracking and multi-provider support.

### File: `mini_agent/llm/litellm_client.py` (NEW)

```python
"""LiteLLM-based client — unified interface to all LLM providers with cost tracking."""

import json
import logging
from typing import Any

from ..retry import RetryConfig
from ..schema import FunctionCall, LLMResponse, Message, TokenUsage, ToolCall
from .base import LLMClientBase

logger = logging.getLogger(__name__)


class LiteLLMClient(LLMClientBase):
    """LLM client using LiteLLM for unified provider access.

    Supports all LiteLLM-compatible models:
    - anthropic/claude-sonnet-4-20250514
    - gpt-4o, gpt-4o-mini
    - deepseek/deepseek-chat
    - together_ai/meta-llama/Llama-3-70b
    - And 100+ more

    Features:
    - Automatic cost tracking per call and cumulative
    - Fallback model configuration
    - Budget limits
    """

    def __init__(
        self,
        api_key: str,
        api_base: str | None = None,
        model: str = "anthropic/claude-sonnet-4-20250514",
        retry_config: RetryConfig | None = None,
        fallback_models: list[str] | None = None,
        budget_limit: float | None = None,
    ):
        super().__init__(
            api_key=api_key,
            api_base=api_base or "",
            model=model,
            retry_config=retry_config,
        )
        self.fallback_models = fallback_models or []
        self.budget_limit = budget_limit
        self.total_cost: float = 0.0
        self.call_costs: list[dict[str, Any]] = []

    async def generate(
        self,
        messages: list[Message],
        tools: list[Any] | None = None,
    ) -> LLMResponse:
        """Generate response using LiteLLM.

        Same signature as existing LLMClientBase.generate() for compatibility.
        """
        from litellm import acompletion, completion_cost

        if self.budget_limit and self.total_cost >= self.budget_limit:
            raise RuntimeError(
                f"Budget limit reached: ${self.total_cost:.4f} >= ${self.budget_limit:.4f}"
            )

        request = self._prepare_request(messages, tools)

        # Execute with retries and fallback
        models_to_try = [self.model] + self.fallback_models
        last_error = None

        for model in models_to_try:
            request["model"] = model
            for attempt in range(self.retry_config.max_retries + 1):
                try:
                    response = await acompletion(**request)

                    # Track cost (best-effort)
                    try:
                        cost = completion_cost(completion_response=response)
                        self.total_cost += cost
                        self.call_costs.append({
                            "model": model, "cost": cost, "total": self.total_cost,
                        })
                    except Exception:
                        pass

                    return self._parse_response(response)

                except Exception as e:
                    last_error = e
                    if attempt < self.retry_config.max_retries:
                        import asyncio
                        delay = self.retry_config.calculate_delay(attempt)
                        if self.retry_callback:
                            self.retry_callback(e, attempt + 1)
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"Model {model} failed after {attempt + 1} attempts: {e}")
                        break

        raise last_error or RuntimeError("All models failed")

    def _prepare_request(
        self, messages: list[Message], tools: list[Any] | None = None,
    ) -> dict[str, Any]:
        system_msg, api_messages = self._convert_messages(messages)

        request: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "api_key": self.api_key,
        }

        if self.api_base:
            request["api_base"] = self.api_base

        if system_msg:
            request["messages"] = [{"role": "system", "content": system_msg}] + api_messages

        if tools:
            tool_defs = []
            for tool in tools:
                if hasattr(tool, "to_openai_schema"):
                    tool_defs.append(tool.to_openai_schema())
                elif isinstance(tool, dict):
                    tool_defs.append(tool)
            if tool_defs:
                request["tools"] = tool_defs
                request["tool_choice"] = "auto"

        return request

    def _convert_messages(
        self, messages: list[Message]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        system_msg = None
        api_messages = []

        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content if isinstance(msg.content, str) else str(msg.content)
                continue

            api_msg: dict[str, Any] = {"role": msg.role}

            if msg.role == "assistant":
                api_msg["content"] = msg.content if isinstance(msg.content, str) else ""
                if msg.tool_calls:
                    api_msg["tool_calls"] = [
                        {
                            "id": tc.id, "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": json.dumps(tc.function.arguments),
                            },
                        }
                        for tc in msg.tool_calls
                    ]
            elif msg.role == "tool":
                api_msg["content"] = msg.content if isinstance(msg.content, str) else str(msg.content)
                api_msg["tool_call_id"] = msg.tool_call_id or ""
                if msg.name:
                    api_msg["name"] = msg.name
            else:
                api_msg["content"] = msg.content if isinstance(msg.content, str) else str(msg.content)

            api_messages.append(api_msg)

        return system_msg, api_messages

    def _parse_response(self, response: Any) -> LLMResponse:
        choice = response.choices[0]
        message = choice.message

        content = message.content or ""

        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {}
                tool_calls.append(ToolCall(
                    id=tc.id, type="function",
                    function=FunctionCall(name=tc.function.name, arguments=args),
                ))

        usage = None
        if response.usage:
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens or 0,
                completion_tokens=response.usage.completion_tokens or 0,
                total_tokens=response.usage.total_tokens or 0,
            )

        return LLMResponse(
            content=content, thinking=None, tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop", usage=usage,
        )

    def get_cost_report(self) -> dict[str, Any]:
        return {
            "total_cost_usd": round(self.total_cost, 6),
            "num_calls": len(self.call_costs),
            "budget_limit": self.budget_limit,
            "budget_remaining": round(self.budget_limit - self.total_cost, 6) if self.budget_limit else None,
            "recent_calls": self.call_costs[-10:],
        }
```

### Changes to Existing Files (minimal, backward-compatible)

**`mini_agent/schema/schema.py`** — Add one line to the enum:

```python
class LLMProvider(str, Enum):
    """LLM provider types."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LITELLM = "litellm"  # <-- ADD THIS LINE
```

**`mini_agent/llm/llm_wrapper.py`** — Add LiteLLM branch in `__init__` (after line ~102):

```python
# After the existing `elif provider == LLMProvider.OPENAI:` block, add:

elif provider == LLMProvider.LITELLM:
    from .litellm_client import LiteLLMClient
    self._client = LiteLLMClient(
        api_key=api_key,
        api_base=full_api_base if not is_minimax else None,
        model=self.model,
        retry_config=retry_config,
    )
```

---

## Section 7: DSPy Integration

### Strategy

DSPy modules are wrapped as `Tool` instances so they integrate seamlessly with the existing agent loop. Each DSPy module:
1. Defines a `Signature` (typed input/output schema)
2. Implements a `Module` (the logic with chain-of-thought)
3. Is wrapped in a `Tool` subclass for the agent to call

DSPy optimization runs **offline** (not during agent execution) to improve module quality.

### File: `mini_agent/research/dspy_modules/signatures.py`

```python
"""DSPy Signature definitions for research tasks."""

import dspy


class GenerateResearchQuestions(dspy.Signature):
    """Generate research questions from a topic and literature context."""
    topic: str = dspy.InputField(desc="Research topic or area of interest")
    literature_context: str = dspy.InputField(desc="Summary of existing literature and gaps")
    num_questions: int = dspy.InputField(desc="Number of questions to generate", default=3)

    research_questions: list[str] = dspy.OutputField(desc="List of specific, testable research questions")
    rationale: str = dspy.OutputField(desc="Explanation of why these questions are important")


class SynthesizeLiterature(dspy.Signature):
    """Synthesize findings from multiple papers into coherent themes."""
    papers: str = dspy.InputField(desc="JSON list of paper summaries with key findings")
    research_questions: str = dspy.InputField(desc="Research questions to synthesize around")

    themes: list[str] = dspy.OutputField(desc="Major themes identified across papers")
    synthesis: str = dspy.OutputField(desc="Narrative synthesis of the literature")
    gaps: list[str] = dspy.OutputField(desc="Identified gaps in the literature")


class DesignMethodology(dspy.Signature):
    """Design a research methodology for given research questions."""
    research_questions: str = dspy.InputField(desc="Research questions to address")
    data_description: str = dspy.InputField(desc="Available data sources and characteristics")
    constraints: str = dspy.InputField(desc="Any constraints (time, budget, ethical)")

    methodology: str = dspy.OutputField(desc="Detailed methodology description")
    statistical_tests: list[str] = dspy.OutputField(desc="Recommended statistical tests")
    limitations: list[str] = dspy.OutputField(desc="Known limitations of this approach")


class InterpretResults(dspy.Signature):
    """Interpret statistical results in context of research questions."""
    research_question: str = dspy.InputField(desc="The research question being addressed")
    statistical_output: str = dspy.InputField(desc="Raw statistical output")
    methodology_context: str = dspy.InputField(desc="How the analysis was conducted")

    interpretation: str = dspy.OutputField(desc="Plain-language interpretation")
    implications: list[str] = dspy.OutputField(desc="Practical and theoretical implications")
    caveats: list[str] = dspy.OutputField(desc="Important caveats or limitations")
    apa_report: str = dspy.OutputField(desc="APA-formatted statistical report")
```

### Wrapping DSPy Modules as Tools

The pattern for wrapping any DSPy module as a Tool (follows the same `Tool` ABC from `tools/base.py`):

```python
"""Example: DSPy module wrapped as a Tool for the agent."""

from typing import Any
from ...tools.base import Tool, ToolResult


class DSPyResearchQuestionTool(Tool):
    """Tool wrapper for DSPy ResearchQuestionGenerator module."""

    def __init__(self, dspy_lm=None):
        self._lm = dspy_lm
        self._module = None

    def _ensure_module(self):
        if self._module is None:
            import dspy
            from .research_question import ResearchQuestionGenerator
            if self._lm:
                dspy.configure(lm=self._lm)
            self._module = ResearchQuestionGenerator()

    @property
    def name(self) -> str:
        return "generate_research_questions"

    @property
    def description(self) -> str:
        return (
            "Generate high-quality, testable research questions based on a topic "
            "and literature context. Uses optimized prompting for academic rigor."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Research topic or area of interest",
                },
                "literature_context": {
                    "type": "string",
                    "description": "Summary of existing literature, key findings, and gaps",
                },
                "num_questions": {
                    "type": "integer",
                    "description": "Number of research questions to generate (default: 3)",
                    "default": 3,
                },
            },
            "required": ["topic", "literature_context"],
        }

    async def execute(
        self, topic: str, literature_context: str, num_questions: int = 3,
    ) -> ToolResult:
        self._ensure_module()
        try:
            result = self._module(
                topic=topic,
                literature_context=literature_context,
                num_questions=num_questions,
            )
            output = "## Generated Research Questions\n\n"
            for i, q in enumerate(result.research_questions, 1):
                output += f"{i}. {q}\n"
            output += f"\n## Rationale\n{result.rationale}"
            return ToolResult(success=True, content=output)
        except Exception as e:
            return ToolResult(success=False, content="", error=f"Failed: {str(e)}")
```

---

## Section 8: New Tool Implementations

All tools implement the same `Tool` ABC from `mini_agent/tools/base.py` (55 lines). Each tool must define: `name`, `description`, `parameters` (JSON Schema), and `async execute() -> ToolResult`.

### Tool 1: PythonREPLTool (`research/tools/python_repl.py`)

```python
"""Python REPL Tool — sandboxed code execution for data analysis."""

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from ...tools.base import Tool, ToolResult


class PythonREPLTool(Tool):
    """Execute Python code in a sandboxed environment.

    Supports: "local" (subprocess), "e2b" (cloud sandbox), "docker" (container).
    Pre-installed: pandas, numpy, scipy, statsmodels, sklearn, matplotlib, seaborn.
    """

    def __init__(self, workspace_dir: str = "./workspace", sandbox_type: str = "local",
                 timeout: int = 120, e2b_api_key: str | None = None):
        self.workspace_dir = Path(workspace_dir)
        self.sandbox_type = sandbox_type
        self.timeout = timeout
        self.e2b_api_key = e2b_api_key

    @property
    def name(self) -> str:
        return "python_repl"

    @property
    def description(self) -> str:
        return (
            "Execute Python code for data analysis, statistical computation, and visualization. "
            "Has access to: pandas, numpy, scipy, statsmodels, sklearn, matplotlib, seaborn. "
            "For plots, save to the figures/ directory and return the file path."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute."},
                "description": {"type": "string", "description": "Brief description of what this code does."},
            },
            "required": ["code"],
        }

    async def execute(self, code: str, description: str = "") -> ToolResult:
        if self.sandbox_type == "local":
            return await self._execute_local(code)
        elif self.sandbox_type == "e2b":
            return await self._execute_e2b(code)
        return ToolResult(success=False, content="", error=f"Unknown sandbox: {self.sandbox_type}")

    async def _execute_local(self, code: str) -> ToolResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", dir=str(self.workspace_dir), delete=False) as f:
            f.write("import sys, os, warnings\nwarnings.filterwarnings('ignore')\n" + code)
            script_path = f.name
        try:
            proc = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_dir),
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")
            if proc.returncode == 0:
                output = stdout_str + (f"\n[stderr]: {stderr_str}" if stderr_str else "")
                return ToolResult(success=True, content=output or "(no output)")
            return ToolResult(success=False, content=stdout_str, error=f"Exit code {proc.returncode}\n{stderr_str}")
        except asyncio.TimeoutError:
            return ToolResult(success=False, content="", error=f"Timed out after {self.timeout}s")
        finally:
            Path(script_path).unlink(missing_ok=True)

    async def _execute_e2b(self, code: str) -> ToolResult:
        try:
            from e2b_code_interpreter import AsyncSandbox
            async with AsyncSandbox(api_key=self.e2b_api_key) as sandbox:
                execution = await sandbox.run_code(code, timeout=self.timeout)
                if execution.error:
                    return ToolResult(success=False, content="",
                        error=f"{execution.error.name}: {execution.error.value}")
                outputs = [r.text for r in execution.results if r.text]
                if execution.logs.stdout:
                    outputs.append(execution.logs.stdout)
                return ToolResult(success=True, content="\n".join(outputs) or "(no output)")
        except ImportError:
            return ToolResult(success=False, content="", error="E2B not installed. Run: pip install e2b-code-interpreter")
        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))
```

### Tool 2: LiteratureSearchTool (`research/tools/literature_search.py`)

```python
"""Literature Search Tool — academic paper discovery via Semantic Scholar + OpenAlex."""

import aiohttp
from typing import Any
from ...tools.base import Tool, ToolResult


class LiteratureSearchTool(Tool):
    """Search academic literature using Semantic Scholar API (free, no key needed)."""

    def __init__(self, workspace_dir: str = "./workspace", max_results: int = 20):
        self.workspace_dir = workspace_dir
        self.max_results = max_results

    @property
    def name(self) -> str:
        return "literature_search"

    @property
    def description(self) -> str:
        return (
            "Search academic literature databases for relevant papers. "
            "Returns paper titles, authors, years, abstracts, and citation counts. "
            "Use specific academic search queries."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Academic search query"},
                "year_from": {"type": "integer", "description": "Filter papers from this year"},
                "year_to": {"type": "integer", "description": "Filter papers until this year"},
                "max_results": {"type": "integer", "description": "Max results (default: 10)", "default": 10},
            },
            "required": ["query"],
        }

    async def execute(self, query: str, year_from: int | None = None,
                      year_to: int | None = None, max_results: int = 10) -> ToolResult:
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": min(max_results, 100),
                "fields": "title,authors,year,abstract,citationCount,externalIds",
            }
            if year_from or year_to:
                params["year"] = f"{year_from or ''}-{year_to or ''}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        return ToolResult(success=False, content="", error=f"API returned {resp.status}")
                    data = await resp.json()

            papers = data.get("data", [])
            if not papers:
                return ToolResult(success=True, content="No papers found. Try broader search terms.")

            output = f"## Literature Search Results ({len(papers)} papers)\n\n"
            for i, paper in enumerate(papers, 1):
                authors = ", ".join(a.get("name", "") for a in paper.get("authors", [])[:3])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                output += f"### {i}. {paper.get('title', 'Untitled')}\n"
                output += f"- **Authors**: {authors}\n"
                output += f"- **Year**: {paper.get('year', 'N/A')}\n"
                output += f"- **Citations**: {paper.get('citationCount', 0)}\n"
                doi = (paper.get("externalIds") or {}).get("DOI", "")
                if doi:
                    output += f"- **DOI**: {doi}\n"
                abstract = paper.get("abstract", "")
                if abstract:
                    output += f"- **Abstract**: {abstract[:300]}{'...' if len(abstract) > 300 else ''}\n"
                output += "\n"

            return ToolResult(success=True, content=output)
        except Exception as e:
            return ToolResult(success=False, content="", error=f"Literature search failed: {str(e)}")
```

### Tool 3: CitationManagerTool (`research/tools/citation_manager.py`)

```python
"""Citation Manager Tool — BibTeX bibliography management."""

import re
from pathlib import Path
from typing import Any
from ...tools.base import Tool, ToolResult


class CitationManagerTool(Tool):
    """Manage BibTeX bibliography for the research project."""

    def __init__(self, workspace_dir: str = "./workspace", bibliography_file: str = "references.bib"):
        self.workspace_dir = Path(workspace_dir)
        self.bib_file = Path(bibliography_file)

    @property
    def name(self) -> str:
        return "citation_manager"

    @property
    def description(self) -> str:
        return (
            "Manage the project bibliography (references.bib). "
            "Actions: add (add a BibTeX entry), list (list all entries), "
            "search (find entries by keyword), format (format a citation)."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "search", "format"],
                           "description": "Action to perform"},
                "bibtex_entry": {"type": "string", "description": "BibTeX entry to add (for 'add' action)"},
                "keyword": {"type": "string", "description": "Search keyword (for 'search' action)"},
                "citation_key": {"type": "string", "description": "Citation key (for 'format' action)"},
                "style": {"type": "string", "description": "Citation style (apa, chicago, ieee)", "default": "apa"},
            },
            "required": ["action"],
        }

    async def execute(self, action: str, bibtex_entry: str = "", keyword: str = "",
                      citation_key: str = "", style: str = "apa") -> ToolResult:
        try:
            if action == "add":
                return self._add_entry(bibtex_entry)
            elif action == "list":
                return self._list_entries()
            elif action == "search":
                return self._search_entries(keyword)
            elif action == "format":
                return self._format_citation(citation_key, style)
            return ToolResult(success=False, content="", error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))

    def _add_entry(self, entry: str) -> ToolResult:
        if not entry.strip():
            return ToolResult(success=False, content="", error="Empty BibTeX entry")
        self.bib_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.bib_file, "a", encoding="utf-8") as f:
            f.write("\n" + entry.strip() + "\n")
        key_match = re.search(r"@\w+\{(\w+),", entry)
        key = key_match.group(1) if key_match else "unknown"
        return ToolResult(success=True, content=f"Added entry with key: {key}")

    def _list_entries(self) -> ToolResult:
        if not self.bib_file.exists():
            return ToolResult(success=True, content="Bibliography is empty.")
        content = self.bib_file.read_text(encoding="utf-8")
        keys = re.findall(r"@\w+\{(\w+),", content)
        if not keys:
            return ToolResult(success=True, content="Bibliography is empty.")
        output = f"## Bibliography ({len(keys)} entries)\n\n"
        for key in keys:
            output += f"- {key}\n"
        return ToolResult(success=True, content=output)

    def _search_entries(self, keyword: str) -> ToolResult:
        if not self.bib_file.exists():
            return ToolResult(success=True, content="Bibliography is empty.")
        content = self.bib_file.read_text(encoding="utf-8")
        entries = re.split(r"(?=@\w+\{)", content)
        matches = [e.strip() for e in entries if keyword.lower() in e.lower() and e.strip()]
        if not matches:
            return ToolResult(success=True, content=f"No entries matching '{keyword}'.")
        return ToolResult(success=True, content=f"Found {len(matches)} matches:\n\n" + "\n\n".join(matches))

    def _format_citation(self, key: str, style: str) -> ToolResult:
        return ToolResult(success=True, content=f"\\cite{{{key}}}")
```

### Tool 4: StatisticalAnalysisTool (`research/tools/statistical_analysis.py`)

```python
"""Statistical Analysis Tool — high-level statistical operations."""

from typing import Any
from ...tools.base import Tool, ToolResult


class StatisticalAnalysisTool(Tool):
    """Run common statistical tests with proper reporting."""

    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "statistical_analysis"

    @property
    def description(self) -> str:
        return (
            "Run common statistical tests and return properly formatted results. "
            "Supports: t_test, anova, chi_square, correlation, regression, "
            "descriptive_stats, normality_test. Returns APA-formatted output."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_type": {
                    "type": "string",
                    "enum": ["t_test", "anova", "chi_square", "correlation",
                             "regression", "descriptive_stats", "normality_test"],
                    "description": "Type of statistical test to run",
                },
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "variables": {"type": "array", "items": {"type": "string"},
                              "description": "Variable/column names to analyze"},
                "group_var": {"type": "string", "description": "Grouping variable (for t_test, anova)"},
                "alpha": {"type": "number", "description": "Significance level (default: 0.05)", "default": 0.05},
            },
            "required": ["test_type", "data_path", "variables"],
        }

    async def execute(self, test_type: str, data_path: str, variables: list[str],
                      group_var: str = "", alpha: float = 0.05) -> ToolResult:
        """Execute statistical test by generating and running Python code."""
        # Generate appropriate Python code for the test
        code = self._generate_test_code(test_type, data_path, variables, group_var, alpha)

        # Use PythonREPLTool to execute (delegate to avoid code duplication)
        from .python_repl import PythonREPLTool
        repl = PythonREPLTool(workspace_dir=self.workspace_dir)
        return await repl.execute(code=code, description=f"Statistical test: {test_type}")

    def _generate_test_code(self, test_type: str, data_path: str,
                            variables: list[str], group_var: str, alpha: float) -> str:
        """Generate Python code for the specified statistical test."""
        var_list = ", ".join(f'"{v}"' for v in variables)

        if test_type == "descriptive_stats":
            return f"""
import pandas as pd
df = pd.read_csv("{data_path}")
vars_to_analyze = [{var_list}]
print("## Descriptive Statistics\\n")
print(df[vars_to_analyze].describe().to_string())
print("\\n## Missing Values\\n")
print(df[vars_to_analyze].isnull().sum().to_string())
"""
        elif test_type == "correlation":
            return f"""
import pandas as pd
from scipy import stats
df = pd.read_csv("{data_path}")
vars_to_analyze = [{var_list}]
print("## Correlation Matrix\\n")
corr = df[vars_to_analyze].corr()
print(corr.to_string())
# Pairwise significance
print("\\n## Pairwise Correlations with p-values\\n")
for i, v1 in enumerate(vars_to_analyze):
    for v2 in vars_to_analyze[i+1:]:
        clean = df[[v1, v2]].dropna()
        r, p = stats.pearsonr(clean[v1], clean[v2])
        sig = "*" if p < {alpha} else ""
        print(f"  {{v1}} x {{v2}}: r = {{r:.3f}}, p = {{p:.4f}} {{sig}}")
"""
        elif test_type == "t_test":
            return f"""
import pandas as pd
from scipy import stats
df = pd.read_csv("{data_path}")
var = "{variables[0]}"
group = "{group_var}"
groups = df[group].unique()
g1 = df[df[group] == groups[0]][var].dropna()
g2 = df[df[group] == groups[1]][var].dropna()
t_stat, p_val = stats.ttest_ind(g1, g2)
cohens_d = (g1.mean() - g2.mean()) / ((g1.std()**2 + g2.std()**2) / 2)**0.5
print(f"## Independent Samples t-test\\n")
print(f"Groups: {{groups[0]}} (n={{len(g1)}}) vs {{groups[1]}} (n={{len(g2)}})")
print(f"t({{len(g1)+len(g2)-2}}) = {{t_stat:.3f}}, p = {{p_val:.4f}}")
print(f"Cohen's d = {{cohens_d:.3f}}")
print(f"Mean difference: {{g1.mean():.3f}} - {{g2.mean():.3f}} = {{g1.mean()-g2.mean():.3f}}")
"""
        else:
            return f'print("Test type {test_type} — generate code manually using python_repl")'
```

### Tool 5: VisualizationTool, PaperWriterTool, QualityGateTool, DataLoaderTool

These follow the exact same pattern. Each has `name`, `description`, `parameters`, and `execute()`. See the full skeletons in the `research/tools/` directory. Key signatures:

```python
# visualization.py
class VisualizationTool(Tool):
    name = "visualization"
    # Generates matplotlib/seaborn code, executes via PythonREPLTool, saves to figures/

# paper_writer.py
class PaperWriterTool(Tool):
    name = "paper_writer"
    # Actions: draft_section, edit_section, compile_paper
    # Writes LaTeX or Markdown to paper/sections/

# quality_gate_tool.py
class QualityGateTool(Tool):
    name = "quality_gate"
    # Agent-callable tool that triggers QualityGateEvaluator
    # Returns pass/fail with feedback

# data_loader.py
class DataLoaderTool(Tool):
    name = "data_loader"
    # Actions: load_csv, load_excel, load_json, describe, preview
    # Loads data into workspace and returns summary statistics
```

---

## Section 9: CLI Extension

### Strategy

Add a `research` subcommand to the existing CLI (`cli.py`). This is done by adding a new subparser — **no existing code is modified**.

### Changes to `mini_agent/cli.py`

Add the following after the existing `log_parser` definition (around line 315):

```python
    # research subcommand — NEW
    research_parser = subparsers.add_parser(
        "research",
        help="Start an academic research project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bpsagent research --project ./my-study          # Start new project
  bpsagent research --project ./my-study --resume  # Resume existing project
  bpsagent research --project ./my-study --phase analyze  # Jump to phase
        """,
    )
    research_parser.add_argument(
        "--project", "-p",
        type=str,
        required=True,
        help="Project directory (created if doesn't exist)",
    )
    research_parser.add_argument(
        "--resume",
        action="store_true",
        default=False,
        help="Resume from last session checkpoint",
    )
    research_parser.add_argument(
        "--phase",
        type=str,
        choices=["plan", "collect", "analyze", "write", "review"],
        default=None,
        help="Override starting phase (default: resume from project state)",
    )
    research_parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Research topic (for new projects)",
    )
    research_parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Maximum LLM spend in USD",
    )
```

### Add handler in `main()` function (around line 840):

```python
    # Handle research subcommand — NEW
    if args.command == "research":
        from mini_agent.research.cli_handler import run_research_mode
        project_dir = Path(args.project).expanduser().absolute()
        asyncio.run(run_research_mode(
            project_dir=project_dir,
            resume=args.resume,
            phase_override=args.phase,
            topic=args.topic,
            budget_limit=args.budget,
        ))
        return
```

### New File: `mini_agent/research/cli_handler.py`

```python
"""CLI handler for research mode — bridges CLI args to ResearchOrchestrator."""

import asyncio
from datetime import datetime
from pathlib import Path

from ..agent import Agent
from ..config import Config
from ..llm import LLMClient
from ..schema import LLMProvider
from ..tools.base import Tool
from ..tools.bash_tool import BashTool, BashOutputTool, BashKillTool
from ..tools.file_tools import ReadTool, WriteTool, EditTool
from ..tools.note_tool import SessionNoteTool, RecallNoteTool
from .orchestrator import ResearchOrchestrator
from .phase_manager import ResearchPhase

from ..colors import Colors


async def run_research_mode(
    project_dir: Path,
    resume: bool = False,
    phase_override: str | None = None,
    topic: str | None = None,
    budget_limit: float | None = None,
):
    """Run the research agent in interactive mode.

    Args:
        project_dir: Root directory for the research project
        resume: Whether to resume from last checkpoint
        phase_override: Override starting phase
        topic: Research topic (for new projects)
        budget_limit: Maximum LLM spend in USD
    """
    # 1. Load configuration
    config_path = Config.get_default_config_path()
    if not config_path.exists():
        print(f"{Colors.RED}Error: Configuration file not found. Run 'bpsagent setup' first.{Colors.RESET}")
        return

    config = Config.from_yaml(config_path)

    # 2. Initialize LLM client (prefer LiteLLM for research mode)
    from ..retry import RetryConfig as RetryConfigBase

    retry_config = RetryConfigBase(
        enabled=config.llm.retry.enabled,
        max_retries=config.llm.retry.max_retries,
        initial_delay=config.llm.retry.initial_delay,
        max_delay=config.llm.retry.max_delay,
        exponential_base=config.llm.retry.exponential_base,
        retryable_exceptions=(Exception,),
    )

    # Use LiteLLM if available, fall back to configured provider
    try:
        from ..llm.litellm_client import LiteLLMClient
        llm_client = LLMClient(
            api_key=config.llm.api_key,
            provider=LLMProvider.LITELLM,
            model=config.llm.model,
            retry_config=retry_config if config.llm.retry.enabled else None,
        )
        print(f"{Colors.GREEN}Using LiteLLM provider with cost tracking{Colors.RESET}")
    except ImportError:
        provider = LLMProvider.ANTHROPIC if config.llm.provider.lower() == "anthropic" else LLMProvider.OPENAI
        llm_client = LLMClient(
            api_key=config.llm.api_key,
            provider=provider,
            api_base=config.llm.api_base,
            model=config.llm.model,
            retry_config=retry_config if config.llm.retry.enabled else None,
        )
        print(f"{Colors.YELLOW}LiteLLM not installed, using {provider.value} provider{Colors.RESET}")

    # 3. Initialize base tools (available in all phases)
    workspace_dir = str(project_dir)
    base_tools: list[Tool] = [
        BashTool(workspace_dir=workspace_dir),
        BashOutputTool(),
        BashKillTool(),
        ReadTool(workspace_dir=workspace_dir),
        WriteTool(workspace_dir=workspace_dir),
        EditTool(workspace_dir=workspace_dir),
        SessionNoteTool(memory_file=str(project_dir / ".agent_memory.json")),
        RecallNoteTool(memory_file=str(project_dir / ".agent_memory.json")),
    ]

    # 4. Load research system prompt
    system_prompt_path = Path(__file__).parent / "prompts" / "orchestrator_system.md"
    if system_prompt_path.exists():
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
    else:
        system_prompt = (
            "You are an Academic Research Agent. You help researchers conduct "
            "rigorous academic research through a structured workflow: "
            "Plan -> Collect -> Analyze -> Write -> Review.\n\n"
            "You manage the research project state, delegate to specialist "
            "sub-agents when needed, and ensure quality at every phase."
        )

    # 5. Get research config
    research_config = {}
    if hasattr(config, "research") and config.research:
        research_config = config.research.model_dump() if hasattr(config.research, "model_dump") else {}

    if budget_limit:
        research_config["budget_limit"] = budget_limit

    # 6. Create ResearchOrchestrator
    orchestrator = ResearchOrchestrator(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=base_tools,
        project_dir=workspace_dir,
        max_steps=research_config.get("max_steps", 100),
        token_limit=research_config.get("token_limit", 120000),
        config=research_config,
    )

    # 7. Handle topic for new projects
    if topic and not orchestrator.project_state.project.topic:
        orchestrator.project_state.project.topic = topic
        orchestrator.project_state.save()

    # 8. Handle phase override
    if phase_override:
        orchestrator.project_state.phase.current = phase_override
        orchestrator.project_state.save()
        # Reload tools for overridden phase
        new_tools = orchestrator.phase_manager.get_active_tools(phase_override)
        orchestrator.tools = {tool.name: tool for tool in new_tools}

    # 9. Print research banner
    _print_research_banner(orchestrator, project_dir, config.llm.model)

    # 10. Interactive loop (reuses prompt_toolkit from cli.py pattern)
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.history import FileHistory

    history_file = project_dir / ".sessions" / ".history"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    session = PromptSession(
        history=FileHistory(str(history_file)),
        auto_suggest=AutoSuggestFromHistory(),
    )

    session_start = datetime.now()

    while True:
        try:
            phase = orchestrator.project_state.phase.current
            user_input = await session.prompt_async(
                f"[{phase}] You > ",
                multiline=False,
            )
            user_input = user_input.strip()

            if not user_input:
                continue

            if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                print(f"\n{Colors.BRIGHT_YELLOW}Research session ended.{Colors.RESET}")
                _print_research_stats(orchestrator, session_start)
                break

            if user_input == "/status":
                print(orchestrator.project_state.get_summary())
                continue

            if user_input == "/phase":
                print(f"Current phase: {orchestrator.project_state.phase.current}")
                print(f"Gates passed: {orchestrator.project_state.quality.gates_passed}")
                continue

            if user_input.startswith("/cost"):
                if hasattr(llm_client, "_client") and hasattr(llm_client._client, "get_cost_report"):
                    report = llm_client._client.get_cost_report()
                    print(f"Total cost: ${report['total_cost_usd']:.4f}")
                    print(f"Calls: {report['num_calls']}")
                    if report.get("budget_remaining") is not None:
                        print(f"Budget remaining: ${report['budget_remaining']:.4f}")
                else:
                    print("Cost tracking not available with current provider.")
                continue

            if user_input == "/help":
                _print_research_help()
                continue

            # Normal conversation
            print(f"\n{Colors.BRIGHT_BLUE}Research Agent{Colors.RESET} {Colors.DIM}[{phase}] Thinking...{Colors.RESET}\n")
            orchestrator.add_user_message(user_input)

            cancel_event = asyncio.Event()
            try:
                await orchestrator.run(cancel_event=cancel_event)
            except Exception as e:
                print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")

            print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW}Research session interrupted.{Colors.RESET}")
            _print_research_stats(orchestrator, session_start)
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")


def _print_research_banner(orchestrator, project_dir, model):
    """Print research mode welcome banner."""
    state = orchestrator.project_state
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  Academic Research Agent{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
    print(f"  Project: {project_dir}")
    print(f"  Model:   {model}")
    print(f"  Phase:   {state.phase.current}")
    if state.project.topic:
        print(f"  Topic:   {state.project.topic}")
    print(f"  Tools:   {len(orchestrator.tools)} active")
    print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
    print(f"  Type /help for commands, /exit to quit\n")


def _print_research_help():
    """Print research mode help."""
    print("""
Research Mode Commands:
  /status   - Show project state summary
  /phase    - Show current phase and gates passed
  /cost     - Show LLM cost tracking
  /help     - Show this help
  /exit     - End research session
""")


def _print_research_stats(orchestrator, session_start):
    """Print session statistics."""
    duration = datetime.now() - session_start
    state = orchestrator.project_state
    print(f"\n  Session duration: {duration}")
    print(f"  Phase: {state.phase.current}")
    print(f"  Research questions: {len(state.research_questions)}")
    print(f"  Papers collected: {state.literature.total_papers_included}")
    print(f"  Analyses completed: {len(state.analyses)}")
    print()
```

---

## Section 10: Configuration Extension

### Changes to `config.yaml`

Add an optional `research:` section. The existing config loads fine without it (backward compatible).

```yaml
# ─── Existing configuration (UNCHANGED) ───────────────────────
api_key: "YOUR_API_KEY_HERE"
api_base: "https://api.minimax.io"
model: "MiniMax-M2.5"
provider: "anthropic"

max_steps: 50
workspace_dir: "./workspace"
system_prompt_path: "system_prompt.md"

retry:
  enabled: true
  max_retries: 3
  initial_delay: 1.0
  max_delay: 60.0
  exponential_base: 2.0

tools:
  enable_file_tools: true
  enable_bash: false
  enable_note: true
  enable_skills: true
  skills_dir: "./skills"
  enable_mcp: true
  mcp_config_path: "mcp.json"
  mcp:
    connect_timeout: 10.0
    execute_timeout: 60.0
    sse_read_timeout: 120.0

# ─── NEW: Research configuration (optional) ────────────────────
research:
  # LLM settings for research mode (overrides top-level if set)
  model: "anthropic/claude-sonnet-4-20250514"    # LiteLLM model identifier
  provider: "litellm"                        # Use LiteLLM for cost tracking
  fallback_models:                           # Fallback chain
    - "gpt-4o"
    - "deepseek/deepseek-chat"

  # Agent settings
  max_steps: 100                             # More steps for research tasks
  token_limit: 120000                        # Higher token limit

  # Sandbox for code execution
  sandbox_type: "local"                      # "local", "e2b", or "docker"
  e2b_api_key: ""                            # Required if sandbox_type is "e2b"

  # Budget
  budget_limit: 10.0                         # Max USD spend per session (null = unlimited)

  # Paper defaults
  paper_format: "latex"                      # "latex" or "markdown"
  target_word_count: 8000
  citation_style: "apa"                      # "apa", "chicago", "ieee"

  # MCP servers for research tools (loaded in addition to base MCP)
  research_mcp_config: "research_mcp.json"
```

### Changes to `mini_agent/config.py`

Add `ResearchConfig` model and optional field to `Config`:

```python
# Add after ToolsConfig class (around line 83):

class ResearchConfig(BaseModel):
    """Research mode configuration (optional)."""
    model: str | None = None
    provider: str = "litellm"
    fallback_models: list[str] = Field(default_factory=list)
    max_steps: int = 100
    token_limit: int = 120000
    sandbox_type: str = "local"
    e2b_api_key: str = ""
    budget_limit: float | None = None
    paper_format: str = "latex"
    target_word_count: int = 8000
    citation_style: str = "apa"
    research_mcp_config: str = "research_mcp.json"


# Modify Config class to add optional research field:

class Config(BaseModel):
    """Main configuration class"""
    llm: LLMConfig
    agent: AgentConfig
    tools: ToolsConfig
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    research: ResearchConfig | None = None  # <-- ADD THIS LINE
```

And in `from_yaml()`, add parsing (around line 215):

```python
        # Parse research configuration (optional)
        research_data = data.get("research")
        research_config = None
        if research_data:
            research_config = ResearchConfig(**research_data)

        return cls(
            llm=llm_config,
            agent=agent_config,
            tools=tools_config,
            logging=logging_config,
            tracing=tracing_config,
            research=research_config,  # <-- ADD THIS
        )
```

---

## Section 11: Step-by-Step Implementation Order

### Phase 0: Foundation (Days 1-2)

```
Step 1: Create the package structure
    mkdir -p mini_agent/research/{prompts,tools,dspy_modules,config}
    touch mini_agent/research/__init__.py
    touch mini_agent/research/tools/__init__.py
    touch mini_agent/research/dspy_modules/__init__.py
    touch mini_agent/research/config/__init__.py
    touch mini_agent/research/prompts/__init__.py

Step 2: Implement ProjectState (project_state.py)
    - All Pydantic models (ProjectMetadata, ResearchQuestion, etc.)
    - YAML load/save logic
    - get_summary() method
    TEST: Create a ProjectState, save to YAML, reload, verify round-trip

Step 3: Implement ResearchWorkspace (workspace.py)
    - Directory structure properties
    - ensure_structure() method
    TEST: Create workspace, verify all directories exist

Step 4: Implement SessionResumeManager (session_resume.py)
    - Checkpoint save/load
    - Resume context generation
    TEST: Create checkpoint, reload, verify context string
```

### Phase 1: Core Orchestration (Days 3-5)

```
Step 5: Implement PhaseManager (phase_manager.py)
    - ResearchPhase enum
    - PHASE_TOOLS and GATE_CRITERIA dicts
    - get_active_tools() (initially return base tools only)
    - get_phase_prompt() with fallback prompts
    - can_transition()
    TEST: Verify tool lists per phase, transition validation

Step 6: Implement QualityGateEvaluator (quality_gate.py)
    - GateResult dataclass
    - evaluate() method with LLM-based assessment
    - _parse_evaluation() response parser
    TEST: Mock LLM response, verify gate pass/fail logic

Step 7: Implement ResearchOrchestrator (orchestrator.py)
    - __init__ with all component wiring
    - _build_phase_prompt()
    - enter_phase()
    - run() override with session persistence
    TEST: Create orchestrator, verify it initializes and runs basic agent loop

Step 8: Implement specialist delegation
    - _create_specialist()
    - delegate_to_specialist()
    - _build_specialist_task()
    TEST: Create a specialist, verify it has correct tools and prompt
```

### Phase 2: LiteLLM Integration (Days 6-7)

```
Step 9: Add LITELLM to LLMProvider enum
    - Edit mini_agent/schema/schema.py (1 line)
    TEST: Verify enum value exists

Step 10: Implement LiteLLMClient (llm/litellm_client.py)
    - Full implementation with cost tracking
    - Fallback model support
    - Budget limits
    TEST: Call generate() with a simple prompt, verify response format

Step 11: Wire LiteLLM into LLMClient wrapper
    - Edit mini_agent/llm/llm_wrapper.py (add elif branch)
    TEST: Create LLMClient with provider="litellm", verify it works

Step 12: Verify backward compatibility
    - Run existing BPS agent with provider="anthropic"
    - Run existing BPS agent with provider="openai"
    - Verify both still work identically
    TEST: Run full integration test with existing config
```

### Phase 3: Research Tools (Days 8-12)

```
Step 13: Implement PythonREPLTool (research/tools/python_repl.py)
    - Local subprocess execution
    - E2B integration (optional)
    TEST: Execute "print(1+1)", verify output "2"

Step 14: Implement LiteratureSearchTool (research/tools/literature_search.py)
    - Semantic Scholar API integration
    - Result formatting
    TEST: Search "machine learning", verify structured results

Step 15: Implement CitationManagerTool (research/tools/citation_manager.py)
    - BibTeX add/list/search/format
    TEST: Add entry, list entries, search by keyword

Step 16: Implement StatisticalAnalysisTool (research/tools/statistical_analysis.py)
    - Code generation for common tests
    - Delegation to PythonREPLTool
    TEST: Run descriptive_stats on a sample CSV

Step 17: Implement VisualizationTool (research/tools/visualization.py)
    - Chart generation via matplotlib/seaborn
    - Save to figures/ directory
    TEST: Generate a scatter plot, verify PNG file created

Step 18: Implement PaperWriterTool (research/tools/paper_writer.py)
    - Section drafting and editing
    - LaTeX and Markdown output
    TEST: Draft an introduction section, verify file created

Step 19: Implement QualityGateTool (research/tools/quality_gate_tool.py)
    - Agent-callable wrapper for QualityGateEvaluator
    TEST: Call tool, verify it returns gate result

Step 20: Implement DataLoaderTool (research/tools/data_loader.py)
    - CSV/Excel/JSON loading
    - Data preview and summary
    TEST: Load a CSV, verify summary output

Step 21: Wire all tools into PhaseManager
    - Update _ensure_tools_initialized() with all tool instances
    TEST: Verify get_active_tools("analyze") returns correct tool set
```

### Phase 4: CLI and Configuration (Days 13-14)

```
Step 22: Add ResearchConfig to config.py
    - ResearchConfig Pydantic model
    - Optional field in Config
    - Parsing in from_yaml()
    TEST: Load config with and without research section

Step 23: Add research subcommand to cli.py
    - New subparser
    - Handler in main()
    TEST: Run `bpsagent research --help`, verify output

Step 24: Implement cli_handler.py
    - run_research_mode() function
    - Interactive loop with phase-aware prompt
    - /status, /phase, /cost commands
    TEST: Start research mode, verify banner and prompt

Step 25: Write phase-specific system prompts
    - orchestrator_system.md
    - plan_phase.md, collect_phase.md, etc.
    TEST: Verify prompts load correctly
```

### Phase 5: DSPy Integration (Days 15-17)

```
Step 26: Implement DSPy signatures (dspy_modules/signatures.py)
    - GenerateResearchQuestions
    - SynthesizeLiterature
    - DesignMethodology
    - InterpretResults
    TEST: Verify signatures compile

Step 27: Implement DSPy modules
    - ResearchQuestionGenerator
    - LiteratureSynthesizer
    - MethodologyDesigner
    - ResultsInterpreter
    TEST: Run each module with sample input

Step 28: Create DSPy Tool wrappers
    - DSPyResearchQuestionTool
    - (Optional) Other DSPy tool wrappers
    TEST: Call tool.execute(), verify ToolResult output

Step 29: Implement optimizer.py (offline optimization)
    - Training data format
    - Optimization workflow
    - Model saving/loading
    TEST: Run optimization with 5 training examples
```

### Phase 6: Integration Testing (Days 18-20)

```
Step 30: End-to-end test: New project creation
    - bpsagent research --project /tmp/test-study --topic "test"
    - Verify workspace structure created
    - Verify project.yaml initialized

Step 31: End-to-end test: Planning phase
    - Define research questions
    - Search literature
    - Pass quality gate
    - Transition to collect phase

Step 32: End-to-end test: Full workflow
    - Run through all 5 phases
    - Verify state persistence across simulated sessions
    - Verify quality gates enforce criteria

Step 33: Backward compatibility test
    - Run `bpsagent` (no subcommand) — must work identically
    - Run `bpsagent --task "test"` — must work identically
    - Run `bpsagent setup` — must work identically

Step 34: Performance and cost test
    - Run research session with budget limit
    - Verify cost tracking accuracy
    - Verify budget enforcement
```

### Verification Checklist

Before considering the implementation complete, verify:

- [ ] `bpsagent` (no args) works identically to before
- [ ] `bpsagent --task "cari data inflasi"` works identically
- [ ] `bpsagent setup` works identically
- [ ] `bpsagent research --project ./test --topic "test"` starts research mode
- [ ] Project workspace structure is created correctly
- [ ] project.yaml persists and reloads correctly
- [ ] Phase transitions work with quality gates
- [ ] All 8 research tools execute successfully
- [ ] LiteLLM cost tracking reports accurate costs
- [ ] Session resume works across separate invocations
- [ ] Sub-agent delegation works for at least 2 specialist roles
- [ ] No existing tests are broken

---

## Appendix A: File Sizes and Complexity Estimates

| File | Estimated Lines | Complexity |
|------|----------------|------------|
| `research/__init__.py` | 15 | Low |
| `research/orchestrator.py` | 350 | High |
| `research/phase_manager.py` | 300 | Medium |
| `research/project_state.py` | 250 | Medium |
| `research/workspace.py` | 120 | Low |
| `research/session_resume.py` | 200 | Medium |
| `research/quality_gate.py` | 150 | Medium |
| `research/cli_handler.py` | 200 | Medium |
| `research/tools/python_repl.py` | 150 | Medium |
| `research/tools/literature_search.py` | 120 | Medium |
| `research/tools/citation_manager.py` | 130 | Low |
| `research/tools/statistical_analysis.py` | 150 | Medium |
| `research/tools/visualization.py` | 120 | Medium |
| `research/tools/paper_writer.py` | 150 | Medium |
| `research/tools/quality_gate_tool.py` | 80 | Low |
| `research/tools/data_loader.py` | 120 | Low |
| `research/dspy_modules/signatures.py` | 60 | Low |
| `research/dspy_modules/research_question.py` | 40 | Low |
| `research/dspy_modules/optimizer.py` | 100 | Medium |
| `llm/litellm_client.py` | 200 | Medium |
| **Total new code** | **~3,000** | |
| **Existing code modified** | **~20 lines** | |

## Appendix B: Dependency Additions

Add to `pyproject.toml` or `requirements.txt`:

```
# Required for research mode
litellm>=1.40.0          # Unified LLM interface with cost tracking
aiohttp>=3.9.0           # Async HTTP for Semantic Scholar API
pyyaml>=6.0              # Already a dependency (for project.yaml)
pydantic>=2.0            # Already a dependency (for ProjectState)

# Optional (for specific features)
dspy-ai>=2.5.0           # DSPy optimization (optional)
e2b-code-interpreter>=0.0.11  # E2B sandbox (optional)
bibtexparser>=2.0        # Advanced BibTeX parsing (optional)

# Already installed (used by research tools)
# pandas, numpy, scipy, statsmodels, scikit-learn
# matplotlib, seaborn
```

## Appendix C: MCP Server Configuration for Research

### File: `mini_agent/config/research_mcp.json`

```json
{
  "mcpServers": {
    "paper-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/paper-search-mcp"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"],
      "env": {}
    }
  }
}
```

---

*End of Implementation Guide. Follow the steps in Section 11 sequentially. Each step builds on the previous one. Test after every step.*
