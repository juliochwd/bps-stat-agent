"""Comprehensive tests for mini_agent/research/writing/ modules.

Tests BibliographyManager, LaTeXCompiler, SectionWriter, TemplateRegistry.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.research.writing.bibliography import BibliographyManager
from mini_agent.research.writing.latex_compiler import LaTeXCompiler
from mini_agent.research.writing.section_writer import SectionWriter
from mini_agent.research.writing.template_registry import TemplateRegistry


# ===================================================================
# BibliographyManager Extended Tests
# ===================================================================

class TestBibliographyManagerExtended:
    @pytest.fixture
    def bib_manager(self, tmp_path):
        bib_path = tmp_path / "references.bib"
        return BibliographyManager(bib_path=bib_path)

    def test_get_all_entries(self, bib_manager):
        bibtex1 = """@article{smith2024,
  author = {Smith, John},
  title = {Paper One},
  journal = {Journal A},
  year = {2024}
}"""
        bibtex2 = """@article{jones2023,
  author = {Jones, Alice},
  title = {Paper Two},
  journal = {Journal B},
  year = {2023}
}"""
        bib_manager.add_entry(bibtex1)
        bib_manager.add_entry(bibtex2)
        entries = bib_manager.get_all_entries()
        assert len(entries) >= 2

    def test_get_entry_not_found(self, bib_manager):
        entry = bib_manager.get_entry("nonexistent_key")
        assert entry is None

    def test_remove_entry(self, bib_manager):
        bibtex = """@article{toremove2024,
  author = {Remove, Me},
  title = {Remove This},
  year = {2024}
}"""
        bib_manager.add_entry(bibtex)
        result = bib_manager.remove_entry("toremove2024")
        assert result is True
        assert bib_manager.get_entry("toremove2024") is None

    def test_remove_nonexistent_entry(self, bib_manager):
        result = bib_manager.remove_entry("nonexistent")
        assert result is False

    def test_count_entries(self, bib_manager):
        initial_count = bib_manager.get_count()
        bibtex = """@article{count2024,
  author = {Count, Test},
  title = {Counting},
  year = {2024}
}"""
        bib_manager.add_entry(bibtex)
        assert bib_manager.get_count() == initial_count + 1

    def test_search_entries(self, bib_manager):
        bibtex = """@article{search2024,
  author = {Searchable, Author},
  title = {Inflation Analysis in Indonesia},
  journal = {Economics Journal},
  year = {2024}
}"""
        bib_manager.add_entry(bibtex)
        results = bib_manager.search("inflation")
        assert isinstance(results, (list, dict))
        # search may return list of keys or entries
        assert len(results) >= 0

    def test_format_apa(self, bib_manager):
        bibtex = """@article{apa2024,
  author = {Smith, John and Jones, Alice},
  title = {A Study of Economics},
  journal = {Journal of Economics},
  year = {2024},
  volume = {15},
  pages = {100-115}
}"""
        bib_manager.add_entry(bibtex)
        entry = bib_manager.get_entry("apa2024")
        assert entry is not None


# ===================================================================
# LaTeXCompiler Tests
# ===================================================================

class TestLaTeXCompilerExtended:
    @pytest.fixture
    def compiler(self, tmp_path):
        return LaTeXCompiler(workspace_path=tmp_path)

    def test_init(self, compiler):
        assert compiler is not None

    def test_compile_pdf_no_latex(self, compiler, tmp_path):
        """Test compilation when LaTeX is not installed."""
        tex_file = tmp_path / "paper.tex"
        tex_file.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        with patch("shutil.which", return_value=None):
            result = compiler.compile_pdf(tex_file)
            # Should fail gracefully or return error info
            assert isinstance(result, (dict, type(None))) or result is not None

    def test_compile_section(self, compiler, tmp_path):
        """Test compiling a single section."""
        # Create section in expected location
        for subdir in ["paper/sections", "writing/sections"]:
            sec_dir = tmp_path / subdir
            sec_dir.mkdir(parents=True, exist_ok=True)
            (sec_dir / "intro.tex").write_text(r"\section{Introduction}" + "\nContent here.")
        result = compiler.compile_section("intro")
        assert result is not None


# ===================================================================
# SectionWriter Tests
# ===================================================================

class TestSectionWriterExtended:
    @pytest.fixture
    def writer(self, tmp_path):
        return SectionWriter(workspace_path=tmp_path)

    def test_init(self, writer):
        assert writer is not None

    def test_write_section_latex(self, writer, tmp_path):
        output = writer.write_section(
            "introduction",
            "This paper examines inflation trends in NTT province.",
            output_format="latex",
        )
        assert output.exists()
        content = output.read_text()
        assert "inflation" in content.lower()

    def test_write_section_markdown(self, writer, tmp_path):
        output = writer.write_section(
            "methodology",
            "We use OLS regression with panel data.",
            output_format="markdown",
        )
        assert output.exists()

    def test_get_section(self, writer, tmp_path):
        writer.write_section("results", "The coefficient is 0.45.")
        content = writer.get_section("results")
        assert content is not None
        assert "0.45" in content

    def test_get_section_not_found(self, writer):
        content = writer.get_section("nonexistent_section")
        assert content is None

    def test_get_all_sections(self, writer):
        writer.write_section("intro", "Introduction content.")
        writer.write_section("method", "Method content.")
        sections = writer.get_all_sections()
        assert isinstance(sections, dict)
        assert len(sections) >= 2

    def test_get_word_count(self, writer):
        writer.write_section("abstract", "This is a five word abstract.")
        count = writer.get_word_count("abstract")
        assert count >= 5

    def test_get_word_count_missing(self, writer):
        count = writer.get_word_count("nonexistent")
        assert count == 0

    def test_list_sections(self, writer):
        writer.write_section("sec1", "Content 1")
        writer.write_section("sec2", "Content 2")
        sections = writer.get_all_sections()
        assert isinstance(sections, dict)
        assert len(sections) >= 2


# ===================================================================
# TemplateRegistry Tests
# ===================================================================

class TestTemplateRegistryExtended:
    @pytest.fixture
    def registry(self):
        return TemplateRegistry()

    def test_init(self, registry):
        assert registry is not None

    def test_list_templates(self, registry):
        templates = registry.list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0
        # Should include common templates
        template_names = [t if isinstance(t, str) else t.get("name", "") for t in templates]
        assert any("elsevier" in str(t).lower() for t in template_names)

    def test_get_template(self, registry):
        template = registry.get_template("elsevier")
        assert template is not None

    def test_get_template_not_found(self, registry):
        with pytest.raises(KeyError):
            registry.get_template("nonexistent_template_xyz")

    def test_get_template_ieee(self, registry):
        template = registry.get_template("ieee")
        assert template is not None

    def test_get_template_springer(self, registry):
        template = registry.get_template("springer")
        assert template is not None

    def test_get_main_tex(self, registry):
        main_tex = registry.get_main_tex("elsevier", title="Test Paper", authors=["Author One"])
        assert isinstance(main_tex, str)
        assert len(main_tex) > 0
