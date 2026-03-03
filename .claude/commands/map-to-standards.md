---
description: Map code changes to all Minty Living coding standards with structured scorecards
---

# Map Code Changes to Coding Standards

Map code changes against the **complete set** of Minty Living coding standards, producing a structured scorecard with specific findings and recommendations.

## Input

$ARGUMENTS

## Pre-computed Context

### Current Branch
!`git branch --show-current 2>/dev/null || echo "detached HEAD"`

### Recent Commits (last 15)
!`git log --oneline -15 2>/dev/null || echo "No commits"`

### Base Branch
!`git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main"`

## Instructions

### Step 1: Determine Commit Range

Parse `$ARGUMENTS` to determine what to evaluate:

| Input | Interpretation |
|-------|---------------|
| PR number (e.g., `#123` or `123`) | Fetch PR diff via `gh pr diff 123` |
| Commit range (e.g., `abc123..def456`) | Use as-is with `git diff` and `git log` |
| Single commit (e.g., `abc123`) | Evaluate that commit: `git diff abc123~1..abc123` |
| Branch name (e.g., `feature/foo`) | Compare to base branch |
| Nothing / empty | Use the most recent pull (last merge or batch of non-merge commits on current branch) |

### Step 2: Gather the Diff and Commit History

1. **Get the full diff** for the determined range
2. **Get the commit log** with messages for the range
3. **List all changed files** with their paths
4. **Read each changed file fully** — do not rely solely on the diff; you need full file context to evaluate standards compliance

### Step 3: Load Coding Standards

Load the Minty Living coding standards from these locations (check both; prefer `$MINTY_DOCS_PATH` if set):

**Primary**: `$MINTY_DOCS_PATH/cross-cutting/coding-standards/` (environment variable)
**Fallback**: `~/dev/minty-docs/cross-cutting/coding-standards/`

Load these standard documents:

1. `python-docstrings.md` — Docstring Engineering Standard
2. `python-code-style-guide.md` — Code Style Guide
3. `python-visual-formatting.md` — Visual Formatting
4. `functional-first-and-class-usage.md` — Functional-First & Class Usage
5. `python-environment-configuration.md` — Environment Configuration
6. `client-code.md` — Client Code Standards
7. `array-based-implementation.md` — Array-Based Implementation (Vectorization)
8. `gitignore-ai-files.md` — Gitignore AI Files

Also load testing standards from:
- `$MINTY_DOCS_PATH/testing-framework/` or `~/dev/minty-docs/testing-framework/`
- Specifically: `testing-evaluation-rubric.md` if it exists

**If standards cannot be found**, tell the user and ask for the path. Do not proceed without them — the evaluation is meaningless without the reference documents.

### Step 4: Evaluate Each Standard

For **each** of the 9 standards below, evaluate the changes systematically. For standards that don't apply to the changes (e.g., no array operations → Array-Based Implementation is N/A), mark as **N/A** with a brief explanation.

---

#### Standard 1: Testing Standards

- Are there **new tests** for new/changed behavior?
- Are **existing tests updated** to reflect changes?
- If Hypothesis strategies exist, are they used for property-based testing where appropriate?
- Are test markers (`@pytest.mark.slow`, `@pytest.mark.integration`) applied correctly?
- Does coverage remain above the configured gate?

**Score 0-10** with specific gaps identified.

#### Standard 2: Python Docstring Engineering Standard

- Do **new functions** have NumPy-style docstrings?
- Are docstrings required per the standard? (public, cross-module, business-logic, system-flow functions)
- Do docstrings describe **behavior, semantics, side effects** — not just repeat the signature?
- Are **Raises** sections included where exceptions are thrown?
- Were **existing docstrings updated** when function behavior changed?
- Are there anti-pattern docstrings (repeating type info already in annotations)?

**Score 0-10** with specific functions cited.

#### Standard 3: Code Style Guide

- **Type annotations**: All parameters and return types annotated? Modern syntax (`X | None`, not `Optional[X]`)?
- **Keyword-only arguments**: `*` used to force keyword-only on custom functions?
- **Package management**: `uv` used (not pip, poetry, conda)?
- **Naming conventions**: snake_case functions, PascalCase classes?

**Score 0-10** per sub-area.

#### Standard 4: Visual Formatting

- **Whitespace**: Two blank lines between top-level definitions? Visual paragraphs within functions?
- **Import organization**: stdlib → third-party → local, with blank lines between groups?
- **Exception handling**: Specific exception types (not bare `except Exception`)? Compact formatting?
- **Line length**: Within 88-100 char soft limit?

