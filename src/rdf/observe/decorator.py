"""
Observation decorator with call graph integration.

Position
--------
Provides the @observe decorator for instrumenting functions.
Integrates with CallGraphTracker for relationship tracking.

Invariants
----------
- Decorated functions behave identically to undecorated ones
- Observations are stored globally (thread-safe)
- Decorator preserves function metadata via functools.wraps
- Records caller/callee relationships
"""

from __future__ import annotations

import functools
import inspect
import threading
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, TypeVar

from rdf.observe.call_graph import get_global_tracker
from rdf.observe.models import CallObservation, FunctionProfile, ValueAnalysis

F = TypeVar("F", bound=Callable[..., Any])

_profiles: dict[str, FunctionProfile] = {}
_lock = threading.Lock()


def observe(func: F) -> F:
    """
    Decorator to observe function behavior for docstring generation.

    Tracks:
    - Argument types and values
    - Return types and values
    - Caller/callee relationships
    - Call depth

    Parameters
    ----------
    func : Callable
        Function to instrument.

    Returns
    -------
    Callable
        Wrapped function that records observations.

    Examples
    --------
    >>> @observe
    ... def add(a: int, b: int) -> int:
    ...     return a + b
    >>> add(1, 2)
    3
    >>> profiles = get_observations()
    >>> any("add" in k for k in profiles.keys())
    True
    """
    sig = inspect.signature(func)

    try:
        source_file = inspect.getfile(func)
    except (TypeError, OSError):
        source_file = "<unknown>"

    try:
        source_lines = inspect.getsourcelines(func)
        line_number = source_lines[1] if source_lines else 0
    except (TypeError, OSError):
        line_number = 0

    qualname = f"{func.__module__}.{func.__qualname__}"

    # Initialize profile
    with _lock:
        if qualname not in _profiles:
            _profiles[qualname] = FunctionProfile(
                qualname=qualname,
                module_name=func.__module__,
                file_path=source_file,
                line_number=line_number,
            )

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Re-create profile if cleared
        with _lock:
            if qualname not in _profiles:
                _profiles[qualname] = FunctionProfile(
                    qualname=qualname,
                    module_name=func.__module__,
                    file_path=source_file,
                    line_number=line_number,
                )
            profile = _profiles[qualname]

        tracker = get_global_tracker()

        # Get call context from global tracker
        caller = tracker.get_caller()
        depth = tracker.get_depth()

        # Update call graph in profile
        with _lock:
            if caller:
                profile.callers.add(caller)
            profile.call_count += 1
            profile.max_call_depth = max(profile.max_call_depth, depth)
            profile.min_call_depth = min(profile.min_call_depth, depth)

        # Bind and analyze arguments
        try:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            analyzed_args = tuple(
                (name, _analyze_value(value)) for name, value in bound.arguments.items()
            )
        except TypeError:
            # If binding fails, just capture positional args
            analyzed_args = tuple((f"arg{i}", _analyze_value(v)) for i, v in enumerate(args))

        # Execute function
        exception_name = None
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            exception_name = type(e).__name__
            raise
        finally:
            # Record observation
            if exception_name:
                return_analysis = ValueAnalysis(type_name="<exception>", is_none=True)
            else:
                return_analysis = _analyze_value(result)

            observation = CallObservation(
                function_name=func.__name__,
                module_name=func.__module__,
                qualname=qualname,
                file_path=source_file,
                line_number=line_number,
                timestamp=datetime.now(timezone.utc),
                arguments=analyzed_args,
                return_value=return_analysis,
                raised_exception=exception_name,
                caller=caller,
                call_depth=depth,
            )

            with _lock:
                profile.observations.append(observation)

    return wrapper  # type: ignore[return-value]


def _analyze_value(value: Any) -> ValueAnalysis:
    """Extract observable properties from a value."""
    type_name = type(value).__name__
    is_none = value is None

    numeric_value = None
    string_length = None
    string_patterns: tuple[str, ...] = ()
    collection_length = None
    collection_is_empty = None
    dict_keys: tuple[str, ...] = ()

    if isinstance(value, bool):
        pass  # Handle bool before int (bool is subclass of int)
    elif isinstance(value, (int, float)):
        numeric_value = float(value)
    elif isinstance(value, str):
        string_length = len(value)
        string_patterns = tuple(_extract_patterns(value))
    elif isinstance(value, (list, tuple, set, frozenset)):
        collection_length = len(value)
        collection_is_empty = len(value) == 0
    elif isinstance(value, dict):
        collection_length = len(value)
        collection_is_empty = len(value) == 0
        dict_keys = tuple(str(k) for k in list(value.keys())[:20])

    return ValueAnalysis(
        type_name=type_name,
        is_none=is_none,
        numeric_value=numeric_value,
        string_length=string_length,
        string_patterns=string_patterns,
        collection_length=collection_length,
        collection_is_empty=collection_is_empty,
        dict_keys=dict_keys,
    )


def _extract_patterns(s: str) -> list[str]:
    """Extract pattern hints from a string."""
    patterns = []
    # File extensions
    for ext in (".csv", ".json", ".yaml", ".yml", ".py", ".txt", ".md"):
        if s.endswith(ext):
            patterns.append(f"ends_with_{ext[1:]}")
    # Common patterns
    if "@" in s and "." in s:
        patterns.append("looks_like_email")
    if s.startswith("/") or s.startswith("./"):
        patterns.append("looks_like_path")
    if s.startswith("http://") or s.startswith("https://"):
        patterns.append("looks_like_url")
    return patterns


def get_observations() -> dict[str, FunctionProfile]:
    """Get all collected function profiles."""
    with _lock:
        return dict(_profiles)


def clear_observations() -> None:
    """Clear all collected observations."""
    with _lock:
        _profiles.clear()
