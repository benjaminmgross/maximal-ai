"""Tests for ContextValidator."""

from pathlib import Path

from rdf.validators.context import ContextValidator

# Reusable valid content strings
_SUBSTRATE = (
    "# Substrate\n\n## Reading Paths\n\n"
    "| Audience | Path |\n|---|---|\n"
)
_ANTI_PATTERNS = (
    "# Anti-Patterns\n\n## Pattern 1\n\n"
    "### Wrong\n\n### Right\n"
)
_GLOSSARY = (
    "# Glossary\n\n"
    "| Term | Definition | Where Used |\n|---|---|---|\n"
)


class TestContextValidator:
    """Tests for the ContextValidator class."""

    def test_validates_missing_substrate(self, temp_dir: Path) -> None:
        """Test that missing substrate.md produces CTX001 error."""
        (temp_dir / ".context").mkdir()
        (temp_dir / ".context" / "ai-rules.md").write_text("# Rules\n")

        validator = ContextValidator(root=temp_dir)
        result = validator.validate()

        errors = [v for v in result.violations if v.code == "CTX001"]
        assert len(errors) == 1
        assert "substrate.md" in errors[0].message

    def test_validates_missing_recommended_file(self, temp_dir: Path) -> None:
        """Test that missing recommended files produce CTX002 warnings."""
        context = temp_dir / ".context"
        context.mkdir()
        (context / "substrate.md").write_text("# Substrate\n")
        (context / "ai-rules.md").write_text("# Rules\n")

        validator = ContextValidator(root=temp_dir)
        result = validator.validate()

        warnings = [v for v in result.violations if v.code == "CTX002"]
        # Should warn about glossary, anti-patterns, testing
        assert len(warnings) == 3

    def test_validates_glossary_format(self, temp_dir: Path) -> None:
        """Test that glossary without table produces CTX003 warning."""
        context = temp_dir / ".context"
        context.mkdir()
        (context / "substrate.md").write_text(_SUBSTRATE)
        (context / "ai-rules.md").write_text("# Rules\n")
        (context / "glossary.md").write_text("# Glossary\n\nSome terms.\n")

        validator = ContextValidator(root=temp_dir)
        result = validator.validate()

        warnings = [v for v in result.violations if v.code == "CTX003"]
        assert len(warnings) >= 1

    def test_validates_anti_patterns_format(self, temp_dir: Path) -> None:
        """Test that anti-patterns without wrong/right produces CTX003."""
        context = temp_dir / ".context"
        context.mkdir()
        (context / "substrate.md").write_text(_SUBSTRATE)
        (context / "ai-rules.md").write_text("# Rules\n")
        (context / "anti-patterns.md").write_text(
            "# Anti-Patterns\n\nSome patterns.\n"
        )

        validator = ContextValidator(root=temp_dir)
        result = validator.validate()

        warnings = [v for v in result.violations if v.code == "CTX003"]
        assert any("anti-patterns" in w.message for w in warnings)

    def test_passes_complete_context(self, temp_dir: Path) -> None:
        """Test that a fully populated .context/ passes validation."""
        context = temp_dir / ".context"
        context.mkdir()
        (context / "substrate.md").write_text(_SUBSTRATE)
        (context / "ai-rules.md").write_text("# AI Rules\n\n## Constraints\n")
        (context / "anti-patterns.md").write_text(_ANTI_PATTERNS)
        (context / "glossary.md").write_text(_GLOSSARY)
        (context / "testing.md").write_text("# Testing\n\n## Framework\n")
        (context / "architecture").mkdir()
        (context / "decisions").mkdir()

        validator = ContextValidator(root=temp_dir)
        result = validator.validate()
        assert result.passed

    def test_no_context_directory(self, temp_dir: Path) -> None:
        """Test validation when .context/ directory doesn't exist."""
        validator = ContextValidator(root=temp_dir)
        result = validator.validate()

        errors = [v for v in result.violations if v.code == "CTX001"]
        # Should report missing required files
        assert len(errors) >= 2

    def test_empty_directory_produces_info(self, temp_dir: Path) -> None:
        """Test that empty subdirectories produce CTX004 info."""
        context = temp_dir / ".context"
        context.mkdir()
        (context / "substrate.md").write_text(_SUBSTRATE)
        (context / "ai-rules.md").write_text("# Rules\n")
        (context / "architecture").mkdir()
        (context / "decisions").mkdir()
        (context / "prompts").mkdir()

        validator = ContextValidator(root=temp_dir)
        result = validator.validate()

        infos = [v for v in result.violations if v.code == "CTX004"]
        assert len(infos) >= 1
