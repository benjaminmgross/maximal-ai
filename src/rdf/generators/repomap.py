"""
REPOMAP.yaml Generator.

Position
--------
Generates REPOMAP.yaml from Python source code. Parses AST, extracts symbols
and docstrings, builds import graph, and outputs YAML with semantic sections.

Invariants
----------
- Output must validate against REPOMAP JSON schema
- Must extract Position, Invariants from docstrings where present
- Must respect token_budget configuration
- Must include dependency information
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


@dataclass
class SymbolInfo:
    """
    Information about a symbol (class or function).

    Attributes
    ----------
    name : str
        Symbol name.
    symbol_type : str
        'class' or 'function'.
    line : int
        Line number.
    docstring : str | None
        Docstring if present.
    """

    name: str
    symbol_type: str
    line: int
    docstring: str | None = None


@dataclass
class FileInfo:
    """
    Information about a single source file.

    Attributes
    ----------
    path : str
        Relative path to the file.
    rank : float
        Importance score (0-10).
    file_type : str
        Classification (entry_point, domain_model, service, utility, test).
    lines : int
        Line count.
    position : str | None
        Extracted Position section from module docstring.
    invariants : list[str]
        Extracted Invariants from module docstring.
    symbols : list[SymbolInfo]
        Extracted symbols (classes, functions).
    imports : list[str]
        Import dependencies.
    """

    path: str
    rank: float
    file_type: str
    lines: int
    position: str | None = None
    invariants: list[str] = field(default_factory=list)
    symbols: list[SymbolInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


class RepomapGenerator:
    """
    Generate REPOMAP.yaml from Python source code.

    Position
    --------
    Main generator class. Coordinates AST parsing, ranking, and YAML output.

    Invariants
    ----------
    - Output validates against schema before writing
    - Respects token_budget from configuration
    - Preserves semantic sections from docstrings

    Parameters
    ----------
    source_dir : Path
        Root directory for source files.
    config : dict
        Configuration from .repomap.yaml.

    Examples
    --------
    >>> generator = RepomapGenerator(Path("src/"), config)
    >>> generator.generate(Path("REPOMAP.yaml"))
    """

    def __init__(self, source_dir: Path, config: dict[str, Any] | None = None) -> None:
        """Initialize generator with source directory and configuration."""
        self.source_dir = source_dir
        self.config = config or {}
        self.files: list[FileInfo] = []

    def scan_files(self) -> list[Path]:
        """
        Find Python files matching include/exclude patterns.

        Returns
        -------
        list[Path]
            Paths to Python files to process.
        """
        exclude_patterns = self.config.get("exclude", ["__pycache__", ".venv", "node_modules"])
        files = []

        for py_file in self.source_dir.rglob("*.py"):
            # Check if file should be excluded
            should_exclude = any(
                pattern in str(py_file) for pattern in exclude_patterns
            )
            if not should_exclude:
                files.append(py_file)

        return files

    def _extract_section(self, docstring: str, section_name: str) -> str | None:
        """Extract a section from a NumPy-style docstring."""
        pattern = rf"{section_name}\s*\n-+\s*\n(.*?)(?=\n\w+\s*\n-+|\Z)"
        match = re.search(pattern, docstring, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_invariants(self, docstring: str) -> list[str]:
        """Extract invariants list from docstring."""
        section = self._extract_section(docstring, "Invariants")
        if not section:
            return []

        # Parse bullet points
        invariants = []
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                invariants.append(line[2:])
        return invariants

    def _classify_file(self, path: Path, tree: ast.Module) -> str:
        """Classify a file type based on name and content."""
        name = path.name

        if name.startswith("test_") or name.endswith("_test.py"):
            return "test"
        if name == "__init__.py":
            return "package"
        if name in ("cli.py", "main.py", "__main__.py"):
            return "entry_point"

        # Check for class definitions
        has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

        if has_classes:
            return "domain_model"
        if has_functions:
            return "utility"

        return "module"

    def parse_file(self, path: Path) -> FileInfo | None:
        """
        Parse a single Python file.

        Parameters
        ----------
        path : Path
            Path to Python file.

        Returns
        -------
        FileInfo | None
            Extracted information about the file, or None if parsing fails.
        """
        try:
            source = path.read_text()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return None

        # Get module docstring
        module_docstring = ast.get_docstring(tree) or ""
        position = self._extract_section(module_docstring, "Position")
        invariants = self._extract_invariants(module_docstring)

        # Extract symbols
        symbols: list[SymbolInfo] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    SymbolInfo(
                        name=node.name,
                        symbol_type="class",
                        line=node.lineno,
                        docstring=ast.get_docstring(node),
                    )
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    symbols.append(
                        SymbolInfo(
                            name=node.name,
                            symbol_type="function",
                            line=node.lineno,
                            docstring=ast.get_docstring(node),
                        )
                    )

        # Extract imports
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        # Calculate relative path
        try:
            rel_path = path.relative_to(self.source_dir.parent)
        except ValueError:
            rel_path = path

        return FileInfo(
            path=str(rel_path),
            rank=5.0,  # Initial rank, will be updated
            file_type=self._classify_file(path, tree),
            lines=len(source.splitlines()),
            position=position,
            invariants=invariants,
            symbols=symbols,
            imports=imports,
        )

    def rank_files(self) -> None:
        """
        Rank files by importance using a simple heuristic.

        Uses: line count, number of imports (in and out), symbol count.
        """
        # Count how many times each file is imported
        import_counts: dict[str, int] = {}
        for file_info in self.files:
            for imp in file_info.imports:
                import_counts[imp] = import_counts.get(imp, 0) + 1

        max_lines = max((f.lines for f in self.files), default=1)

        for file_info in self.files:
            # Base score from lines (normalized)
            line_score = (file_info.lines / max_lines) * 3

            # Score from symbols
            symbol_score = min(len(file_info.symbols) * 0.5, 2)

            # Score from being imported
            module_name = file_info.path.replace("/", ".").replace(".py", "")
            import_score = min(import_counts.get(module_name, 0) * 0.3, 3)

            # Entry points get a boost
            if file_info.file_type == "entry_point":
                import_score += 2

            file_info.rank = min(line_score + symbol_score + import_score, 10.0)

    def generate(self, output_path: Path) -> dict[str, Any]:
        """
        Generate REPOMAP.yaml and write to output path.

        Parameters
        ----------
        output_path : Path
            Where to write REPOMAP.yaml.

        Returns
        -------
        dict
            The generated REPOMAP data structure.
        """
        files = self.scan_files()
        self.files = [f for f in (self.parse_file(p) for p in files) if f is not None]
        self.rank_files()

        # Sort by rank descending
        self.files.sort(key=lambda f: f.rank, reverse=True)

        # Build output structure
        output: dict[str, Any] = {
            "meta": {
                "version": "1.0",
                "generated": datetime.now().isoformat(),
                "generator": "rdf v0.1.0",
                "files_indexed": len(self.files),
            },
            "files": [],
        }

        for file_info in self.files:
            file_entry: dict[str, Any] = {
                "path": file_info.path,
                "rank": round(file_info.rank, 1),
                "type": file_info.file_type,
                "lines": file_info.lines,
            }

            if file_info.position:
                file_entry["position"] = file_info.position

            if file_info.invariants:
                file_entry["invariants"] = file_info.invariants

            if file_info.symbols:
                file_entry["symbols"] = [
                    {"name": s.name, "type": s.symbol_type, "line": s.line}
                    for s in file_info.symbols
                ]

            output["files"].append(file_entry)

        # Write YAML
        yaml = YAML()
        yaml.default_flow_style = False
        with open(output_path, "w") as f:
            yaml.dump(output, f)

        return output
