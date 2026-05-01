"""Phase-aware tool registration and loading.

Manages all available tools and controls which tools are visible to the
LLM at each research phase.  Core tools are always available regardless
of the active phase.  Enforces the ``MAX_TOOLS_PER_PHASE`` constraint.
"""

from __future__ import annotations

from ..tools.base import Tool
from .constants import MAX_TOOLS_PER_PHASE
from .project_state import ResearchPhase


class ToolRegistry:
    """Registry that manages tools with phase-aware loading.

    Tools can be registered as phase-specific (available only during
    certain phases) or as core tools (always available).  The registry
    validates that the total number of tools per phase does not exceed
    ``MAX_TOOLS_PER_PHASE``.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._phase_tools: dict[ResearchPhase, list[str]] = {phase: [] for phase in ResearchPhase}
        self._core_tools: set[str] = set()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        tool: Tool,
        phases: list[str] | None = None,
    ) -> None:
        """Register a tool, optionally binding it to specific phases.

        If ``phases`` is ``None`` the tool is registered as a core tool
        (always available in every phase).  Otherwise it is bound only
        to the listed phases.

        Args:
            tool: The tool instance to register.
            phases: Phase names during which this tool is available.
                    Pass ``None`` to register as a core (always-on) tool.

        Raises:
            ValueError: If adding the tool would exceed
                ``MAX_TOOLS_PER_PHASE`` for any target phase.
        """
        self._tools[tool.name] = tool

        if phases is None:
            # Register as core tool (always available)
            self._core_tools.add(tool.name)
            return

        for phase_name in phases:
            phase = self._resolve_phase(phase_name)
            if phase is None:
                continue

            if tool.name not in self._phase_tools[phase]:
                # Validate max tools constraint
                current_count = self.get_phase_tool_count(phase.value)
                if current_count >= MAX_TOOLS_PER_PHASE:
                    raise ValueError(
                        f"Cannot register tool '{tool.name}' for phase "
                        f"'{phase.value}': would exceed limit of "
                        f"{MAX_TOOLS_PER_PHASE} tools per phase "
                        f"(current: {current_count})."
                    )
                self._phase_tools[phase].append(tool.name)

    # ------------------------------------------------------------------
    # Phase-aware retrieval
    # ------------------------------------------------------------------

    def get_tools_for_phase(self, phase: str) -> list[Tool]:
        """Get all tools available during a specific phase.

        Returns core tools followed by phase-specific tools, with no
        duplicates.

        Args:
            phase: The research phase name (e.g. ``"plan"``).

        Returns:
            Ordered list of Tool instances (core first, then
            phase-specific).
        """
        resolved = self._resolve_phase(phase)
        seen: set[str] = set()
        result: list[Tool] = []

        # Core tools first
        for name in sorted(self._core_tools):
            if name in self._tools and name not in seen:
                result.append(self._tools[name])
                seen.add(name)

        # Phase-specific tools
        if resolved is not None:
            for name in self._phase_tools.get(resolved, []):
                if name in self._tools and name not in seen:
                    result.append(self._tools[name])
                    seen.add(name)

        return result

    def get_all_tools(self) -> list[Tool]:
        """Get all registered tools regardless of phase.

        Returns:
            List of all Tool instances.
        """
        return list(self._tools.values())

    def get_tool_by_name(self, name: str) -> Tool | None:
        """Look up a single tool by name.

        Args:
            name: Tool name to look up.

        Returns:
            The Tool instance, or ``None`` if not found.
        """
        return self._tools.get(name)

    # ------------------------------------------------------------------
    # Unregistration
    # ------------------------------------------------------------------

    def unregister(self, tool_name: str) -> None:
        """Remove a tool from the registry entirely.

        Removes the tool from all phase lists and the core set.

        Args:
            tool_name: Name of the tool to remove.
        """
        self._tools.pop(tool_name, None)
        self._core_tools.discard(tool_name)

        for phase in ResearchPhase:
            phase_list = self._phase_tools.get(phase, [])
            if tool_name in phase_list:
                phase_list.remove(tool_name)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_phase_tool_count(self, phase: str) -> int:
        """Count the total tools available in a phase.

        Includes both core tools and phase-specific tools (no
        double-counting).

        Args:
            phase: Phase name.

        Returns:
            Number of unique tools available in the phase.
        """
        resolved = self._resolve_phase(phase)
        names: set[str] = set(self._core_tools)

        if resolved is not None:
            names.update(self._phase_tools.get(resolved, []))

        # Only count tools that are actually registered
        return sum(1 for n in names if n in self._tools)

    def list_all(self) -> dict[str, list[str]]:
        """List all registered tools grouped by phase.

        Returns:
            Dict mapping phase name to list of tool names.
            Includes a ``"core"`` key for always-available tools.
        """
        result: dict[str, list[str]] = {
            "core": sorted(self._core_tools),
        }
        for phase in ResearchPhase:
            result[phase.value] = list(self._phase_tools.get(phase, []))
        return result

    @property
    def tool_count(self) -> int:
        """Total number of unique registered tools.

        Returns:
            Count of all registered tools.
        """
        return len(self._tools)

    # ------------------------------------------------------------------
    # Phase loading / unloading (lifecycle hooks)
    # ------------------------------------------------------------------

    def load_phase(self, phase: str) -> list[Tool]:
        """Load tools for a phase (returns the active tool set).

        Convenience wrapper around ``get_tools_for_phase`` that can be
        called during phase transitions.

        Args:
            phase: The phase to load tools for.

        Returns:
            List of Tool instances active for the phase.
        """
        return self.get_tools_for_phase(phase)

    def unload_phase(self, phase: str) -> None:
        """Unload phase-specific tools (lifecycle hook).

        This method exists as a lifecycle hook for phase transitions.
        The registry itself is stateless with respect to "loaded"
        phases, but subclasses or wrappers may override this to
        release resources.

        Args:
            phase: The phase being exited.
        """
        # No-op: the registry doesn't hold "loaded" state.
        pass

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_phase(phase: str | ResearchPhase) -> ResearchPhase | None:
        """Resolve a phase name string to a ``ResearchPhase`` enum.

        Args:
            phase: Phase name or enum value.

        Returns:
            The resolved ``ResearchPhase``, or ``None`` if invalid.
        """
        if isinstance(phase, ResearchPhase):
            return phase

        try:
            return ResearchPhase(phase.lower())
        except ValueError:
            return None
