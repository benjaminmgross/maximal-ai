---
description: Run adversarial review-fix loop on a PR using sub-agents
---

# Review-Fix PR Loop

You are a **coordinator** orchestrating an adversarial review-fix loop. You do NOT review or fix code yourself — you spawn sub-agents for each role and manage the loop.

<pr_identifier>
$ARGUMENTS
</pr_identifier>

**Usage:**
- `/review-fix-pr-loop 42`
- `/review-fix-pr-loop 42 --max-rounds 5`
- `/review-fix-pr-loop https://github.com/user/repo/pull/42`
- `/review-fix-pr-loop [this pr](https://github.com/user/repo/pull/42)`

## Pre-computed Context

### Clean PR Identifier (strips markdown link syntax, extracts URL or number)
!`echo "$ARGUMENTS" | sed 's/\[.*\](\([^)]*\))/\1/' | awk '{print $1}'`

### PR Metadata
!`echo "$ARGUMENTS" | sed 's/\[.*\](\([^)]*\))/\1/' | awk '{print $1}' | xargs -I{} gh pr view {} --json number,title,body,author,headRefName,baseRefName,additions,deletions,changedFiles,state,url 2>/dev/null || echo "PR not found - specify PR number as argument"`

### PR Number Extracted
!`echo "$ARGUMENTS" | grep -oE 'pull/[0-9]+' | head -1 | grep -oE '[0-9]+' || echo "$ARGUMENTS" | grep -oE '[0-9]+' | head -1`

### Username for Review File
!`grep "^username:" .claude/config.yaml 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "${RPI_USERNAME:-user}"`

### Git Username (fallback)
!`git config user.name 2>/dev/null | tr ' ' '-' | tr '[:upper:]' '[:lower:]' || echo "user"`

### Today's Date
!`date +%Y.%m.%d`

### Current Branch
!`git branch --show-current 2>/dev/null || echo "unknown"`

### Existing Reviews for This PR
!`ls -t thoughts/reviews/*-review-*.md 2>/dev/null | head -10 || echo "No existing reviews"`

### Linked Plan File (from PR body)
!`echo "$ARGUMENTS" | sed 's/\[.*\](\([^)]*\))/\1/' | awk '{print $1}' | xargs -I{} gh pr view {} --json body --jq '.body' 2>/dev/null | grep -oE 'thoughts/plans/[^)>\s]+\.md' | head -1 || echo "No plan file linked"`

## Coordinator Instructions

### Step 1: Parse Arguments

The user may pass a PR identifier in several formats:
- Bare number: `42`
- GitHub URL: `https://github.com/user/repo/pull/42`
- Markdown link: `[this pr](https://github.com/user/repo/pull/42)`
- Any of the above with `--max-rounds N` appended

Extract from `$ARGUMENTS`:
1. **PR number** — use the "PR Number Extracted" pre-computed value (handles all formats: tries `pull/N` from URLs first, falls back to first bare number)
2. **Max rounds** — from `--max-rounds N` (default: 3)

The "Clean PR Identifier" pre-computed value strips markdown link syntax and gives you a clean URL or number suitable for `gh pr view`.

If no PR number is found, stop and ask the user:
```
No PR number found.
Usage: /review-fix-pr [PR_NUMBER|PR_URL|[text](PR_URL)] [--max-rounds N]
```

### Step 2: Initialize Loop State

Set:
- `round = 1`
- `max_rounds` = parsed value or 3
- `approved = false`
- `pr_number` = extracted PR number
- `date` = today's date from pre-computed context
- `reviewer_username` = from pre-computed context

Report to the user:
```
Starting adversarial review-fix loop for PR #[NUMBER]
Max rounds: [N]
Branch: [branch]
```

### Step 3: Run the Review-Fix Loop

Repeat until `approved == true` OR `round > max_rounds`:

#### 3a. Spawn Reviewer Sub-Agent

Use the Task tool with `subagent_type: "general-purpose"` to spawn a reviewer. The reviewer gets fresh context and fetches its own diff.

**Reviewer prompt template** (fill in variables before sending):

