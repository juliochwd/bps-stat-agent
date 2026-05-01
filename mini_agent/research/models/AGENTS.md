<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# models

## Purpose
Data models for research project tracking. Provides audit trail logging (DecisionLog) and LLM cost tracking (CostTracker) used throughout the research workflow.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Package exports: `DecisionLog`, `CostTracker` |
| `decision_log.py` | `DecisionLog` — records research decisions with rationale, phase, timestamp for audit trail |
| `cost_tracker.py` | `CostTracker` — tracks LLM API costs per model/phase, enforces budget limits (`max_cost_per_project`) |

## For AI Agents

### Working In This Directory
- `DecisionLog` entries are append-only — never modify past decisions
- `CostTracker` raises `ResearchError` when budget exceeded
- Both models persist to JSON in the project workspace directory
- Used by `ResearchOrchestrator` to maintain project accountability

### Key Interfaces
```python
# Decision logging
log = DecisionLog(workspace_path)
log.record(phase="ANALYZE", decision="Use OLS regression", rationale="...")
log.get_decisions(phase="ANALYZE")  # Filter by phase

# Cost tracking
tracker = CostTracker(max_cost=10.0)
tracker.record_usage(model="claude-sonnet-4-20250514", tokens=1500, cost=0.003)
tracker.total_cost  # Current spend
tracker.check_budget()  # Raises if exceeded
```

## Dependencies

### Internal
- `mini_agent.research.exceptions` — `ResearchError` for budget violations
- `mini_agent.research.constants` — default limits

### External
- `pydantic` — model validation

<!-- MANUAL: -->
