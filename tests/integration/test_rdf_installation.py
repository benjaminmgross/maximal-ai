"""
Layer 3: End-to-End Installation Tests.

These tests run the full `rdf init` + `scaffold-context-files` workflow
against a realistic mock repository and verify the acceptance criteria
from the bug spec:

1. Each .context.md heading matches its actual directory name
2. No two .context.md files in different directories are identical
3. AGENTS.md reflects the actual tech stack
4. substrate.md contains the actual project name
5. No placeholder residue in any generated file

These tests would have caught the original bug immediately because they
test the *user-visible output*, not just the mechanism.
"""

import re
from pathlib import Path

from click.testing import CliRunner

from rdf.cli import main

# Regex to find unfilled {{...}} or [PLACEHOLDER] patterns
DOUBLE_BRACE_PATTERN = re.compile(r"\{\{[A-Z_]+\}\}")
BRACKET_PLACEHOLDER = re.compile(r"\[(?:PROJECT_NAME|ONE_LINE_DESCRIPTION)\]")


def _create_realistic_python_project(root: Path) -> None:
    """Create a multi-directory Python project with realistic structure."""
    # pyproject.toml
    (root / "pyproject.toml").write_text("""\
[project]
name = "acme-payments"
description = "Payment processing for Acme Corp"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.100",
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
    "redis>=5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
""")
    (root / "uv.lock").write_text("")

    # Source directories (multiple, to test uniqueness)
    src = root / "src"
    for pkg in ["api", "models", "services", "utils", "workers"]:
        pkg_dir = src / "acme_payments" / pkg
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "__init__.py").write_text(f'"""The {pkg} package."""\n')
        (pkg_dir / f"{pkg}_core.py").write_text(f'"""Core {pkg} logic."""\n')

    # Tests directory
    tests = root / "tests"
    tests.mkdir()
    (tests / "conftest.py").write_text('"""Test config."""\n')
    (tests / "test_api.py").write_text('"""API tests."""\n')


