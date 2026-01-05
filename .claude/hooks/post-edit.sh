#!/bin/bash
set -e

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

# Run tests in background, log results (don't block Claude)
LOG_FILE="/tmp/claude-test-results.log"
echo "=== $(date) ===" >> "$LOG_FILE"
echo "Triggered by: $FILE_PATH" >> "$LOG_FILE"

if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
  (cd "$CLAUDE_PROJECT_DIR" && npm test --passWithNoTests 2>&1 | tail -20 >> "$LOG_FILE") &
elif [ -f "$CLAUDE_PROJECT_DIR/pyproject.toml" ] || [ -f "$CLAUDE_PROJECT_DIR/setup.py" ]; then
  (cd "$CLAUDE_PROJECT_DIR" && python -m pytest -q 2>&1 | tail -20 >> "$LOG_FILE") &
fi

exit 0
