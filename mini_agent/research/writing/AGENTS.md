<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# writing

## Purpose
Academic writing pipeline for the research engine. Handles section-by-section paper writing, bibliography management, LaTeX compilation, and template-based document generation.

## Key Files
| File | Description |
|------|-------------|
| `__init__.py` | Package exports: `SectionWriter`, `TemplateRegistry`, `Bibliography`, `LaTeXCompiler` |
| `section_writer.py` | `SectionWriter` — LLM-powered section generation with citation integration and style enforcement |
| `template_registry.py` | `TemplateRegistry` — manages paper templates (IEEE, Elsevier, Springer, MDPI, APA7, Springer LNCS) |
| `bibliography.py` | `Bibliography` — BibTeX management, DOI lookup via CrossRef (habanero), deduplication |
| `latex_compiler.py` | `LaTeXCompiler` — compiles LaTeX to PDF, handles multi-pass compilation for references |

## For AI Agents

### Working In This Directory
- `SectionWriter` generates one section at a time (abstract, introduction, methodology, results, discussion, conclusion)
- Templates define document structure, required sections, and LaTeX preamble
- `Bibliography` maintains a `.bib` file — entries added via DOI lookup or manual BibTeX
- `LaTeXCompiler` requires a LaTeX distribution (texlive) installed on the system
- Writing happens during the WRITE phase of the research workflow

### Template System
```python
registry = TemplateRegistry()
template = registry.get("elsevier")
# template.sections: ["abstract", "introduction", "methodology", ...]
# template.preamble: LaTeX document class and packages
# template.citation_style: "natbib" | "biblatex"
```

### Writing Flow
```
SectionWriter.write(section="introduction", context=...)
  ├── Load template requirements for section
  ├── Gather relevant citations from Bibliography
  ├── Generate content via LLM (with academic style prompt)
  ├── Verify citations are properly referenced
  └── Save to workspace/sections/{section}.tex
```

## Dependencies

### Internal
- `mini_agent.research.llm_gateway` — LLM calls for content generation
- `mini_agent.research.models.CostTracker` — cost tracking
- `mini_agent.research.quality.WritingQuality` — post-write quality check

### External
- `pylatex` — LaTeX document generation
- `python-docx` — DOCX output (alternative to LaTeX)
- `bibtexparser` — BibTeX file parsing and writing
- `habanero` — CrossRef DOI lookup for bibliography

<!-- MANUAL: -->
