"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing."""
    file_path = temp_dir / "sample.py"
    file_path.write_text('''"""Sample module docstring."""

def hello():
    """Say hello."""
    return "Hello, World!"

class Greeter:
    """A greeter class."""

    def greet(self, name):
        """Greet someone."""
        return f"Hello, {name}!"
''')
    return file_path
