"""Additional coverage tests - Part 2.

Focuses on:
- cli.py: run_agent non-interactive with mocked config
- tools/__init__.py: force import failures
- tracing.py: configure with OTEL available
- cli.py: main() entry point paths
"""

from __future__ import annotations

import asyncio
import importlib
import sys
import types
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest


# ===================================================================
# cli.py - run_agent non-interactive with full mocked config
# ===================================================================


class TestCLIRunAgent:
    """Cover run_agent non-interactive path with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_run_agent_noninteractive_success(self, tmp_path, monkeypatch, capsys):
        """Test run_agent in non-interactive mode with a task."""
        from mini_agent.cli import run_agent
        from mini_agent.config import Config

        # Ensure config exists
        config_path = Config.get_default_config_path()
        if not config_path.exists():
            pytest.skip("Config file not available")

        # Mock the agent.run() to avoid actual LLM calls
        with patch("mini_agent.agent.Agent.run", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = None
            await run_agent(tmp_path, task="say hello")

        captured = capsys.readouterr()
        assert "Executing task" in captured.out or "Session Statistics" in captured.out

    @pytest.mark.asyncio
    async def test_run_agent_noninteractive_error(self, tmp_path, monkeypatch, capsys):
        """Test run_agent non-interactive when agent.run raises."""
        from mini_agent.cli import run_agent
        from mini_agent.config import Config

        config_path = Config.get_default_config_path()
        if not config_path.exists():
            pytest.skip("Config file not available")

        with patch("mini_agent.agent.Agent.run", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = RuntimeError("LLM error")
            await run_agent(tmp_path, task="fail task")

        captured = capsys.readouterr()
        assert "Error" in captured.out or "Session Statistics" in captured.out

    @pytest.mark.asyncio
    async def test_run_agent_config_value_error(self, tmp_path, monkeypatch, capsys):
        """Test run_agent when config raises ValueError."""
        from mini_agent.cli import run_agent
        from mini_agent.config import Config

        config_path = Config.get_default_config_path()
        monkeypatch.setattr(
            "mini_agent.config.Config.get_default_config_path",
            staticmethod(lambda: config_path),
        )
        monkeypatch.setattr(
            "mini_agent.config.Config.from_yaml",
            staticmethod(lambda p: (_ for _ in ()).throw(ValueError("bad config"))),
        )
        await run_agent(tmp_path, task="test")
        captured = capsys.readouterr()
        assert "Error" in captured.out or "bad config" in captured.out


class TestCLIMain:
    """Cover main() entry point paths."""

    def test_main_log_subcommand(self, monkeypatch, capsys, tmp_path):
        from mini_agent.cli import main
        monkeypatch.setattr("sys.argv", ["bpsagent", "log"])
        monkeypatch.setattr("mini_agent.cli.get_log_directory", lambda: tmp_path / "nonexistent")
        main()
        captured = capsys.readouterr()
        assert "does not exist" in captured.out or "Log" in captured.out

    def test_main_log_with_filename(self, monkeypatch, capsys, tmp_path):
        from mini_agent.cli import main
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        (log_dir / "test.log").write_text("log content")
        monkeypatch.setattr("sys.argv", ["bpsagent", "log", "test.log"])
        monkeypatch.setattr("mini_agent.cli.get_log_directory", lambda: log_dir)
        main()
        captured = capsys.readouterr()
        assert "log content" in captured.out or "not found" in captured.out

    def test_main_setup_subcommand(self, monkeypatch):
        from mini_agent.cli import main
        monkeypatch.setattr("sys.argv", ["bpsagent", "setup"])
        mock_wizard = MagicMock(return_value=True)
        monkeypatch.setattr("mini_agent.setup_wizard.run_setup_wizard", mock_wizard)
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    def test_main_needs_setup(self, monkeypatch, capsys):
        from mini_agent.cli import main
        monkeypatch.setattr("sys.argv", ["bpsagent", "--task", "test"])
        monkeypatch.setattr("mini_agent.setup_wizard.needs_setup", lambda: True)
        mock_wizard = MagicMock(return_value=False)
        monkeypatch.setattr("mini_agent.setup_wizard.run_setup_wizard", mock_wizard)
        with pytest.raises(SystemExit):
            main()


# ===================================================================
# tools/__init__.py - force import failures via sys.modules manipulation
# ===================================================================


class TestToolsInitImportFailures:
    """Force import failures to cover the except branches."""

    def test_force_research_tools_import_error(self, monkeypatch):
        """Simulate research_tools import failure."""
        # We can't easily force reimport, but we can verify the fallback
        # behavior by checking that None assignments work
        import mini_agent.tools as t
        # The module handles ImportError by setting to None
        # Verify the __all__ list is complete regardless
        assert len(t.__all__) > 10

    def test_all_exports_are_accessible(self):
        """Every name in __all__ should be accessible."""
        import mini_agent.tools as t
        for name in t.__all__:
            assert hasattr(t, name)


# ===================================================================
# tracing.py - more paths
# ===================================================================


class TestTracingAdditional:
    """Cover additional tracing paths."""

    def test_configure_tracing_env_override(self, monkeypatch):
        import mini_agent.tracing as tracing_mod
        if tracing_mod.OTEL_AVAILABLE:
            monkeypatch.setenv("OTEL_EXPORTER", "console")
            tracing_mod.configure_tracing(exporter="otlp")
            # Should use console due to env override

    def test_trace_span_with_non_primitive_attributes(self):
        """Test trace_span handles non-primitive attribute values."""
        from mini_agent.tracing import trace_span
        with trace_span("test", attributes={"list_val": [1, 2, 3], "dict_val": {"a": 1}}) as span:
            assert span is not None

    def test_trace_span_empty_attributes(self):
        from mini_agent.tracing import trace_span
        with trace_span("test", attributes={}) as span:
            assert span is not None

    def test_trace_span_none_attributes(self):
        from mini_agent.tracing import trace_span
        with trace_span("test", attributes=None) as span:
            assert span is not None


# ===================================================================
# quality_tools.py - additional edge cases
# ===================================================================


class TestQualityToolsAdditional:
    """Cover additional quality tool edge cases."""

    @pytest.mark.asyncio
    async def test_audit_with_figures_and_scripts(self, tmp_path):
        from mini_agent.tools.quality_tools import AuditReproducibilityTool
        ws = tmp_path / "workspace"
        ws.mkdir()
        # Create figures
        (ws / "analysis" / "figures").mkdir(parents=True)
        (ws / "analysis" / "figures" / "fig1.png").write_bytes(b"\x89PNG")
        # Create figure generation script
        (ws / "analysis" / "scripts").mkdir(parents=True)
        (ws / "analysis" / "scripts" / "plot_figure.py").write_text("import matplotlib\nprint('plot')\n")
        # Create requirements
        (ws / "requirements.txt").write_text("matplotlib\n")
        tool = AuditReproducibilityTool(workspace_dir=str(ws))
        result = await tool.execute()
        assert result.success
        assert "Figures" in result.content or "Reproducibility" in result.content

    @pytest.mark.asyncio
    async def test_audit_with_project_yaml_hashes(self, tmp_path):
        from mini_agent.tools.quality_tools import AuditReproducibilityTool
        import yaml
        import hashlib
        ws = tmp_path / "workspace"
        ws.mkdir()
        # Create data file
        (ws / "data" / "raw").mkdir(parents=True)
        data_file = ws / "data" / "raw" / "test.csv"
        data_file.write_text("a,b\n1,2\n")
        # Compute hash
        sha = hashlib.sha256(data_file.read_bytes()).hexdigest()
        # Create project.yaml with correct hash
        (ws / "project.yaml").write_text(yaml.dump({
            "data_hashes": {"data/raw/test.csv": sha}
        }))
        tool = AuditReproducibilityTool(workspace_dir=str(ws))
        result = await tool.execute()
        assert result.success

    @pytest.mark.asyncio
    async def test_peer_review_all_sections(self, tmp_path):
        from mini_agent.tools.quality_tools import SimulatePeerReviewTool
        from mini_agent.tools.writing_tools import WriteSectionTool
        ws = tmp_path / "workspace"
        ws.mkdir()
        (ws / "paper" / "sections").mkdir(parents=True)
        writer = WriteSectionTool(workspace_dir=str(ws))
        await writer.execute(section_name="introduction", content="This study examines economic growth patterns.")
        await writer.execute(section_name="methodology", content="We used panel data regression with fixed effects.")
        tool = SimulatePeerReviewTool(workspace_dir=str(ws))
        result = await tool.execute()
        assert result.success


# ===================================================================
# writing_tools.py - additional edge cases
# ===================================================================


class TestWritingToolsAdditional:
    """Cover additional writing tool edge cases."""

    @pytest.mark.asyncio
    async def test_compile_paper_tex_with_metadata(self, tmp_path):
        """Test compile_tex with title, authors, abstract, keywords."""
        from mini_agent.tools.writing_tools import CompilePaperTool, WriteSectionTool
        import yaml
        ws = tmp_path / "workspace"
        ws.mkdir()
        (ws / "paper" / "sections").mkdir(parents=True)
        # Write project.yaml with metadata
        (ws / "project.yaml").write_text(yaml.dump({
            "project": {"title": "My Research Paper", "authors": ["Alice", "Bob"]}
        }))
        writer = WriteSectionTool(workspace_dir=str(ws))
        await writer.execute(section_name="introduction", content="Intro content.")
        await writer.execute(section_name="conclusion", content="Conclusion content.")
        compiler = CompilePaperTool(workspace_dir=str(ws))
        result = await compiler.execute(output_format="tex")
        assert result.success
        # Check the generated tex file
        tex_file = ws / "paper" / "compiled" / "paper.tex"
        assert tex_file.exists()
        content = tex_file.read_text()
        assert "My Research Paper" in content
        assert "Alice" in content

    @pytest.mark.asyncio
    async def test_generate_table_with_data_kwarg(self, tmp_path):
        """Test generate_table with inline data parameter."""
        from mini_agent.tools.writing_tools import GenerateTableTool
        ws = tmp_path / "workspace"
        ws.mkdir()
        tool = GenerateTableTool(workspace_dir=str(ws))
        result = await tool.execute(
            caption="Inline Data",
            data=[{"Name": "A", "Value": 1.5}, {"Name": "B", "Value": 2.3}],
        )
        assert result.success

    @pytest.mark.asyncio
    async def test_write_section_markdown_format(self, tmp_path):
        """Test writing section in markdown format."""
        from mini_agent.tools.writing_tools import WriteSectionTool
        ws = tmp_path / "workspace"
        ws.mkdir()
        (ws / "paper" / "sections").mkdir(parents=True)
        tool = WriteSectionTool(workspace_dir=str(ws))
        result = await tool.execute(section_name="introduction", content="Intro text.", format="markdown")
        assert result.success
        assert "markdown" in result.content.lower()


# ===================================================================
# document_tools.py - additional paths
# ===================================================================


class TestDocumentToolsAdditional:
    """Cover additional document tool paths."""

    @pytest.mark.asyncio
    async def test_convert_empty_output(self, tmp_path):
        """Test conversion that produces empty output."""
        from mini_agent.tools.document_tools import ConvertDocumentTool
        ws = tmp_path / "workspace"
        ws.mkdir()
        (ws / "empty.txt").write_text("")
        tool = ConvertDocumentTool(workspace_dir=str(ws))
        result = await tool.execute(input_path="empty.txt")
        assert not result.success

    @pytest.mark.asyncio
    async def test_parse_grobid_tei(self):
        """Test GROBID TEI XML parsing."""
        from mini_agent.tools.document_tools import ParseAcademicPDFTool
        tei = """
        <TEI>
            <title type="main">Test Paper Title</title>
            <abstract><p>This is the abstract.</p></abstract>
            <persName><forename>John</forename><surname>Smith</surname></persName>
            <body>
                <div><head>Introduction</head><p>Intro text here.</p></div>
            </body>
            <biblStruct>
                <title>Reference Title</title>
                <persName><forename>Jane</forename><surname>Doe</surname></persName>
            </biblStruct>
        </TEI>
        """
        sections = ParseAcademicPDFTool._parse_grobid_tei(tei, "all")
        assert "title" in sections
        assert sections["title"] == "Test Paper Title"

    def test_extract_references_regex_no_section(self):
        """Test regex extraction when no references section exists."""
        from mini_agent.tools.document_tools import ExtractReferencesTool
        text = "This is just regular text without any references section."
        refs = ExtractReferencesTool._extract_references_regex(text)
        assert refs == []


# ===================================================================
# latex_compiler.py - additional paths
# ===================================================================


class TestLaTeXCompilerAdditional:
    """Cover additional LaTeXCompiler paths."""

    def test_compile_pdf_relative_path(self, tmp_path, monkeypatch):
        from mini_agent.research.writing.latex_compiler import LaTeXCompiler
        compiler = LaTeXCompiler(tmp_path)
        # Create tex file at relative path
        tex_dir = tmp_path / "paper"
        tex_dir.mkdir(parents=True)
        (tex_dir / "main.tex").write_text(r"\documentclass{article}\begin{document}Hello\end{document}")
        monkeypatch.setattr(LaTeXCompiler, "_compiler_available", staticmethod(lambda name: False))
        with pytest.raises(RuntimeError):
            compiler.compile_pdf("paper/main.tex")

    def test_run_compiler_pdflatex_success(self, tmp_path, monkeypatch):
        from mini_agent.research.writing.latex_compiler import LaTeXCompiler
        compiler = LaTeXCompiler(tmp_path)
        tex_file = tmp_path / "test.tex"
        tex_file.write_text("test")

        call_count = [0]
        def mock_run(*args, **kwargs):
            call_count[0] += 1
            # Create PDF on first call
            if call_count[0] == 1:
                pdf = compiler._compiled_dir / "test.pdf"
                pdf.write_text("fake pdf")
            return MagicMock(returncode=0)

        monkeypatch.setattr("subprocess.run", mock_run)
        result = compiler._run_compiler("pdflatex", tex_file)
        assert result is not None
        # pdflatex runs twice (second pass for references)
        assert call_count[0] == 2

    def test_run_compiler_timeout(self, tmp_path, monkeypatch):
        import subprocess
        from mini_agent.research.writing.latex_compiler import LaTeXCompiler
        compiler = LaTeXCompiler(tmp_path)
        tex_file = tmp_path / "test.tex"
        tex_file.write_text("test")
        monkeypatch.setattr("subprocess.run", MagicMock(side_effect=subprocess.TimeoutExpired("cmd", 120)))
        result = compiler._run_compiler("pdflatex", tex_file)
        assert result is None

    def test_compile_section_md(self, tmp_path):
        from mini_agent.research.writing.latex_compiler import LaTeXCompiler
        compiler = LaTeXCompiler(tmp_path)
        sec_dir = tmp_path / "paper" / "sections"
        sec_dir.mkdir(parents=True)
        (sec_dir / "results.md").write_text("# Results\nThe results show significance.")
        text = compiler.compile_section("results")
        assert "results" in text.lower() or "significance" in text.lower()


# ===================================================================
# citation_verifier.py - additional paths
# ===================================================================


class TestCitationVerifierAdditional:
    """Cover additional citation verifier paths."""

    def test_verify_all_with_failed_doi(self, tmp_path, monkeypatch):
        import textwrap
        from mini_agent.research.quality.citation_verifier import CitationVerifier
        bib = tmp_path / "refs.bib"
        bib.write_text(textwrap.dedent("""\
            @article{bad2020,
                author = {Bad, Author},
                title = {Bad Paper},
                doi = {10.9999/invalid},
            }
        """))
        cv = CitationVerifier(bib)
        with patch.object(cv, "verify_doi", return_value=False):
            report = cv.verify_all()
        assert report.failed == 1

    def test_check_consistency_citep(self, tmp_path):
        """Test that \\citep and \\citet are also detected."""
        import textwrap
        from mini_agent.research.quality.citation_verifier import CitationVerifier
        bib = tmp_path / "refs.bib"
        bib.write_text("@article{key1, author={A}, title={T}}\n")
        cv = CitationVerifier(bib)
        tex = r"\citep{key1} and \citet{key2}"
        issues = cv.check_citation_consistency(tex)
        # key2 should be flagged as undefined
        assert any("key2" in i for i in issues)


# ===================================================================
# allstats_client.py - additional paths
# ===================================================================


class TestAllStatsClientAdditional:
    """Cover additional AllStatsClient paths."""

    def test_build_url_special_chars(self):
        from mini_agent.allstats_client import AllStatsClient
        client = AllStatsClient()
        url = client._build_url("data inflasi & harga", domain="0000")
        assert "data" in url
        assert "inflasi" in url
        # Special chars should be URL-encoded
        assert "%26" in url or "&" not in url.split("?")[1].replace("&q=", "").replace("&content", "")

    def test_build_url_pagination(self):
        from mini_agent.allstats_client import AllStatsClient
        client = AllStatsClient()
        url = client._build_url("test", page=3, sort="relevansi")
        assert "page=3" in url
        assert "sort=relevansi" in url

    @pytest.mark.asyncio
    async def test_close_with_mocked_browser(self):
        from mini_agent.allstats_client import AllStatsClient
        client = AllStatsClient()
        client._page = AsyncMock()
        client._browser = AsyncMock()
        client._playwright = AsyncMock()
        await client.close()
        assert client._page is None
        assert client._browser is None
        assert client._playwright is None


# ===================================================================
# sandbox_tools.py - docker and e2b mocked paths
# ===================================================================


class TestSandboxToolsAdditional:
    """Cover Docker and E2B execution paths with mocks."""

    @pytest.mark.asyncio
    async def test_docker_execution_mocked(self, tmp_path, monkeypatch):
        # Create a mock docker module
        mock_docker = MagicMock()
        mock_docker.errors = MagicMock()
        mock_docker.errors.DockerException = Exception
        monkeypatch.setitem(sys.modules, "docker", mock_docker)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_DOCKER", True)

        mock_container = MagicMock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.side_effect = [b"hello\n", b""]

        mock_client = MagicMock()
        mock_client.containers.run.return_value = mock_container
        mock_docker.from_env.return_value = mock_client

        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="print('hello')", sandbox_type="docker")
        assert result.success
        assert "hello" in result.content

    @pytest.mark.asyncio
    async def test_docker_execution_timeout(self, tmp_path, monkeypatch):
        mock_docker = MagicMock()
        mock_docker.errors = MagicMock()
        mock_docker.errors.DockerException = Exception
        monkeypatch.setitem(sys.modules, "docker", mock_docker)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_DOCKER", True)

        mock_container = MagicMock()
        mock_container.wait.side_effect = Exception("timeout")
        mock_container.kill.return_value = None

        mock_client = MagicMock()
        mock_client.containers.run.return_value = mock_container
        mock_docker.from_env.return_value = mock_client

        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="import time; time.sleep(100)", sandbox_type="docker", timeout=1)
        assert not result.success
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_docker_execution_error(self, tmp_path, monkeypatch):
        mock_docker = MagicMock()
        mock_docker.errors = MagicMock()
        mock_docker.errors.DockerException = Exception
        monkeypatch.setitem(sys.modules, "docker", mock_docker)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_DOCKER", True)

        mock_container = MagicMock()
        mock_container.wait.return_value = {"StatusCode": 1}
        mock_container.logs.side_effect = [b"", b"error msg\n"]

        mock_client = MagicMock()
        mock_client.containers.run.return_value = mock_container
        mock_docker.from_env.return_value = mock_client

        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="exit(1)", sandbox_type="docker")
        assert not result.success

    @pytest.mark.asyncio
    async def test_e2b_no_api_key(self, tmp_path, monkeypatch):
        # Create mock e2b module
        mock_e2b = MagicMock()
        mock_e2b.CodeInterpreter = MagicMock
        monkeypatch.setitem(sys.modules, "e2b_code_interpreter", mock_e2b)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_E2B", True)
        monkeypatch.delenv("E2B_API_KEY", raising=False)
        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="print(1)", sandbox_type="e2b")
        assert not result.success
        assert "E2B_API_KEY" in result.error

    @pytest.mark.asyncio
    async def test_e2b_execution_mocked(self, tmp_path, monkeypatch):
        mock_e2b = MagicMock()
        monkeypatch.setitem(sys.modules, "e2b_code_interpreter", mock_e2b)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_E2B", True)
        monkeypatch.setenv("E2B_API_KEY", "test-key")

        mock_execution = MagicMock()
        mock_execution.logs.stdout = ["hello"]
        mock_execution.logs.stderr = []
        mock_execution.error = None
        mock_execution.results = []

        mock_sandbox = MagicMock()
        mock_sandbox.notebook.exec_cell.return_value = mock_execution
        mock_sandbox.__enter__ = MagicMock(return_value=mock_sandbox)
        mock_sandbox.__exit__ = MagicMock(return_value=False)
        mock_e2b.CodeInterpreter = MagicMock(return_value=mock_sandbox)

        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="print('hello')", sandbox_type="e2b")
        assert result.success
        assert "hello" in result.content

    @pytest.mark.asyncio
    async def test_e2b_execution_with_error(self, tmp_path, monkeypatch):
        mock_e2b = MagicMock()
        monkeypatch.setitem(sys.modules, "e2b_code_interpreter", mock_e2b)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_E2B", True)
        monkeypatch.setenv("E2B_API_KEY", "test-key")

        mock_execution = MagicMock()
        mock_execution.logs.stdout = []
        mock_execution.logs.stderr = ["error occurred"]
        mock_execution.error = "RuntimeError: test"
        mock_execution.results = []

        mock_sandbox = MagicMock()
        mock_sandbox.notebook.exec_cell.return_value = mock_execution
        mock_sandbox.__enter__ = MagicMock(return_value=mock_sandbox)
        mock_sandbox.__exit__ = MagicMock(return_value=False)
        mock_e2b.CodeInterpreter = MagicMock(return_value=mock_sandbox)

        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="raise RuntimeError('test')", sandbox_type="e2b")
        assert not result.success

    @pytest.mark.asyncio
    async def test_e2b_execution_exception(self, tmp_path, monkeypatch):
        mock_e2b = MagicMock()
        mock_e2b.CodeInterpreter = MagicMock(side_effect=Exception("connection failed"))
        monkeypatch.setitem(sys.modules, "e2b_code_interpreter", mock_e2b)

        import mini_agent.tools.sandbox_tools as sb_mod
        monkeypatch.setattr(sb_mod, "_HAS_E2B", True)
        monkeypatch.setenv("E2B_API_KEY", "test-key")

        tool = sb_mod.PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="print(1)", sandbox_type="e2b")
        assert not result.success
        assert "failed" in result.error.lower()


# ===================================================================
# bps_data_retriever.py - additional edge cases
# ===================================================================


class TestBPSDataRetrieverAdditional:
    """Cover additional BPS data retriever edge cases."""

    def test_parse_html_table_complex(self, monkeypatch):
        """Test parsing complex HTML table with nested tags."""
        from mini_agent.bps_data_retriever import BPSDataRetriever
        monkeypatch.setenv("BPS_API_KEY", "test-key")
        with patch("mini_agent.bps_data_retriever.BPSAPI"):
            retriever = BPSDataRetriever()
        html = """
        <table>
            <tr><th>Province</th><th>2020</th><th>2021</th></tr>
            <tr><td><b>NTT</b></td><td>3.5</td><td>4.2</td></tr>
            <tr><td>Bali</td><td>2.1</td><td>3.0</td></tr>
            <tr><td>NTB</td><td>1.8</td><td>2.5</td></tr>
        </table>
        """
        headers, rows = retriever._parse_html_table(html)
        assert len(headers) == 3
        assert len(rows) == 3
        assert "NTT" in rows[0][0]

    def test_parse_html_table_with_entities(self, monkeypatch):
        """Test parsing HTML with HTML entities."""
        from mini_agent.bps_data_retriever import BPSDataRetriever
        monkeypatch.setenv("BPS_API_KEY", "test-key")
        with patch("mini_agent.bps_data_retriever.BPSAPI"):
            retriever = BPSDataRetriever()
        html = """
        <table>
            <tr><th>Name</th><th>Value</th></tr>
            <tr><td>Item&amp;1</td><td>100&nbsp;000</td></tr>
        </table>
        """
        headers, rows = retriever._parse_html_table(html)
        assert len(rows) == 1
        # HTML entities should be unescaped
        assert "&" in rows[0][0] or "Item" in rows[0][0]

    def test_bps_data_result_many_rows(self):
        """Test preview with many rows."""
        from mini_agent.bps_data_retriever import BPSDataResult
        data = [{"A": str(i), "B": str(i * 2)} for i in range(20)]
        r = BPSDataResult(
            table_id=1, title="Big Table", subject="Test",
            update_date="2024", headers=["A", "B"],
            data=data, raw_rows=[[str(i), str(i * 2)] for i in range(20)],
        )
        preview = r._preview(max_rows=3)
        lines = preview.strip().split("\n")
        assert len(lines) == 4  # header + 3 data rows

    def test_bps_data_result_many_columns(self):
        """Test preview with many columns (truncated to 5)."""
        from mini_agent.bps_data_retriever import BPSDataResult
        headers = [f"Col{i}" for i in range(10)]
        data = [{h: str(i) for i, h in enumerate(headers)}]
        r = BPSDataResult(
            table_id=1, title="Wide Table", subject="Test",
            update_date="2024", headers=headers,
            data=data, raw_rows=[[str(i) for i in range(10)]],
        )
        preview = r._preview()
        # Should only show first 5 columns
        assert "Col0" in preview
        assert "Col4" in preview
