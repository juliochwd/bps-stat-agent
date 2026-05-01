<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# tools — Tool Implementations

## Purpose

Extensible tool system for the BPS Stat Agent. All tools are executed by the agent during the tool-use loop. The system includes core tools (bash, file, notes), MCP integration for external tool servers, progressive skill disclosure, and a comprehensive suite of research-specific tools (statistics, analysis, citations, writing, quality, sandbox, documents, knowledge management).

17 modules providing 40+ tool classes across 12,000+ lines of code.

## Key Files

| File | Lines | Description |
|------|-------|-------------|
| `base.py` | 55 | **Base classes.** `Tool` abstract base with `name`, `description`, `parameters` properties and `execute()` method. `ToolResult` Pydantic model (`success: bool`, `content: str`, `error: str|None`). Schema conversion: `to_schema()` (Anthropic format), `to_openai_schema()` (OpenAI format). |
| `__init__.py` | 81 | Package init with lazy imports. Exports core tools unconditionally; research/statistics/citation tools via try/except (None if extras not installed). |
| `bash_tool.py` | 630 | **Shell execution.** `BashTool` — foreground/background command execution with configurable timeout, workspace cwd. `BashOutputTool` — read stdout/stderr from background processes. `BashKillTool` — SIGTERM to running processes. |
| `file_tools.py` | 326 | **File operations.** `ReadTool` — read files with token-aware truncation. `WriteTool` — create/overwrite files. `EditTool` — surgical string replacement in files. All resolve paths relative to `workspace_dir` (security boundary). |
| `mcp_loader.py` | 445 | **MCP client integration.** `MCPTool` class proxies `execute()` to remote MCP servers. `load_mcp_tools_async(config_path)` reads `mcp.json`, connects to each server (stdio/SSE/streamable HTTP). Configurable timeouts: `connect_timeout`, `execute_timeout`, `sse_read_timeout`. `cleanup_mcp_connections()` for shutdown. |
| `note_tool.py` | 222 | **Session memory.** `SessionNoteTool` — save structured notes to JSON file (`.agent_memory.json`). `RecallNoteTool` — retrieve notes by keyword or list all. Workspace-scoped persistence. |
| `skill_tool.py` | 84 | **Progressive skill disclosure (Level 2).** `GetSkillTool` — on-demand retrieval of full skill content when agent needs domain-specific guidance. Created via `create_skill_tools()` factory. |
| `skill_loader.py` | 255 | **Skill discovery.** `SkillLoader` — discovers skill packages from skills directory, extracts metadata for system prompt injection (Level 1), loads full content on demand (Level 2). |
| `research_tools.py` | 235 | **Research project management.** `ProjectInitTool` — create new research project with template. `ProjectStatusTool` — show current phase, progress, questions. `SwitchPhaseTool` — transition between research phases. |
| `statistics_tools.py` | 1914 | **Statistical analysis.** `DescriptiveStatsTool` — summary statistics, distributions. `RegressionAnalysisTool` — OLS, logistic, panel data. `HypothesisTestTool` — t-test, chi-square, ANOVA, Mann-Whitney. `CreateVisualizationTool` — matplotlib/seaborn charts. Plus: `TimeSeriesAnalysisTool`, `BayesianAnalysisTool`, `CausalInferenceTool`, `SurvivalAnalysisTool`, `NonparametricTestTool`. |
| `analysis_tools.py` | 1893 | **Advanced analysis.** `TimeSeriesAnalysisTool` — ARIMA, seasonal decomposition. `BayesianAnalysisTool` — posterior estimation, credible intervals. `CausalInferenceTool` — DiD, IV, propensity score. `SurvivalAnalysisTool` — Kaplan-Meier, Cox PH. `ValidateDataTool` — data quality checks. `CheckStatisticalValidityTool` — assumption testing. `ConversationalAnalysisTool` — natural language data queries. `AutomatedEDATool` — automated exploratory data analysis. `AutoVisualizeTool` — smart chart selection. |
| `citation_tools.py` | 358 | **Literature management.** `LiteratureSearchTool` — search Semantic Scholar, CrossRef, OpenAlex. `CitationManagerTool` — add/format citations, manage BibTeX. `VerifyCitationsTool` — validate DOIs, check retraction status. |
| `writing_tools.py` | 1082 | **Paper writing.** `WriteSectionTool` — generate LaTeX sections with template awareness. `CompilePaperTool` — assemble and compile full paper. `GenerateTableTool` — LaTeX/markdown tables from data. `GenerateDiagramTool` — TikZ/mermaid diagrams. `ConvertFigureTikzTool` — convert figures to TikZ code. |
| `quality_tools.py` | 1017 | **Quality assurance.** `CheckGrammarTool` — grammar/spelling checks. `CheckStyleTool` — academic writing style. `CheckReadabilityTool` — Flesch-Kincaid, readability metrics. `SimulatePeerReviewTool` — AI peer review simulation. `DetectPlagiarismTool` — similarity detection. `AuditReproducibilityTool` — reproducibility audit. |
| `sandbox_tools.py` | 310 | **Python REPL sandbox.** `PythonREPLTool` — execute Python code in isolated environment (Docker or RestrictedPython fallback). Workspace-scoped with timeout. |
| `document_tools.py` | 970 | **Document processing.** `ConvertDocumentTool` — convert between PDF/DOCX/LaTeX/Markdown. `ParseAcademicPDFTool` — extract structured content from academic PDFs. `ExtractReferencesTool` — extract bibliography from documents. |
| `knowledge_tools.py` | 1929 | **Knowledge management.** `ChunkDocumentTool` — split documents into semantic chunks. `EmbedPapersTool` — generate embeddings for papers. `VectorSearchTool` — semantic similarity search. `BuildKnowledgeGraphTool` — construct citation/concept graphs. `QueryKnowledgeGraphTool` — traverse knowledge graphs. `PaperQATool` — question answering over paper corpus. |
| `config_tools.py` | 433 | **Configuration management tools.** Runtime config inspection and modification. |

