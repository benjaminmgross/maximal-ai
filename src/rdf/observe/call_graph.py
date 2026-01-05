"""
Call graph tracking during observation.

Position
--------
Tracks caller/callee relationships between functions during execution.
Uses sys.setprofile for lightweight call tracking.

Invariants
----------
- Minimal overhead (no argument inspection during tracking)
- Thread-safe call stack management
- Accurately tracks call depth
"""

from __future__ import annotations

import sys
import threading
from dataclasses import dataclass, field
from types import FrameType
from typing import Any


@dataclass
class CallGraphTracker:
    """
    Track function call relationships.

    Position
    --------
    Lightweight call graph builder using sys.setprofile.

    Invariants
    ----------
    - Does not inspect argument values (that's the decorator's job)
    - Tracks only Python function calls
    - Thread-local call stacks
    """

    # Tracked modules (only track calls within these)
    tracked_modules: set[str] = field(default_factory=set)

    # Call relationships: callee -> set of callers
    callers: dict[str, set[str]] = field(default_factory=dict)

    # Call relationships: caller -> set of callees
    callees: dict[str, set[str]] = field(default_factory=dict)

    # Thread-local call stacks
    _local: threading.local = field(default_factory=threading.local)

    # Lock for thread-safe updates
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def _get_stack(self) -> list[str]:
        """Get thread-local call stack."""
        if not hasattr(self._local, "stack"):
            self._local.stack = []
        return self._local.stack

    def _profile_callback(self, frame: FrameType, event: str, arg: Any) -> None:
        """Profile callback for sys.setprofile."""
        if event not in ("call", "return"):
            return

        # Get function info
        code = frame.f_code
        module = frame.f_globals.get("__name__", "")

        # Only track specified modules (if any specified)
        if self.tracked_modules and not any(module.startswith(m) for m in self.tracked_modules):
            return

        qualname = f"{module}.{code.co_name}"
        stack = self._get_stack()

        if event == "call":
            # Record caller relationship
            if stack:
                caller = stack[-1]
                with self._lock:
                    if qualname not in self.callers:
                        self.callers[qualname] = set()
                    self.callers[qualname].add(caller)

                    if caller not in self.callees:
                        self.callees[caller] = set()
                    self.callees[caller].add(qualname)

            stack.append(qualname)

        elif event == "return":
            if stack and stack[-1] == qualname:
                stack.pop()

    def start(self) -> None:
        """Start tracking."""
        sys.setprofile(self._profile_callback)

    def stop(self) -> None:
        """Stop tracking."""
        sys.setprofile(None)

    def get_caller(self) -> str | None:
        """Get the current caller (second from top of stack)."""
        stack = self._get_stack()
        if len(stack) >= 2:
            return stack[-2]
        return None

    def get_current(self) -> str | None:
        """Get the current function (top of stack)."""
        stack = self._get_stack()
        if stack:
            return stack[-1]
        return None

    def get_depth(self) -> int:
        """Get current call depth."""
        return len(self._get_stack())

    def clear(self) -> None:
        """Clear all tracked data."""
        with self._lock:
            self.callers.clear()
            self.callees.clear()
        if hasattr(self._local, "stack"):
            self._local.stack.clear()


# Global instance for module-level tracking
_global_tracker: CallGraphTracker | None = None


def get_global_tracker() -> CallGraphTracker:
    """Get or create the global call graph tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CallGraphTracker()
    return _global_tracker


def start_tracking(modules: set[str] | None = None) -> None:
    """Start global call graph tracking."""
    tracker = get_global_tracker()
    if modules:
        tracker.tracked_modules = modules
    tracker.start()


def stop_tracking() -> None:
    """Stop global call graph tracking."""
    tracker = get_global_tracker()
    tracker.stop()


def clear_tracking() -> None:
    """Clear global tracking data."""
    tracker = get_global_tracker()
    tracker.clear()
