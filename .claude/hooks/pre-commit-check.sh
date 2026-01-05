#!/bin/bash
set -e

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only intercept git commit commands
if [[ ! "$COMMAND" =~ ^git\ commit ]]; then
  exit 0
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
