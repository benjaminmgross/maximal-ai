---
description: Commit changes, push to remote, and create PR with pre-computed context
---

# Commit, Push, and Create PR

## Pre-computed Git Context

### Current Status
!`git status --short 2>/dev/null || echo "Not a git repository"`

### Current Branch
!`git branch --show-current 2>/dev/null || echo "unknown"`

### Remote Tracking
!`git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "No upstream set"`

### Recent Commits (for message style reference)
!`git log -5 --oneline 2>/dev/null || echo "No commits yet"`

### Staged Changes
!`git diff --cached --stat 2>/dev/null || echo "Nothing staged"`

### Unstaged Changes
!`git diff --stat 2>/dev/null || echo "No unstaged changes"`

### Untracked Files
!`git ls-files --others --exclude-standard 2>/dev/null | head -20`

## Instructions

Based on the git information above:

1. **Stage relevant changes**:
   - Review the unstaged and untracked files shown above
   - Stage files that should be committed (avoid secrets, build artifacts, node_modules)
   - Use `git add <file>` for specific files or `git add .` if all changes are related

2. **Create a descriptive commit**:
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

3. **Push to remote**:
   - If "No upstream set" shown above, use `git push -u origin <branch-name>`
   - Otherwise use `git push`
   - Retry up to 3 times if network errors occur

4. **Create PR** (if requested or implied):
   - Use `gh pr create` with clear title and description
   - Format:
     ```bash
     gh pr create --title "feat: Title here" --body "$(cat <<'EOF'
     ## Summary
     - Bullet point 1
     - Bullet point 2

     ## Test plan
     - [ ] How to verify this works
     EOF
     )"
     ```

## Scope Control

- If the user only says "commit" → stop after committing
- If the user says "commit and push" → stop after pushing
- If the user says "commit, push, and PR" or just uses this command → do all three
- Always confirm the PR URL when created

## Safety Guidelines

- Never commit `.env`, credentials, or secrets
- Never force push without explicit user request
- Never push to main/master directly without warning
- Check for large files before committing
