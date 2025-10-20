# Epic Oneshot

Executes a complete research → plan → implement workflow in a single session for well-defined tasks.

## Initial Response

When this command is invoked, respond with:
```
I'll execute a complete RPI workflow for your task. This will include research, planning, and implementation phases in sequence.

Please describe the task or feature you want to implement.
```

Then wait for the user's task description.

## Process Steps

### Step 1: Research Phase

After receiving the task:

1. **Announce phase start**:
   ```
   ## Starting Research Phase
   Investigating the codebase to understand current implementation and requirements...
   ```

2. **Execute research**:
   - **Check for coding standards** and load if present:
     - Use Bash to check if `docs/coding-standards/` exists
     - If standards exist, spawn **codebase-analyzer** to synthesize standards
   - Use codebase-locator to find relevant files
   - Use codebase-analyzer to understand implementation
   - Use codebase-pattern-finder for similar patterns
   - Use web-search-researcher if external info needed
   - Cross-reference findings with standards (if loaded)

3. **Save research document**:
   - Create `research/YYYY-MM-DD-[topic].md`
   - Include comprehensive findings
   - **Include "Coding Standards Adherence" section** if standards were loaded
   - Document all discoveries

4. **Present summary**:
   ```
   Research complete! Document saved to: research/YYYY-MM-DD-[topic].md

   Key findings:
   - [Major discovery 1]
   - [Major discovery 2]
   **Standards**: [Brief note if standards were considered]

   Moving to planning phase...
   ```

### Step 2: Planning Phase

1. **Announce phase start**:
   ```
   ## Starting Planning Phase
   Creating detailed implementation plan based on research findings...
   ```

2. **Read research document**:
   - Load the just-created research file
   - Extract key implementation points
   - **Load coding standards** (same process as /plan command):
     - Check for docs/coding-standards/ directory
     - Spawn codebase-analyzer to synthesize if present
     - Wait for synthesis before proceeding

3. **Create implementation plan**:
   - Define phases with specific changes
   - Include exact code modifications
   - **Validate all decisions against coding standards** (if loaded)
   - **Include "Coding Standards Compliance" section** in plan (if standards exist)
   - Add verification criteria
   - Document what we're NOT doing

4. **Save plan document**:
   - Create `plans/YYYY-MM-DD-[feature].md`
   - Include all phases and verification
   - Include standards references (if applicable)

5. **Get user approval**:
   ```
   Plan complete! Document saved to: plans/YYYY-MM-DD-[feature].md

   Plan overview:
   - Phase 1: [Description]
   - Phase 2: [Description]
   - Phase 3: [Description]
   **Standards compliance**: [Brief note if standards were applied]

   Ready to proceed with implementation? (yes/no)
   ```

### Step 3: Implementation Phase

If user approves:

1. **Announce phase start**:
   ```
   ## Starting Implementation Phase
   Executing the plan with verification at each step...
   ```

2. **Execute plan phases**:
   - **Load coding standards** (same process as /implement command):
     - Check for docs/coding-standards/ directory
     - Spawn codebase-analyzer to synthesize if present
     - Keep standards in context during implementation
   - Use TodoWrite to track progress
   - Implement each phase sequentially
   - **Follow coding standards** for all code changes (if loaded)
   - Run verification after each phase
   - Document any deviations (including from standards)

3. **Run final verification**:
   ```bash
   # For JavaScript/TypeScript projects:
   npm test
   npm run lint
   npm run typecheck
   npm run build

   # For Python projects:
   pytest
   python -m pytest --cov=.
   ruff check .  # or: flake8 .
   mypy .  # or: pyright
   python -m build  # if building package

   # For mixed projects, run both sets as appropriate
   ```

4. **Present completion summary**:
   ```
   ## Epic Oneshot Complete! ✅

   **Artifacts Created:**
   - Research: research/YYYY-MM-DD-[topic].md
   - Plan: plans/YYYY-MM-DD-[feature].md

   **Implementation Summary:**
   - Files modified: X
   - Tests passing: ✅
   - Verification complete: ✅
   **Coding standards**: [✅ Followed | ⚠️ N/A - no standards present]

   **Next Steps:**
   1. Review the changes
   2. Test manually if needed
   3. Commit when ready
   ```

## Important Guidelines

1. **Maintain phase separation** - Each phase builds on the previous
2. **Document everything** - Create proper research and plan documents
3. **Apply coding standards** - Load and follow standards at each phase when present
4. **Verify continuously** - Don't proceed if verification fails
5. **Track progress** - Use TodoWrite throughout
6. **Handle errors gracefully** - Stop and ask for guidance if blocked

## When to Use

Best for:
- Well-defined features or fixes
- Tasks that can complete in one session
- When you want full RPI documentation
- Exploratory implementations

Not ideal for:
- Large refactoring projects
- Tasks requiring multiple context resets
- Unclear or evolving requirements
- Multi-day implementations

## Error Handling

If any phase fails:
```
⚠️ Issue encountered during [phase] phase:
[Error description]

Options:
1. Fix and continue
2. Abort and save progress
3. Skip to next phase (not recommended)

How would you like to proceed?
```

Remember: This command chains the full RPI workflow while maintaining the quality and documentation standards of running each command separately.