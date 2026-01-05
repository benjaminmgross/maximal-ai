"""
Interactive Docstring Generator - Observation Module.

Position
--------
Entry point for runtime observation. Provides decorators, collectors,
and utilities for capturing function behavior at runtime.

Invariants
----------
- Observation is opt-in via decorator or sys.setprofile
- Does not modify observed functions' behavior
- Thread-safe data collection
- Tracks call graph relationships
"""

from rdf.observe.call_graph import (
    CallGraphTracker,
    clear_tracking,
    get_global_tracker,
    start_tracking,
    stop_tracking,
)
from rdf.observe.decorator import clear_observations, get_observations, observe

__all__ = [
    "observe",
    "get_observations",
    "clear_observations",
    "CallGraphTracker",
    "get_global_tracker",
    "start_tracking",
    "stop_tracking",
    "clear_tracking",
]
