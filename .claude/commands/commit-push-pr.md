---
description: Commit changes, push to remote, and create PR with pre-computed context
---

# Commit, Push, and Create PR

## Pre-computed Git Context

### Current Status
!`git status --short 2>/dev/null || echo "Not a git repository"`

### Current Branch
!`git branch --show-current 2>/dev/null || echo "unknown"`

### Base Branch
!`git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main"`

### Remote Tracking
!`git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "No upstream set"`

### Existing PR for This Branch
!`gh pr view --json number,title,url,state 2>/dev/null || echo "No existing PR"`

### Recent Commits (for message style reference)
!`git log -5 --oneline 2>/dev/null || echo "No commits yet"`

### Commits Not Yet in PR (if PR exists)
!`gh pr view --json commits --jq '.commits | length' 2>/dev/null || echo "0"` commits in PR
!`BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || git branch -r | grep -E 'origin/(main|master|develop|dev)$' | head -1 | sed 's@.*origin/@@' || echo "main"); git rev-list --count $(git merge-base HEAD origin/$BASE 2>/dev/null || echo HEAD~10)..HEAD 2>/dev/null || echo "?"` commits on branch

### Staged Changes
!`git diff --cached --stat 2>/dev/null || echo "Nothing staged"`

### Unstaged Changes
!`git diff --stat 2>/dev/null || echo "No unstaged changes"`

### Untracked Files
!`git ls-files --others --exclude-standard 2>/dev/null | head -20`

### Recent Plan Files (for PR reference)
!`ls -t thoughts/plans/*.md 2>/dev/null | head -3 || echo "No plan files found"`

## Instructions

Based on the git information above:

### 1. Stage Relevant Changes
- Review the unstaged and untracked files shown above
- Stage files that should be committed (avoid secrets, build artifacts, node_modules)
- Use `git add <file>` for specific files or `git add .` if all changes are related

### 2. Create a Descriptive Commit
- Follow the commit style from the recent commits shown above
- Use conventional commits format: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Focus on the "why" not just the "what"
- Use a HEREDOC for multi-line messages:
  ```bash
  git commit -m "$(cat <<'EOF'
  feat: Add new feature

  - Detail about the change
  - Another detail
  EOF
  )"
  ```

### 3. Push to Remote
- If "No upstream set" shown above, use `git push -u origin <branch-name>`
- Otherwise use `git push`
- Retry up to 3 times if network errors occur

### 4. Handle PR Creation/Update

**Check the "Existing PR for This Branch" section above:**

#### If PR Already Exists:
The push automatically updates the PR. Just confirm:
```bash
gh pr view --web  # Opens PR in browser
```
Or show the PR URL:
```bash
gh pr view --json url --jq '.url'
```

#### If No Existing PR:
Create a new PR with rich markdown formatting:

```bash
gh pr create --title "feat: [Concise title]" --body "$(cat <<'EOF'
## Summary

[2-3 sentence description of what this PR accomplishes and why]

## Changes

- **[Category 1]**: [Description of changes]
- **[Category 2]**: [Description of changes]
- **[Category 3]**: [Description of changes]

## Implementation Details

[If relevant, explain key technical decisions or non-obvious implementation choices]

## Related

- **Plan**: `thoughts/plans/[YYYY.MM.DD-username-description].md`
- **Issue**: #[number] (if applicable)

## Test Plan

- [ ] [Specific verification step 1]
- [ ] [Specific verification step 2]
- [ ] All tests pass (`npm test` / `pytest`)
- [ ] Types check (`npm run typecheck` / `mypy`)
- [ ] Lint passes (`npm run lint` / `ruff check`)

## Screenshots

[If UI changes, include before/after screenshots]

---

*Generated with RPI workflow - see plan file for full context*
EOF
)"
```

**PR Title Conventions:**
- `feat: Add [feature]` - New functionality
- `fix: Resolve [issue]` - Bug fixes
- `refactor: Improve [component]` - Code improvements
- `docs: Update [documentation]` - Documentation only
- `test: Add tests for [feature]` - Test additions
- `chore: [maintenance task]` - Build, deps, etc.

## Scope Control

- If the user only says "commit" → stop after committing
- If the user says "commit and push" → stop after pushing
- If the user says "commit, push, and PR" or just uses this command → do all three
- **If PR already exists** → push only (PR auto-updates), confirm URL
- Always confirm the PR URL when done

## Safety Guidelines

- Never commit `.env`, credentials, or secrets
- Never force push without explicit user request
- Never push to main/master directly without warning
- Check for large files before committing
- If PR exists, pushing updates it - no need to create new PR
