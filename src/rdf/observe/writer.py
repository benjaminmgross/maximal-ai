"""
Docstring writer - applies generated docstrings to source files.

Position
--------
Modifies Python source files to insert or update docstrings.
Creates backups before modification.

Invariants
----------
- Always creates backup before modifying
- Preserves file formatting where possible
- Uses AST for accurate insertion points
"""

from __future__ import annotations

import ast
import shutil
from datetime import datetime
from pathlib import Path

from rich.console import Console

from rdf.observe.models import GeneratedDocstring

console = Console()


def apply_docstrings(docstrings: list[GeneratedDocstring]) -> None:
    """
    Apply generated docstrings to source files.

    Parameters
    ----------
    docstrings : list[GeneratedDocstring]
        Docstrings to apply.
    """
    # Group by file
    by_file: dict[str, list[GeneratedDocstring]] = {}
    for doc in docstrings:
        by_file.setdefault(doc.file_path, []).append(doc)

    for file_path, file_docs in by_file.items():
        _apply_to_file(Path(file_path), file_docs)


def _apply_to_file(path: Path, docstrings: list[GeneratedDocstring]) -> None:
    """Apply docstrings to a single file."""
    if not path.exists():
        console.print(f"[yellow]Skipping {path} - file not found[/yellow]")
        return

    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".py.bak.{timestamp}")
    shutil.copy(path, backup_path)
    console.print(f"[dim]Backup created: {backup_path}[/dim]")

    # Read source
    source = path.read_text()
    lines = source.splitlines(keepends=True)

    # Ensure file ends with newline for consistent handling
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    # Parse AST to find function locations
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        console.print(f"[red]Syntax error in {path}: {e}[/red]")
        return

    # Sort docstrings by line number (descending) to apply from bottom up
    # This prevents line number shifts from affecting later insertions
    docstrings.sort(key=lambda d: d.line_number, reverse=True)

    for doc in docstrings:
        # Find the function node
        func_node = _find_function_node(tree, doc.line_number)
        if not func_node:
            console.print(f"[yellow]Could not find function at line {doc.line_number}[/yellow]")
            continue

        # Calculate indentation from the def line
        def_line_idx = func_node.lineno - 1
        if def_line_idx >= len(lines):
            continue

        def_line = lines[def_line_idx]
        base_indent = len(def_line) - len(def_line.lstrip())
        body_indent = base_indent + 4  # Standard 4-space indent for body
        indent_str = " " * body_indent

        # Format new docstring
        docstring_content = doc.render()
        formatted_lines = [f'{indent_str}"""\n']
        for line in docstring_content.splitlines():
            if line.strip():
                formatted_lines.append(f"{indent_str}{line}\n")
            else:
                formatted_lines.append("\n")
        formatted_lines.append(f'{indent_str}"""\n')

        # Check if there's an existing docstring
        existing_docstring = ast.get_docstring(func_node)

        if existing_docstring and func_node.body:
            # Replace existing docstring
            docstring_node = func_node.body[0]
            if isinstance(docstring_node, ast.Expr) and isinstance(
                docstring_node.value, (ast.Str, ast.Constant)
            ):
                start_line = docstring_node.lineno - 1
                end_line = (
                    docstring_node.end_lineno if docstring_node.end_lineno else start_line + 1
                )

                # Replace the lines
                lines[start_line:end_line] = formatted_lines
        else:
            # Insert new docstring after the def line
            # Find where the body starts
            if func_node.body:
                first_body_line = func_node.body[0].lineno - 1
                lines[first_body_line:first_body_line] = formatted_lines
            else:
                # Empty function - insert after def
                lines.insert(def_line_idx + 1, "".join(formatted_lines))

    # Write back
    path.write_text("".join(lines))
    console.print(f"[green]✓ Updated {path}[/green]")


def _find_function_node(
    tree: ast.Module, line_number: int
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Find function node by line number."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno == line_number:
                return node
    return None
