"""
Inference engine for Invariants and Position.

Position
--------
Analyzes collected observations to infer docstring content.
Produces both Invariant candidates and Position hints.

Invariants
----------
- Only suggests with sufficient confidence
- Never modifies source code directly
- Returns structured suggestions for human review
"""

from __future__ import annotations

from rdf.observe.models import (
    FunctionProfile,
    InferredInvariant,
    InferredPosition,
    IOPattern,
    StructuralRole,
    ValueAnalysis,
)


class InferenceEngine:
    """
    Analyze function profiles to infer docstring content.

    Position
    --------
    Core inference engine. Produces Position hints and Invariant candidates.

    Invariants
    ----------
    - Requires minimum observation count for invariant inference
    - Position inference works with any observation count
    - Does not infer overly specific invariants
    """

    MIN_OBSERVATIONS = 5
    HIGH_CONFIDENCE_THRESHOLD = 0.95

    def __init__(self, profiles: dict[str, FunctionProfile]) -> None:
        """
        Initialize the inference engine.

        Parameters
        ----------
        profiles : dict[str, FunctionProfile]
            Function profiles to analyze.
        """
        self.profiles = profiles

    def infer_all(
        self,
    ) -> dict[str, tuple[InferredPosition, list[InferredInvariant]]]:
        """
        Infer Position and Invariants for all functions.

        Returns
        -------
        dict[str, tuple[InferredPosition, list[InferredInvariant]]]
            Mapping from qualname to (position, invariants).
        """
        results = {}
        for qualname, profile in self.profiles.items():
            position = self._infer_position(profile)
            invariants = self._infer_invariants(profile)
            results[qualname] = (position, invariants)
        return results

    def _infer_position(self, profile: FunctionProfile) -> InferredPosition:
        """Infer Position section content from call graph and I/O patterns."""
        # Determine structural role
        role = self._classify_role(profile)

        # Build call graph description
        call_graph_parts = []
        if profile.callers:
            caller_names = [c.split(".")[-1] for c in list(profile.callers)[:3]]
            call_graph_parts.append(f"Called by {', '.join(caller_names)}")
        if profile.callees:
            callee_names = [c.split(".")[-1] for c in list(profile.callees)[:3]]
            call_graph_parts.append(f"calls {', '.join(callee_names)}")
        call_graph_desc = "; ".join(call_graph_parts) if call_graph_parts else ""

        # Build I/O description
        io_desc = None
        if profile.io_patterns:
            io_parts = []
            if IOPattern.FILESYSTEM_READ in profile.io_patterns:
                io_parts.append("reads from filesystem")
            if IOPattern.FILESYSTEM_WRITE in profile.io_patterns:
                io_parts.append("writes to filesystem")
            if IOPattern.NETWORK_CALL in profile.io_patterns:
                io_parts.append("makes network calls")
            if IOPattern.DATABASE_READ in profile.io_patterns:
                io_parts.append("reads from database")
            if IOPattern.DATABASE_WRITE in profile.io_patterns:
                io_parts.append("writes to database")
            if io_parts:
                io_desc = ", ".join(io_parts).capitalize()

        # Depth description
        depth_desc = None
        if profile.is_entry_point:
            depth_desc = "Entry point"
        elif profile.min_call_depth >= 3:
            depth_desc = "Deep utility"

        return InferredPosition(
            structural_role=role,
            call_graph_description=call_graph_desc,
            io_description=io_desc,
            depth_description=depth_desc,
        )

    def _classify_role(self, profile: FunctionProfile) -> StructuralRole:
        """Classify the structural role of a function."""
        num_callers = len(profile.callers)
        num_callees = len(profile.callees)

        # Entry point detection
        if profile.is_entry_point:
            if num_callees > 3:
                return StructuralRole.ORCHESTRATOR
            return StructuralRole.ENTRY_POINT

        # Leaf detection
        if profile.is_leaf:
            # Check if it's a validator (returns bool consistently)
            if profile.observations:
                return_types = [o.return_value.type_name for o in profile.observations]
                if all(t == "bool" for t in return_types):
                    return StructuralRole.VALIDATOR
            return StructuralRole.LEAF

        # Utility: called by many, calls few
        if num_callers > 3 and num_callees <= 2:
            return StructuralRole.UTILITY

        # Orchestrator: calls many
        if num_callees > 3:
            return StructuralRole.ORCHESTRATOR

        # Coordinator: called by few, calls some
        if num_callers <= 2 and num_callees > 1:
            return StructuralRole.COORDINATOR

        return StructuralRole.UNKNOWN

    def _infer_invariants(self, profile: FunctionProfile) -> list[InferredInvariant]:
        """Infer invariants from observations."""
        if len(profile.observations) < self.MIN_OBSERVATIONS:
            return []

        invariants = []

        # Get parameter names from first observation
        if not profile.observations:
            return []

        first_obs = profile.observations[0]

        # Analyze each parameter
        for param, _ in first_obs.arguments:
            analyses = []
            for obs in profile.observations:
                for p, v in obs.arguments:
                    if p == param:
                        analyses.append(v)
                        break

            if analyses:
                invariants.extend(self._infer_param_invariants(param, analyses))

        # Analyze return value
        return_analyses = [
            o.return_value for o in profile.observations if o.raised_exception is None
        ]
        if len(return_analyses) >= self.MIN_OBSERVATIONS:
            invariants.extend(self._infer_param_invariants("__return__", return_analyses))

        return invariants

    def _infer_param_invariants(
        self, param: str, analyses: list[ValueAnalysis]
    ) -> list[InferredInvariant]:
        """Infer invariants for a single parameter."""
        invariants = []
        param_desc = "Return value" if param == "__return__" else f"`{param}`"

        # Nullability
        none_count = sum(1 for a in analyses if a.is_none)
        if none_count == 0:
            invariants.append(
                InferredInvariant(
                    parameter=param,
                    invariant_type="nullability",
                    description=f"{param_desc} is never None",
                    confidence=1.0,
                    observations_count=len(analyses),
                    supporting_count=len(analyses),
                )
            )

        # Type consistency
        types = [a.type_name for a in analyses if not a.is_none]
        unique_types = set(types)
        if len(unique_types) == 1 and types:
            type_name = unique_types.pop()
            invariants.append(
                InferredInvariant(
                    parameter=param,
                    invariant_type="type",
                    description=f"{param_desc} is always {type_name}",
                    confidence=1.0,
                    observations_count=len(analyses),
                    supporting_count=len(types),
                )
            )

        # Numeric range
        values = [a.numeric_value for a in analyses if a.numeric_value is not None]
        if len(values) >= self.MIN_OBSERVATIONS:
            min_val = min(values)

            # Prefer stronger invariant (> 0) over weaker (>= 0)
            if min_val > 0:
                invariants.append(
                    InferredInvariant(
                        parameter=param,
                        invariant_type="range",
                        description=f"{param_desc} is always > 0",
                        confidence=1.0,
                        observations_count=len(values),
                        supporting_count=len(values),
                    )
                )
            elif min_val >= 0:
                invariants.append(
                    InferredInvariant(
                        parameter=param,
                        invariant_type="range",
                        description=f"{param_desc} is always >= 0",
                        confidence=1.0,
                        observations_count=len(values),
                        supporting_count=len(values),
                    )
                )

        # Collection non-empty
        empties = [a.collection_is_empty for a in analyses if a.collection_is_empty is not None]
        if empties and all(not e for e in empties) and len(empties) >= self.MIN_OBSERVATIONS:
            invariants.append(
                InferredInvariant(
                    parameter=param,
                    invariant_type="collection",
                    description=f"{param_desc} is never empty",
                    confidence=1.0,
                    observations_count=len(empties),
                    supporting_count=len(empties),
                )
            )

        return invariants
