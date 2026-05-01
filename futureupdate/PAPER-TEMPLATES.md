# BPS Academic Research Agent — Journal Paper Templates

**Version:** 2.0  
**Created:** 2025-07-14  
**Updated:** 2025-07-15

---

## Supported Journal Templates

| Template ID | Journal Family | Class File | Columns | Citation Style |
|-------------|---------------|-----------|---------|---------------|
| `ieee` | IEEE Transactions | `IEEEtran.cls` | 2 | Numeric [1] |
| `elsevier` | Elsevier Journals | `elsarticle.cls` | 1 or 2 | Numeric or Author-year |
| `springer` | Springer Journals | `svjour3.cls` | 1 | Numeric |
| `springer_lncs` | Springer LNCS | `llncs.cls` | 1 | Numeric [1] |
| `mdpi` | MDPI Journals | `mdpi.cls` | 1 | Numeric (ACS) |
| `apa7` | APA Journals | `apa7.cls` | 1 | Author-year (Smith, 2023) |

---

## Template Specifications

### IEEE (IEEEtran)

| Property | Value |
|----------|-------|
| Paper size | US Letter (8.5" x 11") |
| Columns | Two-column |
| Column width | 88.9mm (3.5") |
| Column separation | 5.08mm (0.2") |
| Margins | Top: 0.75", Bottom: 1", Left/Right: 0.625" |
| Body font | Times Roman, 10pt |
| Title font | 24pt, centered |
| Section headings | Small caps, centered, Roman numerals |
| Subsection headings | Italic, left-aligned |
| Abstract | Bold "Abstract--" prefix, italic |
| References | 8pt font, numbered [1] |
| Figures | Single or double column width |

### Elsevier (elsarticle)

| Property | Value |
|----------|-------|
| Paper size | A4 |
| Layout models | 1p (single), 3p (wide single), 5p (double) |
| Body font | 12pt (preprint), 10pt (final) |
| Title | Bold, large |
| Authors | With affiliations, corresponding author marked |
| Abstract | Standard environment |
| Keywords | Separated by `\sep` |
| Highlights | 3-5 bullet points (optional) |
| Graphical abstract | Optional image |
| References | natbib, numbered or author-year |

### Springer (svjour3)

| Property | Value |
|----------|-------|
| Paper size | Journal-dependent |
| Layout | Single column |
| Body font | 10pt Computer Modern |
| Title | Bold, large |
| Authors | With `\institute` blocks |
| Abstract | Standard environment |
| Keywords | `\keywords{First \and Second}` |
| References | spbasic.bst (numeric) |

### Springer LNCS (llncs)

| Property | Value |
|----------|-------|
| Paper size | A4 (LNCS trim: 155mm x 235mm) |
| Layout | Single column |
| Body font | 10pt Computer Modern |
| Page limit | 16 pages (regular), 12 pages (short) |
| Title | Bold, large, centered |
| Authors | With `\inst{}` references |
| Running heads | Author names + short title |
| References | splncs04.bst (numeric) |

### MDPI

| Property | Value |
|----------|-------|
| Paper size | A4 |
| Layout | Single column |
| Body font | 10pt Palatino (mathpazo) |
| Margins | 2.54cm all sides |
| Title | 18pt bold |
| Section headings | Bold, numbered |
| Line spacing | Single |
| References | ACS-style numbered |

### APA 7th Edition

| Property | Value |
|----------|-------|
| Paper size | US Letter |
| Body font | 12pt Times New Roman |
| Margins | 1 inch all sides |
| Line spacing | Double throughout |
| Title page | Centered bold title, author, affiliation, author note |
| Headings | 5 levels (centered bold -> indented italic) |
| Abstract | 150-250 words, single paragraph |
| References | Hanging indent, double-spaced |
| Running head | Shortened title + page number |
| Tables | APA format (no vertical lines) |

---

## Typst Templates (Modern Alternative)

### Why Typst for Academic Papers

| Feature | LaTeX | Typst |
|---------|-------|-------|
| Compilation speed | 5-30s | 50-200ms |
| Syntax complexity | High (macros) | Low (scripting) |
| Package management | Manual (TeX Live) | Built-in registry |
| Error messages | Cryptic | Clear with line numbers |
| Incremental compilation | No | Yes |
| PDF output quality | Excellent | Excellent |
| Journal acceptance | Universal | Growing (preprints, theses) |

### Typst Equivalents for Each Journal

| LaTeX Template | Typst Equivalent | Registry Package |
|----------------|-----------------|-----------------|
| IEEEtran | `@preview/ieee-tran` | `typst-ieee` |
| elsarticle | `@preview/elsevier` | `typst-elsevier` |
| svjour3 | `@preview/springer-sv` | `typst-springer` |
| llncs | `@preview/lncs` | `typst-lncs` |
| mdpi | Custom template | (use general academic) |
| apa7 | `@preview/apa7th` | `typst-apa` |

### Typst Template Registry Pattern

```typst
// Import from Typst package registry
#import "@preview/ieee-tran:0.1.0": ieee

#show: ieee.with(
  title: "Analysis of Regional Economic Inequality in Indonesia",
  authors: (
    (
      name: "First Author",
      department: "Department of Economics",
      organization: "University Name",
      email: "author@university.edu"
    ),
  ),
  abstract: [
    This paper examines the determinants of regional economic inequality
    across Indonesian provinces using panel data from 2015-2022.
  ],
  keywords: ("Gini ratio", "panel data", "Indonesia", "regional inequality"),
  bibliography: bibliography("references.bib"),
)

= Introduction

Regional economic inequality remains a persistent challenge...

= Methodology

== Data Sources

We utilize panel data from BPS (Badan Pusat Statistik) covering
34 provinces over the period 2015--2022.

== Model Specification

The fixed-effects panel regression model is specified as:

$ "Gini"_(i t) = alpha_i + beta_1 "GRDP"_(i t) + beta_2 "Inflation"_(i t) + epsilon_(i t) $

= Results

#figure(
  table(
    columns: 5,
    align: (left, center, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Variable*], [*M*], [*SD*], [*n*], [*95% CI*],
    table.hline(stroke: 0.5pt),
    [Gini Ratio], [0.38], [0.04], [272], [\[0.37, 0.39\]],
    [Inflation (%)], [3.21], [1.85], [272], [\[2.99, 3.43\]],
    [GRDP (trillion Rp)], [245.3], [312.1], [272], [\[208.0, 282.6\]],
    table.hline(stroke: 0.8pt),
  ),
  caption: [Descriptive Statistics for Study Variables],
) <tab:descriptive>

= Conclusion

The findings suggest that...
```

### Example Typst Academic Paper (Full)

```typst
// paper.typ — Complete academic paper in Typst
#set document(
  title: "Regional Inequality Determinants in Indonesia: A Panel Data Approach",
  author: "Research Team",
  date: datetime.today(),
)

// Page setup
#set page(paper: "a4", margin: 2.54cm)
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.1")

// Citation setup
#set bibliography(style: "ieee")

// Title block
#align(center)[
  #text(size: 16pt, weight: "bold")[
    Regional Inequality Determinants in Indonesia:\
    A Panel Data Approach (2015--2022)
  ]
  #v(1em)
  #text(size: 11pt)[First Author#super[1], Second Author#super[2]]
  #v(0.5em)
  #text(size: 9pt, style: "italic")[
    #super[1]Department of Economics, University A \
    #super[2]Department of Statistics, University B
  ]
]

#v(1em)

// Abstract
#block(inset: (left: 2em, right: 2em))[
  *Abstract* --- This study investigates the determinants of regional
  economic inequality across 34 Indonesian provinces using panel data
  from 2015 to 2022. Employing fixed-effects regression with robust
  standard errors, we find that GRDP growth, inflation, and human
  development significantly predict Gini ratio variations.
  
  *Keywords:* Gini ratio, panel data, fixed effects, Indonesia, BPS
]

#v(1em)

= Introduction

Regional economic inequality remains one of the most pressing
development challenges in Indonesia @worldbank2023.

= Data and Methodology

== Data Sources

All data are sourced from BPS (Badan Pusat Statistik Indonesia)
via the official WebAPI.

== Econometric Model

$ Y_(i t) = alpha_i + bold(X)_(i t) bold(beta) + epsilon_(i t) $

where $Y_(i t)$ is the Gini ratio for province $i$ at time $t$.

= Results

Results of the fixed-effects estimation are presented in @tab:results.

#figure(
  table(
    columns: 4,
    align: (left, center, center, center),
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Variable*], [*Coefficient*], [*SE*], [*p-value*],
    table.hline(stroke: 0.5pt),
    [GRDP (log)], [-0.023], [(0.008)], [0.004],
    [Inflation], [0.012], [(0.005)], [0.018],
    [HDI], [-0.045], [(0.012)], [< 0.001],
    [Constant], [0.892], [(0.156)], [< 0.001],
    table.hline(stroke: 0.5pt),
    table.cell(colspan: 4)[_R_#super[2] = 0.43, _N_ = 272, _F_(3, 233) = 18.7],
    table.hline(stroke: 0.8pt),
  ),
  caption: [Fixed-Effects Panel Regression Results],
) <tab:results>

= Conclusion

Our findings demonstrate that...

#bibliography("references.bib")
```

---

## Tectonic Compilation

### Overview

Tectonic is a modernized, self-contained TeX/LaTeX engine that requires zero configuration and automatically downloads packages on demand.

| Feature | Tectonic | Traditional (TeX Live) |
|---------|----------|----------------------|
| Installation | Single binary (~25MB) | Full install (~5GB) |
| Package management | Auto-download on demand | Manual `tlmgr` |
| Configuration | Zero-config | texmf.cnf, PATH, etc. |
| Multiple passes | Automatic (bibtex, refs) | Manual (run 3x) |
| Reproducibility | Lockfile support | Version-dependent |
| CI/CD friendly | Yes (single binary) | Complex setup |

### Installation

```bash
# Linux/macOS
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# Or via cargo
cargo install tectonic

# Or via conda
conda install -c conda-forge tectonic
```

### Usage as Compilation Backend

```bash
# Basic compilation (handles all passes automatically)
tectonic paper.tex

# With specific output format
tectonic -X compile paper.tex --outfmt pdf

# Keep intermediate files for debugging
tectonic -X compile paper.tex --keep-intermediates

# Use a bundle lock for reproducibility
tectonic -X compile paper.tex --bundle-lock tectonic.lock
```

### Integration with Agent Pipeline

```python
import subprocess
import shutil
from pathlib import Path

def compile_with_tectonic(tex_path: Path, output_dir: Path = None) -> Path:
    """Compile LaTeX using Tectonic (recommended for agent use).
    
    Advantages:
    - Single command, no multiple passes needed
    - Auto-downloads any missing packages
    - Clear error messages
    - No TeX Live installation required
    """
    if output_dir is None:
        output_dir = tex_path.parent
    
    result = subprocess.run(
        ["tectonic", "-X", "compile", str(tex_path), "--outfmt", "pdf"],
        capture_output=True,
        text=True,
        cwd=str(tex_path.parent),
        timeout=120,
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Tectonic compilation failed:\n{result.stderr}")
    
    pdf_path = tex_path.with_suffix(".pdf")
    if output_dir != tex_path.parent:
        dest = output_dir / pdf_path.name
        shutil.move(str(pdf_path), str(dest))
        return dest
    return pdf_path
```

---

## Compilation Pipeline Options

```
Option A: Tectonic (recommended for agent)
  paper.tex --> tectonic --> paper.pdf
  - Single command, auto-handles bibtex/multiple passes
  - Auto-downloads packages on demand
  - No TeX Live installation needed
  - Clear error messages
  
Option B: Typst (fastest iteration)
  paper.typ --> typst compile --> paper.pdf
  - Millisecond compilation (50-200ms)
  - Clean modern syntax
  - Built-in package registry
  - Best for drafting and iteration
  
Option C: Traditional (maximum compatibility)
  paper.tex --> pdflatex + bibtex x 3 --> paper.pdf
  - pdflatex paper.tex
  - bibtex paper
  - pdflatex paper.tex
  - pdflatex paper.tex
  - Maximum journal compatibility
  - Required for some submission systems
  
Option D: Pandoc (format-agnostic)
  paper.md --> pandoc --citeproc --> paper.pdf/docx/html
  - Write in Markdown with YAML metadata
  - Output to any format (PDF, DOCX, HTML, LaTeX)
  - --citeproc handles citations from .bib
  - --template for journal-specific formatting
  - Best for multi-format submissions
```

### Pipeline Selection Logic

```python
def select_compilation_pipeline(
    source_format: str,
    target_journal: str,
    priority: str = "speed"
) -> str:
    """Select optimal compilation pipeline.
    
    Args:
        source_format: "tex", "typ", "md"
        target_journal: journal template ID
        priority: "speed", "compatibility", "flexibility"
    
    Returns:
        Pipeline identifier
    """
    # Typst: fastest for drafting
    if source_format == "typ":
        return "typst"
    
    # Pandoc: when source is markdown or multi-format needed
    if source_format == "md":
        return "pandoc"
    
    # LaTeX source
    if priority == "speed":
        return "tectonic"
    elif priority == "compatibility":
        return "traditional"
    else:
        return "tectonic"  # default for agent use


PIPELINE_COMMANDS = {
    "tectonic": ["tectonic", "-X", "compile", "{input}", "--outfmt", "pdf"],
    "typst": ["typst", "compile", "{input}", "{output}"],
    "traditional": [
        "pdflatex -interaction=nonstopmode {input}",
        "bibtex {stem}",
        "pdflatex -interaction=nonstopmode {input}",
        "pdflatex -interaction=nonstopmode {input}",
    ],
    "pandoc": [
        "pandoc", "{input}",
        "--citeproc",
        "--bibliography={bib}",
        "--template={template}",
        "-o", "{output}",
    ],
}
```

---

## Writing Quality Tools Integration

### LanguageTool Rules for Academic Writing

```python
ACADEMIC_LANGUAGETOOL_CONFIG = {
    "language": "en-US",
    "enabled_rules": [
        "PASSIVE_VOICE",           # Flag excessive passive
        "SENTENCE_WHITESPACE",     # Spacing issues
        "COMMA_PARENTHESIS_WHITESPACE",
        "EN_QUOTES",               # Smart quotes
        "MORFOLOGIK_RULE_EN_US",   # Spelling
        "UPPERCASE_SENTENCE_START",
        "EN_UNPAIRED_BRACKETS",
    ],
    "disabled_rules": [
        "WHITESPACE_RULE",         # LaTeX commands trigger this
        "COMMA_PARENTHESIS_WHITESPACE",  # Citations trigger this
    ],
    "disabled_categories": [
        "TYPOGRAPHY",  # Conflicts with LaTeX formatting
    ],
    # Custom patterns for academic writing
    "custom_rules": [
        {
            "id": "HEDGING_OVERUSE",
            "pattern": r"\b(somewhat|rather|quite|fairly|slightly)\b",
            "message": "Consider removing hedging language for stronger claims",
            "severity": "info",
        },
        {
            "id": "FIRST_PERSON_SINGULAR",
            "pattern": r"\bI\b(?!\.\w)",  # "I" not in abbreviations
            "message": "Avoid first-person singular in academic writing; use 'we' or passive",
            "severity": "warning",
        },
        {
            "id": "INFORMAL_LANGUAGE",
            "pattern": r"\b(a lot|lots of|thing|stuff|kind of|sort of|pretty much)\b",
            "message": "Replace informal language with precise academic vocabulary",
            "severity": "warning",
        },
        {
            "id": "VAGUE_QUANTIFIER",
            "pattern": r"\b(many|several|some|few|various|numerous)\b",
            "message": "Consider replacing with specific numbers or proportions",
            "severity": "info",
        },
    ],
}
```

### proselint Checks Relevant to Papers

```python
PROSELINT_ACADEMIC_CHECKS = {
    "enabled": [
        "annotations.misc",          # TODO/FIXME left in text
        "consistency.spacing",       # Inconsistent spacing
        "consistency.spelling",      # Inconsistent spelling
        "hedging.misc",             # Hedging language
        "hyperbole.misc",           # Exaggerated claims
        "jargon.misc",             # Unnecessary jargon
        "lexical_illusions.misc",   # Repeated words
        "mixed_metaphors.misc",     # Mixed metaphors
        "redundancy.misc",          # Redundant phrases
        "skunked_terms.misc",       # Contested usage
        "weasel_words.misc",        # Weasel words
    ],
    "disabled": [
        "typography.symbols",       # Conflicts with LaTeX
        "typography.exclamation",   # Rare in academic text anyway
    ],
}

def run_proselint_check(text: str) -> list[dict]:
    """Run proselint on extracted paper text."""
    import proselint
    
    suggestions = proselint.tools.lint(text)
    # Filter to academic-relevant checks
    return [
        s for s in suggestions
        if s["check"] in PROSELINT_ACADEMIC_CHECKS["enabled"]
    ]
```

### textstat Readability Targets for Academic Text

```python
ACADEMIC_READABILITY_TARGETS = {
    # Target ranges for academic papers by section
    "abstract": {
        "flesch_reading_ease": (20, 40),      # Difficult to read
        "flesch_kincaid_grade": (14, 18),      # Graduate level
        "gunning_fog": (14, 18),
        "avg_sentence_length": (20, 30),       # Words per sentence
    },
    "introduction": {
        "flesch_reading_ease": (25, 45),       # Slightly more accessible
        "flesch_kincaid_grade": (12, 16),
        "gunning_fog": (12, 16),
        "avg_sentence_length": (18, 28),
    },
    "methodology": {
        "flesch_reading_ease": (15, 35),       # Most technical
        "flesch_kincaid_grade": (14, 20),
        "gunning_fog": (14, 20),
        "avg_sentence_length": (20, 35),
    },
    "results": {
        "flesch_reading_ease": (20, 40),
        "flesch_kincaid_grade": (13, 17),
        "gunning_fog": (13, 17),
        "avg_sentence_length": (18, 28),
    },
    "discussion": {
        "flesch_reading_ease": (25, 45),       # More accessible
        "flesch_kincaid_grade": (12, 16),
        "gunning_fog": (12, 16),
        "avg_sentence_length": (18, 28),
    },
    "conclusion": {
        "flesch_reading_ease": (30, 50),       # Most accessible
        "flesch_kincaid_grade": (12, 15),
        "gunning_fog": (12, 15),
        "avg_sentence_length": (15, 25),
    },
}

def check_readability(text: str, section: str) -> dict:
    """Check readability metrics against academic targets."""
    import textstat
    
    targets = ACADEMIC_READABILITY_TARGETS.get(section, ACADEMIC_READABILITY_TARGETS["introduction"])
    
    metrics = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog": textstat.gunning_fog(text),
        "avg_sentence_length": textstat.avg_sentence_length(text),
    }
    
    issues = []
    for metric, value in metrics.items():
        low, high = targets[metric]
        if value < low:
            issues.append(f"{metric}: {value:.1f} (too low, target: {low}-{high})")
        elif value > high:
            issues.append(f"{metric}: {value:.1f} (too high, target: {low}-{high})")
    
    return {
        "section": section,
        "metrics": metrics,
        "targets": targets,
        "issues": issues,
        "pass": len(issues) == 0,
    }
```

### Custom Rules for Common Academic Mistakes

```python
ACADEMIC_MISTAKE_RULES = [
    # Citation placement
    {
        "id": "CITATION_BEFORE_PERIOD",
        "pattern": r"\.\s*\\cite\{",
        "fix": "Place citation before the period: '...results \\cite{ref}.'",
        "severity": "error",
    },
    # Number formatting
    {
        "id": "NUMBER_START_SENTENCE",
        "pattern": r"(?<=\.\s)\d+\s+\w+",
        "fix": "Spell out numbers that begin a sentence",
        "severity": "warning",
    },
    # Tense consistency
    {
        "id": "RESULTS_PAST_TENSE",
        "section": "results",
        "pattern": r"\b(show|indicate|demonstrate|reveal|suggest)s?\b",
        "fix": "Use past tense in Results section: 'showed', 'indicated'",
        "severity": "info",
    },
    # Common word confusions
    {
        "id": "AFFECT_EFFECT",
        "pattern": r"\baffect\b(?=.*\b(on|of)\b)",
        "fix": "Did you mean 'effect' (noun)? 'affect' is typically a verb.",
        "severity": "warning",
    },
    # Dangling modifiers
    {
        "id": "USING_DANGLING",
        "pattern": r"^Using\s+\w+.*,\s+(the|this|these|it)\b",
        "fix": "Possible dangling modifier. Ensure the subject performs the action.",
        "severity": "info",
    },
    # Abbreviation introduction
    {
        "id": "ABBREVIATION_NOT_INTRODUCED",
        "pattern": r"\b[A-Z]{3,}\b",
        "check": "verify_abbreviation_introduced",
        "fix": "Introduce abbreviation on first use: 'Gross Regional Domestic Product (GRDP)'",
        "severity": "warning",
    },
    # Figure/Table references
    {
        "id": "FIGURE_LOWERCASE",
        "pattern": r"\bfigure\s+\d",
        "fix": "Capitalize 'Figure' when referring to a specific figure: 'Figure 1'",
        "severity": "error",
    },
    {
        "id": "TABLE_LOWERCASE",
        "pattern": r"\btable\s+\d",
        "fix": "Capitalize 'Table' when referring to a specific table: 'Table 1'",
        "severity": "error",
    },
    # Avoid contractions
    {
        "id": "CONTRACTION",
        "pattern": r"\b(don't|won't|can't|isn't|aren't|wasn't|weren't|hasn't|haven't|didn't|shouldn't|couldn't|wouldn't)\b",
        "fix": "Avoid contractions in academic writing",
        "severity": "error",
    },
]
```

---

## Figure Standards (Enhanced)

### Figure Specifications by Journal

| Journal | Min DPI | Formats | Font | Single Col | Double Col | Max File Size |
|---------|---------|---------|------|-----------|-----------|--------------|
| IEEE | 300 | TIFF, EPS, PDF | Times New Roman | 88mm (3.5") | 181mm (7.16") | 5MB |
| Elsevier | 300 | TIFF, EPS, PDF | Arial/Helvetica | 90mm | 190mm | 10MB |
| Springer | 300 | TIFF, EPS, PDF | Helvetica | 84mm | 174mm | 10MB |
| MDPI | 300 | TIFF, EPS, PDF | Arial | 85mm | 190mm | 20MB |
| Nature | 300 | TIFF, EPS, PDF | Arial/Helvetica | 89mm | 183mm | 10MB |
| APA | 300 | TIFF, EPS | Times/Arial | 84mm | 174mm | 5MB |

### Publication-Quality Matplotlib Config (Per Journal)

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

# ============================================================
# Colorblind-friendly Okabe-Ito palette
# ============================================================
OKABE_ITO = {
    "black":    "#000000",
    "orange":   "#E69F00",
    "sky_blue": "#56B4E9",
    "green":    "#009E73",
    "yellow":   "#F0E442",
    "blue":     "#0072B2",
    "vermilion":"#D55E00",
    "purple":   "#CC79A7",
}

OKABE_ITO_CYCLE = [
    "#0072B2",  # blue
    "#D55E00",  # vermilion
    "#009E73",  # green
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#CC79A7",  # purple
    "#F0E442",  # yellow
    "#000000",  # black
]


def get_journal_rcparams(journal: str) -> dict:
    """Get matplotlib rcParams for publication-quality figures.
    
    Args:
        journal: One of 'ieee', 'elsevier', 'springer', 'mdpi', 'apa7', 'nature'
    
    Returns:
        Dictionary of rcParams to apply
    """
    # Base params (shared across all journals)
    base = {
        # Colorblind-friendly defaults
        "axes.prop_cycle": plt.cycler(color=OKABE_ITO_CYCLE),
        
        # High-quality rendering
        "figure.dpi": 150,          # Screen display
        "savefig.dpi": 600,         # Publication quality
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        
        # Clean style
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "axes.linewidth": 0.8,
        
        # Tick styling
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        
        # Legend
        "legend.frameon": False,
        "legend.fontsize": 8,
        
        # Lines
        "lines.linewidth": 1.5,
        "lines.markersize": 5,
        
        # PDF backend for vector output
        "savefig.format": "pdf",
        "pdf.fonttype": 42,         # TrueType (editable in Illustrator)
        "ps.fonttype": 42,
    }
    
    # Journal-specific overrides
    journal_configs = {
        "ieee": {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "figure.figsize": (3.5, 2.5),       # Single column
            "figure.dpi": 150,
            "savefig.dpi": 600,
        },
        "ieee_double": {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.figsize": (7.16, 4.0),      # Double column
            "savefig.dpi": 600,
        },
        "elsevier": {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.figsize": (3.54, 2.65),     # 90mm single column
            "savefig.dpi": 600,
        },
        "springer": {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.figsize": (3.31, 2.48),     # 84mm single column
            "savefig.dpi": 600,
        },
        "mdpi": {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.figsize": (3.35, 2.51),     # 85mm single column
            "savefig.dpi": 600,
        },
        "apa7": {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "figure.figsize": (6.5, 4.5),       # Full page width
            "savefig.dpi": 300,
        },
        "nature": {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica"],
            "font.size": 7,
            "axes.labelsize": 7,
            "axes.titlesize": 8,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "figure.figsize": (3.5, 2.63),      # 89mm single column
            "savefig.dpi": 600,
        },
    }
    
    config = {**base, **journal_configs.get(journal, journal_configs["elsevier"])}
    return config


def apply_journal_style(journal: str):
    """Apply journal-specific matplotlib style globally."""
    params = get_journal_rcparams(journal)
    mpl.rcParams.update(params)


def save_figure(fig, filename: str, journal: str, formats: list = None):
    """Save figure in publication-ready formats.
    
    Args:
        fig: matplotlib Figure object
        filename: Base filename (without extension)
        journal: Journal template ID
        formats: List of formats (default: ['pdf', 'tiff'])
    """
    if formats is None:
        formats = ["pdf", "tiff"]
    
    dpi_map = {
        "pdf": 600,   # Vector, DPI for rasterized elements
        "tiff": 600,
        "eps": 600,
        "png": 600,
        "svg": None,  # Vector
    }
    
    for fmt in formats:
        dpi = dpi_map.get(fmt, 600)
        save_kwargs = {"format": fmt, "bbox_inches": "tight", "pad_inches": 0.02}
        if dpi:
            save_kwargs["dpi"] = dpi
        if fmt == "tiff":
            save_kwargs["pil_kwargs"] = {"compression": "lzw"}
        
        fig.savefig(f"{filename}.{fmt}", **save_kwargs)
```

### tikzplotlib: matplotlib to TikZ for Native LaTeX Figures

```python
import tikzplotlib

def save_as_tikz(fig, filename: str, journal: str = "ieee"):
    """Convert matplotlib figure to TikZ for native LaTeX rendering.
    
    Benefits:
    - Fonts match document perfectly
    - Scales with document without quality loss
    - Editable in LaTeX source
    - Smaller file sizes
    """
    # Figure width in cm per journal
    widths = {
        "ieee": "\\columnwidth",        # 88.9mm
        "ieee_double": "\\textwidth",   # 181mm
        "elsevier": "\\columnwidth",    # 90mm
        "springer": "\\columnwidth",    # 84mm
        "mdpi": "\\columnwidth",        # 85mm
        "apa7": "\\textwidth",          # 165mm
    }
    
    tikzplotlib.save(
        f"{filename}.tex",
        figure=fig,
        axis_width=widths.get(journal, "\\columnwidth"),
        axis_height=None,  # Auto from aspect ratio
        extra_axis_parameters=[
            "tick align=outside",
            "tick pos=left",
        ],
        extra_tikzpicture_parameters=["font=\\small"],
    )
```

### Colorblind-Friendly Okabe-Ito Palette

```
Color Name    | Hex       | RGB              | Use Case
--------------+-----------+------------------+---------------------------
Black         | #000000   | (0, 0, 0)        | Primary/reference line
Orange        | #E69F00   | (230, 159, 0)    | Second category
Sky Blue      | #56B4E9   | (86, 180, 233)   | Third category
Bluish Green  | #009E73   | (0, 158, 115)    | Fourth category
Yellow        | #F0E442   | (240, 228, 66)   | Highlight (use sparingly)
Blue          | #0072B2   | (0, 114, 178)    | First/primary category
Vermilion     | #D55E00   | (213, 94, 0)     | Alert/important
Reddish Purple| #CC79A7   | (204, 121, 167)  | Additional category
```

**Usage rules:**
1. Use Blue (#0072B2) as primary color for first data series
2. Use Vermilion (#D55E00) for contrast/second series
3. Avoid Yellow (#F0E442) for thin lines (low contrast on white)
4. Combine color with shape/pattern for maximum accessibility
5. Test with color blindness simulator (e.g., Coblis)

---

## Table Standards (Enhanced)

### booktabs Format (No Vertical Lines)

```
Rules for professional academic tables:
1. NEVER use vertical lines (|)
2. ONLY use \toprule, \midrule, \bottomrule (from booktabs)
3. Use \cmidrule{a-b} for partial horizontal rules
4. Left-align text columns
5. Right-align or center numeric columns
6. Align decimal points where possible
7. Use consistent decimal places within a column
8. Table number and title ABOVE the table
9. Notes BELOW the table
10. No bold/italic in body cells (only headers)
```

### APA Table Formatting Rules

```
APA 7th Edition Table Checklist:
[ ] Table numbered sequentially (Table 1, Table 2, ...)
[ ] Title in italic below number
[ ] Column headers clearly labeled with units
[ ] Body cells: no bold, no italic (except statistical symbols)
[ ] Confidence intervals in brackets: [LL, UL]
[ ] Probability notes: *p < .05. **p < .01. ***p < .001.
[ ] General note starts with "Note."
[ ] Specific notes use superscript letters (a, b, c)
[ ] No vertical lines
[ ] Horizontal lines: top, below header, bottom only
[ ] Single-spaced within table (even in double-spaced manuscript)
```

### pandas DataFrame to LaTeX Table Generator

```python
import pandas as pd
import numpy as np
from typing import Optional

def dataframe_to_latex_table(
    df: pd.DataFrame,
    caption: str,
    label: str,
    note: str = None,
    journal: str = "apa7",
    decimal_places: dict = None,
    highlight_significant: bool = True,
    p_col: str = None,
) -> str:
    """Convert pandas DataFrame to publication-ready LaTeX table.
    
    Args:
        df: DataFrame with data
        caption: Table caption
        label: LaTeX label (e.g., 'tab:results')
        note: Table note (APA style)
        journal: Target journal for formatting
        decimal_places: Dict mapping column names to decimal places
        highlight_significant: Add significance stars
        p_col: Column containing p-values (for significance stars)
    
    Returns:
        Complete LaTeX table string
    """
    # Format numeric columns
    formatted_df = df.copy()
    if decimal_places:
        for col, places in decimal_places.items():
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: f"{x:.{places}f}" if pd.notna(x) else ""
                )
    
    # Add significance stars
    if highlight_significant and p_col and p_col in df.columns:
        stars = df[p_col].apply(lambda p: 
            "***" if p < 0.001 else
            "**" if p < 0.01 else
            "*" if p < 0.05 else ""
        )
        # Append stars to coefficient column (first numeric column)
        coef_col = [c for c in df.columns if c != p_col and df[c].dtype in ['float64', 'int64']][0]
        formatted_df[coef_col] = formatted_df[coef_col].astype(str) + stars
    
    # Column alignment
    alignments = []
    for col in formatted_df.columns:
        if formatted_df[col].dtype == 'object' or col == formatted_df.columns[0]:
            alignments.append("l")
        else:
            alignments.append("c")
    align_str = "".join(alignments)
    
    # Build LaTeX
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")
    
    if journal == "apa7":
        lines.append("\\small")
    
    lines.append(f"\\begin{{tabular}}{{{align_str}}}")
    lines.append("\\toprule")
    
    # Header
    header = " & ".join([f"\\textbf{{{col}}}" for col in formatted_df.columns])
    lines.append(f"{header} \\\\")
    lines.append("\\midrule")
    
    # Body
    for _, row in formatted_df.iterrows():
        row_str = " & ".join([str(v) for v in row.values])
        lines.append(f"{row_str} \\\\")
    
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    
    # Notes
    if note:
        lines.append("\\begin{tablenotes}")
        lines.append("\\small")
        lines.append(f"\\item \\textit{{Note.}} {note}")
        if highlight_significant:
            lines.append("\\item $*p < .05$. $**p < .01$. $***p < .001$.")
        lines.append("\\end{tablenotes}")
    
    lines.append("\\end{table}")
    
    return "\n".join(lines)
```

### Regression Results Table Template

```python
def regression_table(
    models: list[dict],
    caption: str = "Regression Results",
    label: str = "tab:regression",
    dv_name: str = "Dependent Variable",
) -> str:
    """Generate a multi-model regression results table.
    
    Args:
        models: List of dicts with keys:
            - name: Model name (e.g., "Model 1")
            - coefficients: Dict[var_name, (coef, se, p)]
            - r_squared: float
            - adj_r_squared: float
            - n: int
            - f_stat: (F, p)
    
    Returns:
        LaTeX table string
    """
    # Collect all variables across models
    all_vars = []
    for model in models:
        for var in model["coefficients"]:
            if var not in all_vars:
                all_vars.append(var)
    
    n_models = len(models)
    col_align = "l" + "c" * n_models
    
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")
    lines.append(f"\\begin{{tabular}}{{{col_align}}}")
    lines.append("\\toprule")
    
    # Header
    header = f"& " + " & ".join([f"\\textbf{{{m['name']}}}" for m in models])
    lines.append(f"{header} \\\\")
    lines.append(f"& " + " & ".join([f"({i+1})" for i in range(n_models)]) + " \\\\")
    lines.append("\\midrule")
    
    # Coefficients
    for var in all_vars:
        coef_row = [var]
        se_row = [""]
        for model in models:
            if var in model["coefficients"]:
                coef, se, p = model["coefficients"][var]
                stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                coef_row.append(f"{coef:.3f}{stars}")
                se_row.append(f"({se:.3f})")
            else:
                coef_row.append("")
                se_row.append("")
        
        lines.append(" & ".join(coef_row) + " \\\\")
        lines.append(" & ".join(se_row) + " \\\\[3pt]")
    
    # Model statistics
    lines.append("\\midrule")
    
    # R-squared
    r2_row = ["$R^2$"] + [f"{m['r_squared']:.3f}" for m in models]
    lines.append(" & ".join(r2_row) + " \\\\")
    
    # Adjusted R-squared
    adj_r2_row = ["Adj. $R^2$"] + [f"{m['adj_r_squared']:.3f}" for m in models]
    lines.append(" & ".join(adj_r2_row) + " \\\\")
    
    # N
    n_row = ["$N$"] + [f"{m['n']}" for m in models]
    lines.append(" & ".join(n_row) + " \\\\")
    
    # F-statistic
    f_row = ["$F$"] + [f"{m['f_stat'][0]:.2f}" for m in models]
    lines.append(" & ".join(f_row) + " \\\\")
    
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\begin{tablenotes}")
    lines.append("\\small")
    lines.append(f"\\item \\textit{{Note.}} {dv_name}. Standard errors in parentheses.")
    lines.append("\\item $*p < .05$. $**p < .01$. $***p < .001$.")
    lines.append("\\end{tablenotes}")
    lines.append("\\end{table}")
    
    return "\n".join(lines)
```

### Descriptive Statistics Table Template

```python
def descriptive_stats_table(
    df: pd.DataFrame,
    variables: list[str],
    caption: str = "Descriptive Statistics",
    label: str = "tab:descriptive",
    include_ci: bool = True,
    include_skew_kurt: bool = False,
) -> str:
    """Generate APA-formatted descriptive statistics table.
    
    Args:
        df: DataFrame with raw data
        variables: List of column names to describe
        caption: Table caption
        label: LaTeX label
        include_ci: Include 95% confidence intervals
        include_skew_kurt: Include skewness and kurtosis
    """
    from scipy import stats
    
    # Compute statistics
    rows = []
    for var in variables:
        data = df[var].dropna()
        row = {
            "Variable": var,
            "M": data.mean(),
            "SD": data.std(),
            "Min": data.min(),
            "Max": data.max(),
            "n": len(data),
        }
        if include_ci:
            ci = stats.t.interval(0.95, len(data)-1, loc=data.mean(), scale=stats.sem(data))
            row["95% CI"] = f"[{ci[0]:.2f}, {ci[1]:.2f}]"
        if include_skew_kurt:
            row["Skew"] = data.skew()
            row["Kurt"] = data.kurtosis()
        rows.append(row)
    
    stats_df = pd.DataFrame(rows)
    
    # Format
    decimal_places = {"M": 2, "SD": 2, "Min": 2, "Max": 2, "Skew": 2, "Kurt": 2}
    
    return dataframe_to_latex_table(
        stats_df,
        caption=caption,
        label=label,
        note="CI = confidence interval.",
        journal="apa7",
        decimal_places=decimal_places,
    )
```

---

## Statistical Reporting (APA 7th)

### Complete Formatting Rules for All Test Types

| Test | Format | Example |
|------|--------|---------|
| t-test (independent) | *t*(df) = value, *p* = value, *d* = value | *t*(58) = 2.87, *p* = .006, *d* = 0.74 |
| t-test (paired) | *t*(df) = value, *p* = value, *d* = value | *t*(29) = 3.41, *p* = .002, *d* = 0.62 |
| One-way ANOVA | *F*(df_b, df_w) = value, *p* = value, eta_p^2 = value | *F*(2, 117) = 4.52, *p* = .013, eta_p^2 = .07 |
| Two-way ANOVA | *F*(df_1, df_2) = value, *p* = value, eta_p^2 = value | *F*(1, 96) = 8.23, *p* = .005, eta_p^2 = .08 |
| Pearson correlation | *r*(df) = value, *p* = value | *r*(200) = .81, *p* < .001 |
| Spearman correlation | *r_s*(N) = value, *p* = value | *r_s*(150) = .67, *p* < .001 |
| Chi-square (GoF) | chi^2(df) = value, *p* = value | chi^2(4) = 12.53, *p* = .014 |
| Chi-square (independence) | chi^2(df, *N* = value) = value, *p* = value, *V* = value | chi^2(6, *N* = 200) = 24.53, *p* = .002, *V* = .35 |
| Linear regression | *R*^2 = value, *F*(df_1, df_2) = value, *p* = value | *R*^2 = .43, *F*(3, 268) = 67.8, *p* < .001 |
| Logistic regression | *OR* = value, 95% CI [LL, UL], *p* = value | *OR* = 2.34, 95% CI [1.45, 3.78], *p* = .001 |
| Mann-Whitney U | *U* = value, *p* = value, *r* = value | *U* = 1234, *p* = .023, *r* = .31 |
| Wilcoxon signed-rank | *T* = value, *p* = value, *r* = value | *T* = 45, *p* = .008, *r* = .42 |
| Kruskal-Wallis | *H*(df) = value, *p* = value | *H*(2) = 8.67, *p* = .013 |
| Mixed-effects model | *b* = value, SE = value, *t* = value, *p* = value | *b* = 0.45, SE = 0.12, *t* = 3.75, *p* < .001 |

### Python Formatter Functions

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StatResult:
    """Container for a statistical test result."""
    test_type: str
    statistic: float
    df: tuple  # (df1,) or (df1, df2)
    p_value: float
    effect_size: Optional[float] = None
    effect_size_type: Optional[str] = None  # "d", "eta_p_sq", "r", "V", "OR"
    ci: Optional[tuple] = None  # (lower, upper)
    n: Optional[int] = None


def format_p_value(p: float) -> str:
    """Format p-value per APA 7th rules.
    
    Rules:
    - No leading zero (p cannot exceed 1)
    - If p < .001, report as '< .001'
    - Otherwise, report exact value to 3 decimal places
    - Never report p = .000
    """
    if p < 0.001:
        return "< .001"
    else:
        return f"= {p:.3f}".replace("= 0.", "= .")


def format_stat_no_leading_zero(value: float, decimals: int = 2) -> str:
    """Format a statistic that cannot exceed 1 (no leading zero).
    
    Used for: p-values, correlations, R^2, proportions, eta^2
    """
    formatted = f"{value:.{decimals}f}"
    if formatted.startswith("0."):
        formatted = formatted[1:]  # Remove leading zero
    elif formatted.startswith("-0."):
        formatted = "-" + formatted[2:]  # Remove leading zero from negative
    return formatted


def format_stat_with_leading_zero(value: float, decimals: int = 2) -> str:
    """Format a statistic that can exceed 1 (keep leading zero).
    
    Used for: means, SDs, t-values, F-values, chi-square, Cohen's d
    """
    return f"{value:.{decimals}f}"


def format_t_test(t: float, df: int, p: float, d: float = None) -> str:
    """Format t-test result in APA style.
    
    Example: t(58) = 2.87, p = .006, d = 0.74
    """
    result = f"*t*({df}) = {format_stat_with_leading_zero(t)}, *p* {format_p_value(p)}"
    if d is not None:
        result += f", *d* = {format_stat_with_leading_zero(d)}"
    return result


def format_anova(f: float, df_between: int, df_within: int, p: float, 
                 eta_sq: float = None) -> str:
    """Format ANOVA result in APA style.
    
    Example: F(2, 117) = 4.52, p = .013, eta_p^2 = .07
    """
    result = f"*F*({df_between}, {df_within}) = {format_stat_with_leading_zero(f)}, *p* {format_p_value(p)}"
    if eta_sq is not None:
        result += f", $\\eta_p^2$ = {format_stat_no_leading_zero(eta_sq)}"
    return result


def format_correlation(r: float, df: int, p: float, 
                       corr_type: str = "pearson") -> str:
    """Format correlation result in APA style.
    
    Example: r(200) = .81, p < .001
    """
    symbol = "*r*" if corr_type == "pearson" else "*r_s*"
    result = f"{symbol}({df}) = {format_stat_no_leading_zero(r)}, *p* {format_p_value(p)}"
    return result


def format_chi_square(chi2: float, df: int, p: float, 
                      n: int = None, v: float = None) -> str:
    """Format chi-square result in APA style.
    
    Example: chi^2(6, N = 200) = 24.53, p = .002, V = .35
    """
    if n:
        result = f"$\\chi^2$({df}, *N* = {n}) = {format_stat_with_leading_zero(chi2)}"
    else:
        result = f"$\\chi^2$({df}) = {format_stat_with_leading_zero(chi2)}"
    result += f", *p* {format_p_value(p)}"
    if v is not None:
        result += f", *V* = {format_stat_no_leading_zero(v)}"
    return result


def format_regression(r_sq: float, f: float, df1: int, df2: int, p: float,
                      adj_r_sq: float = None) -> str:
    """Format regression model result in APA style.
    
    Example: R^2 = .43, F(3, 268) = 67.8, p < .001
    """
    result = f"*R*$^2$ = {format_stat_no_leading_zero(r_sq)}"
    if adj_r_sq is not None:
        result += f" (adj. *R*$^2$ = {format_stat_no_leading_zero(adj_r_sq)})"
    result += f", *F*({df1}, {df2}) = {format_stat_with_leading_zero(f)}, *p* {format_p_value(p)}"
    return result


def format_regression_coefficient(b: float, se: float, t: float, p: float,
                                   beta: float = None, ci: tuple = None) -> str:
    """Format individual regression coefficient.
    
    Example: b = 0.45, SE = 0.12, t = 3.75, p < .001, beta = .32
    """
    result = f"*b* = {format_stat_with_leading_zero(b)}, SE = {format_stat_with_leading_zero(se)}"
    result += f", *t* = {format_stat_with_leading_zero(t)}, *p* {format_p_value(p)}"
    if beta is not None:
        result += f", $\\beta$ = {format_stat_no_leading_zero(beta)}"
    if ci is not None:
        result += f", 95% CI [{ci[0]:.2f}, {ci[1]:.2f}]"
    return result


def format_odds_ratio(or_val: float, ci: tuple, p: float) -> str:
    """Format odds ratio (logistic regression).
    
    Example: OR = 2.34, 95% CI [1.45, 3.78], p = .001
    """
    return f"*OR* = {format_stat_with_leading_zero(or_val)}, 95% CI [{ci[0]:.2f}, {ci[1]:.2f}], *p* {format_p_value(p)}"


def format_ci(lower: float, upper: float, level: int = 95) -> str:
    """Format confidence interval.
    
    Example: 95% CI [4.32, 7.26]
    """
    return f"{level}% CI [{lower:.2f}, {upper:.2f}]"


def format_descriptive(mean: float, sd: float, n: int = None) -> str:
    """Format descriptive statistics.
    
    Example: M = 4.52, SD = 1.23
    """
    result = f"*M* = {mean:.2f}, *SD* = {sd:.2f}"
    if n is not None:
        result += f", *n* = {n}"
    return result
```

### Decimal Place Rules

| Statistic Type | Decimal Places | Leading Zero | Examples |
|---------------|---------------|-------------|----------|
| Means, SDs | 2 | Yes | *M* = 4.52, *SD* = 1.23 |
| Correlations | 2 | No | *r* = .81, *r* = -.23 |
| Proportions | 2 | No | .45, .03 |
| *p*-values | 3 (exact) | No | *p* = .042, *p* < .001 |
| *R*^2, eta^2 | 2 | No | *R*^2 = .43, eta^2 = .07 |
| Cohen's *d* | 2 | Yes | *d* = 0.74 |
| *t*-values | 2 | Yes | *t* = 2.87 |
| *F*-values | 2 | Yes | *F* = 4.52 |
| chi^2 values | 2 | Yes | chi^2 = 24.53 |
| *b* coefficients | 2-3 | Yes | *b* = 0.453 |
| beta weights | 2 | No | beta = .32 |
| Odds ratios | 2 | Yes | *OR* = 2.34 |
| CI bounds | 2 | Yes | [4.32, 7.26] |
| Percentages | 1 | Yes | 45.3% |
| df | 0 (integer) | Yes | df = 58 |

### Italicization Rules

**Italicize (statistical symbols):**
- *M* (mean), *SD* (standard deviation)
- *F* (F-ratio), *t* (t-statistic)
- *p* (probability), *N* (total sample), *n* (subsample)
- *r* (correlation), *R*^2 (coefficient of determination)
- *d* (Cohen's d), *OR* (odds ratio)
- *df* (degrees of freedom)
- *b* (unstandardized coefficient)
- *SE* (standard error), *CI* (confidence interval)
- *z* (z-score), *U* (Mann-Whitney)

**Do NOT italicize:**
- Greek letters: alpha, beta, eta^2, chi^2, epsilon, lambda
- Abbreviations that are not statistics: ANOVA, MANOVA, SD (when spelled out)
- Subscripts/superscripts that are identifiers: R^2_adj, F_change

### Effect Size Reporting Requirements

| Test | Required Effect Size | Interpretation |
|------|---------------------|----------------|
| t-test | Cohen's *d* | Small: 0.2, Medium: 0.5, Large: 0.8 |
| ANOVA | eta_p^2 or omega^2 | Small: .01, Medium: .06, Large: .14 |
| Correlation | *r* (is its own effect size) | Small: .10, Medium: .30, Large: .50 |
| Chi-square | Cramer's *V* | Small: .10, Medium: .30, Large: .50 |
| Regression | *R*^2, *f*^2 | Small: .02, Medium: .15, Large: .35 |
| Logistic regression | *OR* | Small: 1.5, Medium: 2.5, Large: 4.0 |
| Non-parametric | *r* = Z/sqrt(N) | Small: .10, Medium: .30, Large: .50 |

---

## LaTeX Preamble Templates

### IEEE

```latex
\documentclass[journal]{IEEEtran}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{hyperref}

\begin{document}
\title{Paper Title}
\author{\IEEEauthorblockN{First Author}
\IEEEauthorblockA{Department\\University\\City, Country\\email@uni.edu}}
\maketitle

\begin{abstract}
Abstract text.
\end{abstract}

\begin{IEEEkeywords}
keyword1, keyword2, keyword3
\end{IEEEkeywords}

\section{Introduction}
% Content...

\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
```

### Elsevier

```latex
\documentclass[preprint,12pt]{elsarticle}
\usepackage{natbib}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{lineno}

\journal{Journal Name}

\begin{document}
\begin{frontmatter}
\title{Paper Title}
\author[1]{First Author\corref{cor1}}
\ead{author@university.edu}
\author[2]{Second Author}
\cortext[cor1]{Corresponding author}
\affiliation[1]{organization={Department}, city={City}, country={Country}}
\affiliation[2]{organization={Department}, city={City}, country={Country}}

\begin{abstract}
Abstract text.
\end{abstract}

\begin{keyword}
keyword1 \sep keyword2 \sep keyword3
\end{keyword}
\end{frontmatter}

\section{Introduction}
% Content...

\bibliographystyle{elsarticle-num}
\bibliography{references}
\end{document}
```

### Springer (svjour3)

```latex
\documentclass[smallextended]{svjour3}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{hyperref}

\journalname{Journal Name}

\begin{document}
\title{Paper Title}
\author{First Author \and Second Author}
\institute{F. Author \at Department, University \\ \email{author@uni.edu}
\and S. Author \at Department, University}

\maketitle

\begin{abstract}
Abstract text.
\keywords{First \and Second \and Third}
\end{abstract}

\section{Introduction}
% Content...

\bibliographystyle{spbasic}
\bibliography{references}
\end{document}
```

### Springer LNCS

```latex
\documentclass[runningheads]{llncs}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{hyperref}

\begin{document}
\title{Paper Title}
\titlerunning{Short Title}
\author{First Author\inst{1}\orcidID{0000-0000-0000-0000} \and
Second Author\inst{2}}
\authorrunning{F. Author et al.}
\institute{University One, City, Country \\ \email{author@uni.edu} \and
University Two, City, Country}

\maketitle

\begin{abstract}
Abstract text.
\keywords{First keyword \and Second keyword \and Third keyword}
\end{abstract}

\section{Introduction}
% Content...

\bibliographystyle{splncs04}
\bibliography{references}
\end{document}
```

### MDPI

```latex
\documentclass[journal,article,submit,pdftex]{mdpi}
\usepackage{booktabs}

\Title{Paper Title}
\Author{First Author $^{1,*}$ and Second Author $^{2}$}
\AuthorNames{First Author and Second Author}
\address{%
$^{1}$ \quad Department, University, City, Country; \\
$^{2}$ \quad Department, University, City, Country}
\corres{Correspondence: author@uni.edu}

\abstract{Abstract text (200 words max).}
\keyword{keyword1; keyword2; keyword3}

\begin{document}
\section{Introduction}
% Content...

\end{document}
```

### APA 7

```latex
\documentclass[man,12pt]{apa7}
\usepackage[american]{babel}
\usepackage{csquotes}
\usepackage[style=apa,backend=biber]{biblatex}
\addbibresource{references.bib}

\title{Paper Title}
\shorttitle{Short Title}
\author{First Author}
\affiliation{University}
\authornote{Author note...}

\abstract{Abstract text (150-250 words).}
\keywords{keyword1, keyword2, keyword3}

\begin{document}
\maketitle

\section{Introduction}
% Content...

\printbibliography
\end{document}
```

---

## Template Registry (Python)

```python
JOURNAL_TEMPLATES = {
    "ieee": {
        "class": "IEEEtran",
        "options": ["journal"],
        "bst": "IEEEtran",
        "packages": ["cite", "amsmath", "amssymb", "amsfonts", "algorithmic",
                     "graphicx", "textcomp", "xcolor", "booktabs"],
        "columns": 2,
        "font_size": 10,
        "paper": "letterpaper",
        "citation_style": "numeric",
        "abstract_style": "bold_prefix",  # "Abstract--"
        "keywords_env": "IEEEkeywords",
        "author_format": "IEEEauthorblockN",
        "section_style": "roman_caps",  # I. INTRODUCTION
        # Figure specs
        "figure_single_col_mm": 88.9,
        "figure_double_col_mm": 181.0,
        "figure_font": "Times New Roman",
        "figure_min_dpi": 300,
        "figure_formats": ["tiff", "eps", "pdf"],
        # Compilation
        "preferred_pipeline": "tectonic",
        "bibtex_required": True,
        # Typst equivalent
        "typst_package": "@preview/ieee-tran:0.1.0",
        "typst_show_rule": "ieee.with",
    },
    "elsevier": {
        "class": "elsarticle",
        "options": ["preprint", "12pt"],  # or "5p" for 2-column
        "bst": "elsarticle-num",
        "packages": ["natbib", "graphicx", "amsmath", "booktabs",
                     "hyperref", "lineno"],
        "columns": 1,
        "font_size": 12,
        "paper": "a4paper",
        "citation_style": "numeric",
        "has_graphical_abstract": True,
        "has_highlights": True,
        "has_keywords_sep": True,  # \sep between keywords
        "frontmatter": True,  # \begin{frontmatter}...\end{frontmatter}
        # Figure specs
        "figure_single_col_mm": 90.0,
        "figure_double_col_mm": 190.0,
        "figure_font": "Arial",
        "figure_min_dpi": 300,
        "figure_formats": ["tiff", "eps", "pdf"],
        # Compilation
        "preferred_pipeline": "tectonic",
        "bibtex_required": True,
        # Typst equivalent
        "typst_package": "@preview/elsevier:0.1.0",
        "typst_show_rule": "elsevier.with",
    },
    "springer": {
        "class": "svjour3",
        "options": ["smallextended"],
        "bst": "spbasic",
        "packages": ["graphicx", "amsmath", "booktabs", "hyperref"],
        "columns": 1,
        "font_size": 10,
        "paper": "a4paper",
        "citation_style": "numeric",
        "has_institute": True,
        "keywords_command": "keywords",
        "keywords_separator": "\\and",
        # Figure specs
        "figure_single_col_mm": 84.0,
        "figure_double_col_mm": 174.0,
        "figure_font": "Helvetica",
        "figure_min_dpi": 300,
        "figure_formats": ["tiff", "eps", "pdf"],
        # Compilation
        "preferred_pipeline": "tectonic",
        "bibtex_required": True,
        # Typst equivalent
        "typst_package": "@preview/springer-sv:0.1.0",
        "typst_show_rule": "springer.with",
    },
    "springer_lncs": {
        "class": "llncs",
        "options": ["runningheads"],
        "bst": "splncs04",
        "packages": ["graphicx", "amsmath", "booktabs", "hyperref"],
        "columns": 1,
        "font_size": 10,
        "paper": "a4paper",
        "page_limit": 16,
        "citation_style": "numeric",
        "has_orcid": True,
        "has_running_heads": True,
        "keywords_separator": "\\and",
        # Figure specs
        "figure_single_col_mm": 84.0,
        "figure_double_col_mm": 122.0,  # LNCS text width
        "figure_font": "Helvetica",
        "figure_min_dpi": 300,
        "figure_formats": ["tiff", "eps", "pdf"],
        # Compilation
        "preferred_pipeline": "tectonic",
        "bibtex_required": True,
        # Typst equivalent
        "typst_package": "@preview/lncs:0.1.0",
        "typst_show_rule": "lncs.with",
    },
    "mdpi": {
        "class": "mdpi",
        "options": ["journal", "article", "submit", "pdftex"],
        "bst": None,  # Uses internal
        "packages": [],  # mdpi.cls loads most
        "columns": 1,
        "font_size": 10,
        "font_family": "mathpazo",  # Palatino
        "paper": "a4paper",
        "citation_style": "numeric",
        # Figure specs
        "figure_single_col_mm": 85.0,
        "figure_double_col_mm": 190.0,
        "figure_font": "Arial",
        "figure_min_dpi": 300,
        "figure_formats": ["tiff", "eps", "pdf", "png"],
        # Compilation
        "preferred_pipeline": "tectonic",
        "bibtex_required": False,  # Internal handling
        # Typst equivalent
        "typst_package": None,  # Use custom template
        "typst_show_rule": None,
    },
    "apa7": {
        "class": "apa7",
        "options": ["man", "12pt"],  # man=manuscript, jou=journal, doc=document
        "bst": None,  # Uses biblatex
        "biblatex_style": "apa",
        "biblatex_backend": "biber",
        "packages": ["babel", "csquotes", "biblatex"],
        "columns": 1,
        "font_size": 12,
        "paper": "letterpaper",
        "citation_style": "authoryear",
        "line_spacing": "double",
        "has_running_head": True,
        "has_author_note": True,
        "has_keywords": True,
        # Figure specs
        "figure_single_col_mm": 84.0,
        "figure_double_col_mm": 174.0,
        "figure_font": "Times New Roman",
        "figure_min_dpi": 300,
        "figure_formats": ["tiff", "eps"],
        # Compilation
        "preferred_pipeline": "tectonic",
        "bibtex_required": False,  # Uses biber
        "biber_required": True,
        # Typst equivalent
        "typst_package": "@preview/apa7th:0.1.0",
        "typst_show_rule": "apa.with",
        # APA-specific formatting
        "heading_levels": 5,
        "abstract_word_limit": (150, 250),
        "table_style": "apa",  # No vertical lines, specific note format
        "stat_reporting": "apa7",  # Use APA 7th stat formatting
    },
}


# ============================================================
# Typst template registry
# ============================================================
TYPST_TEMPLATES = {
    "ieee": {
        "package": "@preview/ieee-tran:0.1.0",
        "show_rule": "ieee.with",
        "params": {
            "title": str,
            "authors": "list[dict]",  # [{name, department, organization, email}]
            "abstract": str,
            "keywords": "tuple[str]",
            "bibliography": "bibliography('refs.bib')",
        },
        "page_setup": {"paper": "us-letter", "columns": 2},
    },
    "elsevier": {
        "package": "@preview/elsevier:0.1.0",
        "show_rule": "elsevier.with",
        "params": {
            "title": str,
            "authors": "list[dict]",
            "abstract": str,
            "keywords": "tuple[str]",
            "journal": str,
            "bibliography": "bibliography('refs.bib')",
        },
        "page_setup": {"paper": "a4", "columns": 1},
    },
    "springer": {
        "package": "@preview/springer-sv:0.1.0",
        "show_rule": "springer.with",
        "params": {
            "title": str,
            "authors": "list[dict]",
            "abstract": str,
            "keywords": "tuple[str]",
            "bibliography": "bibliography('refs.bib')",
        },
        "page_setup": {"paper": "a4", "columns": 1},
    },
    "lncs": {
        "package": "@preview/lncs:0.1.0",
        "show_rule": "lncs.with",
        "params": {
            "title": str,
            "short_title": str,
            "authors": "list[dict]",
            "abstract": str,
            "keywords": "tuple[str]",
            "bibliography": "bibliography('refs.bib')",
        },
        "page_setup": {"paper": "a4", "columns": 1},
    },
    "apa7": {
        "package": "@preview/apa7th:0.1.0",
        "show_rule": "apa.with",
        "params": {
            "title": str,
            "running_head": str,
            "authors": "list[dict]",
            "abstract": str,
            "keywords": "tuple[str]",
            "bibliography": "bibliography('refs.bib', style: 'apa')",
        },
        "page_setup": {"paper": "us-letter", "columns": 1, "margin": "1in"},
    },
}


# ============================================================
# Compilation pipeline registry
# ============================================================
COMPILATION_PIPELINES = {
    "tectonic": {
        "command": ["tectonic", "-X", "compile", "{input}", "--outfmt", "pdf"],
        "requires_install": "cargo install tectonic",
        "handles_bibtex": True,
        "handles_multiple_passes": True,
        "auto_downloads_packages": True,
        "typical_time_seconds": 10,
    },
    "typst": {
        "command": ["typst", "compile", "{input}", "{output}"],
        "requires_install": "cargo install typst-cli",
        "handles_bibtex": True,  # Built-in bibliography
        "handles_multiple_passes": True,  # Single pass
        "auto_downloads_packages": True,
        "typical_time_seconds": 0.2,
    },
    "traditional": {
        "commands": [
            ["pdflatex", "-interaction=nonstopmode", "{input}"],
            ["bibtex", "{stem}"],
            ["pdflatex", "-interaction=nonstopmode", "{input}"],
            ["pdflatex", "-interaction=nonstopmode", "{input}"],
        ],
        "requires_install": "texlive-full",
        "handles_bibtex": False,  # Separate step
        "handles_multiple_passes": False,  # Manual
        "auto_downloads_packages": False,
        "typical_time_seconds": 30,
    },
    "pandoc": {
        "command": [
            "pandoc", "{input}",
            "--citeproc",
            "--bibliography={bib}",
            "--template={template}",
            "-o", "{output}",
        ],
        "requires_install": "apt install pandoc",
        "handles_bibtex": True,  # --citeproc
        "handles_multiple_passes": True,
        "auto_downloads_packages": False,
        "typical_time_seconds": 5,
        "output_formats": ["pdf", "docx", "html", "latex"],
    },
}


# ============================================================
# Writing quality tool configuration
# ============================================================
WRITING_QUALITY_CONFIG = {
    "languagetool": {
        "language": "en-US",
        "level": "picky",
        "disabled_rules": ["WHITESPACE_RULE", "COMMA_PARENTHESIS_WHITESPACE"],
    },
    "proselint": {
        "checks": ["hedging", "redundancy", "weasel_words", "jargon"],
    },
    "textstat": {
        "target_grade_level": (14, 18),  # Graduate level
        "target_flesch": (20, 40),        # Difficult
    },
    "custom_rules": "ACADEMIC_MISTAKE_RULES",  # Reference to rules list above
}
```

---

## Quick Reference: Agent Workflow

```
1. User specifies journal target
2. Agent selects JOURNAL_TEMPLATES[journal]
3. Agent generates content (sections, tables, figures)
4. Writing quality checks run (LanguageTool + proselint + textstat)
5. Statistical results formatted (APA 7th formatters)
6. Figures generated (journal matplotlib config + Okabe-Ito palette)
7. Tables generated (booktabs + APA format)
8. Template assembled (LaTeX preamble + content)
9. Compilation pipeline selected and executed
10. PDF output delivered
```
