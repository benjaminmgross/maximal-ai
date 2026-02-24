"""
RDF Command-Line Interface.

Position
--------
Main entry point for all RDF CLI commands. Orchestrates init, scaffold-context,
scaffold-context-files, generate-repomap, validate, status, and observe operations.

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
from rdf.generators.context_file import ContextFileGenerator
from rdf.generators.repomap import RepomapGenerator
from rdf.linters.docstring import DocstringLinter, Severity, Strictness
from rdf.validators.context import ContextValidator

console = Console()

# Template directory for .context/ files
_TEMPLATE_BASE = Path(__file__).resolve().parent.parent.parent / "templates" / "rdf"

# Mapping of context file types to their template paths and output paths
_CONTEXT_FILE_MAP: dict[str, tuple[str, str]] = {
    "substrate": ("context/substrate.md.template", "substrate.md"),
    "ai-rules": ("context/ai-rules.md.template", "ai-rules.md"),
    "anti-patterns": ("context/anti-patterns.md.template", "anti-patterns.md"),
    "glossary": ("context/glossary.md.template", "glossary.md"),
    "testing": ("context/testing.md.template", "testing.md"),
}

_CONTEXT_DIR_MAP: dict[str, list[tuple[str, str]]] = {
    "prompts": [
        ("context/prompts/README.md.template", "README.md"),
        ("context/prompts/new-endpoint.md.template", "new-endpoint.md"),
        ("context/prompts/fix-bug.md.template", "fix-bug.md"),
        ("context/prompts/refactor.md.template", "refactor.md"),
    ],
    "architecture": [
        ("context/architecture/overview.md.template", "overview.md"),
    ],
    "decisions": [
        ("context/decisions/adr-template.md.template", "adr-template.md"),
    ],
}


def _load_template(template_path: str) -> str:
    """Load a template file from the templates directory."""
    full_path = _TEMPLATE_BASE / template_path
    return full_path.read_text()


def _scaffold_context_dir(
    *,
    context_dir: Path,
    force: bool = False,
    quiet: bool = False,
) -> None:
    """Scaffold the full .context/ directory from templates."""
    context_dir.mkdir(exist_ok=True)

    # Create top-level files
    for _type, (template_path, filename) in _CONTEXT_FILE_MAP.items():
        filepath = context_dir / filename
        if not filepath.exists() or force:
            filepath.write_text(_load_template(template_path))
            if not quiet:
                console.print(f"  Created .context/{filename}")
        elif not quiet:
            console.print(f"  Skipped .context/{filename} (already exists)")

    # Create subdirectories and their files
    for dirname, file_list in _CONTEXT_DIR_MAP.items():
        subdir = context_dir / dirname
        subdir.mkdir(exist_ok=True)
        for template_path, filename in file_list:
            filepath = subdir / filename
            if not filepath.exists() or force:
                filepath.write_text(_load_template(template_path))
                if not quiet:
                    console.print(f"  Created .context/{dirname}/{filename}")
            elif not quiet:
                console.print(f"  Skipped .context/{dirname}/{filename} (already exists)")


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
        console.print("  [dir] .context/")
        for _file_type, (_tpl, filename) in _CONTEXT_FILE_MAP.items():
            console.print(f"  [file] .context/{filename}")
        for dirname, file_list in _CONTEXT_DIR_MAP.items():
            console.print(f"  [dir] .context/{dirname}/")
            for _tpl, filename in file_list:
                console.print(f"  [file] .context/{dirname}/{filename}")
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

    # Scaffold .context/ directory
    console.print("\n[bold]Scaffolding .context/ directory...[/bold]")
    _scaffold_context_dir(context_dir=Path(".context"))

    console.print("\n[bold green]RDF initialized![/bold green]")


@main.command("scaffold-context")
@click.argument(
    "file_type",
    type=click.Choice([
        "substrate", "ai-rules", "anti-patterns", "glossary",
        "testing", "prompts", "architecture", "decisions", "all",
    ]),
)
@click.option("--force", is_flag=True, help="Overwrite existing files")
def scaffold_context(file_type: str, *, force: bool) -> None:
    """Scaffold individual .context/ files from templates."""
    context_dir = Path(".context")
    context_dir.mkdir(exist_ok=True)

    if file_type == "all":
        _scaffold_context_dir(context_dir=context_dir, force=force)
        console.print("\n[bold green]All .context/ files scaffolded![/bold green]")
        return

    # Check if it's a top-level file
    if file_type in _CONTEXT_FILE_MAP:
        template_path, filename = _CONTEXT_FILE_MAP[file_type]
        filepath = context_dir / filename
        if not filepath.exists() or force:
            filepath.write_text(_load_template(template_path))
            console.print(f"  Created .context/{filename}")
        else:
            console.print(f"  Skipped .context/{filename} (already exists, use --force)")
        return

    # Check if it's a directory type
    if file_type in _CONTEXT_DIR_MAP:
        subdir = context_dir / file_type
        subdir.mkdir(exist_ok=True)
        for template_path, filename in _CONTEXT_DIR_MAP[file_type]:
            filepath = subdir / filename
            if not filepath.exists() or force:
                filepath.write_text(_load_template(template_path))
                console.print(f"  Created .context/{file_type}/{filename}")
            else:
                console.print(
                    f"  Skipped .context/{file_type}/{filename} (already exists, use --force)"
                )
        return


@main.command("scaffold-context-files")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without writing files",
)
def scaffold_context_files(path: str, *, dry_run: bool) -> None:
    """
    Add .context.md files to source directories.

    Scans PATH recursively and creates .context.md templates for folders
    that don't have them.
    """
    source_path = Path(path)
    console.print(f"[bold green]Scaffolding .context.md in {source_path}[/bold green]")

    # Find directories without .context.md
    dirs_to_scaffold = []
    for dir_path in source_path.rglob("*"):
        if dir_path.is_dir() and not dir_path.name.startswith("."):
            if "__pycache__" in str(dir_path):
                continue
            context_md = dir_path / ".context.md"
            if not context_md.exists():
                dirs_to_scaffold.append(dir_path)

    # Also check the root
    root_context_md = source_path / ".context.md"
    if not root_context_md.exists():
        dirs_to_scaffold.insert(0, source_path)

    if not dirs_to_scaffold:
        console.print("[yellow]All directories already have .context.md files[/yellow]")
        return

    if dry_run:
        console.print("[yellow]Dry run - would create .context.md in:[/yellow]")
        for d in dirs_to_scaffold:
            console.print(f"  {d}/")
        return

    for dir_path in dirs_to_scaffold:
        generator = ContextFileGenerator(dir_path)
        generator.generate(dry_run=False)
        console.print(f"  Created {dir_path}/.context.md")

    console.print(
        f"\n[bold green]Created {len(dirs_to_scaffold)} .context.md files[/bold green]"
    )


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
    context_dir = Path(".context")
    result = generator.generate(
        output_path,
        context_dir=context_dir if context_dir.exists() else None,
    )

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
@click.option(
    "--skip-context",
    is_flag=True,
    help="Skip .context/ directory validation",
)
def validate(*, strict: bool, path: str, skip_context: bool) -> None:
    """
    Validate RDF compliance.

    Checks .context/ directory, .context.md coverage, REPOMAP freshness,
    and docstring requirements.
    """
    console.print("[bold green]Validating RDF compliance...[/bold green]\n")

    source_path = Path(path)
    strictness = Strictness.STRICT if strict else Strictness.STANDARD

    # Run docstring linter
    linter = DocstringLinter(strictness=strictness)
    result = linter.lint_directory(source_path)

    # Check .context.md coverage
    dirs_without_contextmd = []
    for dir_path in source_path.rglob("*"):
        if dir_path.is_dir() and not dir_path.name.startswith("."):
            if "__pycache__" in str(dir_path):
                continue
            context_md = dir_path / ".context.md"
            if not context_md.exists():
                dirs_without_contextmd.append(dir_path)

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

    # .context.md check
    if not dirs_without_contextmd:
        table.add_row(".context.md coverage", "[green]PASS[/green]", "All directories covered")
    else:
        table.add_row(
            ".context.md coverage",
            "[yellow]WARN[/yellow]",
            f"{len(dirs_without_contextmd)} directories missing",
        )

    # .context/ directory check
    all_violations = list(result.violations)
    if not skip_context:
        context_result = ContextValidator(root=Path(".")).validate()
        ctx_errors = sum(1 for v in context_result.violations if v.severity == Severity.ERROR)
        ctx_warnings = sum(1 for v in context_result.violations if v.severity == Severity.WARNING)
        ctx_infos = sum(1 for v in context_result.violations if v.severity == Severity.INFO)

        if ctx_errors == 0 and ctx_warnings == 0:
            table.add_row(".context/ directory", "[green]PASS[/green]", "All files present")
        elif ctx_errors > 0:
            table.add_row(
                ".context/ directory",
                "[red]FAIL[/red]",
                f"{ctx_errors} missing required, {ctx_warnings} warnings",
            )
        else:
            table.add_row(
                ".context/ directory",
                "[yellow]WARN[/yellow]",
                f"{ctx_warnings} warnings, {ctx_infos} info",
            )

        all_violations.extend(context_result.violations)

    # REPOMAP check
    repomap_path = Path("REPOMAP.yaml")
    if repomap_path.exists():
        table.add_row("REPOMAP.yaml", "[green]EXISTS[/green]", str(repomap_path))
    else:
        table.add_row("REPOMAP.yaml", "[yellow]MISSING[/yellow]", "Run: rdf generate-repomap")

    console.print(table)

    # Show violations if any
    if all_violations:
        console.print("\n[bold]Violations:[/bold]")
        for v in all_violations[:10]:  # Limit to first 10
            severity_color = "red" if v.severity == Severity.ERROR else "yellow"
            console.print(
                f"  [{severity_color}]{v.code}[/{severity_color}] {v.path}:{v.line} - {v.message}"
            )
        if len(all_violations) > 10:
            console.print(f"  ... and {len(all_violations) - 10} more")

    # Exit with appropriate code
    total_errors = sum(1 for v in all_violations if v.severity == Severity.ERROR)
    if total_errors > 0:
        sys.exit(1)


@main.command()
@click.argument("script", type=click.Path(exists=True), required=False)
@click.option("--entrypoint", "-e", default="main", help="Function to call")
@click.option("--non-interactive", is_flag=True, help="Skip human prompts")
@click.option("--dry-run", is_flag=True, help="Preview without applying")
@click.option("--filter", "func_filter", help="Only process functions matching pattern")
@click.option(
    "--resume",
    type=click.Path(exists=True),
    help="Resume from saved observation JSON file",
)
def observe(
    script: str | None,
    entrypoint: str,
    *,
    non_interactive: bool,
    dry_run: bool,
    func_filter: str | None,
    resume: str | None,
) -> None:
    """
    Run a script and interactively generate docstrings.

    Observes function behavior at runtime, infers what it can,
    and prompts you for business context. Generates complete
    NumPy-format docstrings.

    \b
    Examples:
        rdf observe myapp.py --entrypoint main
        rdf observe myapp.py --non-interactive --dry-run
        rdf observe myapp.py --filter "calculate_*"
        rdf observe --resume observations.json
    """
    import fnmatch
    import json

    from rdf.observe.analyzer import InferenceEngine
    from rdf.observe.interactive import InteractiveSession
    from rdf.observe.models import FunctionProfile
    from rdf.observe.runner import run_with_observation
    from rdf.observe.writer import apply_docstrings

    # Load from resume file or run observation
    if resume:
        console.print(f"[bold]Resuming from {resume}...[/bold]")
        with open(resume) as f:
            data = json.load(f)
        profiles = {k: FunctionProfile.from_dict(v) for k, v in data.get("profiles", {}).items()}
        console.print(f"[green]✓ Loaded {len(profiles)} function profiles[/green]")
    elif script:
        console.print(f"[bold]Running {script}...[/bold]")
        profiles = run_with_observation(Path(script), entrypoint)
        total_calls = sum(p.call_count for p in profiles.values())
        console.print(
            f"[green]✓ Collected {total_calls} observations from {len(profiles)} functions[/green]"
        )
    else:
        console.print(
            "[red]Error: Either provide a script to run or --resume with a JSON file[/red]"
        )
        sys.exit(2)

    if not profiles:
        console.print(
            "[yellow]No functions were observed. "
            "Make sure functions are decorated with @observe.[/yellow]"
        )
        return

    # Filter if requested
    if func_filter:
        profiles = {k: v for k, v in profiles.items() if fnmatch.fnmatch(k, f"*{func_filter}*")}
        console.print(f"[dim]Filtered to {len(profiles)} functions matching '{func_filter}'[/dim]")

    # Analyze
    console.print("\n[bold]Analyzing...[/bold]")
    engine = InferenceEngine(profiles)
    inferences = engine.infer_all()

    # Interactive session
    session = InteractiveSession(
        profiles=profiles,
        inferences=inferences,
        non_interactive=non_interactive,
    )

    generated = session.run()

    # Apply or preview
    if generated:
        console.print(f"\n[bold]Generated {len(generated)} docstrings[/bold]")

        if dry_run:
            console.print("[yellow]Dry run - no changes applied[/yellow]")
        else:
            apply_docstrings(generated)
            console.print("[green]✓ Docstrings applied successfully[/green]")
    else:
        console.print("[yellow]No docstrings generated[/yellow]")


@main.command()
@click.option("--path", type=click.Path(exists=True), default=".", help="Project root")
def status(path: str) -> None:
    """Show RDF documentation status and coverage."""
    project = Path(path).resolve()

    console.print("[bold]RDF Documentation Status[/bold]\n")

    # Check each component
    checks: list[tuple[str, bool]] = [
        ("CLAUDE.md", (project / "CLAUDE.md").exists()),
        (
            "CLAUDE.md has RDF bootstrap",
            _has_rdf_bootstrap(project / "CLAUDE.md"),
        ),
        (".context/ directory", (project / ".context").is_dir()),
        (
            ".context/substrate.md",
            (project / ".context" / "substrate.md").exists(),
        ),
        (
            ".context/ai-rules.md",
            (project / ".context" / "ai-rules.md").exists(),
        ),
        ("REPOMAP.yaml", (project / "REPOMAP.yaml").exists()),
        ("docs/AGENTS.md", (project / "docs" / "AGENTS.md").exists()),
    ]

    for check_name, check_status in checks:
        icon = "[green]✓[/green]" if check_status else "[red]✗[/red]"
        console.print(f"  {icon} {check_name}")

    # Count .context.md coverage in source directories
    source_dirs = [
        d
        for d in project.iterdir()
        if d.is_dir() and d.name in ("src", "lib", "app")
    ]

    total_dirs = 0
    covered_dirs = 0
    for src in source_dirs:
        # Include the source root directory itself
        total_dirs += 1
        if (src / ".context.md").exists() or (src / ".folder.md").exists():
            covered_dirs += 1
        for d in src.rglob("*"):
            if (
                d.is_dir()
                and not d.name.startswith(".")
                and "__pycache__" not in str(d)
            ):
                total_dirs += 1
                if (d / ".context.md").exists() or (d / ".folder.md").exists():
                    covered_dirs += 1

    if total_dirs > 0:
        pct = int(covered_dirs / total_dirs * 100)
        color = "green" if pct > 80 else "yellow" if pct > 50 else "red"
        console.print(
            f"\n  .context.md coverage: [{color}]{covered_dirs}/{total_dirs} ({pct}%)[/{color}]"
        )

    # Suggest next steps
    suggestions = []
    if not _has_rdf_bootstrap(project / "CLAUDE.md"):
        suggestions.append(
            "Run: maximal-ai rdf-framework -l 1  (to add RDF bootstrap to CLAUDE.md)"
        )
    if not (project / ".context").is_dir():
        suggestions.append(
            "Run: rdf scaffold-context all  (to create .context/ directory)"
        )
    if not (project / "REPOMAP.yaml").exists():
        suggestions.append("Run: rdf generate-repomap --source src/")
    if total_dirs > 0 and covered_dirs < total_dirs:
        missing = total_dirs - covered_dirs
        suggestions.append(
            f"Run: rdf scaffold-context-files src/  ({missing} dirs need .context.md)"
        )

    if suggestions:
        console.print("\n[bold]Suggested next steps:[/bold]")
        for s in suggestions:
            console.print(f"  → {s}")
    else:
        console.print("\n[bold green]All documentation checks passed![/bold green]")


def _has_rdf_bootstrap(claude_md_path: Path) -> bool:
    """Check if CLAUDE.md contains the RDF bootstrap section."""
    if not claude_md_path.exists():
        return False
    content = claude_md_path.read_text()
    return "## Repository Documentation Framework (RDF)" in content


def _agents_template() -> str:
    """Return AGENTS.md template."""
    return """# AGENTS.md

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
"""


def _repomap_config_template() -> str:
    """Return .repomap.yaml template."""
    return """# REPOMAP.yaml Configuration
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
"""


if __name__ == "__main__":
    main()