## For AI Agents

### Working In This Directory

- All tools subclass `Tool` from `base.py` and implement: `name` (property), `description` (property), `parameters` (JSON Schema dict property), `execute(**kwargs) -> ToolResult`
- `execute()` uses **explicit kwargs** matching the JSON Schema properties — NOT `**kwargs`
- Tools return `ToolResult(success=bool, content=str, error=str|None)`
- Schema conversion: `to_schema()` -> Anthropic format, `to_openai_schema()` -> OpenAI format
- File tools resolve paths relative to `workspace_dir` (security boundary)
- BashTool has configurable timeout; BashKillTool sends SIGTERM to running processes
- MCP tools are loaded dynamically at startup from `mcp.json` config — each MCP server connection is managed via `AsyncExitStack`
- Research/statistics/citation/writing/quality/sandbox/document/knowledge tools are conditionally loaded (only when their dependencies are installed)

### How to Add a New Tool

1. Create file in `tools/` (or add to existing file)
2. Subclass `Tool` from `base.py`
3. Implement properties: `name`, `description`, `parameters` (JSON Schema dict)
4. Implement `async execute(**explicit_kwargs) -> ToolResult`
5. Register in `cli.py` -> `add_workspace_tools()` or `initialize_base_tools()`
6. Add to `__init__.py` exports (with try/except if optional dependency)

```python
from .base import Tool, ToolResult

class MyTool(Tool):
    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Does something useful"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "First argument"},
            },
            "required": ["arg1"],
        }

    async def execute(self, arg1: str) -> ToolResult:
        return ToolResult(success=True, content=f"Result: {arg1}")
```

### Testing Requirements

- Each tool should have unit tests that verify `execute()` returns correct `ToolResult`
- File tools: test path resolution, workspace boundary enforcement, token truncation
- Bash tools: test timeout behavior, background process management, kill functionality
- MCP tools: mock MCP server connections, test timeout handling
- Statistics tools: test with known datasets, verify numerical accuracy
- Use `pytest-asyncio` for all async `execute()` tests
- Test `to_schema()` and `to_openai_schema()` output format

### Common Patterns

- **Workspace scoping**: Most tools accept `workspace_dir` in constructor and resolve relative paths against it
- **Graceful degradation**: Optional tools wrapped in try/except ImportError at module level
- **Token truncation**: `ReadTool` truncates large file content to prevent context overflow
- **MCP proxy**: `MCPTool.execute()` serializes arguments, calls remote server, deserializes response
- **Progressive disclosure**: Skills loaded in two levels — metadata at startup, full content on demand

## Dependencies

### Internal
- `mini_agent.schema` — `Message`, `ToolCall` (used in tool results)
- `mini_agent.retry` — retry logic for MCP connections
- `mini_agent.research` — research tools depend on research package

### External (Core)
- `mcp` (>=1.23.0) — MCP client (stdio, SSE, streamable HTTP)
- `pydantic` (>=2.0) — `ToolResult` model

### External (Optional — research extras)
- `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn` — statistics/analysis tools
- `matplotlib`, `seaborn` — visualization tools
- `bibtexparser`, `habanero` — citation tools
- `pylatex`, `python-docx` — writing/document tools
- `docker`, `RestrictedPython` — sandbox tools
- `language-tool-python` — grammar checking
- `playwright` — browser automation (some tools)
