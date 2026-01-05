#!/bin/bash
set -e

# Post-edit hook with graceful degradation
# Runs tests in background after source file edits
# Uses TMPDIR if available, falls back to /tmp

# Read hook input from stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

# Skip if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Skip non-source files
if [[ ! "$FILE_PATH" =~ \.(py|ts|tsx|js|jsx)$ ]]; then
  exit 0
fi

# Use TMPDIR if available, otherwise fall back to /tmp
LOG_DIR="${TMPDIR:-/tmp}"
LOG_FILE="${LOG_DIR}/claude-test-results.log"

echo "=== $(date) ===" >> "$LOG_FILE"
echo "Triggered by: $FILE_PATH" >> "$LOG_FILE"

# Run tests in background, log results (don't block Claude)
# Gracefully degrades if test runners are not available
if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
  if command -v npm &> /dev/null; then
    (cd "$CLAUDE_PROJECT_DIR" && npm test --passWithNoTests 2>&1 | tail -20 >> "$LOG_FILE") &
  fi
elif [ -f "$CLAUDE_PROJECT_DIR/pyproject.toml" ] || [ -f "$CLAUDE_PROJECT_DIR/setup.py" ]; then
  if command -v pytest &> /dev/null || command -v python &> /dev/null; then
    (cd "$CLAUDE_PROJECT_DIR" && python -m pytest -q 2>&1 | tail -20 >> "$LOG_FILE") &
  fi
fi

exit 0
