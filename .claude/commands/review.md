---
description: Review code changes with pre-computed diff and context
---

# Code Review

Review the current branch's changes against the base branch.

## Pre-computed Review Context

### Branch Information
!`echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'detached HEAD')"`
!`echo "Base branch: $(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo 'main')"`
!`echo "Commits ahead: $(git rev-list --count $(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD origin/master 2>/dev/null || echo HEAD~10)..HEAD 2>/dev/null || echo 'unknown')"`

### Files Changed
!`git diff --name-only $(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD origin/master 2>/dev/null || echo HEAD~5) HEAD 2>/dev/null | head -30 || echo "No changes detected"`

### Diff Statistics
!`git diff --stat $(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD origin/master 2>/dev/null || echo HEAD~5) HEAD 2>/dev/null | tail -15 || echo "No diff stats"`

### Commits to Review
!`git log --oneline $(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD origin/master 2>/dev/null || echo HEAD~5)..HEAD 2>/dev/null | head -20 || echo "No commits"`

### Full Diff (first 300 lines)
!`git diff $(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD origin/master 2>/dev/null || echo HEAD~5) HEAD 2>/dev/null | head -300 || echo "No diff"`

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

## Review Output Format

Provide feedback in this structure:

```markdown
## Review Summary

**Overall**: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION

**Strengths**:
- [What was done well]

**Issues Found**:

### Critical (Must Fix)
1. **[Issue]** - `file.ts:42`
   - Problem: [description]
   - Suggestion: [how to fix]

### Suggestions (Nice to Have)
1. **[Suggestion]** - `file.ts:100`
   - [description and recommendation]

### Questions
1. [Clarifying question about design decision]

## Detailed File Reviews

### `path/to/file.ts`
- Line 42: [specific feedback]
- Line 100-105: [specific feedback]
```

## Additional Context Needed?

If the diff is truncated or you need more context:
- Use `git diff <base>..HEAD -- path/to/specific/file` for full file diff
- Use `git show <commit>` to see individual commit changes
- Read specific files mentioned in the diff for full context
