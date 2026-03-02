"""Tests for unified .context/ templates.

Layer 1 of the RDF quality testing strategy: Template Invariant Tests.

These tests verify that templates are *parameterized* (contain placeholders)
and never contain *hardcoded* project-specific content. They are the cheapest
and fastest line of defense against the "407 identical files" class of bugs.
"""

import pathlib

import pytest

TEMPLATE_DIR = pathlib.Path("templates/rdf")

# Known hardcoded strings that should never appear in templates.
# These were present in the original bug: the Layer 2 template contained
# a complete description of a specific FastAPI routes/ directory.
FORBIDDEN_HARDCODED_CONTENT = [
    "auth.py",
    "users.py",
    "health.py",
    "src/app/api/routes/",
    "routes/ → services/ → models/",
    "get_user_service",
    "UserResponse",
    "SQLAlchemy 2.0+ with async",
    "PostgreSQL 16, Redis 7",
    "pytest-asyncio, pytest-cov",
    "FastAPI 0.115+",
]


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
    table_rows = [line for line in template.splitlines() if line.strip().startswith("|")]
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


# ============================================================
# Layer 1: Template Invariant Tests
# ============================================================


class TestLayer2TemplateIsParameterized:
    """Verify the Layer 2 (.context.md) template uses placeholders, not hardcoded content."""

    def test_contains_folder_name_placeholder(self) -> None:
        """The template MUST contain {{FOLDER_NAME}} for awk substitution to work."""
        template = (TEMPLATE_DIR / "layer2" / ".context.md.template").read_text()
        assert "{{FOLDER_NAME}}" in template, (
            "Layer 2 template missing {{FOLDER_NAME}} placeholder. "
            "The installer's awk substitution will produce identical files."
        )

    @pytest.mark.parametrize("forbidden", FORBIDDEN_HARDCODED_CONTENT)
    def test_no_hardcoded_project_content(self, forbidden: str) -> None:
        """No template should contain hardcoded project-specific content."""
        template = (TEMPLATE_DIR / "layer2" / ".context.md.template").read_text()
        assert forbidden not in template, (
            f"Layer 2 template contains hardcoded content '{forbidden}'. "
            "Templates must use placeholders or TODO markers, never examples "
            "that look like real documentation."
        )

    def test_uses_todo_markers_not_examples(self) -> None:
        """Human-authored sections should have TODO markers, not example content."""
        template = (TEMPLATE_DIR / "layer2" / ".context.md.template").read_text()
        assert "TODO:" in template, (
            "Template should use TODO: markers for sections that need human input"
        )


class TestLayer1TemplatesAreParameterized:
    """Verify Layer 1 templates use placeholders, not hardcoded tech stacks."""

    @pytest.mark.parametrize("forbidden", FORBIDDEN_HARDCODED_CONTENT)
    def test_agents_no_hardcoded_content(self, forbidden: str) -> None:
        """AGENTS.md template must not contain hardcoded project-specific content."""
        template = (TEMPLATE_DIR / "layer1" / "AGENTS.md.template").read_text()
        assert forbidden not in template, (
            f"AGENTS.md template contains hardcoded content '{forbidden}'. "
            "It should use {{...}} placeholders populated by introspection."
        )

    def test_agents_has_language_placeholder(self) -> None:
        """AGENTS.md must have a {{LANGUAGE}} placeholder."""
        template = (TEMPLATE_DIR / "layer1" / "AGENTS.md.template").read_text()
        assert "{{LANGUAGE}}" in template

    def test_agents_has_package_manager_placeholder(self) -> None:
        """AGENTS.md must have a {{PACKAGE_MANAGER}} placeholder."""
        template = (TEMPLATE_DIR / "layer1" / "AGENTS.md.template").read_text()
        assert "{{PACKAGE_MANAGER}}" in template


