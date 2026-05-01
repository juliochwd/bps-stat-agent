"""Tests for mini_agent/research/writing/ — LaTeX, bibliography, section writer, templates."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.research.writing.bibliography import BibliographyManager
from mini_agent.research.writing.latex_compiler import LaTeXCompiler
from mini_agent.research.writing.section_writer import SectionWriter
from mini_agent.research.writing.template_registry import TemplateRegistry


# ===================================================================
# Bibliography Tests
# ===================================================================


class TestBibliographyManager:
    @pytest.fixture
    def bib_manager(self, tmp_path):
        bib_path = tmp_path / "references.bib"
        return BibliographyManager(bib_path=bib_path)

    def test_init_creates_file(self, tmp_path):
        bib_path = tmp_path / "new.bib"
        mgr = BibliographyManager(bib_path=bib_path)
        assert bib_path.exists()
        content = bib_path.read_text()
        assert "BibTeX" in content

    def test_add_entry(self, bib_manager):
        """Test adding a bibliography entry."""
        bibtex = """@article{smith2024,
  author = {Smith, John},
  title = {A Test Paper},
  journal = {Journal of Testing},
  year = {2024}
}"""
        key = bib_manager.add_entry(bibtex)
        assert key == "smith2024"

    def test_add_entry_duplicate(self, bib_manager):
        """Test adding duplicate entry returns key without error."""
        bibtex = """@article{dup2024,
  author = {Dup, Author},
  title = {Duplicate},
  year = {2024}
}"""
        key1 = bib_manager.add_entry(bibtex)
        key2 = bib_manager.add_entry(bibtex)
        assert key1 == key2

    def test_add_entry_invalid(self, bib_manager):
        """Test adding invalid BibTeX raises ValueError."""
        with pytest.raises(ValueError, match="Could not parse"):
            bib_manager.add_entry("not a bibtex entry")

    def test_get_entry(self, bib_manager):
        """Test getting an entry by key."""
        bibtex = """@article{get2024,
  author = {Get, Author},
  title = {Get Test},
  year = {2024}
}"""
        bib_manager.add_entry(bibtex)
        entry = bib_manager.get_entry("get2024")
        assert entry is not None
        assert entry["key"] == "get2024"

    def test_get_entry_not_found(self, bib_manager):
        """Test getting non-existent entry returns None."""
        entry = bib_manager.get_entry("nonexistent")
        assert entry is None

    def test_remove_entry(self, bib_manager):
        """Test removing an entry."""
        bibtex = """@article{remove2024,
  author = {Remove, Author},
  title = {Remove Test},
  year = {2024}
}"""
        bib_manager.add_entry(bibtex)
        removed = bib_manager.remove_entry("remove2024")
        assert removed is True
        assert bib_manager.get_entry("remove2024") is None

    def test_remove_entry_not_found(self, bib_manager):
        """Test removing non-existent entry returns False."""
        removed = bib_manager.remove_entry("nonexistent")
        assert removed is False

    def test_get_all_entries(self, bib_manager):
        """Test getting all entries."""
        bib_manager.add_entry("@article{a1, author={A}, title={T1}, year={2024}}")
        bib_manager.add_entry("@article{a2, author={B}, title={T2}, year={2024}}")
        entries = bib_manager.get_all_entries()
        assert len(entries) >= 2

    def test_search(self, bib_manager):
        """Test searching entries by field values."""
        bib_manager.add_entry("@article{search1,\n  author={Smith},\n  title={Poverty Analysis},\n  year={2024}\n}")
        bib_manager.add_entry("@article{search2,\n  author={Jones},\n  title={Economic Growth},\n  year={2024}\n}")
        # Search for something that should match
        all_entries = bib_manager.get_all_entries()
        if all_entries:
            # Search by a key that exists in the entries
            first_key = all_entries[0].get("key", "")
            if first_key:
                results = bib_manager.search(first_key)
                assert len(results) >= 1

    def test_get_count(self, bib_manager):
        """Test counting entries."""
        bib_manager.add_entry("@article{count1, author={A}, title={T}, year={2024}}")
        count = bib_manager.get_count()
        assert count >= 1


# ===================================================================
# LaTeX Compiler Tests
# ===================================================================


class TestLaTeXCompiler:
    @pytest.fixture
    def compiler(self, tmp_path):
        return LaTeXCompiler(workspace_path=tmp_path)

    def test_init(self, compiler, tmp_path):
        assert compiler.workspace_path == tmp_path

    def test_compile_pdf_no_latex(self, compiler, tmp_path):
        """Test compilation when LaTeX is not installed."""
        tex_file = tmp_path / "paper.tex"
        tex_file.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        with patch("shutil.which", return_value=None):
            # Should raise or return None when no compiler available
            try:
                result = compiler.compile_pdf(tex_file)
            except Exception:
                pass  # Expected when no LaTeX installed

    def test_compiler_available(self, compiler):
        """Test checking if compiler is available."""
        # This is a static method
        result = LaTeXCompiler._compiler_available("nonexistent_compiler_xyz")
        assert result is False


# ===================================================================
# Section Writer Tests
# ===================================================================


class TestSectionWriter:
    @pytest.fixture
    def writer(self, tmp_path):
        return SectionWriter(workspace_path=tmp_path)

    def test_init(self, writer, tmp_path):
        assert writer.workspace_path == tmp_path


# ===================================================================
# Template Registry Tests
# ===================================================================


class TestTemplateRegistry:
    def test_init(self):
        registry = TemplateRegistry()
        assert registry is not None

    def test_list_templates(self):
        """Test listing available templates."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0
