---
description: Address PR review feedback systematically after context reset
---

# Address Review Feedback

You are resuming work in a fresh session after `/clear`. Your job is to address feedback from a code review systematically.

<arguments>
$ARGUMENTS
</arguments>

**Expected arguments:** `[plan-file] [review-file]`
- Example: `/address-review thoughts/plans/2026.01.06-user-oauth.md thoughts/reviews/2026.01.06-pr-123-review-1.md`

## Pre-computed Context

### Current Branch
!`git branch --show-current 2>/dev/null || echo "unknown"`

### Existing PR for This Branch
!`gh pr view --json number,title,url,state 2>/dev/null || echo "No PR found"`

### Current Git Status
!`git status --short 2>/dev/null || echo "Clean"`

### Recent Commits on Branch
!`git log --oneline -10 2>/dev/null || echo "No commits"`

### Changed Files in PR
!`gh pr diff --name-only 2>/dev/null | head -30 || echo "No diff"`

## Process

### Step 1: Parse Arguments

Extract from the arguments provided:
1. **Plan file path** - The implementation plan
2. **Review file path** - The review from Session 2

If arguments are missing, prompt:
```
Please provide both files:
/address-review [plan-file] [review-file]

Recent plan files:
$(ls -t thoughts/plans/*.md 2>/dev/null | head -5)

Recent review files:
$(ls -t thoughts/reviews/*.md 2>/dev/null | head -5)
```

### Step 2: Read Context Files

Read these files COMPLETELY (no limit/offset):

1. **The plan file** - Understand the original intent and design decisions
2. **The review file** - Parse all feedback:
   - Extract `verdict` from YAML frontmatter
   - Extract all Critical Issues (C1, C2, ...)
   - Extract all Suggestions (S1, S2, ...)
   - Extract all Questions (Q1, Q2, ...)

### Step 3: Create Todo List

Use TodoWrite to create a task for each issue:

```
Critical Issues (must fix):
- [ ] C1: [Issue title] - [file:line]
- [ ] C2: [Issue title] - [file:line]

Suggestions (address if reasonable):
- [ ] S1: [Suggestion title] - [file:line]
- [ ] S2: [Suggestion title] - [file:line]

Questions (respond or clarify):
- [ ] Q1: [Question summary]
```

### Step 4: Address Each Issue

For each issue, in priority order (Critical → Suggestions → Questions):

1. **Read the relevant file** completely
2. **Understand the issue** in context
3. **Make the fix** following the reviewer's suggestion or your judgment
4. **Commit immediately** with reference to the issue ID:
   ```bash
   git add [file]
   git commit -m "$(cat <<'EOF'
   fix: address review C1 - [brief description]

   Issue: [what the reviewer found]
   Fix: [what you changed]

   Review: thoughts/reviews/[review-file].md
   EOF
   )"
   ```
5. **Mark todo as complete**
6. **Move to next issue**

### Step 5: Handle Questions

For questions (Q1, Q2, etc.):
- If the answer affects implementation, make appropriate changes
- Document your response in the commit message
- Or note that you'll respond in the PR comments

### Step 6: Create Response Document

After addressing all issues, create a response file at:
`thoughts/reviews/{DATE}-pr-{NUMBER}-response-{ROUND}.md`

Format:
```markdown
---
review_file: thoughts/reviews/[original-review-file].md
pr_number: [NUMBER]
round: [ROUND]
date: [ISO date]
---

# Review Response

## Summary

Addressed [N] critical issues, [N] suggestions, and responded to [N] questions.

## Issue Responses

### C1: [Issue Title]
- **Status:** FIXED
- **Commit:** [hash]
- **Notes:** [What was done]

### C2: [Issue Title]
- **Status:** FIXED
- **Commit:** [hash]
- **Notes:** [What was done]

### S1: [Suggestion Title]
- **Status:** FIXED | WONT_FIX | DEFERRED
- **Commit:** [hash if fixed]
- **Notes:** [Explanation]

### Q1: [Question]
- **Response:** [Your answer]
- **Action taken:** [If any]

## Commits Made

- `abc1234` - fix: address review C1 - [description]
- `def5678` - fix: address review C2 - [description]
- `ghi9012` - fix: address review S1 - [description]

## Ready for Re-review

All critical issues have been addressed. Ready for Session 2 to run:
`/review-pr [PR-NUMBER]`
```

### Step 7: Push Updates

Push all commits to update the existing PR:

```bash
git push
```

The PR automatically updates with new commits.

### Step 8: Notify Ready for Re-review

Output:
```
Review feedback addressed!

Response file: thoughts/reviews/[DATE]-pr-[NUMBER]-response-[ROUND].md

Commits pushed:
- [list of commits]

PR updated: [PR URL]

Next steps:
- Session 2 should run: /review-pr [PR-NUMBER]
- Or re-review with previous context: /review-pr [PR-NUMBER] --round 2
```

Optionally post a comment to the PR:
```bash
gh pr comment [NUMBER] --body "$(cat <<'EOF'
## Review Feedback Addressed

I've addressed the feedback from review round [N]:

**Critical Issues:**
- [x] C1: [Brief description] - fixed in [commit]
- [x] C2: [Brief description] - fixed in [commit]

**Suggestions:**
- [x] S1: [Brief description] - fixed in [commit]
- [ ] S2: [Brief description] - deferred because [reason]

**Questions:**
- Q1: [Brief response]

Ready for re-review. See `thoughts/reviews/[response-file].md` for details.
EOF
)"
```

## Guidelines

### Commit Strategy
- **One commit per issue** - Makes it easy to trace fixes to review comments
- **Reference the issue ID** - `fix: address review C1 - ...`
- **Reference the review file** - Include path in commit body

### When to Push Back
If you disagree with a suggestion:
- Mark as `WONT_FIX` with clear explanation
- Explain your reasoning in the response document
- Let the reviewer decide if it's blocking

### Handling Ambiguity
If an issue is unclear:
- Read the surrounding code for context
- Make your best judgment
- Document your interpretation in the response
- The reviewer can clarify in re-review

## Common Patterns

### Fixing a Bug (Critical Issue)
```bash
# Read the file
# Make the fix
git add src/auth.ts
git commit -m "$(cat <<'EOF'
fix: address review C1 - add null check for user object

Issue: Missing null check could cause runtime error
Fix: Added guard clause at line 42

Review: thoughts/reviews/2026.01.06-pr-123-review-1.md
EOF
)"
```

### Renaming for Clarity (Suggestion)
```bash
git add src/utils.ts
git commit -m "$(cat <<'EOF'
refactor: address review S1 - rename variable for clarity

Changed 'x' to 'tokenExpiry' for better readability

Review: thoughts/reviews/2026.01.06-pr-123-review-1.md
EOF
)"
```

### Responding to Question
Document in response file:
```markdown
### Q1: Why use implicit flow instead of PKCE?
- **Response:** Good catch - this was an oversight. The original plan specified PKCE but I implemented implicit flow by mistake. Fixed in commit abc123.
- **Action taken:** Switched to authorization code flow with PKCE
```

## Error Handling

### If Plan File Not Found
```
Plan file not found: [path]

Available plan files:
$(ls -t thoughts/plans/*.md | head -5)

Please provide correct path.
```

### If Review File Not Found
```
Review file not found: [path]

Available review files:
$(ls -t thoughts/reviews/*.md | head -5)

Please provide correct path.
```

### If No PR Exists
```
No PR found for current branch.

Did you mean to:
1. Run /commit-push-pr first to create a PR?
2. Switch to the correct branch?

Current branch: [branch]
```
