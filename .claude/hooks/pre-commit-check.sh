#!/bin/bash
set -e

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only intercept git commit commands
if [[ ! "$COMMAND" =~ ^git\ commit ]]; then
  exit 0
fi

# Validate CLAUDE_PROJECT_DIR is set (C4 fix)
if [ -z "$CLAUDE_PROJECT_DIR" ]; then
  echo "ERROR: CLAUDE_PROJECT_DIR is not set" >&2
  exit 2  # Block commit to be safe
fi

# Check if on a protected branch
CURRENT_BRANCH=$(cd "$CLAUDE_PROJECT_DIR" && git rev-parse --abbrev-ref HEAD 2>/dev/null)

# Fail safely if we can't determine the branch (C3 fix)
if [ -z "$CURRENT_BRANCH" ]; then
  echo "WARNING: Could not determine current branch. Blocking commit to be safe." >&2
  echo "" >&2
  echo "Ensure you are in a valid git repository with at least one commit." >&2
  exit 2
fi

# Check for detached HEAD state (C1 fix)
if [[ "$CURRENT_BRANCH" == "HEAD" ]]; then
  echo "ERROR: You're in detached HEAD state (possibly mid-rebase or bisect)." >&2
  echo "" >&2
  echo "Commits in this state may be orphaned or disrupt git operations." >&2
  echo "Consider:" >&2
  echo "  git checkout -b temp-branch    # Save work to a new branch" >&2
  echo "  git rebase --abort             # Abort if mid-rebase" >&2
  echo "  git bisect reset               # Exit if mid-bisect" >&2
  exit 2  # Block the commit
fi

# Allow override via environment variable (S1 fix)
PROTECTED_BRANCHES="${CLAUDE_PROTECTED_BRANCHES:-^(main|master|dev|develop|production|staging)$}"

if [[ "$CURRENT_BRANCH" =~ $PROTECTED_BRANCHES ]]; then
  echo "ERROR: Direct commits to '$CURRENT_BRANCH' are not allowed." >&2
  echo "" >&2
  echo "Please create a feature branch first:" >&2
  echo "  git checkout -b feature/your-feature-name" >&2
  echo "" >&2
  echo "Or for hotfixes:" >&2
  echo "  git checkout -b hotfix/issue-description" >&2
  echo "" >&2
  echo "Or for bug fixes:" >&2
  echo "  git checkout -b bugfix/issue-description" >&2
  exit 2  # Block the commit
fi

echo "Running pre-commit verification..." >&2

# Detect project type and run tests
if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
  if ! (cd "$CLAUDE_PROJECT_DIR" && npm test --passWithNoTests 2>/dev/null); then
    echo "ERROR: Tests must pass before commit. Run 'npm test' to see failures." >&2
    exit 2  # Block the commit
  fi
elif [ -f "$CLAUDE_PROJECT_DIR/pyproject.toml" ] || [ -f "$CLAUDE_PROJECT_DIR/setup.py" ]; then
  # Try uv first, then fall back to python -m pytest
  if command -v uv &> /dev/null && [ -f "$CLAUDE_PROJECT_DIR/pyproject.toml" ]; then
    if ! (cd "$CLAUDE_PROJECT_DIR" && uv run pytest -q 2>/dev/null); then
      echo "ERROR: Tests must pass before commit. Run 'uv run pytest' to see failures." >&2
      exit 2  # Block the commit
    fi
  elif ! (cd "$CLAUDE_PROJECT_DIR" && python -m pytest -q 2>/dev/null); then
    echo "ERROR: Tests must pass before commit. Run 'pytest' to see failures." >&2
    exit 2  # Block the commit
  fi
fi

echo "Pre-commit verification passed." >&2
exit 0
