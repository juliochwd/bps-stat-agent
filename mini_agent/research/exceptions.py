"""Research-specific exceptions for the BPS Academic Research Agent.

Provides a structured hierarchy of exceptions for precise error handling
across all research phases: planning, data collection, analysis, writing,
and review.  Every exception carries an optional ``details`` dict for
machine-readable context alongside the human-readable message.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class ResearchError(Exception):
    """Base exception for all research-related errors.

    Args:
        message: Human-readable error description.
        details: Optional machine-readable context dict.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


# ---------------------------------------------------------------------------
# Phase errors
# ---------------------------------------------------------------------------


class PhaseTransitionError(ResearchError):
    """Invalid phase transition attempted.

    Raised when the orchestrator tries to move to a phase that is not
    reachable from the current phase (e.g. jumping from PLAN to WRITE
    without completing COLLECT and ANALYZE).
    """


class PhasePrerequisiteError(ResearchError):
    """Phase prerequisites not met.

    Raised when a phase's entry conditions (e.g. minimum data sources,
    approved analysis plan) have not been satisfied.
    """


# ---------------------------------------------------------------------------
# Project errors
# ---------------------------------------------------------------------------


class ProjectNotFoundError(ResearchError):
    """Project workspace or state file not found.

    Raised when attempting to load a ``project.yaml`` that does not exist
    at the expected workspace path.
    """


class ProjectAlreadyExistsError(ResearchError):
    """Project already exists at the specified path."""


class ProjectStateCorruptedError(ResearchError):
    """Project state file is corrupted or cannot be parsed."""


# ---------------------------------------------------------------------------
# Quality & validation errors
# ---------------------------------------------------------------------------


class QualityGateError(ResearchError):
    """Quality gate check failed.

    Raised when one or more quality-gate criteria are not met and the
    gate is configured to block progression.
    """


class ValidationError(ResearchError):
    """Data or input validation failed.

    Raised for schema mismatches, out-of-range values, or any structural
    validation failure that is *not* specific to a statistical test.
    """


# ---------------------------------------------------------------------------
# Tool errors
# ---------------------------------------------------------------------------


class ToolNotAvailableError(ResearchError):
    """Tool exists but is not available in the current phase.

    Raised when the agent attempts to invoke a tool that is registered
    but not loaded for the active research phase.
    """


class ToolNotFoundError(ResearchError):
    """Requested tool not found in the registry."""


class DependencyMissingError(ResearchError):
    """Required external dependency is not installed.

    Args:
        package: Name of the missing package.
        install_hint: Shell command to install the package.
    """

    def __init__(self, package: str, install_hint: str = "") -> None:
        hint = f" Install with: {install_hint}" if install_hint else ""
        super().__init__(f"Required package '{package}' is not installed.{hint}")
        self.package = package
        self.install_hint = install_hint


# ---------------------------------------------------------------------------
# Sandbox / execution errors
# ---------------------------------------------------------------------------


class SandboxExecutionError(ResearchError):
    """Sandboxed code execution failed.

    Raised when a Python/R script executed inside the analysis sandbox
    returns a non-zero exit code or raises an unhandled exception.
    """


class SandboxTimeoutError(SandboxExecutionError):
    """Sandbox execution exceeded the configured timeout."""


# ---------------------------------------------------------------------------
# Citation / literature errors
# ---------------------------------------------------------------------------


class CitationVerificationError(ResearchError):
    """Citation verification failed.

    Raised when a citation cannot be verified against external APIs
    (Semantic Scholar, CrossRef, OpenAlex) in strict-verification mode.
    """


class CitationNotFoundError(CitationVerificationError):
    """Citation could not be located in any external database."""


class BibTeXError(ResearchError):
    """BibTeX parsing or writing error."""


class APIRateLimitError(ResearchError):
    """External API rate limit exceeded."""


# ---------------------------------------------------------------------------
# Writing / template errors
# ---------------------------------------------------------------------------


class TemplateNotFoundError(ResearchError):
    """Journal template not found.

    Raised when the requested LaTeX/Typst template identifier does not
    match any template in the ``templates/`` directory.
    """


class CompilationError(ResearchError):
    """LaTeX or Typst compilation failed.

    Raised when the document compiler exits with errors.  The ``details``
    dict typically contains ``{"log": "<compiler output>"}``.
    """


# ---------------------------------------------------------------------------
# Analysis errors
# ---------------------------------------------------------------------------


class StatisticalAssumptionError(ResearchError):
    """Statistical assumption violated.

    Raised when a pre-test (normality, homoscedasticity, etc.) indicates
    that the chosen statistical method's assumptions are not met.
    """


# ---------------------------------------------------------------------------
# Gateway / LLM errors
# ---------------------------------------------------------------------------


class ModelNotAvailableError(ResearchError):
    """Requested LLM model is not available or not configured."""


class BudgetExceededError(ResearchError):
    """Project cost budget has been exceeded."""


class GatewayError(ResearchError):
    """LLM Gateway error — routing, fallback, or provider failure."""


# ---------------------------------------------------------------------------
# Approval errors
# ---------------------------------------------------------------------------


class ApprovalRequiredError(ResearchError):
    """Human approval is required before proceeding."""


class ApprovalDeniedError(ResearchError):
    """Human denied the approval request."""


# ---------------------------------------------------------------------------
# Sub-agent errors
# ---------------------------------------------------------------------------


class SubAgentError(ResearchError):
    """Base exception for sub-agent errors."""


class SubAgentTimeoutError(SubAgentError):
    """Sub-agent execution timed out."""
