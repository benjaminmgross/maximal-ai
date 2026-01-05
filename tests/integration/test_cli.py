"""Integration tests for RDF CLI."""

import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from rdf.cli import main


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLI:
    """Integration tests for the RDF CLI."""

    def test_version(self, runner: CliRunner) -> None:
        """Test --version flag."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help(self, runner: CliRunner) -> None:
        """Test --help flag."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "scaffold-folders" in result.output
        assert "generate-repomap" in result.output
        assert "validate" in result.output

    def test_init_dry_run(self, runner: CliRunner) -> None:
        """Test init command in dry-run mode."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--dry-run"])
            assert result.exit_code == 0
            assert "Dry run" in result.output
            assert "docs/AGENTS.md" in result.output

            # Verify no files were created
            assert not Path("docs").exists()

    def test_init_creates_structure(self, runner: CliRunner) -> None:
        """Test init command creates expected structure."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0

            # Verify directories created
            assert Path("docs").exists()
            assert Path("docs/ai/protocols").exists()
            assert Path("docs/ai/checklists").exists()
            assert Path("docs/guides").exists()

            # Verify files created
            assert Path("docs/AGENTS.md").exists()
            assert Path(".repomap.yaml").exists()

    def test_scaffold_folders_dry_run(self, runner: CliRunner) -> None:
        """Test scaffold-folders command in dry-run mode."""
        with runner.isolated_filesystem():
            # Create directory structure
            Path("src/module").mkdir(parents=True)
            Path("src/utils").mkdir()

            result = runner.invoke(main, ["scaffold-folders", "src", "--dry-run"])
            assert result.exit_code == 0
            assert "Dry run" in result.output

            # Verify no files were created
            assert not Path("src/.folder.md").exists()

    def test_scaffold_folders_creates_files(self, runner: CliRunner) -> None:
        """Test scaffold-folders command creates .folder.md files."""
        with runner.isolated_filesystem():
            # Create directory structure
            Path("src/module").mkdir(parents=True)
            Path("src/module/main.py").write_text("# main")

            result = runner.invoke(main, ["scaffold-folders", "src"])
            assert result.exit_code == 0

            assert Path("src/.folder.md").exists()
            assert Path("src/module/.folder.md").exists()

    def test_generate_repomap(self, runner: CliRunner) -> None:
        """Test generate-repomap command."""
        with runner.isolated_filesystem():
            # Create source files
            Path("src").mkdir()
            Path("src/module.py").write_text('"""Module."""\n\ndef hello(): pass')

            result = runner.invoke(main, ["generate-repomap", "--source", "src"])
            assert result.exit_code == 0
            assert "REPOMAP.yaml generated" in result.output

            assert Path("REPOMAP.yaml").exists()

    def test_validate_command(self, runner: CliRunner) -> None:
        """Test validate command."""
        with runner.isolated_filesystem():
            # Create source with proper docstrings
            Path("src").mkdir()
            Path("src/module.py").write_text('''"""
Module docstring.

Returns
-------
None
"""

def hello():
    """Say hello.

    Returns
    -------
    str
        Greeting message.
    """
    return "Hello"
''')

            result = runner.invoke(main, ["validate", "--path", "src"])
            # Exit code depends on validation results
            assert "Validation Results" in result.output

    def test_validate_strict_mode(self, runner: CliRunner) -> None:
        """Test validate command with strict mode."""
        with runner.isolated_filesystem():
            Path("src").mkdir()
            Path("src/module.py").write_text('"""Module."""\n\ndef hello(): pass')

            result = runner.invoke(main, ["validate", "--path", "src", "--strict"])
            assert "Validation Results" in result.output
