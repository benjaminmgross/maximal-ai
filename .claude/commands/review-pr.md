---
description: Review a GitHub PR with structured output for multi-session workflow
---

# Review PR

You are a code reviewer in a fresh session. Your job is to review this PR with fresh eyes - no bias from having written the code.

<pr_identifier>
$ARGUMENTS
</pr_identifier>

**Usage:** `/review-pr [PR_NUMBER]` or `/review-pr [PR_NUMBER] --round [N]`

If `--round` is not specified, the round number will be auto-detected based on existing review files.

## Pre-computed PR Context

### PR Metadata
!`gh pr view $ARGUMENTS --json number,title,body,author,headRefName,baseRefName,additions,deletions,changedFiles,state,url 2>/dev/null || echo "PR not found - specify PR number as argument"`

### PR Commits
!`gh pr view $ARGUMENTS --json commits --jq '.commits[] | "- \(.oid[0:7]) \(.messageHeadline)"' 2>/dev/null | head -20 || echo "No commits"`

### Files Changed
!`gh pr diff $ARGUMENTS --name-only 2>/dev/null | head -50 || echo "No diff available"`

### Diff Statistics
!`gh pr diff $ARGUMENTS --stat 2>/dev/null | tail -20 || echo "No stats"`

### Full Diff (first 600 lines)
!`gh pr diff $ARGUMENTS 2>/dev/null | head -600 || echo "No diff"`

### Total Diff Lines
!`gh pr diff $ARGUMENTS 2>/dev/null | wc -l | tr -d ' '`

**Note:** If total lines > 600, the diff above is truncated. Use `gh pr diff [PR] -- path/to/file` for full file diffs.

### Linked Plan File (from PR body)
!`gh pr view $ARGUMENTS --json body --jq '.body' 2>/dev/null | grep -oE 'thoughts/plans/[^)>\s]+\.md' | head -1 || echo "No plan file linked"`

### Username for Review File
!`grep "^username:" .claude/config.yaml 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "${RPI_USERNAME:-user}"`

### Git Username (fallback)
!`git config user.name 2>/dev/null | tr ' ' '-' | tr '[:upper:]' '[:lower:]' || echo "user"`

### Today's Date
!`date +%Y.%m.%d`

### PR Number Extracted
!`echo "$ARGUMENTS" | grep -oE '[0-9]+' | head -1`

### Existing Reviews (filter by PR number above)
!`ls -t thoughts/reviews/*-review-*.md 2>/dev/null | head -10 || echo "No existing reviews"`

### Review Count (use to compute round number)
!`ls thoughts/reviews/*-review-*.md 2>/dev/null | wc -l | tr -d ' ' || echo "0"`

**Note:** Use the PR number above to filter the review list. The round number is: (count of reviews matching this PR) + 1.

## Review Process

### Step 1: Understand the PR
1. Read the PR title and description
2. If a plan file is linked, read it to understand intent
3. Review the commit messages to understand the progression

### Step 2: Review the Code

For each file in the diff, analyze:

**Correctness**
- Are there logic errors or bugs?
- Are edge cases handled?
- Is error handling appropriate?

**Security**
- No hardcoded secrets or credentials?
- Input validation present?
- No injection vulnerabilities (SQL, XSS, command)?

**Quality**
- Code is readable and self-documenting?
- Follows existing patterns in the codebase?
- No unnecessary complexity?

**Testing**
- Are there tests for new functionality?
- Do tests cover edge cases?

**Performance**
- Any obvious performance issues?
- N+1 queries, unnecessary loops, memory leaks?

**Operational Resilience**
- Do all external HTTP/API calls have explicit `timeout` parameters?
- Are external service calls wrapped in try/except with specific exception types?
- Is there retry logic for idempotent operations to transient-failure-prone services?
- Are there unbounded loops or polls without timeout caps?
- Do exception handlers include `exc_info=True` (or use `logger.exception()`) for debugging?
- What is the failure mode when each external dependency is unavailable?

**Cross-File Pattern Tracing**

When you find an issue in one file, search the ENTIRE diff for the same pattern in other files before moving on. Common cross-cutting patterns:
- `requests.` calls without `timeout=` — find ALL of them
- `datetime.now()` without timezone — find ALL of them
- Exception handlers without `exc_info=True` — find ALL of them
- Hardcoded URLs, IDs, ARNs, or resource identifiers — find ALL of them
- `os.environ.get()` with defaults that make subsequent None-checks dead code

Report ALL instances, not just the first one found.

### Step 3: Create Structured Review Output

**IMPORTANT:** Create the review file at:
`thoughts/reviews/{DATE}-pr-{NUMBER}-review-{ROUND}.md`

Where:
- `{DATE}` is from "Today's Date" above (YYYY.MM.DD format)
- `{NUMBER}` is the PR number
- `{ROUND}` is 1 for first review, 2 for re-review, etc.

Use this exact format:

```markdown
---
pr_number: [NUMBER]
pr_title: "[TITLE]"
pr_url: "[URL]"
round: 1
verdict: REQUEST_CHANGES | APPROVED | NEEDS_DISCUSSION
reviewer: [username]
date: [ISO date]
plan_file: [path if found, or "none"]
---

# PR Review: [PR Title]

## Summary

[2-3 sentences summarizing the PR and your overall assessment]

**Verdict: [REQUEST_CHANGES / APPROVED / NEEDS_DISCUSSION]**

## Strengths

- [What was done well]
- [Good patterns followed]
- [Thorough testing, etc.]

## Critical Issues (Must Fix)

Issues that MUST be addressed before merging. Use these classification rules:

**Always Critical:**
- Security vulnerabilities (injection, auth bypass, credential exposure)
- Hardcoded infrastructure identifiers (AWS account IDs, resource ARNs, API keys)
- Breaking API contracts (response shape changes, removed fields)
- Missing authentication or authorization on external calls
- Missing error handling that would crash the service in production
- Missing timeouts on external HTTP/API calls (can hang indefinitely)
- Data loss or corruption risks

**Always Suggestion:**
- Code style, naming, readability improvements
- Minor inconsistencies that don't affect production behavior
- Dead code that doesn't cause runtime issues
- Missing documentation or type hints
- Performance optimizations without immediate production impact

### C1: [Issue Title]
- **File:** `path/to/file.ts:42`
- **Severity:** Critical
- **Issue:** [Clear description of the problem]
- **Risk:** [What could go wrong if not fixed]
- **Suggestion:**
  ```typescript
  // Suggested fix
  ```

### C2: [Issue Title]
- **File:** `path/to/file.ts:89`
- **Severity:** Critical
- **Issue:** [Description]
- **Risk:** [Risk]
- **Suggestion:** [How to fix]

## Suggestions (Nice to Have)

Issues that would improve the code but aren't blocking.

### S1: [Suggestion Title]
- **File:** `path/to/file.ts:100`
- **Issue:** [Description]
- **Suggestion:** [Recommendation]

### S2: [Suggestion Title]
- **File:** `path/to/file.ts:150`
- **Issue:** [Description]
- **Suggestion:** [Recommendation]

## Questions

Clarifications needed about design decisions.

### Q1: [Question]
- **File:** `path/to/file.ts:200`
- **Context:** [Why you're asking]

## File-by-File Notes

**IMPORTANT:** Every actionable observation below MUST also appear in Critical Issues or Suggestions above. File-by-File Notes provide context for already-classified issues — they are NOT a place for unclassified findings. Before finalizing, re-read these notes and promote any observation with a recommendation ("consider...", "should...", "could...") to the formal issues list.

### `path/to/file1.ts`
- Line 42: [Specific feedback]
- Line 89-95: [Specific feedback]

### `path/to/file2.ts`
- Line 10: [Specific feedback]

---

*Review generated by Session 2 of multi-session PR review workflow*
*Plan file: [path or "not linked"]*
```

### Step 4: Save the Review

1. Ensure `thoughts/reviews/` directory exists
2. Write the review file with the structured format above
3. Confirm the file path to the user

**Note:** Review files in `thoughts/reviews/` are gitignored by default (the entire `thoughts/` directory is excluded). This keeps review artifacts local to your machine. If you want to share reviews, post summaries to GitHub using Step 5.

### Step 5: Optionally Post to GitHub

Ask the user if they want to post a summary to GitHub:

```bash
gh pr review [NUMBER] --comment --body "$(cat <<'EOF'
## Code Review - Round [N]

**Verdict:** [REQUEST_CHANGES / APPROVED]

### Critical Issues
- [ ] C1: [Brief description]
- [ ] C2: [Brief description]

### Suggestions
- [ ] S1: [Brief description]

Full review: `thoughts/reviews/[filename].md`

---
*Multi-session PR review workflow*
EOF
)"
```

## If Diff is Truncated

If you need more context:
- Use `gh pr diff [PR] -- path/to/specific/file` for full file diff
- Use `Read` tool to read specific files mentioned in the diff
- Use `gh pr view [PR] --json files` to see all changed files

## Review Guidelines

1. **Be constructive** - Explain why something is an issue, not just that it is
2. **Be specific** - Include file:line references for every issue
3. **Prioritize** - Critical issues are blockers, suggestions are nice-to-have
4. **Be thorough** - Fresh eyes catch things the author missed
5. **Acknowledge good work** - Note what was done well

## Output

After creating the review file, report:

```
Review complete!

File: thoughts/reviews/[DATE]-pr-[NUMBER]-review-[ROUND].md
Verdict: [REQUEST_CHANGES / APPROVED / NEEDS_DISCUSSION]

Critical issues: [N]
Suggestions: [N]
Questions: [N]

Next steps:
- Session 1 should run: /address-review [plan-file] thoughts/reviews/[review-file]
```
