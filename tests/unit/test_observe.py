"""Tests for the observe module."""

from datetime import datetime, timezone

import pytest

from rdf.observe import clear_observations, get_observations, observe
from rdf.observe.analyzer import InferenceEngine
from rdf.observe.models import (
    CallObservation,
    FunctionProfile,
    GeneratedDocstring,
    HumanInput,
    InferredInvariant,
    InferredPosition,
    StructuralRole,
    ValueAnalysis,
)


@pytest.fixture(autouse=True)
def clean_observations():
    """Clear observations before and after each test."""
    clear_observations()
    yield
    clear_observations()


class TestObserveDecorator:
    """Tests for the @observe decorator."""

    def test_decorator_preserves_function_behavior(self):
        """Decorated functions should behave identically."""

        @observe
        def add(a: int, b: int) -> int:
            return a + b

        assert add(1, 2) == 3
        assert add(10, 20) == 30

    def test_decorator_records_profile(self):
        """Decorator should record function profiles."""

        @observe
        def multiply(x: int, y: int) -> int:
            return x * y

        multiply(3, 4)

        profiles = get_observations()
        assert len(profiles) == 1

        qualname = list(profiles.keys())[0]
        assert "multiply" in qualname

        profile = profiles[qualname]
        assert profile.call_count == 1
        assert len(profile.observations) == 1

    def test_multiple_calls_recorded(self):
        """Multiple calls should be recorded."""

        @observe
        def square(x: int) -> int:
            return x * x

        for i in range(5):
            square(i)

        profiles = get_observations()
        profile = list(profiles.values())[0]
        assert profile.call_count == 5
        assert len(profile.observations) == 5

    def test_numeric_value_analysis(self):
        """Numeric values should be analyzed correctly."""

        @observe
        def process(value: float) -> float:
            return value * 2

        process(42.5)

        profiles = get_observations()
        profile = list(profiles.values())[0]
        obs = profile.observations[0]

        # Check argument analysis
        args_dict = dict(obs.arguments)
        assert args_dict["value"].numeric_value == 42.5

        # Check return value analysis
        assert obs.return_value.numeric_value == 85.0

    def test_none_detection(self):
        """None values should be detected."""

        @observe
        def maybe_none(x: int | None) -> int | None:
            return x

        maybe_none(None)
        maybe_none(5)

        profiles = get_observations()
        profile = list(profiles.values())[0]

        args_0 = dict(profile.observations[0].arguments)
        args_1 = dict(profile.observations[1].arguments)

        assert args_0["x"].is_none is True
        assert args_1["x"].is_none is False

    def test_collection_analysis(self):
        """Collections should be analyzed for length and emptiness."""

        @observe
        def process_list(items: list[str]) -> int:
            return len(items)

        process_list(["a", "b", "c"])
        process_list([])

        profiles = get_observations()
        profile = list(profiles.values())[0]

        args_0 = dict(profile.observations[0].arguments)
        args_1 = dict(profile.observations[1].arguments)

        assert args_0["items"].collection_length == 3
        assert args_0["items"].collection_is_empty is False
        assert args_1["items"].collection_is_empty is True

    def test_exception_handling(self):
        """Exceptions should be recorded."""

        @observe
        def raise_error(x: int) -> int:
            if x < 0:
                raise ValueError("x must be positive")
            return x

        with pytest.raises(ValueError):
            raise_error(-1)

        profiles = get_observations()
        profile = list(profiles.values())[0]
        obs = profile.observations[0]

        assert obs.raised_exception == "ValueError"


