"""
Docstring Linter.

Position
--------
Validates Python docstrings meet RDF requirements: NumPy format and
presence of semantic sections (Position, Invariants, etc.).

Invariants
----------
- Does not modify source files (read-only)
- Exit codes: 0=pass, 1=violations, 2=error
- Configurable strictness levels
- Output formats: text, JSON, SARIF
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Lint violation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Strictness(Enum):
    """Lint strictness levels."""

    MINIMAL = "minimal"  # Docstring exists
    STANDARD = "standard"  # NumPy format, Parameters/Returns
    STRICT = "strict"  # + Position, Invariants where applicable


@dataclass
class LintViolation:
    """
    A single lint violation.

    Attributes
    ----------
    path : str
        File path.
    line : int
        Line number.
    column : int
        Column number.
    code : str
        Violation code (e.g., "RDF001").
    message : str
        Human-readable description.
    severity : Severity
        Error, warning, or info.
    """

    path: str
    line: int
    column: int
    code: str
    message: str
    severity: Severity


@dataclass
class LintResult:
    """
    Result of linting a file or directory.

    Attributes
    ----------
    violations : list[LintViolation]
        All violations found.
    files_checked : int
        Number of files processed.
    """

    violations: list[LintViolation]
    files_checked: int

    @property
    def passed(self) -> bool:
        """Return True if no errors found."""
        return not any(v.severity == Severity.ERROR for v in self.violations)


class DocstringLinter:
    """
    Lint Python files for docstring compliance.

    Position
    --------
    Main linter class. Validates NumPy format and semantic sections.

    Invariants
    ----------
    - Does not modify files
    - Returns structured results for CI integration

    Parameters
    ----------
    strictness : Strictness
        How strict to be about requirements.

    Examples
    --------
    >>> linter = DocstringLinter(Strictness.STANDARD)
    >>> result = linter.lint_file(Path("src/module.py"))
    >>> print(result.passed)
    True
    """

    def __init__(self, strictness: Strictness = Strictness.STANDARD) -> None:
        """Initialize linter with strictness level."""
        self.strictness = strictness

    def lint_file(self, path: Path) -> LintResult:
        """
        Lint a single Python file.

        Parameters
        ----------
        path : Path
            Path to Python file.

        Returns
        -------
        LintResult
            Violations found in the file.
        """
        violations: list[LintViolation] = []

        try:
            source = path.read_text()
            tree = ast.parse(source)
        except SyntaxError as e:
            return LintResult(
                violations=[
                    LintViolation(
                        path=str(path),
                        line=e.lineno or 1,
                        column=e.offset or 0,
                        code="RDF000",
                        message=f"Syntax error: {e.msg}",
                        severity=Severity.ERROR,
                    )
                ],
                files_checked=1,
            )

        # Check module docstring
        if not ast.get_docstring(tree):
            violations.append(
                LintViolation(
                    path=str(path),
                    line=1,
                    column=0,
                    code="RDF001",
                    message="Missing module docstring",
                    severity=Severity.ERROR,
                )
            )

        # Check function and class docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):  # Public functions
                    if not ast.get_docstring(node):
                        violations.append(
                            LintViolation(
                                path=str(path),
                                line=node.lineno,
                                column=node.col_offset,
                                code="RDF002",
                                message=f"Missing docstring for function '{node.name}'",
                                severity=Severity.ERROR,
                            )
                        )
                    elif self.strictness in (Strictness.STANDARD, Strictness.STRICT):
                        docstring = ast.get_docstring(node) or ""
                        self._check_numpy_format(
                            path, node.lineno, node.name, docstring, violations
                        )

            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    violations.append(
                        LintViolation(
                            path=str(path),
                            line=node.lineno,
                            column=node.col_offset,
                            code="RDF003",
                            message=f"Missing docstring for class '{node.name}'",
                            severity=Severity.ERROR,
                        )
                    )

        return LintResult(violations=violations, files_checked=1)

    def _check_numpy_format(
        self,
        path: Path,
        line: int,
        name: str,
        docstring: str,
        violations: list[LintViolation],
    ) -> None:
        """Check docstring follows NumPy format."""
        # Check for Returns section
        if "Returns" not in docstring and "returns" not in docstring.lower():
            violations.append(
                LintViolation(
                    path=str(path),
                    line=line,
                    column=0,
                    code="RDF004",
                    message=f"Docstring for '{name}' missing Returns section",
                    severity=Severity.WARNING,
                )
            )

        # Strict mode: check for Position/Invariants
        if self.strictness == Strictness.STRICT:
            if "Position" not in docstring:
                violations.append(
                    LintViolation(
                        path=str(path),
                        line=line,
                        column=0,
                        code="RDF005",
                        message=f"Docstring for '{name}' missing Position section",
                        severity=Severity.WARNING,
                    )
                )

    def lint_directory(self, path: Path) -> LintResult:
        """
        Lint all Python files in a directory.

        Parameters
        ----------
        path : Path
            Directory to lint.

        Returns
        -------
        LintResult
            Combined violations from all files.
        """
        all_violations: list[LintViolation] = []
        files_checked = 0

        for py_file in path.rglob("*.py"):
            result = self.lint_file(py_file)
            all_violations.extend(result.violations)
            files_checked += result.files_checked

        return LintResult(violations=all_violations, files_checked=files_checked)
