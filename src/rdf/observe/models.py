"""
Data models for runtime observations.

Position
--------
Defines data structures for function observations, call graphs,
and inferred docstring components.

Invariants
----------
- All observation models are immutable dataclasses where appropriate
- Timestamps use UTC
- Values stored as analyzed summaries (not raw objects)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StructuralRole(Enum):
    """Inferred structural role of a function."""

    ENTRY_POINT = "entry_point"  # Called from __main__ or CLI
    ORCHESTRATOR = "orchestrator"  # Calls many, called by few
    COORDINATOR = "coordinator"  # Called by few, calls many
    UTILITY = "utility"  # Called by many, calls few
    LEAF = "leaf"  # Calls nothing
    TRANSFORMER = "transformer"  # Pure data transformation
    VALIDATOR = "validator"  # Returns bool, checks conditions
    IO_READER = "io_reader"  # Reads from external sources
    IO_WRITER = "io_writer"  # Writes to external sources
    UNKNOWN = "unknown"


class IOPattern(Enum):
    """I/O patterns detected during execution."""

    FILESYSTEM_READ = "filesystem_read"
    FILESYSTEM_WRITE = "filesystem_write"
    NETWORK_CALL = "network_call"
    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"
    PURE = "pure"  # No side effects detected


@dataclass(frozen=True)
class ValueAnalysis:
    """Analysis of a single value."""

    type_name: str
    is_none: bool
    # Numeric
    numeric_value: float | None = None
    # String
    string_length: int | None = None
    string_patterns: tuple[str, ...] = ()
    # Collection
    collection_length: int | None = None
    collection_is_empty: bool | None = None
    dict_keys: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type_name": self.type_name,
            "is_none": self.is_none,
            "numeric_value": self.numeric_value,
            "string_length": self.string_length,
            "string_patterns": list(self.string_patterns),
            "collection_length": self.collection_length,
            "collection_is_empty": self.collection_is_empty,
            "dict_keys": list(self.dict_keys),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValueAnalysis:
        """Deserialize from dictionary."""
        return cls(
            type_name=data["type_name"],
            is_none=data["is_none"],
            numeric_value=data.get("numeric_value"),
            string_length=data.get("string_length"),
            string_patterns=tuple(data.get("string_patterns", [])),
            collection_length=data.get("collection_length"),
            collection_is_empty=data.get("collection_is_empty"),
            dict_keys=tuple(data.get("dict_keys", [])),
        )


@dataclass(frozen=True)
class CallObservation:
    """A single function call observation."""

    function_name: str
    module_name: str
    qualname: str
    file_path: str
    line_number: int
    timestamp: datetime
    arguments: tuple[tuple[str, ValueAnalysis], ...]  # Immutable version
    return_value: ValueAnalysis
    raised_exception: str | None = None
    # Call graph context
    caller: str | None = None  # Who called this function
    call_depth: int = 0  # Depth in call stack

    @property
    def arguments_dict(self) -> dict[str, ValueAnalysis]:
        """Get arguments as a dictionary."""
        return dict(self.arguments)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "function_name": self.function_name,
            "module_name": self.module_name,
            "qualname": self.qualname,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "timestamp": self.timestamp.isoformat(),
            "arguments": [(name, val.to_dict()) for name, val in self.arguments],
            "return_value": self.return_value.to_dict(),
            "raised_exception": self.raised_exception,
            "caller": self.caller,
            "call_depth": self.call_depth,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CallObservation:
        """Deserialize from dictionary."""
        return cls(
            function_name=data["function_name"],
            module_name=data["module_name"],
            qualname=data["qualname"],
            file_path=data["file_path"],
            line_number=data["line_number"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            arguments=tuple(
                (name, ValueAnalysis.from_dict(val)) for name, val in data["arguments"]
            ),
            return_value=ValueAnalysis.from_dict(data["return_value"]),
            raised_exception=data.get("raised_exception"),
            caller=data.get("caller"),
            call_depth=data.get("call_depth", 0),
        )


@dataclass
class FunctionProfile:
    """Aggregated profile of a function from multiple observations."""

    qualname: str
    module_name: str
    file_path: str
    line_number: int

    # Call graph
    callers: set[str] = field(default_factory=set)
    callees: set[str] = field(default_factory=set)
    call_count: int = 0
    max_call_depth: int = 0
    min_call_depth: int = 999

    # I/O patterns
    io_patterns: set[IOPattern] = field(default_factory=set)

    # Observations
    observations: list[CallObservation] = field(default_factory=list)

    @property
    def is_entry_point(self) -> bool:
        """True if called from __main__ or has no internal callers."""
        return not self.callers or any("__main__" in c for c in self.callers)

    @property
    def is_leaf(self) -> bool:
        """True if doesn't call other tracked functions."""
        return len(self.callees) == 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary with full observation data."""
        return {
            "qualname": self.qualname,
            "module_name": self.module_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "callers": list(self.callers),
            "callees": list(self.callees),
            "call_count": self.call_count,
            "max_call_depth": self.max_call_depth,
            "min_call_depth": self.min_call_depth,
            "io_patterns": [p.value for p in self.io_patterns],
            "observations": [o.to_dict() for o in self.observations],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FunctionProfile:
        """Deserialize from dictionary with full observation data."""
        profile = cls(
            qualname=data["qualname"],
            module_name=data["module_name"],
            file_path=data["file_path"],
            line_number=data["line_number"],
            callers=set(data.get("callers", [])),
            callees=set(data.get("callees", [])),
            call_count=data.get("call_count", 0),
            max_call_depth=data.get("max_call_depth", 0),
            min_call_depth=data.get("min_call_depth", 999),
            io_patterns={IOPattern(p) for p in data.get("io_patterns", [])},
        )
        # Deserialize observations
        for obs_data in data.get("observations", []):
            profile.observations.append(CallObservation.from_dict(obs_data))
        return profile


@dataclass
class InferredPosition:
    """Auto-inferred Position section content."""

    structural_role: StructuralRole
    call_graph_description: str  # "Called by X, calls Y, Z"
    io_description: str | None  # "Reads from filesystem"
    depth_description: str | None  # "Entry point" or "Deep utility"


@dataclass
class InferredInvariant:
    """A single inferred invariant."""

    parameter: str  # "__return__" for return value
    invariant_type: str  # "type", "range", "nullability", etc.
    description: str  # "x is never None"
    confidence: float  # 0.0 - 1.0
    observations_count: int
    supporting_count: int


@dataclass
class HumanInput:
    """Human-provided docstring content."""

    business_purpose: str | None = None
    architectural_context: str | None = None
    additional_invariants: list[str] = field(default_factory=list)
    parameter_descriptions: dict[str, str] = field(default_factory=dict)
    return_description: str | None = None


@dataclass
class GeneratedDocstring:
    """Complete generated docstring for a function."""

    qualname: str
    file_path: str
    line_number: int

    # Auto-inferred
    inferred_position: InferredPosition
    inferred_invariants: list[InferredInvariant]
    inferred_params: dict[str, ValueAnalysis]
    inferred_return: ValueAnalysis | None

    # Human-provided
    human_input: HumanInput

    def render(self) -> str:
        """Render complete NumPy-format docstring."""
        lines = []

        # Summary line (from human input)
        if self.human_input.business_purpose:
            lines.append(self.human_input.business_purpose)
            lines.append("")

        # Position section
        lines.append("Position")
        lines.append("-" * 8)
        position_parts = []

        # Structural role
        role_desc = self._role_to_description(self.inferred_position.structural_role)
        if role_desc:
            position_parts.append(role_desc)

        # Call graph
        if self.inferred_position.call_graph_description:
            position_parts.append(self.inferred_position.call_graph_description)

        # I/O pattern
        if self.inferred_position.io_description:
            position_parts.append(self.inferred_position.io_description)

        # Human architectural context
        if self.human_input.architectural_context:
            position_parts.append(self.human_input.architectural_context)

        lines.append(
            " ".join(position_parts) if position_parts else "TODO: Add position description"
        )
        lines.append("")

        # Invariants section
        all_invariants = [
            inv.description for inv in self.inferred_invariants if inv.confidence >= 0.95
        ]
        all_invariants.extend(self.human_input.additional_invariants)

        if all_invariants:
            lines.append("Invariants")
            lines.append("-" * 10)
            for inv in all_invariants:
                lines.append(f"- {inv}")
            lines.append("")

        # Parameters section
        if self.inferred_params:
            lines.append("Parameters")
            lines.append("-" * 10)
            for param, analysis in self.inferred_params.items():
                human_desc = self.human_input.parameter_descriptions.get(param, "")
                type_hint = analysis.type_name
                lines.append(f"{param} : {type_hint}")
                lines.append(f"    {human_desc or 'TODO: Add description'}")
            lines.append("")

        # Returns section
        if self.inferred_return and self.inferred_return.type_name != "NoneType":
            lines.append("Returns")
            lines.append("-" * 7)
            lines.append(self.inferred_return.type_name)
            lines.append(f"    {self.human_input.return_description or 'TODO: Add description'}")

        return "\n".join(lines)

    def _role_to_description(self, role: StructuralRole) -> str:
        """Convert structural role to human-readable description."""
        descriptions = {
            StructuralRole.ENTRY_POINT: "Entry point.",
            StructuralRole.ORCHESTRATOR: "Orchestrator that coordinates multiple operations.",
            StructuralRole.COORDINATOR: "Coordinator.",
            StructuralRole.UTILITY: "Utility function.",
            StructuralRole.LEAF: "Leaf function with no dependencies.",
            StructuralRole.TRANSFORMER: "Data transformer.",
            StructuralRole.VALIDATOR: "Validator.",
            StructuralRole.IO_READER: "I/O reader.",
            StructuralRole.IO_WRITER: "I/O writer.",
            StructuralRole.UNKNOWN: "",
        }
        return descriptions.get(role, "")


@dataclass
class ObservationSession:
    """A complete observation session, serializable for save/resume."""

    session_id: str
    started_at: datetime
    script_path: str
    functions: dict[str, FunctionProfile] = field(default_factory=dict)
    completed_functions: set[str] = field(default_factory=set)  # Already processed

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON storage."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "script_path": self.script_path,
            "functions": {
                k: {
                    "qualname": v.qualname,
                    "module_name": v.module_name,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "callers": list(v.callers),
                    "callees": list(v.callees),
                    "call_count": v.call_count,
                }
                for k, v in self.functions.items()
            },
            "completed_functions": list(self.completed_functions),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObservationSession:
        """Deserialize from JSON."""
        functions = {}
        for k, v in data.get("functions", {}).items():
            functions[k] = FunctionProfile(
                qualname=v["qualname"],
                module_name=v["module_name"],
                file_path=v["file_path"],
                line_number=v["line_number"],
                callers=set(v.get("callers", [])),
                callees=set(v.get("callees", [])),
                call_count=v.get("call_count", 0),
            )

        return cls(
            session_id=data["session_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            script_path=data["script_path"],
            functions=functions,
            completed_functions=set(data.get("completed_functions", [])),
        )
