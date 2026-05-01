<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# dspy_modules

## Purpose
DSPy signatures and modules for structured, optimizable research workflows. Provides declarative definitions of research tasks (literature review, hypothesis generation, analysis planning) that can be optimized via DSPy's compilation framework.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Package exports: signatures and module classes |
| `signatures.py` | DSPy `Signature` definitions — input/output specs for research tasks (e.g., `LiteratureReview`, `HypothesisGeneration`, `AnalysisPlan`) |
| `modules.py` | DSPy `Module` implementations — composable research pipelines using signatures with chain-of-thought and retrieval |

## For AI Agents

### Working In This Directory
- DSPy is an OPTIONAL dependency (`research-llm` extra) — modules gracefully degrade without it
- `_dspy_compat.py` in parent directory provides compatibility layer
- Signatures define WHAT a research task does (inputs → outputs)
- Modules define HOW tasks are composed (chain-of-thought, retrieval-augmented)
- These can be compiled/optimized with DSPy's `BootstrapFewShot` or `MIPRO` optimizers

### DSPy Pattern
```python
# Signature (declarative)
class LiteratureReview(dspy.Signature):
    """Review literature on a research topic."""
    topic: str = dspy.InputField()
    papers: list[str] = dspy.InputField()
    synthesis: str = dspy.OutputField()
    gaps: list[str] = dspy.OutputField()

# Module (composable)
class ResearchPipeline(dspy.Module):
    def __init__(self):
        self.review = dspy.ChainOfThought(LiteratureReview)
    def forward(self, topic, papers):
        return self.review(topic=topic, papers=papers)
```

## Dependencies

### Internal
- `mini_agent.research._dspy_compat` — compatibility layer for optional DSPy

### External
- `dspy` (optional, ≥2.0) — declarative LLM programming framework

<!-- MANUAL: -->
