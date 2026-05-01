"""Research Orchestrator — extends Agent with phase management.

The ResearchOrchestrator wraps the existing Agent class to add:
- Phase-gated tool loading (max 15 tools per phase)
- Project state persistence across sessions
- Phase transition with state checkpointing
- Context injection per phase
"""

from __future__ import annotations

from pathlib import Path

from ..agent import Agent
from ..llm import LLMClient
from ..tools.base import Tool
from .phase_manager import PhaseManager, ResearchPhase
from .project_state import ProjectState
from .workspace import WorkspaceScaffolder


class ResearchOrchestrator:
    """Orchestrates academic research workflow using phase-gated tool loading.

    Wraps an Agent instance and manages:
    - Which tools are visible per phase
    - Project state persistence
    - Phase transitions with context injection
    """

    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        all_tools: list[Tool],
        workspace_dir: str = "./workspace",
        max_steps: int = 50,
        token_limit: int = 80000,
    ) -> None:
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.all_tools = {tool.name: tool for tool in all_tools}
        self.workspace_dir = Path(workspace_dir)
        self.max_steps = max_steps
        self.token_limit = token_limit

        self.phase_manager = PhaseManager()
        self.project_state: ProjectState | None = None
        self._agent: Agent | None = None

        # Try to load existing project state
        try:
            self.project_state = ProjectState.load(self.workspace_dir)
            self.phase_manager.current_phase = self.project_state.phase
        except (FileNotFoundError, ValueError):
            pass  # No existing project — will be created via project_init

    def _build_agent(self) -> Agent:
        """Build an Agent instance with phase-appropriate tools.

        Returns:
            Configured Agent for the current phase
        """
        # Get tools for current phase
        active_tool_names = self.phase_manager.get_tool_names_for_phase()
        active_tools = [self.all_tools[name] for name in active_tool_names if name in self.all_tools]

        # Also include any MCP tools (they're always available)
        mcp_tools = [
            tool
            for name, tool in self.all_tools.items()
            if name not in active_tool_names and hasattr(tool, "_mcp_server")
        ]
        active_tools.extend(mcp_tools)

        # Build phase-aware system prompt
        phase_prompt = self._build_phase_prompt()

        agent = Agent(
            llm_client=self.llm_client,
            system_prompt=phase_prompt,
            tools=active_tools,
            max_steps=self.max_steps,
            workspace_dir=str(self.workspace_dir),
            token_limit=self.token_limit,
        )

        return agent

    def _build_phase_prompt(self) -> str:
        """Build system prompt with phase context injected.

        Returns:
            System prompt with phase information
        """
        phase_desc = self.phase_manager.get_phase_description()
        next_phase = self.phase_manager.get_next_phase()

        phase_context = f"\n\n## Current Research Phase\n**{phase_desc}**\n"

        if next_phase:
            next_desc = self.phase_manager.get_phase_description(next_phase)
            phase_context += f"\nNext phase: {next_desc}\n"
            phase_context += "Use `switch_phase` tool when current phase objectives are met.\n"

        if self.project_state:
            phase_context += f"\n{self.project_state.get_progress_summary()}\n"

        return self.system_prompt + phase_context

    def init_project(
        self,
        title: str,
        template: str = "elsevier",
        target_journal: str = "",
        research_questions: list[str] | None = None,
    ) -> ProjectState:
        """Initialize a new research project.

        Args:
            title: Research paper title
            template: Journal template
            target_journal: Target journal name
            research_questions: Initial research questions

        Returns:
            Created ProjectState
        """
        self.project_state = ProjectState.create_new(
            title=title,
            template=template,
            target_journal=target_journal,
            research_questions=research_questions,
        )

        # Scaffold workspace
        scaffolder = WorkspaceScaffolder(self.workspace_dir)
        scaffolder.scaffold(self.project_state)

        return self.project_state

    def switch_phase(self, target_phase: ResearchPhase) -> str:
        """Switch to a different research phase.

        Saves current state, transitions phase, rebuilds agent.

        Args:
            target_phase: Phase to switch to

        Returns:
            Status message
        """
        if not self.phase_manager.can_transition_to(target_phase):
            return f"Already in phase {target_phase.value}"

        old_phase = self.phase_manager.current_phase

        # Save state before transition
        if self.project_state:
            self.project_state.transition_phase(target_phase)
            self.project_state.save(self.workspace_dir)

        self.phase_manager.current_phase = target_phase

        # Rebuild agent with new phase tools
        self._agent = None  # Force rebuild on next run

        return (
            f"Phase transition: {old_phase.value.upper()} → {target_phase.value.upper()}\n"
            f"{self.phase_manager.get_phase_description()}"
        )

    async def run(self, user_message: str | None = None, cancel_event=None) -> str:
        """Run the research agent for one interaction.

        Args:
            user_message: User's message/query
            cancel_event: Optional cancellation event

        Returns:
            Agent's response
        """
        # Build or rebuild agent if needed
        if self._agent is None:
            self._agent = self._build_agent()

        if user_message:
            self._agent.add_user_message(user_message)

        return await self._agent.run(cancel_event=cancel_event)

    def get_status(self) -> str:
        """Get current research status.

        Returns:
            Formatted status string
        """
        if not self.project_state:
            return "No active research project. Use `project_init` to create one."

        return self.project_state.get_progress_summary()
