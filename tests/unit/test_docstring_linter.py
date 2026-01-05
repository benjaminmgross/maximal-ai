"""Tests for DocstringLinter."""

from pathlib import Path

import pytest

from rdf.linters.docstring import DocstringLinter, Severity, Strictness


class TestDocstringLinter:
    """Tests for the DocstringLinter class."""

    def test_lint_file_with_module_docstring(self, sample_python_file: Path) -> None:
        """Test that file with module docstring passes."""
        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_file(sample_python_file)

        # Should not have RDF001 (missing module docstring)
        module_violations = [v for v in result.violations if v.code == "RDF001"]
        assert len(module_violations) == 0
        assert result.files_checked == 1

    def test_lint_file_missing_module_docstring(self, temp_dir: Path) -> None:
        """Test detection of missing module docstring."""
        file_path = temp_dir / "no_docstring.py"
        file_path.write_text("def hello(): pass")

        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_file(file_path)

        assert not result.passed
        module_violations = [v for v in result.violations if v.code == "RDF001"]
        assert len(module_violations) == 1
        assert module_violations[0].severity == Severity.ERROR

    def test_lint_file_missing_function_docstring(self, temp_dir: Path) -> None:
        """Test detection of missing function docstring."""
        file_path = temp_dir / "missing_func_doc.py"
        file_path.write_text('''"""Module docstring."""

def public_function():
    pass
''')

        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_file(file_path)

        func_violations = [v for v in result.violations if v.code == "RDF002"]
        assert len(func_violations) == 1
        assert "public_function" in func_violations[0].message

    def test_lint_file_ignores_private_functions(self, temp_dir: Path) -> None:
        """Test that private functions are not checked."""
        file_path = temp_dir / "private_funcs.py"
        file_path.write_text('''"""Module docstring."""

def _private_function():
    pass

def __double_private():
    pass
''')

        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_file(file_path)

        func_violations = [v for v in result.violations if v.code == "RDF002"]
        assert len(func_violations) == 0

    def test_lint_file_missing_class_docstring(self, temp_dir: Path) -> None:
        """Test detection of missing class docstring."""
        file_path = temp_dir / "missing_class_doc.py"
        file_path.write_text('''"""Module docstring."""

class MyClass:
    pass
''')

        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_file(file_path)

        class_violations = [v for v in result.violations if v.code == "RDF003"]
        assert len(class_violations) == 1
        assert "MyClass" in class_violations[0].message

    def test_lint_file_syntax_error(self, temp_dir: Path) -> None:
        """Test handling of syntax errors."""
        file_path = temp_dir / "syntax_error.py"
        file_path.write_text("def broken(")

        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_file(file_path)

        assert not result.passed
        syntax_violations = [v for v in result.violations if v.code == "RDF000"]
        assert len(syntax_violations) == 1

    def test_standard_mode_checks_returns(self, temp_dir: Path) -> None:
        """Test that STANDARD mode checks for Returns section."""
        file_path = temp_dir / "no_returns.py"
        file_path.write_text('''"""Module docstring."""

def get_value():
    """Get a value."""
    return 42
''')

        linter = DocstringLinter(Strictness.STANDARD)
        result = linter.lint_file(file_path)

        returns_violations = [v for v in result.violations if v.code == "RDF004"]
        assert len(returns_violations) == 1
        assert returns_violations[0].severity == Severity.WARNING

    def test_standard_mode_passes_with_returns(self, temp_dir: Path) -> None:
        """Test that STANDARD mode passes with Returns section."""
        file_path = temp_dir / "has_returns.py"
        file_path.write_text('''"""Module docstring."""

def get_value():
    """Get a value.

    Returns
    -------
    int
        The value 42.
    """
    return 42
''')

        linter = DocstringLinter(Strictness.STANDARD)
        result = linter.lint_file(file_path)

        returns_violations = [v for v in result.violations if v.code == "RDF004"]
        assert len(returns_violations) == 0

    def test_strict_mode_checks_position(self, temp_dir: Path) -> None:
        """Test that STRICT mode checks for Position section."""
        file_path = temp_dir / "no_position.py"
        file_path.write_text('''"""Module docstring."""

def process():
    """Process something.

    Returns
    -------
    None
    """
    pass
''')

        linter = DocstringLinter(Strictness.STRICT)
        result = linter.lint_file(file_path)

        position_violations = [v for v in result.violations if v.code == "RDF005"]
        assert len(position_violations) == 1

    def test_lint_directory(self, temp_dir: Path) -> None:
        """Test linting an entire directory."""
        # Create subdirectory structure
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        (temp_dir / "file1.py").write_text('"""Docstring."""')
        (subdir / "file2.py").write_text('"""Docstring."""')
        (subdir / "file3.py").write_text("# no docstring")

        linter = DocstringLinter(Strictness.MINIMAL)
        result = linter.lint_directory(temp_dir)

        assert result.files_checked == 3
        # file3.py should have a missing module docstring violation
        module_violations = [v for v in result.violations if v.code == "RDF001"]
        assert len(module_violations) == 1

    def test_lint_result_passed_property(self) -> None:
        """Test LintResult.passed property."""
        from rdf.linters.docstring import LintResult, LintViolation

        # No violations = passed
        result = LintResult(violations=[], files_checked=1)
        assert result.passed

        # Warning only = passed
        result = LintResult(
            violations=[
                LintViolation(
                    path="test.py",
                    line=1,
                    column=0,
                    code="RDF004",
                    message="test",
                    severity=Severity.WARNING,
                )
            ],
            files_checked=1,
        )
        assert result.passed

        # Error = not passed
        result = LintResult(
            violations=[
                LintViolation(
                    path="test.py",
                    line=1,
                    column=0,
                    code="RDF001",
                    message="test",
                    severity=Severity.ERROR,
                )
            ],
            files_checked=1,
        )
        assert not result.passed
