"""Pytest fixtures for command testing."""

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def commands_dir(project_root: Path) -> Path:
    """Return the .claude/commands directory."""
    return project_root / ".claude" / "commands"


@pytest.fixture
def mock_arguments() -> dict[str, str]:
    """Provide mock values for common command arguments."""
    return {
        "$ARGUMENTS": "123",
        "$1": "123",
        "${ARGUMENTS}": "123",
    }