class TestInferenceEngine:
    """Tests for the InferenceEngine."""

    def _make_observation(
        self,
        qualname: str,
        args: dict[str, ValueAnalysis],
        return_val: ValueAnalysis,
    ) -> CallObservation:
        """Helper to create observations."""
        return CallObservation(
            function_name=qualname.split(".")[-1],
            module_name="test",
            qualname=qualname,
            file_path="test.py",
            line_number=1,
            timestamp=datetime.now(timezone.utc),
            arguments=tuple(args.items()),
            return_value=return_val,
        )

    def _make_profile(self, qualname: str, observations: list[CallObservation]) -> FunctionProfile:
        """Helper to create profiles."""
        return FunctionProfile(
            qualname=qualname,
            module_name="test",
            file_path="test.py",
            line_number=1,
            observations=observations,
            call_count=len(observations),
        )

    def test_infer_nullability_never_none(self):
        """Should infer 'never None' invariant."""
        observations = [
            self._make_observation(
                "test.process",
                {"x": ValueAnalysis(type_name="int", is_none=False, numeric_value=float(i))},
                ValueAnalysis(type_name="int", is_none=False, numeric_value=float(i * 2)),
            )
            for i in range(10)
        ]

        profile = self._make_profile("test.process", observations)
        engine = InferenceEngine({"test.process": profile})
        results = engine.infer_all()

        _, invariants = results["test.process"]
        nullability = [c for c in invariants if c.invariant_type == "nullability"]
        assert any(c.parameter == "x" and "never None" in c.description for c in nullability)

    def test_infer_numeric_range_positive(self):
        """Should infer 'always > 0' invariant."""
        observations = [
            self._make_observation(
                "test.calc",
                {
                    "value": ValueAnalysis(
                        type_name="float", is_none=False, numeric_value=float(i + 1)
                    )
                },
                ValueAnalysis(type_name="float", is_none=False, numeric_value=float((i + 1) * 2)),
            )
            for i in range(10)
        ]

        profile = self._make_profile("test.calc", observations)
        engine = InferenceEngine({"test.calc": profile})
        results = engine.infer_all()

        _, invariants = results["test.calc"]
        range_inv = [c for c in invariants if c.invariant_type == "range"]
        assert any("always > 0" in c.description for c in range_inv)

    def test_infer_collection_never_empty(self):
        """Should infer 'never empty' invariant."""
        observations = [
            self._make_observation(
                "test.process_list",
                {
                    "items": ValueAnalysis(
                        type_name="list",
                        is_none=False,
                        collection_length=i + 1,
                        collection_is_empty=False,
                    )
                },
                ValueAnalysis(type_name="int", is_none=False, numeric_value=float(i + 1)),
            )
            for i in range(10)
        ]

        profile = self._make_profile("test.process_list", observations)
        engine = InferenceEngine({"test.process_list": profile})
        results = engine.infer_all()

        _, invariants = results["test.process_list"]
        collection_inv = [c for c in invariants if c.invariant_type == "collection"]
        assert any("never empty" in c.description for c in collection_inv)

    def test_minimum_observations_required(self):
        """Should not infer with too few observations."""
        # Only 3 observations - below threshold
        observations = [
            self._make_observation(
                "test.func",
                {"x": ValueAnalysis(type_name="int", is_none=False, numeric_value=float(i))},
                ValueAnalysis(type_name="int", is_none=False, numeric_value=float(i)),
            )
            for i in range(3)
        ]

        profile = self._make_profile("test.func", observations)
        engine = InferenceEngine({"test.func": profile})
        results = engine.infer_all()

        _, invariants = results["test.func"]
        # Should return empty due to insufficient observations
        assert len(invariants) == 0

    def test_infer_position_entry_point(self):
        """Should infer entry point role."""
        profile = FunctionProfile(
            qualname="test.main",
            module_name="test",
            file_path="test.py",
            line_number=1,
            callers=set(),  # No callers = entry point
            callees={"test.helper1", "test.helper2"},
        )

        engine = InferenceEngine({"test.main": profile})
        results = engine.infer_all()

        position, _ = results["test.main"]
        assert position.structural_role == StructuralRole.ENTRY_POINT

    def test_infer_position_leaf(self):
        """Should infer leaf function role."""
        profile = FunctionProfile(
            qualname="test.helper",
            module_name="test",
            file_path="test.py",
            line_number=1,
            callers={"test.main"},
            callees=set(),  # No callees = leaf
        )

        engine = InferenceEngine({"test.helper": profile})
        results = engine.infer_all()

        position, _ = results["test.helper"]
        assert position.structural_role == StructuralRole.LEAF


class TestGeneratedDocstring:
    """Tests for GeneratedDocstring rendering."""

    def test_render_basic_docstring(self):
        """Should render a basic docstring."""
        docstring = GeneratedDocstring(
            qualname="test.func",
            file_path="test.py",
            line_number=1,
            inferred_position=InferredPosition(
                structural_role=StructuralRole.LEAF,
                call_graph_description="Called by main",
                io_description=None,
                depth_description=None,
            ),
            inferred_invariants=[
                InferredInvariant(
                    parameter="x",
                    invariant_type="nullability",
                    description="`x` is never None",
                    confidence=1.0,
                    observations_count=10,
                    supporting_count=10,
                ),
            ],
            inferred_params={"x": ValueAnalysis(type_name="int", is_none=False)},
            inferred_return=ValueAnalysis(type_name="int", is_none=False),
            human_input=HumanInput(
                business_purpose="Calculate the result.",
                architectural_context="Core calculation module.",
            ),
        )

        rendered = docstring.render()

        assert "Calculate the result." in rendered
        assert "Position" in rendered
        assert "Leaf function" in rendered
        assert "Invariants" in rendered
        assert "`x` is never None" in rendered
        assert "Parameters" in rendered
        assert "Returns" in rendered

    def test_render_without_human_input(self):
        """Should render even without human input."""
        docstring = GeneratedDocstring(
            qualname="test.func",
            file_path="test.py",
            line_number=1,
            inferred_position=InferredPosition(
                structural_role=StructuralRole.UNKNOWN,
                call_graph_description="",
                io_description=None,
                depth_description=None,
            ),
            inferred_invariants=[],
            inferred_params={},
            inferred_return=None,
            human_input=HumanInput(),
        )

        rendered = docstring.render()

        assert "Position" in rendered
        assert "TODO: Add position description" in rendered
