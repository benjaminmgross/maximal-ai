"""
Project introspection for RDF template rendering.

Position
--------
Detects project metadata (name, language, framework, dependencies) by reading
manifest files (pyproject.toml, package.json, Cargo.toml, go.mod). Used by
the CLI and installer to populate template placeholders with real project data
instead of hardcoded examples.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectInfo:
    """
    Detected project metadata.

    Parameters
    ----------
    name : str
        Project name from manifest, or directory basename as fallback.
    description : str
        One-line description from manifest, or a TODO placeholder.
    language : str
        Primary language (e.g. "Python 3.12+", "TypeScript 5.x").
    package_manager : str
        Detected package manager (e.g. "uv", "npm", "cargo").
    runtime : str
        Runtime environment (e.g. "CPython", "Node.js").
    framework : str
        Primary framework if detected (e.g. "FastAPI", "Next.js").
    test_framework : str
        Test framework if detected (e.g. "pytest", "vitest").
    formatter : str
        Code formatter if detected (e.g. "ruff format", "prettier").
    linter : str
        Linter if detected (e.g. "ruff", "eslint").
    type_checker : str
        Type checker if detected (e.g. "mypy", "tsc").
    type_strictness : str
        Type checking strictness level.
    line_length : str
        Configured line length.
    dev_commands : str
        Common development commands.
    test_commands : str
        Test run commands.
    lint_commands : str
        Lint/format commands.
    lint_command : str
        Single lint command for pre-commit.
    type_check_command : str
        Single type check command.
    test_command : str
        Single test command.
    dependencies : list[str]
        Key dependencies detected from manifest.
    extra_tech_stack : str
        Additional tech stack lines for AGENTS.md.
    directory_map : str
        Auto-detected directory map for substrate.md.
    project_structure : str
        Tree-like structure for AGENTS.md.
    """

    name: str = "TODO: project-name"
    description: str = "TODO: Add project description"
    language: str = "TODO: detect language"
    package_manager: str = "TODO: detect package manager"
    runtime: str = "TODO: detect runtime"
    framework: str = ""
    test_framework: str = "TODO: detect test framework"
    formatter: str = "TODO: detect formatter"
    linter: str = "TODO: detect linter"
    type_checker: str = "TODO: detect type checker"
    type_strictness: str = "TODO: set strictness"
    line_length: str = "100"
    dev_commands: str = "# TODO: Add development commands"
    test_commands: str = "# TODO: Add test commands"
    lint_commands: str = "# TODO: Add lint/format commands"
    lint_command: str = "# TODO: Add lint command"
    type_check_command: str = "# TODO: Add type check command"
    test_command: str = "# TODO: Add test command"
    dependencies: list[str] = field(default_factory=list)
    extra_tech_stack: str = ""
    directory_map: str = (
        "| `src/` | Application source code | `.context.md` |\n"
        "| `tests/` | Test suite | `.context.md` |"
    )
    project_structure: str = "TODO: Describe project structure"

    def as_substitutions(self) -> dict[str, str]:
        """
        Return a dict of placeholder keys to values for template substitution.

        Returns
        -------
        dict[str, str]
            Mapping from placeholder name (without braces) to value.
        """
        return {
            "PROJECT_NAME": self.name,
            "PROJECT_DESCRIPTION": self.description,
            "LANGUAGE": self.language,
            "PACKAGE_MANAGER": self.package_manager,
            "RUNTIME": self.runtime,
            "TEST_FRAMEWORK": self.test_framework,
            "FORMATTER": self.formatter,
            "LINTER": self.linter,
            "TYPE_CHECKER": self.type_checker,
            "TYPE_STRICTNESS": self.type_strictness,
            "LINE_LENGTH": self.line_length,
            "DEV_COMMANDS": self.dev_commands,
            "TEST_COMMANDS": self.test_commands,
            "LINT_COMMANDS": self.lint_commands,
            "LINT_COMMAND": self.lint_command,
            "TYPE_CHECK_COMMAND": self.type_check_command,
            "TEST_COMMAND": self.test_command,
            "EXTRA_TECH_STACK": self.extra_tech_stack,
            "DIRECTORY_MAP": self.directory_map,
            "PROJECT_STRUCTURE": self.project_structure,
        }


def detect_project_info(project_root: Path) -> ProjectInfo:
    """
    Detect project metadata from manifest files.

    Parameters
    ----------
    project_root : Path
        Root directory of the project to introspect. Must contain at least
        one manifest file (pyproject.toml, package.json, Cargo.toml, go.mod)
        for detection to produce useful results; otherwise all fields default
        to TODO placeholders.

    Returns
    -------
    ProjectInfo
        Detected metadata with real values where possible, TODO placeholders
        where detection failed.
    """
    info = ProjectInfo(name=project_root.resolve().name)

    pyproject = project_root / "pyproject.toml"
    package_json = project_root / "package.json"
    cargo_toml = project_root / "Cargo.toml"
    go_mod = project_root / "go.mod"

    if pyproject.exists():
        _detect_from_pyproject(pyproject, info)
    elif package_json.exists():
        _detect_from_package_json(package_json, info)
    elif cargo_toml.exists():
        _detect_from_cargo(cargo_toml, info)
    elif go_mod.exists():
        _detect_from_go_mod(go_mod, info)

    _detect_directory_structure(project_root, info)

    return info


def _detect_from_pyproject(pyproject: Path, info: ProjectInfo) -> None:
    """Populate ProjectInfo from pyproject.toml."""
    try:
        import tomllib
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ModuleNotFoundError:
            # Fall back to basic parsing
            _detect_from_pyproject_basic(pyproject, info)
            return

    text = pyproject.read_text()
    data = tomllib.loads(text)

    project = data.get("project", {})
    info.name = project.get("name", info.name)
    info.description = project.get("description", info.description)

    # Detect Python version
    python_requires = project.get("requires-python", "")
    if python_requires:
        info.language = f"Python {python_requires.lstrip('>= ')}"
    else:
        info.language = "Python"

    info.runtime = "CPython"

    # Detect package manager
    uv_lock = pyproject.parent / "uv.lock"
    poetry_lock = pyproject.parent / "poetry.lock"
    if uv_lock.exists():
        info.package_manager = "uv"
    elif (
        poetry_lock.exists()
        or data.get("build-system", {}).get("build-backend", "").startswith("poetry")
    ):
        info.package_manager = "poetry"
    else:
        info.package_manager = "pip"

    # Collect dependencies
    deps = project.get("dependencies", [])
    dev_deps_dict = project.get("optional-dependencies", {})
    dev_deps = dev_deps_dict.get("dev", [])
    all_dep_names = [_parse_dep_name(d) for d in deps + dev_deps]
    info.dependencies = all_dep_names

    # Detect framework
    dep_names_lower = [d.lower() for d in all_dep_names]
    if "fastapi" in dep_names_lower:
        info.framework = "FastAPI"
    elif "django" in dep_names_lower:
        info.framework = "Django"
    elif "flask" in dep_names_lower:
        info.framework = "Flask"

    # Detect test framework
    if "pytest" in dep_names_lower:
        info.test_framework = "pytest"
    elif "unittest" in dep_names_lower:
        info.test_framework = "unittest"
    else:
        info.test_framework = "pytest"  # Common default for Python

    # Detect linter/formatter from tool config
    ruff_config = data.get("tool", {}).get("ruff", {})
    if ruff_config:
        info.formatter = "ruff format"
        info.linter = "ruff"
        line_length = ruff_config.get("line-length")
        if line_length:
            info.line_length = str(line_length)

    # Detect type checker
    mypy_config = data.get("tool", {}).get("mypy", {})
    if mypy_config:
        info.type_checker = "mypy"
        strict = mypy_config.get("strict", False)
        info.type_strictness = "strict" if strict else "basic"
    elif "mypy" in dep_names_lower:
        info.type_checker = "mypy"
        info.type_strictness = "basic"
    elif "pyright" in dep_names_lower:
        info.type_checker = "pyright"
        info.type_strictness = "basic"

    # Build command strings
    pm = info.package_manager
    run_prefix = {"uv": "uv run", "poetry": "poetry run"}.get(pm, "")
    run = f"{run_prefix} " if run_prefix else ""
    module = info.name.replace("-", "_")

    info.dev_commands = f"{run}python -m {module}  # Run project"
    info.test_commands = f"{run}pytest"
    info.test_command = f"{run}pytest"

    if info.linter == "ruff":
        lint = f"{run}ruff check . && {run}ruff format ."
        info.lint_commands = lint
        info.lint_command = lint
    else:
        info.lint_commands = "# TODO: Add lint commands"
        info.lint_command = "# TODO"

    if info.type_checker == "mypy":
        info.type_check_command = f"{run}mypy src/"
    else:
        info.type_check_command = "# TODO"

    # Build extra tech stack lines
    extra_lines = []
    if info.framework:
        extra_lines.append(f"- **Framework**: {info.framework}")
    # Detect notable dependencies
    notable = {
        "sqlalchemy": "SQLAlchemy",
        "django": "Django ORM",
        "tortoise-orm": "Tortoise ORM",
        "redis": "Redis",
        "celery": "Celery",
        "pydantic": "Pydantic",
    }
    for dep_lower, label in notable.items():
        if dep_lower in dep_names_lower and label != info.framework:
            extra_lines.append(f"- **{label}**: detected in dependencies")
    if info.test_framework:
        extra_lines.append(f"- **Testing**: {info.test_framework}")
    if info.linter:
        extra_lines.append(f"- **Linting**: {info.linter}")
    if info.type_checker:
        extra_lines.append(f"- **Type Checking**: {info.type_checker}")
    info.extra_tech_stack = "\n".join(extra_lines)


def _detect_from_pyproject_basic(pyproject: Path, info: ProjectInfo) -> None:
    """Parse pyproject.toml without tomllib using regex fallback."""
    import re

    text = pyproject.read_text()

    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if name_match:
        info.name = name_match.group(1)

    desc_match = re.search(r'^description\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if desc_match:
        info.description = desc_match.group(1)

    info.language = "Python"
    info.runtime = "CPython"

    uv_lock = pyproject.parent / "uv.lock"
    if uv_lock.exists():
        info.package_manager = "uv"
    else:
        info.package_manager = "pip"


def _detect_from_package_json(package_json: Path, info: ProjectInfo) -> None:
    """Populate ProjectInfo from package.json."""
    data = json.loads(package_json.read_text())

    info.name = data.get("name", info.name)
    info.description = data.get("description", info.description)
    info.runtime = "Node.js"

    # Detect TypeScript vs JavaScript
    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}
    all_dep_names = list(all_deps.keys())
    info.dependencies = all_dep_names

    if "typescript" in all_deps:
        info.language = "TypeScript"
    else:
        info.language = "JavaScript"

    # Detect package manager
    pnpm_lock = package_json.parent / "pnpm-lock.yaml"
    yarn_lock = package_json.parent / "yarn.lock"
    bun_lock = package_json.parent / "bun.lockb"
    if pnpm_lock.exists():
        info.package_manager = "pnpm"
    elif yarn_lock.exists():
        info.package_manager = "yarn"
    elif bun_lock.exists():
        info.package_manager = "bun"
    else:
        info.package_manager = "npm"

    # Detect framework
    frameworks = [
        ("next", "Next.js"), ("react", "React"), ("vue", "Vue"),
        ("svelte", "Svelte"), ("express", "Express"), ("fastify", "Fastify"),
    ]
    for fw_key, fw_name in frameworks:
        if fw_key in all_deps:
            info.framework = fw_name
            break

    # Detect test framework
    for tf_key, tf_name in [("vitest", "vitest"), ("jest", "jest"), ("mocha", "mocha")]:
        if tf_key in all_deps:
            info.test_framework = tf_name
            break

    # Detect linter/formatter
    if "eslint" in all_deps:
        info.linter = "eslint"
    if "prettier" in all_deps:
        info.formatter = "prettier"
    if "typescript" in all_deps:
        info.type_checker = "tsc"
        info.type_strictness = "strict"

    # Build commands
    pm = info.package_manager
    scripts = data.get("scripts", {})
    info.dev_commands = f"{pm} run dev" if "dev" in scripts else f"{pm} start"
    info.test_commands = f"{pm} test" if "test" in scripts else f"{pm} run test"
    info.test_command = info.test_commands

    if "lint" in scripts:
        info.lint_commands = f"{pm} run lint"
        info.lint_command = f"{pm} run lint"
    else:
        info.lint_commands = "# TODO: Add lint commands"
        info.lint_command = "# TODO"

    if "typecheck" in scripts:
        info.type_check_command = f"{pm} run typecheck"
    elif info.type_checker == "tsc":
        info.type_check_command = "tsc --noEmit"
    else:
        info.type_check_command = "# TODO"

    # Extra tech stack
    extra_lines = []
    if info.framework:
        extra_lines.append(f"- **Framework**: {info.framework}")
    if info.test_framework:
        extra_lines.append(f"- **Testing**: {info.test_framework}")
    if info.linter:
        extra_lines.append(f"- **Linting**: {info.linter}")
    if info.type_checker:
        extra_lines.append(f"- **Type Checking**: {info.type_checker}")
    info.extra_tech_stack = "\n".join(extra_lines)


def _detect_from_cargo(cargo_toml: Path, info: ProjectInfo) -> None:
    """Populate ProjectInfo from Cargo.toml (basic detection)."""
    import re

    text = cargo_toml.read_text()
    info.language = "Rust"
    info.runtime = "native"
    info.package_manager = "cargo"
    info.test_framework = "cargo test"
    info.formatter = "rustfmt"
    info.linter = "clippy"
    info.type_checker = "rustc"
    info.type_strictness = "strict"

    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if name_match:
        info.name = name_match.group(1)

    desc_match = re.search(r'^description\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if desc_match:
        info.description = desc_match.group(1)

    info.dev_commands = "cargo run"
    info.test_commands = "cargo test"
    info.lint_commands = "cargo clippy && cargo fmt --check"
    info.lint_command = "cargo clippy && cargo fmt --check"
    info.type_check_command = "cargo check"
    info.test_command = "cargo test"

    info.extra_tech_stack = "\n".join([
        "- **Build**: cargo",
        "- **Testing**: cargo test",
        "- **Linting**: clippy",
        "- **Formatting**: rustfmt",
    ])


def _detect_from_go_mod(go_mod: Path, info: ProjectInfo) -> None:
    """Populate ProjectInfo from go.mod (basic detection)."""
    import re

    text = go_mod.read_text()
    info.language = "Go"
    info.runtime = "Go runtime"
    info.package_manager = "go modules"
    info.test_framework = "go test"
    info.formatter = "gofmt"
    info.linter = "golangci-lint"
    info.type_checker = "go vet"
    info.type_strictness = "strict"

    module_match = re.search(r"^module\s+(.+)$", text, re.MULTILINE)
    if module_match:
        module_path = module_match.group(1).strip()
        info.name = module_path.split("/")[-1]

    info.dev_commands = "go run ."
    info.test_commands = "go test ./..."
    info.lint_commands = "golangci-lint run && gofmt -l ."
    info.lint_command = "golangci-lint run"
    info.type_check_command = "go vet ./..."
    info.test_command = "go test ./..."

    info.extra_tech_stack = "\n".join([
        "- **Testing**: go test",
        "- **Linting**: golangci-lint",
        "- **Formatting**: gofmt",
    ])


def _detect_directory_structure(project_root: Path, info: ProjectInfo) -> None:
    """Detect top-level directory structure for templates."""
    dir_map_lines = []
    structure_lines = []

    # Common source directories to look for
    visible_dirs = (
        d.name for d in project_root.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    for dirname in sorted(visible_dirs):
        if dirname in ("__pycache__", "node_modules", ".git", ".venv", "venv",
                       ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
                       "build", "dist", ".egg-info", "htmlcov", "coverage"):
            continue

        purpose = _infer_directory_purpose(dirname)
        dir_map_lines.append(f"| `{dirname}/` | {purpose} | `.context.md` |")
        structure_lines.append(f"├── {dirname}/")

    if dir_map_lines:
        info.directory_map = "\n".join(dir_map_lines)
    if structure_lines:
        info.project_structure = "\n".join(structure_lines)


def _infer_directory_purpose(dirname: str) -> str:
    """Infer purpose from common directory naming conventions."""
    purposes = {
        "src": "Application source code",
        "lib": "Library code",
        "app": "Application entry point",
        "api": "API endpoints",
        "tests": "Test suite",
        "test": "Test suite",
        "docs": "Documentation",
        "scripts": "Build and utility scripts",
        "config": "Configuration files",
        "migrations": "Database migrations",
        "alembic": "Database migrations (Alembic)",
        "templates": "Template files",
        "static": "Static assets",
        "public": "Public assets",
        "assets": "Project assets",
        "utils": "Utility modules",
        "helpers": "Helper modules",
        "models": "Data models",
        "schemas": "Data schemas",
        "services": "Service layer",
        "middleware": "Middleware components",
        "plugins": "Plugin modules",
        "extensions": "Extensions",
        "fixtures": "Test fixtures",
        "data": "Data files",
        "bin": "Executable scripts",
        "cmd": "Command entry points",
        "pkg": "Package code",
        "internal": "Internal packages",
        "examples": "Example code",
        "benchmarks": "Performance benchmarks",
        "tools": "Development tools",
        "installers": "Installation scripts",
    }
    return purposes.get(dirname, f"TODO: Describe {dirname}/")


def _parse_dep_name(dep_string: str) -> str:
    """Extract package name from a dependency specifier like 'click>=8.0'."""
    import re

    match = re.match(r"^([a-zA-Z0-9_-]+)", dep_string)
    return match.group(1) if match else dep_string


def render_template(template_content: str, substitutions: dict[str, str]) -> str:
    """
    Replace ``{{KEY}}`` placeholders in template content with values.

    Parameters
    ----------
    template_content : str
        Raw template text containing ``{{KEY}}`` placeholders.
    substitutions : dict[str, str]
        Mapping from placeholder name to replacement value. Keys should not
        include the surrounding braces. Any ``{{KEY}}`` without a matching
        entry in *substitutions* is left unchanged.

    Returns
    -------
    str
        Template with placeholders replaced.
    """
    result = template_content
    for key, value in substitutions.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result
