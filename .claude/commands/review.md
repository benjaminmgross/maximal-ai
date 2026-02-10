---
description: Review code changes with pre-computed diff and context
---

# Code Review

Review the current branch's changes against the base branch.

## Pre-computed Review Context

### Current Branch
!`git branch --show-current 2>/dev/null || echo "detached HEAD"`

### Base Branch
!`git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main"`

### Commits Ahead of origin/main
!`git rev-list --count origin/main..HEAD 2>/dev/null || git rev-list --count origin/master..HEAD 2>/dev/null || echo "unknown"`

### Files Changed (vs origin/main)
!`git diff --name-only origin/main...HEAD 2>/dev/null | head -30 || git diff --name-only HEAD~10 HEAD 2>/dev/null | head -30 || echo "No changes detected"`

### Diff Statistics
!`git diff --stat origin/main...HEAD 2>/dev/null | tail -15 || git diff --stat HEAD~10 HEAD 2>/dev/null | tail -15 || echo "No diff stats"`

### Commits to Review
!`git log --oneline origin/main..HEAD 2>/dev/null | head -20 || git log --oneline -10 2>/dev/null || echo "No commits"`

### Full Diff (first 300 lines)
!`git diff origin/main...HEAD 2>/dev/null | head -300 || git diff HEAD~10 HEAD 2>/dev/null | head -300 || echo "No diff"`

## Review Checklist

Based on the diff context above, analyze the changes:

### 1. High-Level Review
- [ ] What is the purpose of these changes?
- [ ] Are the changes cohesive (single concern) or should they be split?
- [ ] Do the commit messages accurately describe the changes?
- [ ] Is the scope appropriate (not too large, not too small)?

### 2. Code Quality
- [ ] Are there any obvious bugs or logic errors?
- [ ] Is error handling appropriate?
- [ ] Are edge cases considered?
- [ ] Is there unnecessary complexity that could be simplified?
- [ ] Are there any code smells (long functions, deep nesting, magic numbers)?

### 3. Security Review
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Input validation for user-provided data
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities (if web frontend)
- [ ] Proper authentication/authorization checks

### 4. Testing
- [ ] Are there tests for new functionality?
- [ ] Do existing tests still pass?
- [ ] Are edge cases tested?
- [ ] Is test coverage adequate?

### 5. Maintainability
- [ ] Is the code self-documenting?
- [ ] Are variable/function names clear?
- [ ] Are there any TODO/FIXME comments that should be addressed?
- [ ] Does the code follow project conventions?

### 6. Performance
- [ ] Any obvious performance issues (N+1 queries, unnecessary loops)?
- [ ] Are there any memory leaks?
- [ ] Is caching used appropriately?

### 7. Operational Resilience
- [ ] All external HTTP/API calls have explicit `timeout` parameters
- [ ] External service calls wrapped in try/except with specific exception types
- [ ] Retry logic for idempotent operations to transient-failure-prone services
- [ ] No unbounded loops or polls without timeout caps
- [ ] Exception handlers include `exc_info=True` (or use `logger.exception()`)
- [ ] Graceful degradation when external dependencies are unavailable

### 8. Cross-File Pattern Tracing
- [ ] When an issue is found in one file, search the entire diff for the same pattern
- [ ] All `requests.*` calls without `timeout=` identified
- [ ] All `datetime.now()` without timezone identified
- [ ] All hardcoded URLs, IDs, ARNs, or resource identifiers identified
- [ ] All exception handlers without `exc_info=True` identified

## Review Output Format

Provide feedback in this structure:

```markdown
## Review Summary

**Overall**: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION

**Strengths**:
- [What was done well]

**Issues Found**:

### Critical (Must Fix)

**Always Critical:**
- Security vulnerabilities (injection, auth bypass, credential exposure)
- Hardcoded infrastructure identifiers (AWS account IDs, resource ARNs, API keys)
- Breaking API contracts (response shape changes, removed fields)
- Missing authentication or authorization on external calls
- Missing error handling that would crash the service in production
- Missing timeouts on external HTTP/API calls (can hang indefinitely)
- Data loss or corruption risks

1. **[Issue]** - `file.ts:42`
   - Problem: [description]
   - Suggestion: [how to fix]

### Suggestions (Nice to Have)

**Always Suggestion:** Code style/naming, minor inconsistencies, dead code, missing docs/type hints, performance optimizations without immediate impact.

1. **[Suggestion]** - `file.ts:100`
   - [description and recommendation]

### Questions
1. [Clarifying question about design decision]

## Detailed File Reviews

**IMPORTANT:** Every actionable observation below MUST also appear in Critical or Suggestions above. Before finalizing, re-read these notes and promote any observation with a recommendation to the formal issues list.

### `path/to/file.ts`
- Line 42: [specific feedback]
- Line 100-105: [specific feedback]
```

## Additional Context Needed?

If the diff is truncated or you need more context:
- Use `git diff <base>..HEAD -- path/to/specific/file` for full file diff
- Use `git show <commit>` to see individual commit changes
- Read specific files mentioned in the diff for full context