```
You are an adversarial code reviewer. Review this PR with fresh eyes — you have no context about how the code was written or what trade-offs were made.

## Your Task

Review PR #[PR_NUMBER] and write a structured review file.

## Step 1: Gather PR Context

Run these commands to get the PR information:

1. Get PR metadata:
   `gh pr view [PR_NUMBER] --json number,title,body,author,headRefName,baseRefName,additions,deletions,changedFiles,state,url`

2. Get the diff (truncate to avoid context overflow on large PRs):
   `gh pr diff [PR_NUMBER] | head -600`
   If the diff is truncated, use file-specific diffs for files you need to review in full:
   `gh pr diff [PR_NUMBER] -- path/to/specific/file`

3. Get diff stats (file list and change counts):
   `gh pr view [PR_NUMBER] --json additions,deletions,changedFiles`

4. Get commit history:
   `gh pr view [PR_NUMBER] --json commits --jq '.commits[] | "- \(.oid[0:7]) \(.messageHeadline)"'`

5. If a plan file is linked in the PR body, read it for intent.

## Step 2: Review the Code

For each file in the diff, analyze:

**Correctness** - Logic errors, bugs, unhandled edge cases, error handling
**Security** - Hardcoded secrets, input validation, injection vulnerabilities
**Quality** - Readability, follows existing patterns, unnecessary complexity
**Testing** - Tests for new functionality, edge case coverage
**Performance** - N+1 queries, unnecessary loops, memory leaks

Be genuinely adversarial. Your job is to find real issues, not rubber-stamp.

## Step 3: Write the Review File

Create the review file at: `thoughts/reviews/[DATE]-pr-[PR_NUMBER]-review-[ROUND].md`

Where:
- DATE = [DATE]
- PR_NUMBER = [PR_NUMBER]
- ROUND = [ROUND]

Use this EXACT format:

```markdown
---
pr_number: [PR_NUMBER]
pr_title: "[title from metadata]"
pr_url: "[url from metadata]"
round: [ROUND]
verdict: REQUEST_CHANGES | APPROVED | NEEDS_DISCUSSION
reviewer: [REVIEWER_USERNAME]
date: [ISO_DATE]
plan_file: [path if found, or "none"]
---

# PR Review: [PR Title]

## Summary

[2-3 sentences summarizing the PR and your overall assessment]

**Verdict: [REQUEST_CHANGES / APPROVED / NEEDS_DISCUSSION]**

## Strengths

- [What was done well]

## Critical Issues (Must Fix)

Issues that MUST be addressed before merging.

### C1: [Issue Title]
- **File:** `path/to/file:line`
- **Severity:** Critical
- **Issue:** [Clear description]
- **Risk:** [What could go wrong]
- **Suggestion:** [How to fix]

(Continue C2, C3, etc. as needed. If none, write "No critical issues found.")

## Suggestions (Nice to Have)

### S1: [Suggestion Title]
- **File:** `path/to/file:line`
- **Issue:** [Description]
- **Suggestion:** [Recommendation]

(Continue S2, S3, etc. as needed. If none, write "No suggestions.")

## Questions

### Q1: [Question]
- **File:** `path/to/file:line`
- **Context:** [Why you're asking]

(If none, write "No questions.")

## File-by-File Notes

### `path/to/file1`
- Line N: [Specific feedback]

---

*Review generated by adversarial reviewer sub-agent, round [ROUND]*
```

[PRIOR_REVIEW_CONTEXT]

## Step 4: Report Back

After writing the review file, report:
- The verdict (REQUEST_CHANGES, APPROVED, or NEEDS_DISCUSSION)
- Count of critical issues (C1, C2, ...)
- Count of suggestions (S1, S2, ...)
- Count of questions (Q1, Q2, ...)
- The full path to the review file

Format your final response as:
```
VERDICT: [verdict]
CRITICAL: [count]
SUGGESTIONS: [count]
QUESTIONS: [count]
REVIEW_FILE: thoughts/reviews/[filename].md
```
```

**For round 1:** Set `[PRIOR_REVIEW_CONTEXT]` to empty string.

**For round 2+:** Set `[PRIOR_REVIEW_CONTEXT]` to:
```
## Prior Review Context

A previous review was conducted and issues were addressed. You are doing a fresh re-review.
The previous review file is at: [previous_review_file_path]
You may read it for context on what was previously found, but form your own independent assessment.
Focus especially on whether previously-identified critical issues have been properly fixed,
and whether the fixes introduced any new issues.
```

#### 3b. Parse Reviewer Verdict

After the reviewer sub-agent returns:
1. Read the review file it created
2. Extract the `verdict` from YAML frontmatter
3. Count critical issues, suggestions, and questions

Report to the user:
```
Round [N] Review Complete
Verdict: [verdict]
Critical: [count] | Suggestions: [count] | Questions: [count]
Review: thoughts/reviews/[filename].md
```

#### 3c. Check for Approval

If verdict is `APPROVED`:
- Set `approved = true`
- Skip the fixer step
- Break out of the loop

#### 3d. Validate Branch Before Fixing

Before spawning the fixer, verify you are on the correct branch:
1. Compare the "Current Branch" pre-computed value against `headRefName` from the PR metadata
2. If they do NOT match, run `git checkout [headRefName]` to switch to the PR's branch
3. If checkout fails, stop and warn the user: "Cannot fix: not on PR branch [headRefName], currently on [current branch]"

#### 3e. Spawn Fixer Sub-Agent

If verdict is `REQUEST_CHANGES` or `NEEDS_DISCUSSION`, spawn a fixer using the Task tool with `subagent_type: "general-purpose"`.

First, read the review file yourself to extract the list of issues. Then construct the fixer prompt with the specific issues.

**Fixer prompt template** (fill in variables before sending):

```
You are a code fixer. Your job is to address review feedback on PR #[PR_NUMBER] systematically.

## Your Task

Address the following review issues found in round [ROUND]:

## Issues to Fix

[ISSUES_LIST]

(The above issues come from the review file at: [REVIEW_FILE_PATH])

## Instructions

For EACH issue listed above:

1. Read the relevant file completely
2. Understand the issue in context of the surrounding code
3. Make the fix — follow the reviewer's suggestion when it makes sense, use your judgment otherwise
4. Stage and commit immediately with this format:
   ```
   git commit -m "$(cat <<'EOF'
   fix: address review [ISSUE_ID] - [brief description]
   
   Issue: [what the reviewer found]
   Fix: [what you changed]
   
   Review: [REVIEW_FILE_PATH]
   EOF
   )"
   ```

## Priority Order

Fix in this order:
1. Critical issues (C1, C2, ...) — these are blockers
2. Suggestions (S1, S2, ...) — address if reasonable
3. Questions (Q1, Q2, ...) — respond via code changes if applicable

## Guidelines

- One commit per issue for traceability
- Read the file FULLY before making changes
- Follow existing code patterns
- Do NOT push to remote — just commit locally
- If you disagree with a suggestion, skip it and note why

## After Fixing

Create a response file at: `thoughts/reviews/[DATE]-pr-[PR_NUMBER]-response-[ROUND].md`

Format:
```markdown
---
review_file: [REVIEW_FILE_PATH]
pr_number: [PR_NUMBER]
round: [ROUND]
date: [ISO_DATE]
---

