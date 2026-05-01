"""Tests for research workspace scaffolding."""

import tempfile
from pathlib import Path

from mini_agent.research.project_state import ProjectState
from mini_agent.research.workspace import WORKSPACE_DIRS, WorkspaceScaffolder


class TestWorkspaceScaffolder:
    """Test workspace creation and verification."""

    def test_scaffold_creates_all_directories(self):
        """Scaffold creates all required directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)

            for dir_path in WORKSPACE_DIRS:
                assert (Path(tmpdir) / dir_path).is_dir(), f"Missing: {dir_path}"

    def test_scaffold_creates_project_yaml(self):
        """Scaffold creates project.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)

            assert (Path(tmpdir) / "project.yaml").exists()

    def test_scaffold_creates_bib_file(self):
        """Scaffold creates references.bib."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)

            bib_path = Path(tmpdir) / "literature" / "references.bib"
            assert bib_path.exists()
            content = bib_path.read_text()
            assert "BibTeX" in content

    def test_scaffold_creates_gitignore(self):
        """Scaffold creates .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)

            gitignore = Path(tmpdir) / ".gitignore"
            assert gitignore.exists()
            content = gitignore.read_text()
            assert "data/cache/" in content

    def test_scaffold_idempotent(self):
        """Running scaffold twice doesn't break anything."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)
            scaffolder.scaffold(state)  # Second run

            verification = scaffolder.verify()
            assert all(verification.values())

    def test_verify_all_pass(self):
        """Verify returns all True for valid workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)

            verification = scaffolder.verify()
            assert all(verification.values()), f"Failed: {[k for k, v in verification.items() if not v]}"

    def test_verify_detects_missing(self):
        """Verify detects missing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffolder = WorkspaceScaffolder(tmpdir)
            verification = scaffolder.verify()
            assert not all(verification.values())

    def test_get_workspace_summary(self):
        """Summary includes workspace path and directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            scaffolder = WorkspaceScaffolder(tmpdir)
            scaffolder.scaffold(state)

            summary = scaffolder.get_workspace_summary()
            assert "Workspace" in summary
            assert "data/raw" in summary
