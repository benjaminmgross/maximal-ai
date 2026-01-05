"""
Script runner with observation.

Position
--------
Executes Python scripts with automatic instrumentation.

Invariants
----------
- Does not permanently modify the script
- Instruments only functions in the target module
- Returns observations after execution
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from rdf.observe import clear_observations, get_observations, start_tracking, stop_tracking
from rdf.observe.models import FunctionProfile


def run_with_observation(
    script_path: Path,
    entrypoint: str = "main",
) -> dict[str, FunctionProfile]:
    """
    Run a script with observation and return collected data.

    Parameters
    ----------
    script_path : Path
        Path to Python script.
    entrypoint : str
        Function name to call (default: "main").

    Returns
    -------
    dict[str, FunctionProfile]
        Function profiles collected during execution.
    """
    clear_observations()

    # Determine module name from script path
    module_name = script_path.stem

    # Start call graph tracking
    start_tracking({module_name, "__observed__"})

    try:
        # Load module
        spec = importlib.util.spec_from_file_location("__observed__", script_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load {script_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["__observed__"] = module

        # Execute module (this runs top-level code)
        spec.loader.exec_module(module)

        # Call entrypoint if it exists and is callable
        if hasattr(module, entrypoint):
            func = getattr(module, entrypoint)
            if callable(func):
                func()

    finally:
        stop_tracking()

    return get_observations()
