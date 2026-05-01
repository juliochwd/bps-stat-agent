"""Tests for mini_agent/research/exceptions.py — research exception hierarchy."""

import pytest

from mini_agent.research.exceptions import (
    APIRateLimitError,
    ApprovalDeniedError,
    ApprovalRequiredError,
    BibTeXError,
    BudgetExceededError,
    CitationNotFoundError,
    CitationVerificationError,
    CompilationError,
    DependencyMissingError,
    GatewayError,
    ModelNotAvailableError,
    PhasePrerequisiteError,
    PhaseTransitionError,
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    ProjectStateCorruptedError,
    QualityGateError,
    ResearchError,
    SandboxExecutionError,
    SandboxTimeoutError,
    StatisticalAssumptionError,
    SubAgentError,
    SubAgentTimeoutError,
    TemplateNotFoundError,
    ToolNotAvailableError,
    ToolNotFoundError,
    ValidationError,
)


class TestResearchError:
    def test_basic(self):
        err = ResearchError("something went wrong")
        assert str(err) == "something went wrong"
        assert err.details == {}

    def test_with_details(self):
        err = ResearchError("error", details={"key": "value"})
        assert err.details == {"key": "value"}

    def test_is_exception(self):
        assert issubclass(ResearchError, Exception)


class TestPhaseErrors:
    def test_phase_transition_error(self):
        err = PhaseTransitionError("Cannot jump to WRITE")
        assert isinstance(err, ResearchError)

    def test_phase_prerequisite_error(self):
        err = PhasePrerequisiteError("Need data sources")
        assert isinstance(err, ResearchError)


class TestProjectErrors:
    def test_project_not_found(self):
        err = ProjectNotFoundError("No project.yaml")
        assert isinstance(err, ResearchError)

    def test_project_already_exists(self):
        err = ProjectAlreadyExistsError("Already exists")
        assert isinstance(err, ResearchError)

    def test_project_state_corrupted(self):
        err = ProjectStateCorruptedError("Invalid YAML")
        assert isinstance(err, ResearchError)


class TestQualityErrors:
    def test_quality_gate_error(self):
        err = QualityGateError("Gate failed", details={"gate": "plan"})
        assert err.details["gate"] == "plan"

    def test_validation_error(self):
        err = ValidationError("Invalid schema")
        assert isinstance(err, ResearchError)


class TestToolErrors:
    def test_tool_not_available(self):
        err = ToolNotAvailableError("python_repl not in PLAN phase")
        assert isinstance(err, ResearchError)

    def test_tool_not_found(self):
        err = ToolNotFoundError("unknown_tool")
        assert isinstance(err, ResearchError)

    def test_dependency_missing(self):
        err = DependencyMissingError("litellm", install_hint="pip install litellm")
        assert "litellm" in str(err)
        assert "pip install litellm" in str(err)
        assert err.package == "litellm"
        assert err.install_hint == "pip install litellm"

    def test_dependency_missing_no_hint(self):
        err = DependencyMissingError("numpy")
        assert "numpy" in str(err)
        assert err.install_hint == ""


class TestSandboxErrors:
    def test_sandbox_execution_error(self):
        err = SandboxExecutionError("Script failed")
        assert isinstance(err, ResearchError)

    def test_sandbox_timeout(self):
        err = SandboxTimeoutError("Exceeded 120s")
        assert isinstance(err, SandboxExecutionError)
        assert isinstance(err, ResearchError)


class TestCitationErrors:
    def test_citation_verification(self):
        err = CitationVerificationError("Cannot verify DOI")
        assert isinstance(err, ResearchError)

    def test_citation_not_found(self):
        err = CitationNotFoundError("DOI not in any database")
        assert isinstance(err, CitationVerificationError)

    def test_bibtex_error(self):
        err = BibTeXError("Invalid BibTeX entry")
        assert isinstance(err, ResearchError)

    def test_api_rate_limit(self):
        err = APIRateLimitError("CrossRef rate limit")
        assert isinstance(err, ResearchError)


class TestWritingErrors:
    def test_template_not_found(self):
        err = TemplateNotFoundError("elsevier-v2")
        assert isinstance(err, ResearchError)

    def test_compilation_error(self):
        err = CompilationError("LaTeX failed", details={"log": "! Missing $ inserted"})
        assert err.details["log"] == "! Missing $ inserted"


class TestAnalysisErrors:
    def test_statistical_assumption(self):
        err = StatisticalAssumptionError("Normality violated")
        assert isinstance(err, ResearchError)


class TestGatewayErrors:
    def test_model_not_available(self):
        err = ModelNotAvailableError("gpt-5 not found")
        assert isinstance(err, ResearchError)

    def test_budget_exceeded(self):
        err = BudgetExceededError("$50 limit reached")
        assert isinstance(err, ResearchError)

    def test_gateway_error(self):
        err = GatewayError("All models failed")
        assert isinstance(err, ResearchError)


class TestApprovalErrors:
    def test_approval_required(self):
        err = ApprovalRequiredError("Need human approval")
        assert isinstance(err, ResearchError)

    def test_approval_denied(self):
        err = ApprovalDeniedError("User rejected")
        assert isinstance(err, ResearchError)


class TestSubAgentErrors:
    def test_sub_agent_error(self):
        err = SubAgentError("Agent failed")
        assert isinstance(err, ResearchError)

    def test_sub_agent_timeout(self):
        err = SubAgentTimeoutError("Timed out after 60s")
        assert isinstance(err, SubAgentError)
