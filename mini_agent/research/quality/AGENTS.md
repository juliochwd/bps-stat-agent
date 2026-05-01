<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# quality

## Purpose
Quality gate modules for the research engine. Automated verification of citations, statistical methods, writing quality, and peer review simulation. These gates run during the REVIEW phase to ensure research output meets academic standards.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Package exports: `CitationVerifier`, `StatValidator`, `PeerReviewer`, `WritingQuality` |
| `citation_verifier.py` | `CitationVerifier` — validates citation completeness, DOI resolution, format consistency (APA/IEEE) |
| `stat_validator.py` | `StatValidator` — checks statistical methods (sample size, assumptions, p-value reporting, effect sizes) |
| `peer_reviewer.py` | `PeerReviewer` — LLM-powered simulated peer review with structured feedback (strengths, weaknesses, suggestions) |
| `writing_quality.py` | `WritingQuality` — readability metrics (Flesch-Kincaid), grammar checking, academic tone verification |

## For AI Agents

### Working In This Directory
- Quality gates are invoked automatically during REVIEW phase by `ResearchOrchestrator`
- Each gate returns a structured result with pass/fail status and detailed feedback
- Gates can be run independently for iterative improvement
- `PeerReviewer` uses LLM calls — costs tracked via `CostTracker`
- `WritingQuality` uses `language-tool-python` for grammar (optional dep)
- `StatValidator` checks are rule-based (no LLM needed)

### Gate Results Format
```python
@dataclass
class QualityResult:
    passed: bool
    score: float  # 0.0 - 1.0
    issues: list[str]
    suggestions: list[str]
```

### Common Patterns
- All gates accept a `workspace_path` to locate research artifacts
- Gates are idempotent — safe to re-run after fixes
- Citation verifier checks both in-text citations and bibliography entries
- Stat validator ensures reported statistics match methodology

## Dependencies

### Internal
- `mini_agent.research.llm_gateway` — LLM calls for peer review
- `mini_agent.research.models.CostTracker` — cost tracking for LLM-based gates

### External
- `language-tool-python` (optional) — grammar checking
- `textstat` (optional) — readability metrics
- `pandera` (optional) — data validation schemas

<!-- MANUAL: -->
