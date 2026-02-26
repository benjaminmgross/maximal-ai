---
description: /observe-docstrings
---

# /observe-docstrings

Observe function behavior at runtime and interactively generate complete docstrings.

## Usage

```
/observe-docstrings [target]
```

Where `target` is:
- A Python file: `payroll_generation.py`
- A pytest path: `tests/` or `tests/test_payroll.py`
- Empty (runs pytest on entire project)

## What This Command Does

1. **Runs** the target script or tests with observation enabled
2. **Collects** function call data (arguments, returns, call graph)
3. **Infers** what it can automatically:
   - Position (structural role, call graph, I/O patterns)
   - Parameter constraints (types, ranges, nullability, collections)
4. **Prompts** you for what it can't infer:
   - Business purpose
   - Architectural context
   - Additional constraints
5. **Generates** complete NumPy-format docstrings
6. **Applies** approved docstrings to source files

## Interactive Flow

For each function in the call stack:

```
━━━ Function 1/23: calculate_salary ━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 payroll/calculations.py:45

Auto-Inferred:
├─ Role: leaf
├─ Call Graph: Called by process_payroll
├─ I/O: Pure computation
├─ Observations: 89

Parameter Constraints:
  • `employee_id` is never None (100%, 89 obs)
  • `hours` is always >= 0 (100%, 89 obs)
  • `rate` is always > 0 (100%, 89 obs)
  • Return value is always >= 0 (100%, 89 obs)

Human Input:

? Business purpose (what does this do for users/business?):
> Calculates gross salary before tax deductions

? Architectural context (why here? design rationale?) [Enter to skip]:
> Core of compensation pipeline, pure for testability

? Additional invariants the code SHOULD enforce? [Enter to skip]:
>

Generated Docstring:
╭─────────────────────────────────────────────────────────────╮
│ """                                                         │
│ Calculate gross salary before tax deductions.               │
│                                                             │
│ Position                                                    │
│ --------                                                    │
│ Leaf function. Called by process_payroll. Pure computation. │
│ Core of compensation pipeline, pure for testability.        │
│                                                             │
│ Parameters                                                  │
│ ----------                                                  │
│ employee_id : int                                           │
│     TODO: Add description. `employee_id` is never None      │
│ hours : float                                               │
│     TODO: Add description. `hours` is always >= 0           │
│ rate : float                                                │
│     TODO: Add description. `rate` is always > 0             │
│                                                             │
│ Returns                                                     │
│ -------                                                     │
│ float                                                       │
│     TODO: Add description. Return value is always >= 0      │
│ """                                                         │
╰─────────────────────────────────────────────────────────────╯

Action [a/e/s/q]: a
✓ Applied to payroll/calculations.py
```

## Workflow

### Step 1: Determine Target Type

Analyze the target argument:
- If it's a `.py` file → use `rdf observe`
- If it's a directory or test path → use `pytest --rdf-observe`
- If empty → run `pytest --rdf-observe` on the whole project

### Step 2: Run Observation

For a Python script:
```bash
rdf observe {target} --entrypoint main
```

For tests:
```bash
pytest --rdf-observe {target} --rdf-observe-output /tmp/rdf-obs.json
```

### Step 3: Interactive Generation

The `rdf observe` command will:
1. Run the script/tests with instrumentation
2. Show auto-inferred data for each function
3. Prompt for human context
4. Generate complete docstrings
5. Apply to source files (with backup)

## Options

When running `rdf observe`:

| Flag | Description |
|------|-------------|
| `--non-interactive` | Skip prompts, auto-inferred only |
| `--dry-run` | Preview without applying changes |
| `--filter <pattern>` | Only process matching functions |
| `-e, --entrypoint` | Function to call (default: main) |

## Example Commands

```bash
# Observe a script
rdf observe src/payroll/main.py --entrypoint process_all

# Observe with filtering
rdf observe src/app.py --filter "calculate_*"

# Non-interactive mode for CI
rdf observe src/app.py --non-interactive --dry-run

# Run tests with observation
pytest --rdf-observe tests/unit/ --rdf-observe-output observations.json
```

## Requirements

- Python 3.10+
- `rdf` package installed (`pip install -e .`)
- Functions must be decorated with `@observe` OR run via pytest plugin

## How to Use @observe Decorator

Add the decorator to functions you want to document:

```python
from rdf.observe import observe

@observe
def calculate_salary(employee_id: int, hours: float, rate: float) -> float:
    return hours * rate

@observe
def process_payroll(employees: list[dict]) -> list[dict]:
    results = []
    for emp in employees:
        salary = calculate_salary(emp["id"], emp["hours"], emp["rate"])
        results.append({"id": emp["id"], "salary": salary})
    return results
```

Then run:
```bash
rdf observe your_script.py --entrypoint main
```

## Limitations

- Only observes executed code paths
- Cannot infer business meaning automatically
- Test coverage affects quality of inference
- Requires functions to be called during observation
