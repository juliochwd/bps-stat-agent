<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# bps-master-workspace

## Purpose
Evaluation workspace for the BPS Master skill. Contains iteration-based evaluation runs comparing baseline agent performance against skill-enhanced performance on real BPS data queries.

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `iteration-1/` | First evaluation iteration (3 eval cases: inflation-ntt, gdp-national, hdi-ntt) |
| `iteration-2/` | Second evaluation iteration (refined prompts and skill content) |

## For AI Agents

### Working In This Directory
- Each iteration contains `eval-N-{topic}/` directories with `baseline/` and `with_skill/` comparisons
- `baseline/` — agent output WITHOUT the bps-master skill loaded
- `with_skill/` — agent output WITH the bps-master skill loaded
- `outputs/` subdirectories contain the actual agent responses
- Use these to measure skill effectiveness and iterate on skill content
- Do NOT modify completed evaluation results — create new iterations instead

### Evaluation Structure
```
iteration-N/
├── eval-0-{topic}/
│   ├── baseline/
│   │   └── outputs/     # Agent response without skill
│   └── with_skill/
│       └── outputs/     # Agent response with skill
├── eval-1-{topic}/
│   └── ...
└── summary.md           # Iteration results summary
```

## Dependencies

### Internal
- Evaluates `mini_agent/skills/bps-master/` skill effectiveness

### External
- None (evaluation artifacts)

<!-- MANUAL: -->