class TestEndToEndInstallation:
    """Full workflow: rdf init + scaffold-context-files on a realistic repo."""

    def test_full_installation_produces_unique_context_files(self) -> None:
        """AC#2: No two .context.md files in different directories should be identical."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            _create_realistic_python_project(Path(td))

            # Run init
            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0, f"init failed: {result.output}"

            # Run scaffold-context-files
            result = runner.invoke(main, ["scaffold-context-files", "src"])
            assert result.exit_code == 0, f"scaffold failed: {result.output}"

            # Collect all .context.md files
            context_files: dict[str, str] = {}
            for f in Path("src").rglob(".context.md"):
                context_files[str(f)] = f.read_text()

            # Must have created files for multiple directories
            assert len(context_files) >= 3, (
                f"Expected at least 3 .context.md files, got {len(context_files)}: "
                f"{list(context_files.keys())}"
            )

            # No two should be identical
            for i, (path_a, content_a) in enumerate(context_files.items()):
                for path_b, content_b in list(context_files.items())[i + 1 :]:
                    assert content_a != content_b, (
                        f"IDENTICAL .context.md files found:\n"
                        f"  {path_a}\n  {path_b}\n\n"
                        f"This is the '407 identical files' bug. Each file "
                        f"must be directory-specific."
                    )

    def test_context_md_headings_match_directory_names(self) -> None:
        """AC#1: Each .context.md heading must match its directory name."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            _create_realistic_python_project(Path(td))
            runner.invoke(main, ["init"])
            runner.invoke(main, ["scaffold-context-files", "src"])

            for context_md in Path("src").rglob(".context.md"):
                dirname = context_md.parent.name
                content = context_md.read_text()
                first_line = content.strip().splitlines()[0]

                assert dirname in first_line, (
                    f"{context_md}: heading '{first_line}' does not contain "
                    f"directory name '{dirname}'"
                )

    def test_agents_md_reflects_detected_tech_stack(self) -> None:
        """AC#3: AGENTS.md must reflect the actual tech stack."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            _create_realistic_python_project(Path(td))
            runner.invoke(main, ["init"])

            agents_md = Path("docs/AGENTS.md")
            assert agents_md.exists()
            content = agents_md.read_text()

            # Must contain detected values
            assert "Python" in content, "AGENTS.md missing detected language"
            assert "uv" in content, "AGENTS.md missing detected package manager"

            # Must NOT contain hardcoded example tech stack
            assert "PostgreSQL 16" not in content
            assert "FastAPI 0.115+" not in content

    def test_substrate_md_contains_project_name(self) -> None:
        """AC#4: substrate.md must contain actual project name."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            _create_realistic_python_project(Path(td))
            runner.invoke(main, ["init"])

            substrate = Path(".context/substrate.md")
            assert substrate.exists()
            content = substrate.read_text()

            assert "acme-payments" in content, (
                "substrate.md does not contain the project name 'acme-payments'"
            )
            assert "[PROJECT_NAME]" not in content, (
                "substrate.md still has unfilled [PROJECT_NAME] placeholder"
            )

    def test_no_placeholder_residue_in_generated_files(self) -> None:
        """AC#5: No {{...}} or [PLACEHOLDER] residue in any generated file."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            _create_realistic_python_project(Path(td))
            runner.invoke(main, ["init"])
            runner.invoke(main, ["scaffold-context-files", "src"])

            # Check .context/ files
            for f in Path(".context").rglob("*.md"):
                content = f.read_text()
                double_brace = DOUBLE_BRACE_PATTERN.findall(content)
                bracket = BRACKET_PLACEHOLDER.findall(content)
                assert not double_brace, (
                    f"{f} has unfilled {{{{...}}}} placeholders: {double_brace}"
                )
                assert not bracket, (
                    f"{f} has unfilled [...] placeholders: {bracket}"
                )

            # Check AGENTS.md
            agents = Path("docs/AGENTS.md")
            if agents.exists():
                content = agents.read_text()
                double_brace = DOUBLE_BRACE_PATTERN.findall(content)
                assert not double_brace, (
                    f"AGENTS.md has unfilled placeholders: {double_brace}"
                )

    def test_cli_scaffold_context_files_matches_init_quality(self) -> None:
        """AC#6: CLI scaffold-context-files must produce same quality as init."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            _create_realistic_python_project(Path(td))

            # Only run scaffold-context-files (not init)
            result = runner.invoke(main, ["scaffold-context-files", "src"])
            assert result.exit_code == 0

            # Verify same quality standards
            for context_md in Path("src").rglob(".context.md"):
                dirname = context_md.parent.name
                content = context_md.read_text()
                first_line = content.strip().splitlines()[0]

                # Heading must match directory
                assert dirname in first_line, (
                    f"scaffold-context-files: {context_md} heading "
                    f"'{first_line}' doesn't contain '{dirname}'"
                )


class TestCrossProjectConsistency:
    """Verify RDF produces correct output for different project types."""

    def test_js_project_does_not_get_python_content(self) -> None:
        """A JS project must not get Python-specific content."""
        runner = CliRunner()
        with runner.isolated_filesystem() as td:
            # Create a JS project
            (Path(td) / "package.json").write_text("""\
{
    "name": "cool-dashboard",
    "description": "A cool dashboard",
    "dependencies": {"react": "^18.0", "next": "^14.0"},
    "devDependencies": {"typescript": "^5.0", "vitest": "^1.0"}
}
""")
            (Path(td) / "src" / "components").mkdir(parents=True)

            runner.invoke(main, ["init"])

            agents = Path("docs/AGENTS.md")
            assert agents.exists()
            content = agents.read_text()

            # Should have JS-specific content
            assert "TypeScript" in content or "JavaScript" in content
            assert "npm" in content

            # substrate.md should have JS project name
            substrate = Path(".context/substrate.md")
            if substrate.exists():
                assert "cool-dashboard" in substrate.read_text()

    def test_empty_project_uses_todo_markers(self) -> None:
        """A project with no manifest should use TODO markers, not examples."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])

            agents = Path("docs/AGENTS.md")
            assert agents.exists()
            content = agents.read_text()

            # Should have TODO markers, not hardcoded FastAPI stack
            assert "FastAPI 0.115+" not in content
            assert "PostgreSQL 16" not in content
            assert "SQLAlchemy 2.0+ with async" not in content
