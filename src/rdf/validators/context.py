"""
.context/ Directory Validator.

Position
--------
Validates completeness and format of the .context/ project documentation
directory. Part of the unified RDF 3.0 validation pipeline. Read-only —
never modifies any files. Required files produce ERROR violations,
recommended files produce WARNING violations, format checks produce
WARNING violations, and empty directories produce INFO violations.
"""

from __future__ import annotations

from pathlib import Path

from rdf.linters.docstring import LintResult, LintViolation, Severity

REQUIRED_FILES = ["substrate.md", "ai-rules.md"]
RECOMMENDED_FILES = ["glossary.md", "anti-patterns.md", "testing.md"]
EXPECTED_DIRS = ["architecture", "decisions", "prompts"]


class ContextValidator:
    """
    Validate .context/ directory completeness and format.

    Position
    --------
    Checks that the .context/ directory exists with required files,
    recommended files, and proper format for structured files. Read-only —
    never modifies files. Returns structured LintResult for CI integration.

    Parameters
    ----------
    root : Path
        Project root directory containing .context/.
    """

    def __init__(self, *, root: Path) -> None:
        """Initialize validator with project root."""
        self.root = root
        self.context_dir = root / ".context"

    def validate(self) -> LintResult:
        """
        Validate the .context/ directory.

        Returns
        -------
        LintResult
            Violations found during validation.
        """
        violations: list[LintViolation] = []

        self._check_required_files(violations)
        self._check_recommended_files(violations)
        self._check_file_formats(violations)
        self._check_directories(violations)

        return LintResult(violations=violations, files_checked=1)

    def _check_required_files(self, violations: list[LintViolation]) -> None:
        """Check that required .context/ files exist."""
        for filename in REQUIRED_FILES:
            filepath = self.context_dir / filename
            if not filepath.exists():
                violations.append(
                    LintViolation(
                        path=str(filepath),
                        line=0,
                        column=0,
                        code="CTX001",
                        message=(
                            f"Missing required .context/{filename}"
                            f" — run `rdf scaffold-context"
                            f" {filename.replace('.md', '')}`"
                        ),
                        severity=Severity.ERROR,
                    )
                )

    def _check_recommended_files(self, violations: list[LintViolation]) -> None:
        """Check that recommended .context/ files exist."""
        for filename in RECOMMENDED_FILES:
            filepath = self.context_dir / filename
            if not filepath.exists():
                violations.append(
                    LintViolation(
                        path=str(filepath),
                        line=0,
                        column=0,
                        code="CTX002",
                        message=(
                            f"Missing recommended .context/{filename}"
                            f" — run `rdf scaffold-context"
                            f" {filename.replace('.md', '')}`"
                        ),
                        severity=Severity.WARNING,
                    )
                )

    def _check_file_formats(self, violations: list[LintViolation]) -> None:
        """Check that existing .context/ files have proper format."""
        # Check glossary has table structure
        glossary = self.context_dir / "glossary.md"
        if glossary.exists():
            content = glossary.read_text()
            if "| " not in content or "---" not in content:
                violations.append(
                    LintViolation(
                        path=str(glossary),
                        line=0,
                        column=0,
                        code="CTX003",
                        message=(
                            "Malformed .context/glossary.md"
                            " — expected table structure"
                            " (| Term | Definition | Where Used |)"
                        ),
                        severity=Severity.WARNING,
                    )
                )

        # Check anti-patterns has wrong/right format
        anti_patterns = self.context_dir / "anti-patterns.md"
        if anti_patterns.exists():
            content = anti_patterns.read_text()
            has_wrong = "Wrong" in content or "wrong" in content
            has_right = "Right" in content or "right" in content
            if not (has_wrong and has_right):
                violations.append(
                    LintViolation(
                        path=str(anti_patterns),
                        line=0,
                        column=0,
                        code="CTX003",
                        message=(
                            "Malformed .context/anti-patterns.md"
                            " — expected Wrong/Right pattern format"
                        ),
                        severity=Severity.WARNING,
                    )
                )

        # Check substrate has reading paths
        substrate = self.context_dir / "substrate.md"
        if substrate.exists():
            content = substrate.read_text()
            if "Reading Path" not in content and "reading path" not in content.lower():
                violations.append(
                    LintViolation(
                        path=str(substrate),
                        line=0,
                        column=0,
                        code="CTX003",
                        message=(
                            "Malformed .context/substrate.md"
                            " — expected Reading Paths section"
                        ),
                        severity=Severity.WARNING,
                    )
                )

    def _check_directories(self, violations: list[LintViolation]) -> None:
        """Check that expected subdirectories exist and are not empty."""
        for dirname in EXPECTED_DIRS:
            dirpath = self.context_dir / dirname
            if dirpath.exists() and dirpath.is_dir():
                # Check if directory is empty (no files)
                files = list(dirpath.iterdir())
                if not files:
                    violations.append(
                        LintViolation(
                            path=str(dirpath),
                            line=0,
                            column=0,
                            code="CTX004",
                            message=(
                                f"Empty .context/{dirname}/ directory"
                                " — consider adding content or removing"
                            ),
                            severity=Severity.INFO,
                        )
                    )