# Review Response — Round [ROUND]

## Summary

Addressed [N] critical issues, [N] suggestions, and responded to [N] questions.

## Issue Responses

### [ISSUE_ID]: [Issue Title]
- **Status:** FIXED | WONT_FIX | DEFERRED
- **Commit:** [hash]
- **Notes:** [What was done]

(Repeat for each issue)

## Commits Made

- `[hash]` - fix: address review [ID] - [description]

(List all commits made)
```

## Report Back

After all fixes and the response file are written, report:
- How many issues were fixed vs skipped
- List of commit hashes
- Path to the response file

Format your final response as:
```
FIXED: [count]
SKIPPED: [count]
RESPONSE_FILE: thoughts/reviews/[filename].md
COMMITS: [comma-separated hashes]
```
```

#### 3f. Validate Fixes

After the fixer sub-agent returns:
1. Read the response file
2. Run tests if a test command is available: `npm test` or check for test scripts
3. Report fixer results to the user:

```
Round [N] Fixes Complete
Fixed: [count] | Skipped: [count]
Response: thoughts/reviews/[filename].md
Tests: [PASS/FAIL/SKIPPED]
```

If tests fail, note the failure but continue to next round (the re-reviewer will catch regressions).

#### 3g. Increment Round

Set `round = round + 1` and continue the loop.

### Step 4: Final Summary

After the loop ends (approved or max rounds reached), report:

```
## Review-Fix Loop Complete

**PR:** #[NUMBER] — [title]
**Result:** [APPROVED after round N / MAX ROUNDS REACHED (N rounds)]
**Branch:** [branch]

### Round Summary

| Round | Verdict | Critical | Suggestions | Questions | Fixes |
|-------|---------|----------|-------------|-----------|-------|
| 1     | REQUEST_CHANGES | 3 | 2 | 1 | 6 |
| 2     | APPROVED | 0 | 1 | 0 | - |

### Files Created
- Review: thoughts/reviews/[review-files...]
- Response: thoughts/reviews/[response-files...]

### Next Steps
[If APPROVED]: Ready to push and merge. Run `git push` when ready.
[If MAX ROUNDS]: Review remaining issues in the latest review file. Consider manual intervention.
```

## Important Rules

1. **You are the COORDINATOR** — do NOT review or fix code yourself
2. **One reviewer per round** — fresh context ensures genuine adversarial review
3. **One fixer per round** — holistic fixes avoid file conflicts
4. **Read review files between steps** — this is how you bridge reviewer and fixer
5. **Do NOT push** — only commit locally, let the user decide when to push
6. **Keep your own context lean** — delegate all code reading to sub-agents
7. **Track state explicitly** — round number, verdict, issue counts
8. **Run sequentially** — reviewer must finish before fixer starts; fixer must finish before next reviewer
