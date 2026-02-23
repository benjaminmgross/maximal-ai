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
        assert "scaffold-context-files" in result.output
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

    def test_scaffold_context_files_dry_run(self, runner: CliRunner) -> None:
        """Test scaffold-context-files command in dry-run mode."""
        with runner.isolated_filesystem():
            # Create directory structure
            Path("src/module").mkdir(parents=True)
            Path("src/utils").mkdir()

            result = runner.invoke(main, ["scaffold-context-files", "src", "--dry-run"])
            assert result.exit_code == 0
            assert "Dry run" in result.output

            # Verify no files were created
            assert not Path("src/.context.md").exists()

    def test_scaffold_context_files_creates_files(self, runner: CliRunner) -> None:
        """Test scaffold-context-files command creates .context.md files."""
        with runner.isolated_filesystem():
            # Create directory structure
            Path("src/module").mkdir(parents=True)
            Path("src/module/main.py").write_text("# main")

            result = runner.invoke(main, ["scaffold-context-files", "src"])
            assert result.exit_code == 0

            assert Path("src/.context.md").exists()
            assert Path("src/module/.context.md").exists()

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

    def test_init_creates_context_directory(self, runner: CliRunner) -> None:
        """Test init command creates .context/ directory with all expected files."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0

            assert Path(".context/substrate.md").exists()
            assert Path(".context/ai-rules.md").exists()
            assert Path(".context/glossary.md").exists()
            assert Path(".context/anti-patterns.md").exists()
            assert Path(".context/testing.md").exists()
            assert Path(".context/prompts").is_dir()
            assert Path(".context/architecture").is_dir()
            assert Path(".context/decisions").is_dir()

    def test_init_preserves_existing_context(self, runner: CliRunner) -> None:
        """Test init preserves existing .context/ files."""
        with runner.isolated_filesystem():
            Path(".context").mkdir()
            Path(".context/glossary.md").write_text("# My Custom Glossary\n")

            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0

            content = Path(".context/glossary.md").read_text()
            assert content == "# My Custom Glossary\n"

    def test_scaffold_context_creates_single_file(self, runner: CliRunner) -> None:
        """Test scaffold-context creates a single .context/ file."""
        with runner.isolated_filesystem():
            Path(".context").mkdir()
            result = runner.invoke(main, ["scaffold-context", "glossary"])
            assert result.exit_code == 0
            assert Path(".context/glossary.md").exists()

    def test_scaffold_context_all(self, runner: CliRunner) -> None:
        """Test scaffold-context all creates all .context/ files."""
        with runner.isolated_filesystem():
            Path(".context").mkdir()
            result = runner.invoke(main, ["scaffold-context", "all"])
            assert result.exit_code == 0
            assert Path(".context/substrate.md").exists()
            assert Path(".context/ai-rules.md").exists()
            assert Path(".context/glossary.md").exists()

    def test_scaffold_context_force_overwrites(self, runner: CliRunner) -> None:
        """Test scaffold-context --force overwrites existing files."""
        with runner.isolated_filesystem():
            Path(".context").mkdir()
            Path(".context/glossary.md").write_text("# Old content\n")

            result = runner.invoke(main, ["scaffold-context", "glossary", "--force"])
            assert result.exit_code == 0

            content = Path(".context/glossary.md").read_text()
            assert "# Old content" not in content
            assert "Glossary" in content

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