class TestContextTemplatesAreParameterized:
    """Verify .context/ templates use {{...}} placeholders, not [...] pseudo-placeholders."""

    def test_substrate_uses_double_brace_placeholders(self) -> None:
        """substrate.md must use {{PROJECT_NAME}}, not [PROJECT_NAME]."""
        template = (TEMPLATE_DIR / "context" / "substrate.md.template").read_text()
        assert "{{PROJECT_NAME}}" in template, (
            "substrate.md should use {{PROJECT_NAME}} for machine substitution"
        )
        assert "[PROJECT_NAME]" not in template, (
            "substrate.md still has [PROJECT_NAME] which no code substitutes"
        )

    def test_substrate_has_description_placeholder(self) -> None:
        """substrate.md must have {{PROJECT_DESCRIPTION}}."""
        template = (TEMPLATE_DIR / "context" / "substrate.md.template").read_text()
        assert "{{PROJECT_DESCRIPTION}}" in template

    def test_ai_rules_uses_double_brace_placeholders(self) -> None:
        """ai-rules.md must use {{LANGUAGE}}, not [Python 3.12+ / TypeScript 5.x / etc.]."""
        template = (TEMPLATE_DIR / "context" / "ai-rules.md.template").read_text()
        assert "{{LANGUAGE}}" in template
        assert "[Python 3.12+" not in template, (
            "ai-rules.md still has bracket-style pseudo-placeholder"
        )

    def test_ai_rules_has_linter_placeholder(self) -> None:
        """ai-rules.md must have {{LINTER}} placeholder."""
        template = (TEMPLATE_DIR / "context" / "ai-rules.md.template").read_text()
        assert "{{LINTER}}" in template


class TestNoDescriptiveTemplateContainsHardcodedExamples:
    """Scan *descriptive* templates for hardcoded project-specific content.

    Descriptive templates are those that describe the user's actual repo
    (Layer 1 entry points, Layer 2 .context.md, .context/ directory files).
    These MUST NOT contain hardcoded content because they'll be mistaken for
    real documentation about the user's project.

    Excluded from this scan:
    - **Reference templates** (REPOMAP.yaml.template) — generated by code
    - **Instructional templates** (Layer 3 checklists, guides, protocols) —
      these are teaching materials where example filenames are appropriate

    This is the broadest safety net — if someone adds a new descriptive
    template with hardcoded examples, this test catches it.
    """

    # Paths (relative to TEMPLATE_DIR) that contain descriptive templates.
    # These are the templates that get stamped into repos and MUST be
    # parameterized. Everything else is excluded from this scan.
    DESCRIPTIVE_TEMPLATE_PREFIXES = (
        "layer1/",      # AGENTS.md, .repomap.yaml config
        "layer2/.context.md",  # Per-directory documentation
        "layer2/.folder.md",   # Backward-compat variant
        "context/",     # .context/ directory files (substrate, ai-rules, etc.)
    )

    @pytest.fixture
    def descriptive_templates(self) -> list[tuple[str, str]]:
        """Collect all descriptive .template files and their contents."""
        templates = []
        for f in TEMPLATE_DIR.rglob("*.template"):
            rel = str(f.relative_to(TEMPLATE_DIR))
            if any(rel.startswith(p) for p in self.DESCRIPTIVE_TEMPLATE_PREFIXES):
                templates.append((rel, f.read_text()))
        return templates

    @pytest.mark.parametrize("forbidden", FORBIDDEN_HARDCODED_CONTENT)
    def test_no_hardcoded_content_in_descriptive_templates(
        self,
        forbidden: str,
        descriptive_templates: list[tuple[str, str]],
    ) -> None:
        """No descriptive template should contain known hardcoded content."""
        for rel_path, content in descriptive_templates:
            assert forbidden not in content, (
                f"Template '{rel_path}' contains hardcoded content '{forbidden}'. "
                "Descriptive templates (Layer 1, Layer 2, .context/) must use "
                "{{...}} placeholders or TODO markers, never project-specific "
                "examples that could be mistaken for real documentation."
            )