**Score 0-10**.

#### Standard 5: Functional-First & Class Usage

- Are new abstractions **functions** (not unnecessary classes)?
- Are classes used only for **data shape description** or complex state management?
- Are dependencies **passed as arguments**, not via instance state?
- No service classes wrapping a single function?

**Score 0-10**.

#### Standard 6: Environment Configuration

- No `sys.path.append` or `sys.path` manipulation?
- No `os.environ` modification from code?
- No hardcoded paths or configuration values?
- Configuration comes from environment / `.env` files?

**Score 0-10**.

#### Standard 7: Client Code Standards

- New external API integrations follow SDK → Generated → Handwritten hierarchy?
- Existing integration patterns reused?
- Mark **N/A** if no new client/integration code.

**Score 0-10 or N/A**.

#### Standard 8: Array-Based Implementation (Vectorization)

- No Python `for` loops for element-wise operations on arrays/DataFrames?
- Vectorized operations used where applicable?
- Mark **N/A** if no array/DataFrame operations.

**Score 0-10 or N/A**.

#### Standard 9: Gitignore AI Files

- No AI assistant files (`.claude/`, `CLAUDE.md`, `thoughts/`, `.cursor/`) committed?
- No `.env` or credential files committed?

**Pass/Fail**.

---

### Step 5: Identify Specific Issues

Categorize all findings into:

#### Critical (Must Fix)
- Security vulnerabilities
- Missing tests for behavioral changes
- Contract/API changes without documentation
- Exceptions raised in wrong context (e.g., HTTPException in background tasks)

#### High Priority
- Missing docstrings on non-trivial new functions
- Missing regression tests for type migrations
- Bare `except Exception` catches
- Hardcoded configuration

#### Medium Priority
- Pre-existing gaps made worse by the changes
- Missing property-based tests where strategies exist
- Logger configuration from code

#### Credit (What Was Done Well)
- Always include what the developer did correctly
- Acknowledge smart deviations from standards
- Note areas of strong compliance

### Step 6: Write the Evaluation

Write the evaluation to a file following this structure:

**Output path**: `thoughts/reviews/YYYY.MM.DD-{username}-{description}-evaluation.md`

Detect username from `.claude/config.yaml` or fall back to git config.

```markdown
---
title: "Developer Pull Evaluation: [brief description]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [evaluation, coding-standards, testing-standards, docstring-standards, code-review]
status: complete
version: 1
---

# Developer Pull Evaluation Against All Coding Standards

**Date**: YYYY-MM-DD
**Repository**: [repo name]
**Commit Range**: [range evaluated]
**Branch**: [branch name]

## Summary

[2-3 sentence executive summary. Overall grade. Key strengths and weaknesses.]

**Overall Grade: [A through F]** — [one-line justification]

---

## Commits Under Review

| Commit | Message | Category |
|--------|---------|----------|
| ... | ... | ... |

---

## Standard 1: Testing Standards
[Detailed evaluation with scorecard table]

## Standard 2: Python Docstring Engineering Standard
[Detailed evaluation with scorecard table]

## Standard 3: Code Style Guide
[Detailed evaluation with scorecard table]

## Standard 4: Visual Formatting
[Detailed evaluation with scorecard table]

## Standard 5: Functional-First & Class Usage
[Detailed evaluation with scorecard table]

## Standard 6: Environment Configuration
[Detailed evaluation with scorecard table]

## Standard 7: Client Code Standards
[Evaluation or N/A]

## Standard 8: Array-Based Implementation
[Evaluation or N/A]

## Standard 9: Gitignore AI Files
[Pass/Fail]

---

## Overall Assessment

[ASCII scorecard table showing all 9 standards with grades and key findings]

---

## Specific Issues Requiring Attention

### Critical (Must Fix)
[Numbered list with file:line references]

### High Priority
[Numbered list with file:line references]

### Medium Priority
[Numbered list with file:line references]

---

## What the Developer Did Well
[Numbered list — always give credit]

---

## Recommendations by Priority

### Immediate (Before Next PR)
| # | Action | Standard Violated | File |
|---|--------|------------------|------|

### Next Sprint
| # | Action | Standard Violated | File |
|---|--------|------------------|------|
```

### Step 7: Present Results

After writing the file:

1. Tell the user where the evaluation was saved
2. Show the **Overall Assessment** scorecard table
3. Highlight the **Critical** issues (if any)
4. Mention the **Credit** items — always lead with what was done well before the gaps
