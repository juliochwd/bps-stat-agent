---
name: academic-research
description: Academic Research Agent — comprehensive guide for the 5-phase research workflow (PLAN → COLLECT → ANALYZE → WRITE → REVIEW) with statistical analysis, literature search, and paper writing.
tags: [research, academic, statistics, paper, journal, analysis, citation]
---

# Academic Research Skill

## Overview

This skill provides comprehensive guidance for conducting academic research using the BPS Academic Research Agent. It covers the complete workflow from research question formulation to production-ready journal paper.

## Quick Start

```
1. project_init(title="Your Paper Title", template="elsevier")
2. Follow the 5-phase workflow below
3. Use switch_phase() to transition between phases
4. Use project_status() to track progress
```

## Phase 1: PLAN

**Objective:** Define research scope, questions, methodology, and paper structure.

**Tools available:** `project_init`, `literature_search`, `project_status`, `switch_phase`

**Steps:**
1. Initialize project with `project_init`
2. Quick literature scan with `literature_search` (10-15 papers)
3. Define research questions
4. Choose methodology (get human approval)
5. Generate paper outline
6. `switch_phase(target_phase="collect")`

## Phase 2: COLLECT

**Objective:** Gather all data and literature.

**Tools available:** `literature_search`, `citation_manager`, `verify_citations`, BPS tools (62)

**Steps:**
1. Search BPS data: `bps_search`, `bps_get_data`, `bps_answer_query`
2. Deep literature search: `literature_search` (40-60 papers)
3. Add citations: `citation_manager(action="add_from_doi", doi="...")`
4. Verify all: `verify_citations(strict=true)`
5. `switch_phase(target_phase="analyze")`

## Phase 3: ANALYZE

**Objective:** Statistical analysis and visualization.

**Tools available:** `descriptive_stats`, `regression_analysis`, `hypothesis_test`, `create_visualization`

**Steps:**
1. Descriptive statistics: `descriptive_stats(data_path="data/processed/data.csv")`
2. Assumption checks: `hypothesis_test(test="shapiro_wilk", ...)`
3. Main analysis: `regression_analysis(method="ols", ...)`
4. Visualizations: `create_visualization(plot_type="scatter", ...)`
5. `switch_phase(target_phase="write")`

### Statistical Reporting (APA 7th)

| Test | Format |
|------|--------|
| t-test | *t*(df) = value, *p* = value, *d* = value |
| ANOVA | *F*(df₁, df₂) = value, *p* = value, η² = value |
| Correlation | *r*(df) = value, *p* = value |
| Chi-square | χ²(df, *N* = value) = value, *p* = value |
| Regression | *R*² = value, *F*(df₁, df₂) = value |

## Phase 4: WRITE

**Objective:** Generate paper sections following IMRaD structure.

**Paper Structure:**
1. Abstract (150-300 words)
2. Introduction (broad → narrow → gap → objectives)
3. Literature Review (thematic, every claim cited)
4. Methodology (replicable detail)
5. Results (descriptive → main → robustness)
6. Discussion (summary → interpretation → implications → limitations)
7. Conclusion (brief, no new data)

## Phase 5: REVIEW

**Objective:** Quality assurance before submission.

**Checklist:**
- [ ] All citations verified via DOI
- [ ] Statistics reported in APA format
- [ ] Effect sizes and CIs included
- [ ] Tables follow booktabs format
- [ ] Figures at 300+ DPI
- [ ] No fabricated data or citations
- [ ] Methodology sufficient for replication

## Data Accuracy Rules

1. **Never fabricate data** — only report what tools return
2. **Always cite sources** — include DOI and retrieval method
3. **Report errors transparently** — explain failures, suggest alternatives
4. **Verify all citations** — every reference must resolve via DOI
5. **Use APA formatting** — proper statistical reporting

## BPS Domain Codes

| Code | Domain |
|------|--------|
| 0000 | Nasional (National) |
| 5300 | Nusa Tenggara Timur (NTT) |
| 1100-9400 | All provinces |

For full BPS tool documentation, load: `get_skill("bps-master")`
