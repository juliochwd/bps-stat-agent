"""Writing engine for academic paper generation."""

from __future__ import annotations

from .bibliography import BibliographyManager
from .latex_compiler import LaTeXCompiler
from .section_writer import SectionWriter
from .template_registry import TemplateRegistry

__all__ = ["SectionWriter", "LaTeXCompiler", "TemplateRegistry", "BibliographyManager"]
