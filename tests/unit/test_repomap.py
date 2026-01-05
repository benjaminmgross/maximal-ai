"""Tests for RepomapGenerator."""

from pathlib import Path

import pytest

from rdf.generators.repomap import RepomapGenerator, FileInfo, SymbolInfo


class TestRepomapGenerator:
    """Tests for the RepomapGenerator class."""

    def test_scan_files_finds_python_files(self, temp_dir: Path) -> None:
        """Test that scan_files finds Python files."""
        src = temp_dir / "src"
        src.mkdir()
        (src / "module1.py").write_text("# module1")
        (src / "module2.py").write_text("# module2")
        (src / "not_python.txt").write_text("text file")

        generator = RepomapGenerator(src)
        files = generator.scan_files()

        assert len(files) == 2
        assert all(f.suffix == ".py" for f in files)

    def test_scan_files_excludes_pycache(self, temp_dir: Path) -> None:
        """Test that __pycache__ directories are excluded."""
        src = temp_dir / "src"
        pycache = src / "__pycache__"
        pycache.mkdir(parents=True)
        (src / "module.py").write_text("# module")
        (pycache / "module.cpython-311.pyc").write_text("bytecode")

        generator = RepomapGenerator(src)
        files = generator.scan_files()

        assert len(files) == 1
        assert "__pycache__" not in str(files[0])

    def test_parse_file_extracts_basic_info(self, temp_dir: Path) -> None:
        """Test that parse_file extracts basic file information."""
        file_path = temp_dir / "module.py"
        file_path.write_text('''"""Module docstring."""

def hello():
    """Say hello."""
    pass

class Greeter:
    """A greeter."""
    pass
''')

        generator = RepomapGenerator(temp_dir)
        info = generator.parse_file(file_path)

        assert info is not None
        assert info.lines == 9
        assert len(info.symbols) == 2

        # Check symbols
        func_symbols = [s for s in info.symbols if s.symbol_type == "function"]
        class_symbols = [s for s in info.symbols if s.symbol_type == "class"]
        assert len(func_symbols) == 1
        assert len(class_symbols) == 1
        assert func_symbols[0].name == "hello"
        assert class_symbols[0].name == "Greeter"

    def test_parse_file_extracts_position(self, temp_dir: Path) -> None:
        """Test that parse_file extracts Position section from docstring."""
        file_path = temp_dir / "module.py"
        file_path.write_text('''"""
Module docstring.

Position
--------
This module handles user authentication.

Invariants
----------
- Users must be authenticated
- Tokens expire after 24 hours
"""
''')

        generator = RepomapGenerator(temp_dir)
        info = generator.parse_file(file_path)

        assert info is not None
        assert info.position is not None
        assert "user authentication" in info.position
        assert len(info.invariants) == 2
        assert "Users must be authenticated" in info.invariants[0]

    def test_parse_file_handles_syntax_error(self, temp_dir: Path) -> None:
        """Test that parse_file returns None for files with syntax errors."""
        file_path = temp_dir / "broken.py"
        file_path.write_text("def broken(")

        generator = RepomapGenerator(temp_dir)
        info = generator.parse_file(file_path)

        assert info is None

    def test_parse_file_extracts_imports(self, temp_dir: Path) -> None:
        """Test that parse_file extracts import statements."""
        file_path = temp_dir / "module.py"
        file_path.write_text('''"""Module."""

import os
import sys
from pathlib import Path
from typing import List, Optional
''')

        generator = RepomapGenerator(temp_dir)
        info = generator.parse_file(file_path)

        assert info is not None
        assert "os" in info.imports
        assert "sys" in info.imports
        assert "pathlib" in info.imports
        assert "typing" in info.imports

    def test_classify_file_test(self, temp_dir: Path) -> None:
        """Test file classification for test files."""
        test_file = temp_dir / "test_module.py"
        test_file.write_text('"""Test module."""')

        generator = RepomapGenerator(temp_dir)
        info = generator.parse_file(test_file)

        assert info is not None
        assert info.file_type == "test"

    def test_classify_file_entry_point(self, temp_dir: Path) -> None:
        """Test file classification for entry points."""
        cli_file = temp_dir / "cli.py"
        cli_file.write_text('"""CLI module."""')

        generator = RepomapGenerator(temp_dir)
        info = generator.parse_file(cli_file)

        assert info is not None
        assert info.file_type == "entry_point"

    def test_generate_creates_yaml(self, temp_dir: Path) -> None:
        """Test that generate creates a valid YAML file."""
        src = temp_dir / "src"
        src.mkdir()
        (src / "module.py").write_text('"""Module."""\n\ndef hello(): pass')

        output = temp_dir / "REPOMAP.yaml"

        generator = RepomapGenerator(src)
        result = generator.generate(output)

        assert output.exists()
        assert "meta" in result
        assert "files" in result
        assert result["meta"]["files_indexed"] == 1

    def test_rank_files_entry_points_higher(self, temp_dir: Path) -> None:
        """Test that entry points are ranked higher."""
        src = temp_dir / "src"
        src.mkdir()
        (src / "cli.py").write_text('"""CLI."""')
        (src / "utils.py").write_text('"""Utils."""')

        generator = RepomapGenerator(src)
        files = generator.scan_files()
        generator.files = [f for f in (generator.parse_file(p) for p in files) if f is not None]
        generator.rank_files()

        cli_info = next(f for f in generator.files if "cli" in f.path)
        utils_info = next(f for f in generator.files if "utils" in f.path)

        assert cli_info.rank > utils_info.rank


class TestFileInfo:
    """Tests for FileInfo dataclass."""

    def test_file_info_creation(self) -> None:
        """Test creating FileInfo with all fields."""
        info = FileInfo(
            path="src/module.py",
            rank=7.5,
            file_type="utility",
            lines=100,
            position="Handles utilities",
            invariants=["Must be fast", "Must be safe"],
            symbols=[
                SymbolInfo(name="helper", symbol_type="function", line=10),
            ],
            imports=["os", "sys"],
        )

        assert info.path == "src/module.py"
        assert info.rank == 7.5
        assert info.file_type == "utility"
        assert info.lines == 100
        assert info.position == "Handles utilities"
        assert len(info.invariants) == 2
        assert len(info.symbols) == 1
        assert len(info.imports) == 2


class TestSymbolInfo:
    """Tests for SymbolInfo dataclass."""

    def test_symbol_info_creation(self) -> None:
        """Test creating SymbolInfo."""
        symbol = SymbolInfo(
            name="MyClass",
            symbol_type="class",
            line=42,
            docstring="A class that does things.",
        )

        assert symbol.name == "MyClass"
        assert symbol.symbol_type == "class"
        assert symbol.line == 42
        assert symbol.docstring == "A class that does things."
