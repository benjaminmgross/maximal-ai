---
description: Run tests and fix any failures with pre-computed test output
---

# Test and Fix

## Pre-computed Test Results

### Project Type
!`if [ -f "package.json" ]; then echo "javascript/typescript"; elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then echo "python"; elif [ -f "go.mod" ]; then echo "go"; elif [ -f "Cargo.toml" ]; then echo "rust"; else echo "unknown"; fi`

### Test Output (last 100 lines)
!`(npm test 2>&1 || pytest -v 2>&1 || python -m pytest -v 2>&1 || go test ./... 2>&1 || cargo test 2>&1) 2>/dev/null | tail -100 || echo "Could not run tests - check test configuration"`

### Type Check Errors (first 50 lines)
!`(npm run typecheck 2>&1 || npx tsc --noEmit 2>&1 || mypy . 2>&1 || pyright . 2>&1) 2>/dev/null | head -50 || echo "No type check configured"`

### Lint Errors (first 50 lines)
!`(npm run lint 2>&1 || npx eslint . 2>&1 || ruff check . 2>&1 || flake8 . 2>&1) 2>/dev/null | head -50 || echo "No lint check configured"`

### Current Git Status
!`git status --short 2>/dev/null | head -20`

## Instructions

Based on the test results above:

### If All Tests Pass
- Report success with a summary
- Note any warnings or skipped tests
- Mention test count and coverage if available

### If Tests Fail
1. **Analyze the failures**:
   - Read the error messages and stack traces
   - Identify which test file(s) and test case(s) failed
   - Understand what the test expects vs what it received

2. **Identify root cause**:
   - Is it a logic error in the implementation?
   - Is it a missing import or dependency?
   - Is it a type mismatch?
   - Is the test itself incorrect?

3. **Fix the implementation** (preferred):
   - Fix the code to make tests pass
   - Only fix the test if the test itself is wrong

4. **Re-run tests**:
   - After fixing, run tests again to verify
   - Continue until all tests pass

### If Type Errors Exist
- Fix type errors FIRST (they often cause test failures)
- Common fixes: add type annotations, fix null checks, update interfaces
- Re-run type check after fixes

### If Lint Errors Exist
- Fix lint errors after tests and types pass
- Auto-fix when possible: `npm run lint -- --fix` or `ruff check . --fix`
- Manual fix for complex issues

## Iteration Loop

```
while (tests fail OR types fail OR lint fails):
    if type_errors:
        fix_type_errors()
        continue
    if test_failures:
        analyze_and_fix()
        continue
    if lint_errors:
        fix_lint_errors()
        continue
```

## Success Criteria

Only report complete when ALL of these pass:
- [ ] All tests passing (exit code 0)
- [ ] No type errors
- [ ] No lint errors (or only warnings)

## Common Test Frameworks

### JavaScript/TypeScript
```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- path/to/test   # Specific test
npm test -- -t "test name" # By name
```

### Python
```bash
pytest                      # Run all tests
pytest -v                   # Verbose
pytest path/to/test.py     # Specific file
pytest -k "test_name"      # By name pattern
pytest -x                   # Stop on first failure
```

### Go
```bash
go test ./...              # All tests
go test -v ./...           # Verbose
go test -run TestName      # Specific test
```

## Debugging Tips

- If a test fails intermittently, it might be a race condition
- If tests pass locally but fail in CI, check environment differences
- If you can't understand a failure, read the test file to understand intent
- Use `console.log`/`print` statements temporarily to debug
