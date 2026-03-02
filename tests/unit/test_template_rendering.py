"""
Layer 2: Substitution Verification Tests.

These tests verify that templates rendered with introspected project data
contain *actual* values (project name, language, etc.) and no leftover
{{...}} placeholder residue. They would have caught Bug 2 (no substitution
logic in the installer) and Bug 3 (unfilled [PROJECT_NAME] placeholders).
"""

import re
from pathlib import Path

import pytest

from rdf.introspect import detect_project_info, render_template

# Regex to find any unfilled {{...}} placeholder
PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z_]+\}\}")

# Template directory
TEMPLATE_DIR = Path("templates/rdf")


@pytest.fixture
def python_project(temp_dir: Path) -> Path:
    """Create a realistic Python project with pyproject.toml."""
    pyproject = temp_dir / "pyproject.toml"
    pyproject.write_text("""\
[project]
name = "widget-factory"
description = "Produces high-quality widgets"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.100",
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
""")
    (temp_dir / "uv.lock").write_text("")
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "widget_factory").mkdir()
    (temp_dir / "tests").mkdir()
    return temp_dir


@pytest.fixture
def js_project(temp_dir: Path) -> Path:
    """Create a realistic JavaScript/TypeScript project."""
    package_json = temp_dir / "package.json"
    package_json.write_text("""\
{
    "name": "gadget-dashboard",
    "description": "Dashboard for gadget metrics",
    "dependencies": {
        "react": "^18.0",
        "next": "^14.0"
    },
    "devDependencies": {
        "typescript": "^5.0",
        "eslint": "^8.0",
        "vitest": "^1.0"
    },
    "scripts": {
        "dev": "next dev",
        "test": "vitest",
        "lint": "eslint ."
    }
}
""")
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "components").mkdir()
    return temp_dir


