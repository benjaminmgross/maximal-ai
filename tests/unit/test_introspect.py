"""Tests for project introspection module."""

from pathlib import Path

from rdf.introspect import detect_project_info, render_template


class TestRenderTemplate:
    """Tests for the render_template function."""

    def test_replaces_single_placeholder(self) -> None:
        """Test replacing a single {{KEY}} placeholder."""
        result = render_template("Hello {{NAME}}!", {"NAME": "World"})
        assert result == "Hello World!"

    def test_replaces_multiple_placeholders(self) -> None:
        """Test replacing multiple different placeholders."""
        template = "{{A}} and {{B}}"
        result = render_template(template, {"A": "foo", "B": "bar"})
        assert result == "foo and bar"

    def test_replaces_repeated_placeholder(self) -> None:
        """Test replacing a placeholder that appears multiple times."""
        result = render_template("{{X}} then {{X}}", {"X": "y"})
        assert result == "y then y"

    def test_leaves_unknown_placeholders(self) -> None:
        """Test that placeholders without a substitution are left as-is."""
        result = render_template("{{KNOWN}} {{UNKNOWN}}", {"KNOWN": "yes"})
        assert result == "yes {{UNKNOWN}}"

    def test_empty_substitutions(self) -> None:
        """Test with empty substitutions dict."""
        result = render_template("{{KEY}}", {})
        assert result == "{{KEY}}"


class TestDetectProjectInfo:
    """Tests for detecting project metadata from manifest files."""

    def test_pyproject_toml_detection(self, temp_dir: Path) -> None:
        """Test detection from pyproject.toml."""
        pyproject = temp_dir / "pyproject.toml"
        pyproject.write_text("""\
[project]
name = "my-cool-app"
description = "A cool application"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.100",
    "click>=8.0",
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

        info = detect_project_info(temp_dir)

        assert info.name == "my-cool-app"
        assert info.description == "A cool application"
        assert "3.11" in info.language
        assert info.runtime == "CPython"
        assert info.framework == "FastAPI"
        assert info.test_framework == "pytest"
        assert info.linter == "ruff"
        assert info.type_checker == "mypy"
        assert info.type_strictness == "strict"
        assert info.line_length == "100"

    def test_pyproject_with_uv_lock(self, temp_dir: Path) -> None:
        """Test that uv.lock triggers 'uv' package manager detection."""
        (temp_dir / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (temp_dir / "uv.lock").write_text("")

        info = detect_project_info(temp_dir)
        assert info.package_manager == "uv"

    def test_pyproject_with_poetry_lock(self, temp_dir: Path) -> None:
        """Test that poetry.lock triggers 'poetry' package manager detection."""
        (temp_dir / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (temp_dir / "poetry.lock").write_text("")

        info = detect_project_info(temp_dir)
        assert info.package_manager == "poetry"

    def test_package_json_detection(self, temp_dir: Path) -> None:
        """Test detection from package.json."""
        package_json = temp_dir / "package.json"
        package_json.write_text("""\
{
    "name": "my-react-app",
    "description": "A React application",
    "dependencies": {
        "react": "^18.0",
        "next": "^14.0"
    },
    "devDependencies": {
        "typescript": "^5.0",
        "eslint": "^8.0",
        "prettier": "^3.0",
        "vitest": "^1.0"
    },
    "scripts": {
        "dev": "next dev",
        "test": "vitest",
        "lint": "eslint .",
        "typecheck": "tsc --noEmit"
    }
}
""")

        info = detect_project_info(temp_dir)

        assert info.name == "my-react-app"
        assert info.description == "A React application"
        assert info.language == "TypeScript"
        assert info.runtime == "Node.js"
        assert info.framework == "Next.js"
        assert info.test_framework == "vitest"
        assert info.linter == "eslint"
        assert info.formatter == "prettier"
        assert info.type_checker == "tsc"

    def test_package_json_npm_default(self, temp_dir: Path) -> None:
        """Test that npm is default package manager for package.json."""
        (temp_dir / "package.json").write_text('{"name": "test"}')

        info = detect_project_info(temp_dir)
        assert info.package_manager == "npm"

    def test_package_json_pnpm(self, temp_dir: Path) -> None:
        """Test pnpm-lock.yaml triggers pnpm detection."""
        (temp_dir / "package.json").write_text('{"name": "test"}')
        (temp_dir / "pnpm-lock.yaml").write_text("")

        info = detect_project_info(temp_dir)
        assert info.package_manager == "pnpm"

    def test_no_manifest_uses_defaults(self, temp_dir: Path) -> None:
        """Test that missing manifests produce TODO defaults."""
        info = detect_project_info(temp_dir)

        assert info.name == temp_dir.resolve().name
        assert "TODO" in info.description
        assert "TODO" in info.language

    def test_as_substitutions_returns_dict(self, temp_dir: Path) -> None:
        """Test that as_substitutions returns complete dict."""
        (temp_dir / "pyproject.toml").write_text('[project]\nname = "test-proj"\n')

        info = detect_project_info(temp_dir)
        subs = info.as_substitutions()

        assert isinstance(subs, dict)
        assert subs["PROJECT_NAME"] == "test-proj"
        assert "LANGUAGE" in subs
        assert "PACKAGE_MANAGER" in subs

    def test_directory_structure_detection(self, temp_dir: Path) -> None:
        """Test that directory structure is auto-detected."""
        (temp_dir / "src").mkdir()
        (temp_dir / "tests").mkdir()
        (temp_dir / "docs").mkdir()
        (temp_dir / "pyproject.toml").write_text('[project]\nname = "test"\n')

        info = detect_project_info(temp_dir)

        assert "src" in info.directory_map
        assert "tests" in info.directory_map
        assert "docs" in info.directory_map

    def test_hidden_dirs_excluded(self, temp_dir: Path) -> None:
        """Test that hidden directories are excluded from structure."""
        (temp_dir / ".git").mkdir()
        (temp_dir / ".venv").mkdir()
        (temp_dir / "src").mkdir()
        (temp_dir / "pyproject.toml").write_text('[project]\nname = "test"\n')

        info = detect_project_info(temp_dir)

        assert ".git" not in info.directory_map
        assert ".venv" not in info.directory_map


class TestProjectInfoSubstitutions:
    """Tests that template substitution produces correct output."""

    def test_layer2_template_substitution(self) -> None:
        """Test that Layer 2 template gets FOLDER_NAME substituted."""
        template = "# Folder: {{FOLDER_NAME}}/\n\nTODO: Describe."
        result = render_template(template, {"FOLDER_NAME": "my-module"})
        assert "# Folder: my-module/" in result
        assert "{{FOLDER_NAME}}" not in result

    def test_substrate_template_substitution(self) -> None:
        """Test that substrate template gets PROJECT_NAME substituted."""
        template = "{{PROJECT_NAME}} — {{PROJECT_DESCRIPTION}}"
        subs = {"PROJECT_NAME": "cool-app", "PROJECT_DESCRIPTION": "Does cool things"}
        result = render_template(template, subs)
        assert result == "cool-app — Does cool things"
        assert "{{" not in result

    def test_ai_rules_template_substitution(self) -> None:
        """Test that ai-rules template gets language/tooling substituted."""
        template = "- **Language:** {{LANGUAGE}}\n- **Linter:** {{LINTER}}"
        subs = {"LANGUAGE": "Python 3.12+", "LINTER": "ruff"}
        result = render_template(template, subs)
        assert "Python 3.12+" in result
        assert "ruff" in result
