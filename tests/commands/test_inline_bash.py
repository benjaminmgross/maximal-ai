"""Test that inline bash patterns in slash commands execute without errors.

These tests validate that:
1. Inline bash patterns have valid syntax
2. No known-unsafe patterns exist (command substitution, arithmetic, conditionals)
3. Commands follow Claude Code inline bash limitations
"""

import re
import subprocess
from pathlib import Path

import pytest


def extract_inline_bash(content: str) -> list[str]:
    """Extract all !`...` patterns from command file."""
    return re.findall(r"!\`([^`]+)\`", content)


def get_command_files() -> list[Path]:
    """Get all .md files in .claude/commands/."""
    commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
    return list(commands_dir.glob("*.md"))


class TestInlineBashSyntax:
    """Test inline bash patterns for valid syntax."""

    @pytest.mark.parametrize("cmd_file", get_command_files(), ids=lambda p: p.name)
    def test_inline_bash_syntax_valid(self, cmd_file: Path, tmp_path: Path):
        """Each inline bash pattern should have valid bash syntax."""
        content = cmd_file.read_text()
        patterns = extract_inline_bash(content)

        for i, pattern in enumerate(patterns):
            # Replace variables with safe test values
            test_pattern = pattern
            test_pattern = test_pattern.replace("$ARGUMENTS", "123")
            test_pattern = test_pattern.replace("$1", "123")

            # Skip patterns that require external tools
            skip_prefixes = ["gh pr", "gh api", "gh issue"]
            if any(prefix in test_pattern for prefix in skip_prefixes):
                continue

            # Use bash -n for syntax checking only (doesn't execute)
            result = subprocess.run(
                ["bash", "-n", "-c", test_pattern],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=tmp_path,
            )

            assert result.returncode == 0, (
                f"Pattern {i + 1} in {cmd_file.name} has syntax error:\n"
                f"Pattern: {pattern[:100]}...\n"
                f"Error: {result.stderr}"
            )


class TestNoUnsafePatterns:
    """Test that commands don't contain known-unsafe patterns.

    Claude Code's inline bash parser has limitations with:
    - Command substitution $() - gets over-escaped to \\$()
    - Arithmetic expansion $(()) - parse errors
    - Bash conditionals [[ ]] - parse errors

    These patterns work in real bash but fail in Claude Code's inline parser.
    """

    # Patterns that break Claude Code inline bash
    # Format: (regex pattern, description)
    UNSAFE_PATTERNS = [
        (r"!\`[^`]*[A-Z_]+=\$\([^)]+\)", "Variable assignment with command substitution"),
        (r"!\`[^`]*\$\(\(", "Arithmetic expansion $(("),
        (r"!\`[^`]*\[\[", "Bash conditional [["),
    ]

    @pytest.mark.parametrize("cmd_file", get_command_files(), ids=lambda p: p.name)
    def test_no_unsafe_patterns(self, cmd_file: Path):
        """Command files should not contain patterns that break Claude Code."""
        content = cmd_file.read_text()

        for pattern, description in self.UNSAFE_PATTERNS:
            matches = re.findall(pattern, content)
            assert not matches, (
                f"{cmd_file.name} contains unsafe pattern ({description}):\n"
                f"Found: {matches[:3]}"  # Show first 3 matches
            )


class TestCommandFileStructure:
    """Test that command files have proper structure."""

    @pytest.mark.parametrize("cmd_file", get_command_files(), ids=lambda p: p.name)
    def test_has_yaml_frontmatter(self, cmd_file: Path):
        """Command files should have YAML frontmatter."""
        content = cmd_file.read_text()
        assert content.startswith("---"), f"{cmd_file.name} missing YAML frontmatter"
        assert content.count("---") >= 2, f"{cmd_file.name} has incomplete frontmatter"

    @pytest.mark.parametrize("cmd_file", get_command_files(), ids=lambda p: p.name)
    def test_has_description(self, cmd_file: Path):
        """Command files should have a description in frontmatter."""
        content = cmd_file.read_text()
        # Extract frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            assert "description:" in frontmatter, (
                f"{cmd_file.name} missing description in frontmatter"
            )
