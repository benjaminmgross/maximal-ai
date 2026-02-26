"""Tests for ContextFileGenerator (.context.md files)."""

from pathlib import Path

from rdf.generators.context_file import ContextFileGenerator, ContextFileSections


class TestContextFileGenerator:
    """Tests for the ContextFileGenerator class."""

    def test_generate_new_file_dry_run(self, temp_dir: Path) -> None:
        """Test generating a new .context.md in dry-run mode."""
        generator = ContextFileGenerator(temp_dir)
        result = generator.generate(dry_run=True)

        assert "Would write to" in result
        assert "# Folder:" in result
        assert "Purpose" in result
        assert "Constraints" in result

    def test_generate_new_file_creates_file(self, temp_dir: Path) -> None:
        """Test that generate creates .context.md (not .folder.md)."""
        generator = ContextFileGenerator(temp_dir)
        generator.generate(dry_run=False)

        context_md = temp_dir / ".context.md"
        assert context_md.exists()
        assert not (temp_dir / ".folder.md").exists()

        content = context_md.read_text()
        assert "# Folder:" in content
        assert "HUMAN-AUTHORED" in content
        assert "AUTO-GENERATED" in content

    def test_generate_preserves_human_content(self, temp_dir: Path) -> None:
        """Test that human-authored content is preserved on regeneration."""
        context_md = temp_dir / ".context.md"

        # Create initial file with custom human content
        initial_content = """# Folder: test/

## Purpose

<!-- HUMAN-AUTHORED - DO NOT AUTO-GENERATE -->
This folder handles user authentication.

## Invariants

<!-- HUMAN-AUTHORED - DO NOT AUTO-GENERATE -->
- All passwords must be hashed
- Sessions expire after 24 hours

---

<!-- AUTO-GENERATED BELOW - DO NOT EDIT MANUALLY -->
Old auto content
"""
        context_md.write_text(initial_content)

        # Regenerate
        generator = ContextFileGenerator(temp_dir)
        generator.generate(dry_run=False)

        # Check that human content is preserved
        new_content = context_md.read_text()
        assert "This folder handles user authentication" in new_content
        assert "All passwords must be hashed" in new_content
        assert "Sessions expire after 24 hours" in new_content

    def test_generate_creates_backup(self, temp_dir: Path) -> None:
        """Test that a backup is created before modifying existing file."""
        context_md = temp_dir / ".context.md"
        original_content = "# Original content"
        context_md.write_text(original_content)

        generator = ContextFileGenerator(temp_dir)
        generator.generate(dry_run=False)

        backup = temp_dir / ".context.md.bak"
        assert backup.exists()
        assert backup.read_text() == original_content

    def test_parse_existing_returns_none_for_missing(self, temp_dir: Path) -> None:
        """Test that parse_existing returns None when file doesn't exist."""
        generator = ContextFileGenerator(temp_dir)
        result = generator.parse_existing()
        assert result is None

    def test_parse_existing_returns_sections(self, temp_dir: Path) -> None:
        """Test that parse_existing correctly parses file sections."""
        context_md = temp_dir / ".context.md"
        context_md.write_text("""# Header

Content before auto

<!-- AUTO-GENERATED BELOW - DO NOT EDIT MANUALLY -->
Auto content here
""")

        generator = ContextFileGenerator(temp_dir)
        result = generator.parse_existing()

        assert result is not None
        assert isinstance(result, ContextFileSections)
        assert "# Header" in result.preamble
        assert "Content before auto" in result.preamble

    def test_generate_file_table_with_python_files(self, temp_dir: Path) -> None:
        """Test file table generation with Python files present."""
        # Create some Python files
        (temp_dir / "module1.py").write_text("def hello(): pass")
        (temp_dir / "module2.py").write_text("class Foo: pass")

        generator = ContextFileGenerator(temp_dir)
        table = generator.generate_file_table()

        assert "## Files" in table
        assert "module1.py" in table
        assert "module2.py" in table

    def test_generate_file_table_empty_directory(self, temp_dir: Path) -> None:
        """Test file table generation with no Python files."""
        generator = ContextFileGenerator(temp_dir)
        table = generator.generate_file_table()

        assert "No Python files" in table
