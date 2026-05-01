<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# research — Academic Research Engine

## Purpose

Academic research engine that extends the BPS Stat Agent with a phase-gated workflow for conducting full research projects. Manages the complete lifecycle from planning through writing and peer review, with sub-agent delegation, quality gates, multi-session persistence, cost tracking, and LaTeX compilation.

Activated via `bpsagent research --title "Paper Title" --template elsevier`.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports: `PhaseManager`, `ProjectState`, `WorkspaceScaffolder`, `ResearchPhase`, `ResearchError`, `RESEARCH_VERSION`. |
| `orchestrator.py` | **`ResearchOrchestrator`** — wraps `Agent` with phase-gated tool loading (max 15 tools per phase). Manages project state persistence, phase transitions with context injection, and workspace scaffolding. Loads existing `ProjectState` from workspace on init. |
| `phase_manager.py` | **`PhaseManager`** — defines 5 research phases and their tool allowlists. Core tools always available: `read_file`, `write_file`, `edit_file`, `bash`, `project_status`, `switch_phase`, `record_note`, `recall_notes`. Phase-specific tools: PLAN (project_init, literature_search), COLLECT (citation_manager, document tools, embeddings), ANALYZE (stats, regression, visualization, EDA), WRITE (write_section, compile, tables, diagrams), REVIEW (verify_citations, peer_review, grammar, style). |
| `project_state.py` | **`ProjectState`** — persistent project metadata via YAML serialization. Tracks: current `ResearchPhase`, phase history, research questions (`ResearchQuestion` with status), data inventory, literature state, paper writing progress (sections with `SectionStatus`), quality gate results. Enums: `ResearchPhase` (PLAN/COLLECT/ANALYZE/WRITE/REVIEW), `SectionStatus` (PENDING/IN_PROGRESS/DRAFT_V1/DRAFT_V2/FINAL), `QuestionStatus` (PENDING/IN_PROGRESS/ANSWERED). |
| `workspace.py` | **`WorkspaceScaffolder`** — creates standard directory structure: `data/raw`, `data/processed`, `data/cache`, `literature/papers`, `literature/summaries`, `analysis/scripts`, `analysis/results`, `analysis/figures`, `writing/sections`, `writing/compiled`, `review`, `checkpoints`. Creates initial files: `references.bib`, `.gitignore`, `.gitkeep` placeholders. |
| `constants.py` | Research-wide constants. `RESEARCH_VERSION = "1.0.0"`. Token/step limits (120K tokens, 100 steps). Phase ordering. Tool limits (15/phase, 5 persistent). Supported templates: ieee, elsevier, springer, springer_lncs, mdpi, apa7. Supported methodologies: panel_data, cross_sectional, time_series, mixed_methods, meta_analysis. Journal template metadata (class, bst, columns, font_size). IMRaD sections. Workspace dirs. APA formatting rules. Supported data/figure formats. API rate limits. Cache TTL. Embedding dimensions (768). Chunk size (768 tokens, 128 overlap). Quality gate thresholds (max_unverified_citations=0, plagiarism<5%, min_citation_confidence=0.85, min_statistical_power=0.80). Model routing rules per task type. |
| `llm_gateway.py` | Multi-model LLM routing. Primary/fallback model selection per task type (planning, literature_search, data_analysis, writing, review, summarization, embedding). Cost tracking integration. |
| `sub_agents.py` | Sub-agent system for specialized tasks. Delegates literature review, statistical analysis, and writing to focused sub-agents with task-specific system prompts. |
| `session_resume.py` | Cross-session continuity. Save/restore agent state between sessions for long-running research projects. |
| `approval_gates.py` | Human-in-the-loop approval gates. Required for phase transitions and critical decisions (configurable via `auto_phase_transition` in config). |
| `tool_registry.py` | Phase-aware tool registry. Controls which tools are visible to the LLM per research phase. Enforces max 15 tools per phase limit. |
| `exceptions.py` | `ResearchError` base exception and subclasses for research-specific error handling. |
| `apa_formatter.py` | APA citation and number formatting utilities. Date format, decimal places, readability targets per section. |
| `_dspy_compat.py` | DSPy compatibility layer for optimizable research workflows. Graceful fallback when DSPy not installed. |

## Subdirectories

