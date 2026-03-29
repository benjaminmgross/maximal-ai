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

### Existing Reviews (all PRs — coordinator should filter by target PR number)
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
Usage: /review-fix-pr-loop [PR_NUMBER|PR_URL|[text](PR_URL)] [--max-rounds N]
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

**Loop Control Flow (pseudocode — follow this exactly):**

```python
round = 1

while True:                           # always enter the loop body
    verdict = run_reviewer(round)     # Steps 3a–3b
    run_fixer(round)                  # Steps 3c–3f — ALWAYS runs, even if APPROVED
    round += 1                        # Step 3g
    if round > max_rounds or verdict == "APPROVED":
        break                         # exit: either approved or max rounds completed
```

Execute steps 3a through 3g below. The fixer **always** runs — APPROVED means no blocking issues, but suggestions still get implemented. The **only** exit point is after step 3g.

#### 3a. Spawn Reviewer Sub-Agent

Use the Task tool to spawn a general-purpose reviewer sub-agent. The reviewer gets fresh context and fetches its own diff.

**Reviewer prompt template** (fill in variables before sending):

```
You are an adversarial code reviewer. Review this PR with fresh eyes — you have no context about how the code was written or what trade-offs were made.

## Your Task

Review PR #[PR_NUMBER] and write a structured review file.

## Step 1: Gather PR Context

Run these commands to get the PR information:

1. Get PR metadata:
   `gh pr view [PR_NUMBER] --json number,title,body,author,headRefName,baseRefName,additions,deletions,changedFiles,state,url`

2. Get the LOCAL diff against the PR base branch (this includes all local commits, even unpushed fixer commits):
   `git diff $(gh pr view [PR_NUMBER] --json baseRefName --jq '.baseRefName')...HEAD | head -2000`
   If the diff is truncated, use file-specific diffs for files you need to review in full:
   `git diff $(gh pr view [PR_NUMBER] --json baseRefName --jq '.baseRefName')...HEAD -- path/to/specific/file`
   Note: Do NOT use `gh pr diff` as the primary diff source — it fetches the remote state and will miss local fixer commits from prior rounds.

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
**Operational Resilience** - HTTP timeouts, retry logic, error boundaries around external calls, graceful degradation, `exc_info=True` in exception handlers

**Runtime Context** (for shell scripts and multi-process code):
  - Trace the working directory (cwd) through every `cd`, subshell `(cd ...)`,
    and worktree boundary. Check whether relative paths resolve correctly in
    each execution context.
  - For every subprocess invocation, verify: does the subprocess inherit the
    correct cwd? Are relative paths valid from the subprocess's perspective?
  - Check whether `mkdir -p` for output paths runs in the same directory where
    files will actually be written.

**Staleness / Configuration Drift:**
  - Hardcoded version strings, model IDs, SDK versions, or API endpoint versions
    that may become outdated
  - Magic numbers or date-based identifiers that should be configurable or
    sourced from a central config

**Cross-File Pattern Tracing:** When you find an issue in one file, search the ENTIRE diff for the same pattern in other files. Common patterns: `requests.*` without `timeout=`, `datetime.now()` without timezone, exception handlers without `exc_info=True`, hardcoded URLs/IDs/ARNs, `os.environ.get()` with defaults that make subsequent None-checks dead code. Report ALL instances, not just the first.

**Data-Value Flow Tracing:** For variables assembled from external data (jq output,
API responses, user input), ask: "What if this value contains a space, a newline,
a quote, or special characters?" Trace the value from production (where it's created)
through every consumption point (where it's used). Check that delimiters used in
production are not ambiguous with possible field values.

**Shell Argument Safety:** For every variable that participates in word-splitting,
array construction, or string concatenation, ask:
  - What if the value is empty?
  - What if the value contains spaces?
  - What if the value contains shell metacharacters?
Trace from the data source (jq, API, user input) to every consumption point.

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

Issues that MUST be addressed before merging. Use these classification rules:

**Always Critical:**
- Security vulnerabilities (injection, auth bypass, credential exposure)
- Hardcoded infrastructure identifiers (AWS account IDs, resource ARNs, API keys)
- Breaking API contracts (response shape changes, removed fields)
- Missing authentication or authorization on external calls
- Missing error handling that would crash the service in production
- Missing timeouts on external HTTP/API calls (can hang indefinitely)
- Data loss or corruption risks
- Missing verification that critical side-effects occurred (e.g., subprocess pushed
  commits, file was written, API call succeeded) — especially when the action is
  wrapped in `|| true` or run in a subshell whose exit code is discarded

**Always Suggestion:**
- Code style, naming, readability improvements
- Minor inconsistencies that don't affect production behavior
- Dead code that doesn't cause runtime issues
- Missing documentation or type hints
- Performance optimizations without immediate production impact

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

**IMPORTANT:** Every actionable observation below MUST also appear in Critical Issues or Suggestions above. File-by-File Notes provide context for already-classified issues — they are NOT a place for unclassified findings. Before finalizing, re-read these notes and promote any observation with a recommendation ("consider...", "should...", "could...") to the formal issues list.

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
The response file (documenting how each issue was addressed) is at: [previous_response_file_path]
Read the response file to understand which issues were fixed, which were declined (WONT_FIX), and why.
Do not re-raise WONT_FIX items unless you have new evidence they should be reconsidered.
You may read the review file for context on what was previously found, but form your own independent assessment.
Conduct a fully independent review as if this is a new PR you are seeing for the first time.
Give equal or greater weight to discovering NEW issues versus verifying old fixes.
After your independent review, also verify that previously-identified critical issues have
been properly fixed — but do not let verification anchor your attention away from new discovery.
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

#### 3c. Note the Verdict

Record the verdict (`APPROVED`, `REQUEST_CHANGES`, or `NEEDS_DISCUSSION`). Do NOT exit the loop here — the fixer always runs next, regardless of verdict. APPROVED means no blocking issues, but suggestions still get implemented.

> **CRITICAL — THE FIXER ALWAYS RUNS.**
> Do not skip the fixer for any reason — not for APPROVED verdicts, not on the last round.
> APPROVED reviews can still contain suggestions worth implementing.
> The only exit point is after step 3g.

#### 3d. Validate Branch Before Fixing

Before spawning the fixer, verify you are on the correct branch:
1. Compare the "Current Branch" pre-computed value against `headRefName` from the PR metadata
2. If they do NOT match, run `git checkout [headRefName]` to switch to the PR's branch
3. If checkout fails, stop and warn the user: "Cannot fix: not on PR branch [headRefName], currently on [current branch]"

#### 3e. Spawn Fixer Sub-Agent

If verdict is `REQUEST_CHANGES` or `NEEDS_DISCUSSION`, use the Task tool to spawn a general-purpose fixer sub-agent.

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
   git add [files-you-changed]
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

Set `round = round + 1`.

**Exit check:** If `round > max_rounds`, exit the loop and proceed to Step 4 (Final Summary).
Otherwise, continue from step 3a with the next round.

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
9. **The fixer always runs** — Every round is a complete review→fix cycle. The fixer runs after every review, regardless of verdict or round number. APPROVED reviews can still contain suggestions. The only exit point is after step 3g.
