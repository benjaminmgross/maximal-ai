"""Regression tests for SRPI learning retrieval instructions."""

from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text()


def assert_contains_all(path: str, *snippets: str) -> str:
    content = read(path)
    for snippet in snippets:
        assert snippet in content, f"{path} missing: {snippet}"
    return content


def test_srpi_entrypoints_include_relevant_learning_retrieval():
    """Core SRPI commands should retrieve learnings before decisions."""
    command_paths = [
        ".claude/commands/research.md",
        ".claude/commands/plan.md",
        ".claude/commands/implement.md",
        ".claude/commands/epic-oneshot.md",
    ]

    for path in command_paths:
        content = read(path)
        assert "thoughts/learnings" in content, f"{path} missing learnings lookup"
        assert "Relevant Learnings" in content, (
            f"{path} missing artifact/checklist language"
        )


def test_research_learning_retrieval_supports_local_fallback():
    """/research should search centralized or repo-local learnings."""
    assert_contains_all(
        ".claude/commands/research.md",
        "when `$THOUGHTS_PATH` or local `thoughts/` is available",
        "If the **thoughts-locator** agent is unavailable",
        "rg -n -i",
        "thoughts/learnings",
        "classify each as `applies`, `possibly applies`, or `not applicable`",
    )


def test_plan_learning_retrieval_classifies_and_converts_constraints():
    """/plan should classify learnings and convert prevention guidance."""
    assert_contains_all(
        ".claude/commands/plan.md",
        "Classify each as `applies`, `possibly applies`, or `not applicable`",
        "Prevention guidance that should become plan constraints, acceptance criteria, implementation checks, or review prompts",
        "## Relevant Learnings Applied",
        "## Learnings Converted to Constraints",
        "Concrete plan constraint, acceptance criterion, implementation check, or review prompt",
    )


def test_implement_learning_retrieval_creates_checklist_before_editing():
    """/implement should create a learning-derived checklist before edits."""
    content = assert_contains_all(
        ".claude/commands/implement.md",
        "Retrieve relevant learnings before editing",
        "Convert applicable prevention guidance into a **Relevant Learnings Checklist** before implementation",
        "Create a **Relevant Learnings Checklist** from any applicable `thoughts/learnings` results",
        "Apply the **Relevant Learnings Checklist** created during preparation",
    )

    checklist_position = content.index(
        "Create a **Relevant Learnings Checklist** from any applicable"
    )
    implementation_position = content.index("### Step 2: Phase-by-Phase Implementation")
    assert checklist_position < implementation_position


def test_epic_learning_retrieval_carries_through_all_rpi_phases():
    """/epic-oneshot should carry learnings through research, plan, implement."""
    content = assert_contains_all(
        ".claude/commands/epic-oneshot.md",
        "when `$THOUGHTS_PATH` or `thoughts/` is available",
        "Classify retrieved learnings as `applies`, `possibly applies`, or `not applicable`",
        "Include \"Relevant Learnings Applied\" section",
        "Carry forward the research document's **Relevant Learnings Applied** findings",
        "Convert applicable learnings into plan constraints, acceptance criteria, implementation checks, or review prompts",
        "Include \"Relevant Learnings Applied\" and \"Learnings Converted to Constraints\" sections",
        "Re-read the plan's **Relevant Learnings Applied** and \"Learnings Converted to Constraints\" sections before editing",
    )

    research_position = content.index("### Step 1: Research Phase")
    planning_position = content.index("### Step 2: Planning Phase")
    implementation_position = content.index("### Step 3: Implementation Phase")
    assert research_position < planning_position < implementation_position


def test_howto_documents_thoughts_locator_learning_scope():
    """User-facing docs should describe learnings as a thoughts-locator scope."""
    content = read("HOWTO.md")

    assert "thoughts-locator" in content
    assert "learnings" in content
    assert "prior research, plans, handoffs, and learnings" in content
