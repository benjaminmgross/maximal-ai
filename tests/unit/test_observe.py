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


class TestSerialization:
    """Tests for serialization/deserialization."""

    def test_value_analysis_round_trip(self):
        """ValueAnalysis should survive serialization round-trip."""
        original = ValueAnalysis(
            type_name="list",
            is_none=False,
            collection_length=5,
            collection_is_empty=False,
            dict_keys=("a", "b"),
            string_patterns=("looks_like_path",),
        )

        data = original.to_dict()
        restored = ValueAnalysis.from_dict(data)

        assert restored.type_name == original.type_name
        assert restored.is_none == original.is_none
        assert restored.collection_length == original.collection_length
        assert restored.collection_is_empty == original.collection_is_empty
        assert restored.dict_keys == original.dict_keys
        assert restored.string_patterns == original.string_patterns

    def test_call_observation_round_trip(self):
        """CallObservation should survive serialization round-trip."""
        original = CallObservation(
            function_name="test_func",
            module_name="mymodule",
            qualname="mymodule.test_func",
            file_path="/path/to/file.py",
            line_number=42,
            timestamp=datetime.now(timezone.utc),
            arguments=(
                ("x", ValueAnalysis(type_name="int", is_none=False, numeric_value=10.0)),
                ("y", ValueAnalysis(type_name="str", is_none=False, string_length=5)),
            ),
            return_value=ValueAnalysis(type_name="bool", is_none=False),
            raised_exception=None,
            caller="mymodule.main",
            call_depth=2,
        )

        data = original.to_dict()
        restored = CallObservation.from_dict(data)

        assert restored.function_name == original.function_name
        assert restored.qualname == original.qualname
        assert restored.caller == original.caller
        assert restored.call_depth == original.call_depth
        assert len(restored.arguments) == 2
        assert restored.arguments[0][0] == "x"
        assert restored.arguments[0][1].numeric_value == 10.0

    def test_function_profile_round_trip(self):
        """FunctionProfile should survive serialization round-trip with observations."""
        observation = CallObservation(
            function_name="process",
            module_name="test",
            qualname="test.process",
            file_path="test.py",
            line_number=10,
            timestamp=datetime.now(timezone.utc),
            arguments=(("x", ValueAnalysis(type_name="int", is_none=False)),),
            return_value=ValueAnalysis(type_name="int", is_none=False),
        )

        original = FunctionProfile(
            qualname="test.process",
            module_name="test",
            file_path="test.py",
            line_number=10,
            callers={"test.main"},
            callees={"test.helper"},
            call_count=1,
            observations=[observation],
        )

        data = original.to_dict()
        restored = FunctionProfile.from_dict(data)

        assert restored.qualname == original.qualname
        assert restored.callers == original.callers
        assert restored.callees == original.callees
        assert len(restored.observations) == 1
        assert restored.observations[0].function_name == "process"


class TestInvariantInference:
    """Tests for invariant inference edge cases."""

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

    def test_no_redundant_range_invariants(self):
        """Should not emit both >= 0 and > 0 for same parameter."""
        # All values > 0, so we should get "> 0" but NOT ">= 0"
        observations = [
            self._make_observation(
                "test.calc",
                {
                    "value": ValueAnalysis(
                        type_name="float", is_none=False, numeric_value=float(i + 1)
                    )
                },
                ValueAnalysis(type_name="float", is_none=False),
            )
            for i in range(10)
        ]

        profile = self._make_profile("test.calc", observations)
        engine = InferenceEngine({"test.calc": profile})
        results = engine.infer_all()

        _, invariants = results["test.calc"]
        range_inv = [c for c in invariants if c.invariant_type == "range"]

        # Should have exactly one range invariant for this parameter
        value_range_inv = [c for c in range_inv if c.parameter == "value"]
        assert len(value_range_inv) == 1
        assert "> 0" in value_range_inv[0].description

    def test_gte_zero_when_zero_included(self):
        """Should emit >= 0 when values include zero."""
        # Values include 0, so we should get ">= 0" but NOT "> 0"
        observations = [
            self._make_observation(
                "test.calc",
                {"value": ValueAnalysis(type_name="float", is_none=False, numeric_value=float(i))},
                ValueAnalysis(type_name="float", is_none=False),
            )
            for i in range(10)  # 0, 1, 2, ... 9
        ]

        profile = self._make_profile("test.calc", observations)
        engine = InferenceEngine({"test.calc": profile})
        results = engine.infer_all()

        _, invariants = results["test.calc"]
        range_inv = [c for c in invariants if c.invariant_type == "range"]

        value_range_inv = [c for c in range_inv if c.parameter == "value"]
        assert len(value_range_inv) == 1
        assert ">= 0" in value_range_inv[0].description
        assert "> 0" not in value_range_inv[0].description


class TestWriterVerification:
    """Tests for writer verification logic."""

    def test_verify_function_line_valid(self):
        """Should verify valid function line."""
        from rdf.observe.writer import _verify_function_line

        lines = [
            "# comment\n",
            "def my_function(x, y):\n",
            "    return x + y\n",
        ]

        doc = GeneratedDocstring(
            qualname="module.my_function",
            file_path="test.py",
            line_number=2,  # 1-indexed
            inferred_position=InferredPosition(
                structural_role=StructuralRole.LEAF,
                call_graph_description="",
                io_description=None,
                depth_description=None,
            ),
            inferred_invariants=[],
            inferred_params={},
            inferred_return=None,
            human_input=HumanInput(),
        )

        assert _verify_function_line(lines, doc) is True

    def test_verify_function_line_stale(self):
        """Should detect stale line number."""
        from rdf.observe.writer import _verify_function_line

        lines = [
            "# comment\n",
            "# another comment\n",  # No longer a function def
            "def my_function(x, y):\n",
        ]

        doc = GeneratedDocstring(
            qualname="module.my_function",
            file_path="test.py",
            line_number=2,  # Now points to a comment
            inferred_position=InferredPosition(
                structural_role=StructuralRole.LEAF,
                call_graph_description="",
                io_description=None,
                depth_description=None,
            ),
            inferred_invariants=[],
            inferred_params={},
            inferred_return=None,
            human_input=HumanInput(),
        )

        assert _verify_function_line(lines, doc) is False

    def test_verify_async_function(self):
        """Should verify async function definitions."""
        from rdf.observe.writer import _verify_function_line

        lines = [
            "async def fetch_data(url):\n",
            "    pass\n",
        ]

        doc = GeneratedDocstring(
            qualname="module.fetch_data",
            file_path="test.py",
            line_number=1,
            inferred_position=InferredPosition(
                structural_role=StructuralRole.LEAF,
                call_graph_description="",
                io_description=None,
                depth_description=None,
            ),
            inferred_invariants=[],
            inferred_params={},
            inferred_return=None,
            human_input=HumanInput(),
        )

        assert _verify_function_line(lines, doc) is True

    def test_verify_wrong_function_name(self):
        """Should detect wrong function name at line."""
        from rdf.observe.writer import _verify_function_line

        lines = [
            "def other_function(x):\n",
            "    pass\n",
        ]

        doc = GeneratedDocstring(
            qualname="module.expected_function",
            file_path="test.py",
            line_number=1,
            inferred_position=InferredPosition(
                structural_role=StructuralRole.LEAF,
                call_graph_description="",
                io_description=None,
                depth_description=None,
            ),
            inferred_invariants=[],
            inferred_params={},
            inferred_return=None,
            human_input=HumanInput(),
        )

        assert _verify_function_line(lines, doc) is False
