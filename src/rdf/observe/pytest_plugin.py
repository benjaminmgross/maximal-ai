"""
pytest plugin for observation during tests.

Position
--------
Automatically collects observations when tests run.
Outputs suggestions after test session completes.

Invariants
----------
- Minimal overhead when not enabled
- Does not affect test results
- Saves observations for later interactive processing
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from rdf.observe import clear_observations, get_observations, start_tracking, stop_tracking

if TYPE_CHECKING:
    import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command line options."""
    group = parser.getgroup("rdf")
    group.addoption(
        "--rdf-observe",
        action="store_true",
        default=False,
        help="Enable docstring observation during tests",
    )
    group.addoption(
        "--rdf-observe-output",
        type=str,
        default=".rdf-observations.json",
        help="Output file for observations",
    )
    group.addoption(
        "--rdf-observe-modules",
        type=str,
        default="",
        help="Comma-separated list of modules to track (empty = all)",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Initialize observation at session start."""
    if config.getoption("--rdf-observe"):
        clear_observations()

        # Parse modules to track
        modules_str = config.getoption("--rdf-observe-modules")
        if modules_str:
            modules = {m.strip() for m in modules_str.split(",") if m.strip()}
        else:
            modules = None

        start_tracking(modules)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Stop tracking when pytest exits."""
    if config.getoption("--rdf-observe"):
        stop_tracking()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Save observations at session end."""
    if not session.config.getoption("--rdf-observe"):
        return

    profiles = get_observations()
    if not profiles:
        return

    output_file = session.config.getoption("--rdf-observe-output")

    # Serialize profiles
    data = {
        "meta": {
            "total_functions": len(profiles),
            "total_observations": sum(p.call_count for p in profiles.values()),
        },
        "functions": {
            qualname: {
                "file_path": p.file_path,
                "line_number": p.line_number,
                "call_count": p.call_count,
                "callers": list(p.callers),
                "callees": list(p.callees),
                "max_depth": p.max_call_depth,
                "min_depth": p.min_call_depth,
            }
            for qualname, p in profiles.items()
        },
    }

    Path(output_file).write_text(json.dumps(data, indent=2))

    print(f"\nRDF: Saved observations from {len(profiles)} functions to {output_file}")
    print(f"     Total observations: {data['meta']['total_observations']}")
    print(f"Run 'rdf observe --resume {output_file}' to generate docstrings interactively")
