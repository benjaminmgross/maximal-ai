"""
.folder.md Generator.

Position
--------
Creates and updates .folder.md files with human-preserved sections and
auto-generated file listings. Implements the hybrid documentation pattern.

Invariants
----------
- Must preserve content between HUMAN-AUTHORED markers
- Must replace content after AUTO-GENERATED marker
- Must create backup before any modification
- Dry-run mode available for previewing changes
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Regex patterns for marker detection
HUMAN_MARKER = r"<!--\s*HUMAN-AUTHORED.*?-->"
AUTO_MARKER = r"<!--\s*AUTO-GENERATED BELOW.*?-->"


@dataclass
class FolderMdSections:
    """
    Parsed sections of a .folder.md file.

    Attributes
    ----------
    preamble : str
        Content before any markers (title, etc.).
    human_sections : str
        Content between HUMAN-AUTHORED markers.
    auto_section : str
        Content after AUTO-GENERATED marker.
    """

    preamble: str
    human_sections: str
    auto_section: str


class FolderMdGenerator:
    """
    Generate and update .folder.md files.

    Position
    --------
    Handles hybrid documentation files. Preserves human-authored content
    while regenerating auto-generated sections.

    Invariants
    ----------
    - Human sections are NEVER overwritten
    - Backup created before any write
    - Dry-run mode shows preview without changes

    Parameters
    ----------
    target_dir : Path
        Directory to generate .folder.md for.

    Examples
    --------
    >>> generator = FolderMdGenerator(Path("src/processors/"))
    >>> generator.generate(dry_run=True)  # Preview
    >>> generator.generate(dry_run=False)  # Actually write
    """

    def __init__(self, target_dir: Path) -> None:
        """Initialize generator with target directory."""
        self.target_dir = target_dir
        self.folder_md_path = target_dir / ".folder.md"

    def parse_existing(self) -> FolderMdSections | None:
        """
        Parse existing .folder.md if present.

        Returns
        -------
        FolderMdSections | None
            Parsed sections, or None if file doesn't exist.
        """
        if not self.folder_md_path.exists():
            return None

        content = self.folder_md_path.read_text()

        # Find AUTO-GENERATED marker
        auto_match = re.search(AUTO_MARKER, content)
        if not auto_match:
            # No auto section - entire file is human-authored
            return FolderMdSections(
                preamble=content,
                human_sections="",
                auto_section="",
            )

        preamble = content[: auto_match.start()]
        auto_section = content[auto_match.end() :]

        return FolderMdSections(
            preamble=preamble.rstrip(),
            human_sections="",  # Extracted from preamble
            auto_section=auto_section,
        )

    def generate_file_table(self) -> str:
        """
        Generate markdown table of files in directory.

        Returns
        -------
        str
            Markdown table of files.
        """
        files = [
            f for f in self.target_dir.iterdir() if f.is_file() and f.suffix == ".py"
        ]

        if not files:
            return "No Python files in this directory."

        lines = [
            "## Files",
            "",
            "| File | Type | Key Symbols | Lines |",
            "|------|------|-------------|-------|",
        ]

        for f in sorted(files):
            name = f.name
            line_count = len(f.read_text().splitlines())
            lines.append(f"| `{name}` | module | - | {line_count} |")

        return "\n".join(lines)

    def generate(self, *, dry_run: bool = True) -> str:
        """
        Generate or update .folder.md.

        Parameters
        ----------
        dry_run : bool
            If True, return preview without writing.

        Returns
        -------
        str
            Generated content (or preview message).
        """
        existing = self.parse_existing()
        file_table = self.generate_file_table()

        timestamp = datetime.now().isoformat()
        auto_section = f"""
<!-- AUTO-GENERATED BELOW - DO NOT EDIT MANUALLY -->
<!-- Last generated: {timestamp} -->

{file_table}
"""

        if existing:
            # Preserve human content
            full_content = existing.preamble + "\n\n---\n" + auto_section
        else:
            # Create new template
            full_content = f"""# Folder: {self.target_dir.name}/

> **Update Trigger:** Regenerate when files added/removed. Update Purpose/Invariants
> when folder responsibilities change.

## Purpose

<!-- HUMAN-AUTHORED - DO NOT AUTO-GENERATE -->
TODO: Describe what this folder does.

## Invariants

<!-- HUMAN-AUTHORED - DO NOT AUTO-GENERATE -->
TODO: List rules that must always be true.

---
{auto_section}
"""

        if dry_run:
            return f"Would write to {self.folder_md_path}:\n\n{full_content}"

        # Create backup
        if self.folder_md_path.exists():
            backup_path = self.folder_md_path.with_suffix(".md.bak")
            backup_path.write_text(self.folder_md_path.read_text())

        # Write
        self.folder_md_path.write_text(full_content)
        return full_content