| Directory | Description |
|-----------|-------------|
| `models/` | Data models: `DecisionLog` (audit trail for major decisions), `CostTracker` (LLM spend tracking with budget enforcement). |
| `quality/` | Quality gate modules: `StatValidator` (statistical assumption checking), `WritingQuality` (readability, coherence), `PeerReviewer` (AI peer review simulation), `CitationVerifier` (DOI validation, retraction checks). |
| `dspy_modules/` | DSPy signatures and modules for structured research tasks. `signatures.py` defines input/output schemas. `modules.py` implements optimizable pipelines. |
| `writing/` | Writing pipeline: `SectionWriter` (LaTeX section generation), `TemplateRegistry` (journal template management), `Bibliography` (BibTeX management), `LaTeXCompiler` (pdflatex/xelatex compilation). |

## For AI Agents

### Working In This Directory

- Research mode activated via `bpsagent research --title "Paper Title" --template elsevier`
- Phases are strictly ordered: **PLAN -> COLLECT -> ANALYZE -> WRITE -> REVIEW**
- Each phase has a tool allowlist (max 15 tools) — tools outside current phase are hidden from LLM
- Core tools (read/write/edit/bash/project_status/switch_phase/notes) are always available regardless of phase
- Phase transitions require explicit approval (configurable via `auto_phase_transition` in config)
- Project state persisted as YAML in workspace `project.yaml` — enables multi-session research projects
- Sub-agents handle specialized tasks (e.g., literature search, statistical analysis)
- Quality gates run automatically: citation verification, statistical validation, writing quality checks
- Cost tracking enforces `max_cost_per_project` budget limit (default $50)
- Model routing: different LLM models for different task types (e.g., GPT-4o for literature search, Claude for writing)

### Architecture
```
bpsagent research --title "..." --template elsevier
  |
ResearchOrchestrator (orchestrator.py)
  |-- PhaseManager -- current phase + allowed tools (max 15)
  |-- ProjectState -- persistent state (YAML)
  |-- Agent (wrapped) -- tool-use loop with phase-filtered tools
  |-- Sub-agents -- specialized task delegation
  +-- Quality gates -- automated verification
  |
Phases:
  PLAN     -> project_init, literature_search, convert_document, get_skill
  COLLECT  -> literature_search, citation_manager, verify_citations, document tools, embeddings, knowledge_graph
  ANALYZE  -> python_repl, descriptive_stats, regression, time_series, hypothesis_test, bayesian, causal, survival, visualization, EDA
  WRITE    -> write_section, compile_paper, generate_table, generate_diagram, tikz, grammar, style, readability
  REVIEW   -> verify_citations, peer_review, stat_validation, writing_quality, plagiarism, reproducibility
```

### Testing Requirements

- Test phase transitions (valid and invalid sequences)
- Test tool allowlist enforcement per phase
- Test project state serialization/deserialization (YAML round-trip)
- Test workspace scaffolding (directory creation, initial files)
- Test quality gate thresholds
- Test cost tracking budget enforcement
- Mock LLM calls in sub-agent tests
- Use temporary directories for workspace tests

### Common Patterns

- `ProjectState.create_new(title, template, target_journal)` initializes a new research project
- `ProjectState.load(workspace_dir)` restores from existing `project.yaml`
- `WorkspaceScaffolder(workspace_dir).scaffold(state)` creates the directory structure
- Phase transitions: `PhaseManager.transition_to(phase)` with approval gate
- Decision log records all major decisions for audit trail
- Templates: ieee, elsevier, springer, springer_lncs, mdpi, apa7
- Quality thresholds defined in `constants.py:QUALITY_GATE_THRESHOLDS`

## Dependencies

### Internal
- `mini_agent.agent.Agent` — core agent loop (wrapped by orchestrator)
- `mini_agent.llm.LLMClient` — LLM calls
- `mini_agent.tools.base.Tool` — tool interface
- `mini_agent.config.ResearchConfig` — research configuration

### External (research-core)
- `numpy`, `pandas` — data manipulation
- `scipy`, `statsmodels`, `scikit-learn` — statistical analysis
- `matplotlib`, `seaborn` — visualization

### External (research-writing)
- `bibtexparser`, `habanero` — citation management
- `pylatex`, `python-docx` — document generation

### External (research-llm)
- `litellm` — multi-model routing
- `dspy-ai` — optimizable research pipelines

### External (research-quality)
- `language-tool-python` — grammar checking
- `pandera` — data validation

### External (research-sandbox)
- `docker` — containerized code execution
- `RestrictedPython` — sandboxed Python fallback
