"""
RDF Command-Line Interface.

Position
--------
Main entry point for all RDF CLI commands. Orchestrates init, scaffold-folders,
generate-repomap, and validate operations.

Invariants
----------
- All commands are idempotent where possible
- Dry-run mode available for destructive operations
- Exit codes: 0=success, 1=validation failure, 2=error
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from rdf import __version__
from rdf.generators.foldermd import FolderMdGenerator
from rdf.generators.repomap import RepomapGenerator
from rdf.linters.docstring import DocstringLinter, Severity, Strictness

console = Console()


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """
    Repo Documentation Framework (RDF).

    Standardized documentation for humans and AI.
    """


@main.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without writing files",
)
def init(*, dry_run: bool) -> None:
    """
    Initialize RDF in the current repository.

    Creates docs/AGENTS.md, docs/CLAUDE.md, .repomap.yaml, and directory structure.
    """
    console.print("[bold green]Initializing RDF...[/bold green]")

    dirs_to_create = [
        "docs",
        "docs/ai/protocols",
        "docs/ai/checklists",
        "docs/ai/prompts",
        "docs/guides",
        "docs/templates",
        "docs/architecture/decisions",
    ]

    files_to_create = {
        "docs/AGENTS.md": _agents_template(),
        ".repomap.yaml": _repomap_config_template(),
    }

    if dry_run:
        console.print("[yellow]Dry run - would create:[/yellow]")
        for d in dirs_to_create:
            console.print(f"  [dir] {d}/")
        for f in files_to_create:
            console.print(f"  [file] {f}")
        return

    # Create directories
    for d in dirs_to_create:
        Path(d).mkdir(parents=True, exist_ok=True)
        console.print(f"  Created {d}/")

    # Create files
    for filepath, content in files_to_create.items():
        path = Path(filepath)
        if not path.exists():
            path.write_text(content)
            console.print(f"  Created {filepath}")
        else:
            console.print(f"  Skipped {filepath} (exists)")

    console.print("\n[bold green]RDF initialized![/bold green]")


@main.command("scaffold-folders")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without writing files",
)
def scaffold_folders(path: str, *, dry_run: bool) -> None:
    """
    Add .folder.md files to source directories.

    Scans PATH recursively and creates .folder.md templates for folders
    that don't have them.
    """
    source_path = Path(path)
    console.print(f"[bold green]Scaffolding .folder.md in {source_path}[/bold green]")

    # Find directories without .folder.md
    dirs_to_scaffold = []
    for dir_path in source_path.rglob("*"):
        if dir_path.is_dir() and not dir_path.name.startswith("."):
            if "__pycache__" in str(dir_path):
                continue
            folder_md = dir_path / ".folder.md"
            if not folder_md.exists():
                dirs_to_scaffold.append(dir_path)

    # Also check the root
    root_folder_md = source_path / ".folder.md"
    if not root_folder_md.exists():
        dirs_to_scaffold.insert(0, source_path)

    if not dirs_to_scaffold:
        console.print("[yellow]All directories already have .folder.md files[/yellow]")
        return

    if dry_run:
        console.print("[yellow]Dry run - would create .folder.md in:[/yellow]")
        for d in dirs_to_scaffold:
            console.print(f"  {d}/")
        return

    for dir_path in dirs_to_scaffold:
        generator = FolderMdGenerator(dir_path)
        generator.generate(dry_run=False)
        console.print(f"  Created {dir_path}/.folder.md")

    console.print(f"\n[bold green]Created {len(dirs_to_scaffold)} .folder.md files[/bold green]")


@main.command("generate-repomap")
@click.option(
    "--source",
    type=click.Path(exists=True),
    default="src",
    help="Source directory to scan",
)
@click.option(
    "--output",
    type=click.Path(),
    default="REPOMAP.yaml",
    help="Output path for REPOMAP.yaml",
)
def generate_repomap(source: str, output: str) -> None:
    """
    Generate REPOMAP.yaml from source code.

    Parses Python files, extracts symbols and docstrings, builds dependency
    graph, and outputs YAML.
    """
    console.print("[bold green]Generating REPOMAP.yaml...[/bold green]")

    source_path = Path(source)
    output_path = Path(output)

    if not source_path.exists():
        console.print(f"[red]Source directory not found: {source}[/red]")
        sys.exit(2)

    generator = RepomapGenerator(source_path)
    result = generator.generate(output_path)

    console.print(f"  Source: {source}")
    console.print(f"  Output: {output}")
    console.print(f"  Files indexed: {result['meta']['files_indexed']}")
    console.print("\n[bold green]REPOMAP.yaml generated![/bold green]")


@main.command()
@click.option(
    "--strict",
    is_flag=True,
    help="Enable strict validation (require all semantic sections)",
)
@click.option(
    "--path",
    type=click.Path(exists=True),
    default="src",
    help="Path to validate",
)
def validate(*, strict: bool, path: str) -> None:
    """
    Validate RDF compliance.

    Checks .folder.md coverage, REPOMAP freshness, and docstring requirements.
    """
    console.print("[bold green]Validating RDF compliance...[/bold green]\n")

    source_path = Path(path)
    strictness = Strictness.STRICT if strict else Strictness.STANDARD

    # Run docstring linter
    linter = DocstringLinter(strictness=strictness)
    result = linter.lint_directory(source_path)

    # Check .folder.md coverage
    dirs_without_foldermd = []
    for dir_path in source_path.rglob("*"):
        if dir_path.is_dir() and not dir_path.name.startswith("."):
            if "__pycache__" in str(dir_path):
                continue
            folder_md = dir_path / ".folder.md"
            if not folder_md.exists():
                dirs_without_foldermd.append(dir_path)

    # Display results
    table = Table(title="Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    # Docstring check
    error_count = sum(1 for v in result.violations if v.severity == Severity.ERROR)
    warning_count = sum(1 for v in result.violations if v.severity == Severity.WARNING)

    if error_count == 0:
        table.add_row(
            "Docstrings",
            "[green]PASS[/green]",
            f"{result.files_checked} files, {warning_count} warnings",
        )
    else:
        table.add_row(
            "Docstrings",
            "[red]FAIL[/red]",
            f"{error_count} errors, {warning_count} warnings",
        )

    # .folder.md check
    if not dirs_without_foldermd:
        table.add_row(".folder.md coverage", "[green]PASS[/green]", "All directories covered")
    else:
        table.add_row(
            ".folder.md coverage",
            "[yellow]WARN[/yellow]",
            f"{len(dirs_without_foldermd)} directories missing",
        )

    # REPOMAP check
    repomap_path = Path("REPOMAP.yaml")
    if repomap_path.exists():
        table.add_row("REPOMAP.yaml", "[green]EXISTS[/green]", str(repomap_path))
    else:
        table.add_row("REPOMAP.yaml", "[yellow]MISSING[/yellow]", "Run: rdf generate-repomap")

    console.print(table)

    # Show violations if any
    if result.violations:
        console.print("\n[bold]Violations:[/bold]")
        for v in result.violations[:10]:  # Limit to first 10
            severity_color = "red" if v.severity == Severity.ERROR else "yellow"
            console.print(
                f"  [{severity_color}]{v.code}[/{severity_color}] "
                f"{v.path}:{v.line} - {v.message}"
            )
        if len(result.violations) > 10:
            console.print(f"  ... and {len(result.violations) - 10} more")

    # Exit with appropriate code
    if error_count > 0:
        sys.exit(1)


def _agents_template() -> str:
    """Return AGENTS.md template."""
    return '''# AGENTS.md

## Commands

All build, test, and environment commands.

```bash
# Environment Setup
# TODO: Add your environment setup commands

# Run Tests
# TODO: Add test commands

# Lint & Format
# TODO: Add lint/format commands
```

## Code Rules

Rules specific to this repository:

- TODO: Add repository-specific coding rules

## Protocols

AI guidance for complex areas:

- See docs/ai/protocols/ for detailed protocols
- See docs/ai/checklists/ for verification checklists

## Code Structure

See [REPOMAP.yaml](REPOMAP.yaml) for auto-generated dependency graph.

## Conventions

- Branch naming: `feature/`, `fix/`, `refactor/`
- Commit messages: conventional commits format
'''


def _repomap_config_template() -> str:
    """Return .repomap.yaml template."""
    return '''# REPOMAP.yaml Configuration
# Run: rdf generate-repomap to create REPOMAP.yaml

source_dirs:
  - src

exclude:
  - __pycache__
  - .venv
  - node_modules
  - .git

token_budget: 2000

ranking:
  algorithm: simple  # simple or pagerank
'''


if __name__ == "__main__":
    main()
