"""Tests for unified .context/ templates."""

import pathlib

TEMPLATE_DIR = pathlib.Path("templates/rdf")


def test_context_templates_exist():
    """Verify every expected .context template file exists."""
    expected = [
        "context/substrate.md.template",
        "context/ai-rules.md.template",
        "context/anti-patterns.md.template",
        "context/glossary.md.template",
        "context/testing.md.template",
        "context/prompts/README.md.template",
        "context/architecture/overview.md.template",
        "context/decisions/adr-template.md.template",
    ]
    for template in expected:
        assert (TEMPLATE_DIR / template).exists(), f"Missing template: {template}"


def test_docstring_template_includes_contract_sections():
    """Verify source-headers template includes all docstring contract sections."""
    template = (TEMPLATE_DIR / "layer2" / "source-headers.md.template").read_text()
    for section in ["Position", "Raises", "Silences"]:
        assert section in template, f"Missing docstring section: {section}"
    # "Invariants" was removed as a standalone section; constraints now belong
    # inside parameter/return descriptions.  Verify no table row advertises it.
    table_rows = [l for l in template.splitlines() if l.strip().startswith("|")]
    for row in table_rows:
        assert "Invariants" not in row, (
            "Invariants should not appear as a standalone section row in the table"
        )


def test_substrate_template_has_reading_paths():
    """Verify substrate template includes reading paths and token budget."""
    template = (TEMPLATE_DIR / "context" / "substrate.md.template").read_text()
    assert "Reading Path" in template
    assert "Token" in template


def test_anti_patterns_template_has_wrong_right_format():
    """Verify anti-patterns template includes wrong/right format markers."""
    template = (TEMPLATE_DIR / "context" / "anti-patterns.md.template").read_text()
    assert "Wrong" in template
    assert "Right" in template


def test_glossary_template_has_table_structure():
    """Verify glossary template includes table headers."""
    template = (TEMPLATE_DIR / "context" / "glossary.md.template").read_text()
    assert "Term" in template
    assert "Definition" in template
    assert "Where Used" in template