class TestRenderedSubstrateContainsRealData:
    """Verify substrate.md gets filled with actual project data."""

    def test_contains_project_name(self, python_project: Path) -> None:
        """substrate.md must contain the actual project name, not a placeholder."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "substrate.md.template").read_text()
        rendered = render_template(template, subs)

        assert "widget-factory" in rendered
        assert "{{PROJECT_NAME}}" not in rendered

    def test_contains_project_description(self, python_project: Path) -> None:
        """substrate.md must contain the actual project description."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "substrate.md.template").read_text()
        rendered = render_template(template, subs)

        assert "Produces high-quality widgets" in rendered
        assert "{{PROJECT_DESCRIPTION}}" not in rendered

    def test_no_placeholder_residue(self, python_project: Path) -> None:
        """No {{...}} placeholders should remain in rendered substrate.md."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "substrate.md.template").read_text()
        rendered = render_template(template, subs)

        leftover = PLACEHOLDER_PATTERN.findall(rendered)
        assert leftover == [], (
            f"Unfilled placeholders in rendered substrate.md: {leftover}"
        )


class TestRenderedAiRulesContainsRealData:
    """Verify ai-rules.md gets filled with detected tooling."""

    def test_contains_detected_language(self, python_project: Path) -> None:
        """ai-rules.md must show the actual language, not a placeholder."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "ai-rules.md.template").read_text()
        rendered = render_template(template, subs)

        assert "Python" in rendered
        assert "{{LANGUAGE}}" not in rendered

    def test_contains_detected_linter(self, python_project: Path) -> None:
        """ai-rules.md must show the actual linter."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "ai-rules.md.template").read_text()
        rendered = render_template(template, subs)

        assert "ruff" in rendered
        assert "{{LINTER}}" not in rendered

    def test_contains_detected_type_checker(self, python_project: Path) -> None:
        """ai-rules.md must show the actual type checker."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "ai-rules.md.template").read_text()
        rendered = render_template(template, subs)

        assert "mypy" in rendered
        assert "{{TYPE_CHECKER}}" not in rendered

    def test_no_bracket_pseudoplaceholders(self, python_project: Path) -> None:
        """ai-rules.md must not have old-style [Python 3.12+ / ...] placeholders."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "context" / "ai-rules.md.template").read_text()
        rendered = render_template(template, subs)

        assert "[Python 3.12+" not in rendered
        assert "[uv / npm" not in rendered


class TestRenderedAgentsMdContainsRealData:
    """Verify AGENTS.md gets filled with detected tech stack."""

    def test_contains_project_language(self, python_project: Path) -> None:
        """AGENTS.md must reflect detected language."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "layer1" / "AGENTS.md.template").read_text()
        rendered = render_template(template, subs)

        assert "Python" in rendered
        assert "{{LANGUAGE}}" not in rendered

    def test_contains_package_manager(self, python_project: Path) -> None:
        """AGENTS.md must reflect detected package manager."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "layer1" / "AGENTS.md.template").read_text()
        rendered = render_template(template, subs)

        assert "uv" in rendered
        assert "{{PACKAGE_MANAGER}}" not in rendered

    def test_js_project_detected_correctly(self, js_project: Path) -> None:
        """AGENTS.md for a JS project must reflect TypeScript/npm stack."""
        info = detect_project_info(js_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / "layer1" / "AGENTS.md.template").read_text()
        rendered = render_template(template, subs)

        assert "TypeScript" in rendered
        assert "npm" in rendered
        assert "Python" not in rendered


class TestRenderedLayer2ContextMdIsDirectorySpecific:
    """Verify .context.md gets the actual folder name, not hardcoded content."""

    def test_heading_matches_folder_name(self) -> None:
        """The heading must contain the actual folder name."""
        template = (TEMPLATE_DIR / "layer2" / ".context.md.template").read_text()
        rendered = render_template(template, {"FOLDER_NAME": "payment-processor"})

        assert "# Folder: payment-processor/" in rendered

    def test_different_folders_produce_different_output(self) -> None:
        """Two directories must produce different .context.md files."""
        template = (TEMPLATE_DIR / "layer2" / ".context.md.template").read_text()

        rendered_a = render_template(template, {"FOLDER_NAME": "auth"})
        rendered_b = render_template(template, {"FOLDER_NAME": "billing"})

        assert rendered_a != rendered_b, (
            "Two different folders produced identical .context.md files — "
            "the template is not using {{FOLDER_NAME}} properly"
        )

    def test_no_hardcoded_directory_name(self) -> None:
        """Rendered output should not contain the old hardcoded directory."""
        template = (TEMPLATE_DIR / "layer2" / ".context.md.template").read_text()
        rendered = render_template(template, {"FOLDER_NAME": "my-module"})

        assert "src/app/api/routes/" not in rendered


class TestNoPlaceholderResidueAcrossAllDescriptiveTemplates:
    """Verify that rendering with a real project leaves no {{...}} behind.

    This is the broadest Layer 2 check: render every descriptive template
    with a real project's introspection data and scan for leftover
    placeholders. Any unfilled placeholder means either (a) the template
    uses a key that introspection doesn't provide, or (b) the render
    function missed a substitution.
    """

    DESCRIPTIVE_TEMPLATES = [
        "context/substrate.md.template",
        "context/ai-rules.md.template",
        "layer1/AGENTS.md.template",
    ]

    @pytest.mark.parametrize("template_path", DESCRIPTIVE_TEMPLATES)
    def test_no_residue_after_python_project_render(
        self,
        template_path: str,
        python_project: Path,
    ) -> None:
        """All placeholders must be filled when rendering against a Python project."""
        info = detect_project_info(python_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / template_path).read_text()
        rendered = render_template(template, subs)

        leftover = PLACEHOLDER_PATTERN.findall(rendered)
        assert leftover == [], (
            f"Unfilled placeholders in rendered {template_path}: {leftover}"
        )

    @pytest.mark.parametrize("template_path", DESCRIPTIVE_TEMPLATES)
    def test_no_residue_after_js_project_render(
        self,
        template_path: str,
        js_project: Path,
    ) -> None:
        """All placeholders must be filled when rendering against a JS project."""
        info = detect_project_info(js_project)
        subs = info.as_substitutions()
        template = (TEMPLATE_DIR / template_path).read_text()
        rendered = render_template(template, subs)

        leftover = PLACEHOLDER_PATTERN.findall(rendered)
        assert leftover == [], (
            f"Unfilled placeholders in rendered {template_path}: {leftover}"
        )
