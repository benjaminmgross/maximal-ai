---
description: Quick verification - run tests, lint, and typecheck with pre-computed output
---

# Verify

Quick health check of the codebase. Use this to verify everything passes before committing.

## Pre-computed Verification Results

### Project Type
!`if [ -f "package.json" ]; then echo "javascript/typescript"; elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then echo "python"; else echo "unknown"; fi`

### Test Results (summary)
!`(npm test 2>&1 || pytest -q 2>&1 || python -m pytest -q 2>&1) 2>/dev/null | tail -20 || echo "Tests: not configured"`

### Type Check Results
!`(npm run typecheck 2>&1 || npx tsc --noEmit 2>&1 || mypy . --ignore-missing-imports 2>&1 || pyright . 2>&1) 2>/dev/null | tail -15 || echo "Types: not configured"`

### Lint Results
!`(npm run lint 2>&1 || npx eslint . --max-warnings=0 2>&1 || ruff check . 2>&1 || flake8 . 2>&1) 2>/dev/null | tail -15 || echo "Lint: not configured"`

### Build Results
!`(npm run build 2>&1 || python -m build 2>&1 || go build ./... 2>&1) 2>/dev/null | tail -10 || echo "Build: not configured"`

### Git Status
!`git status --short 2>/dev/null | head -10`

## Summary Report

Based on the verification results above, provide a concise status report:

| Check | Status | Notes |
|-------|--------|-------|
| Tests | PASS/FAIL/N/A | X passing, Y failing |
| Types | PASS/FAIL/N/A | X errors found |
| Lint | PASS/FAIL/N/A | X issues found |
| Build | PASS/FAIL/N/A | Success/Failed |

### Overall Status
- **HEALTHY**: All checks pass - safe to commit
- **NEEDS ATTENTION**: Some checks fail - fix before committing
- **PARTIAL**: Some checks not configured - verify manually

## If Checks Fail

List the specific issues that need attention:

1. **Test Failures**: [list failing tests]
2. **Type Errors**: [list type issues with file:line]
3. **Lint Issues**: [list lint errors with file:line]
4. **Build Errors**: [list build issues]

## Quick Fix Commands

### JavaScript/TypeScript
```bash
npm run lint -- --fix     # Auto-fix lint issues
npx prettier --write .    # Format code
```

### Python
```bash
ruff check . --fix        # Auto-fix lint issues
ruff format .             # Format code
isort .                   # Sort imports
```

## When to Use This Command

- Before committing changes
- After making significant edits
- Before creating a PR
- When CI fails and you need to debug locally
- As a sanity check during development

This command is read-only and doesn't make any changes. Use `/test-and-fix` if you want to automatically fix issues.
