#!/bin/bash

# Session completion hook
# Logs session summary with uncommitted changes
# Uses TMPDIR if available, falls back to /tmp

LOG_DIR="${TMPDIR:-/tmp}"
LOG_FILE="${LOG_DIR}/claude-session-summary.log"

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "Session ended: $(date)" >> "$LOG_FILE"
echo "Directory: $CLAUDE_PROJECT_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Check for uncommitted changes
if [ -n "$(cd "$CLAUDE_PROJECT_DIR" && git status --porcelain 2>/dev/null)" ]; then
  echo "" >> "$LOG_FILE"
  echo "Uncommitted changes:" >> "$LOG_FILE"
  (cd "$CLAUDE_PROJECT_DIR" && git status --short) >> "$LOG_FILE"
  echo "" >> "$LOG_FILE"
  echo "Diff summary:" >> "$LOG_FILE"
  (cd "$CLAUDE_PROJECT_DIR" && git diff --stat) >> "$LOG_FILE"

  # Generate suggested commit message
  CHANGES=$(cd "$CLAUDE_PROJECT_DIR" && git diff --name-only 2>/dev/null | head -5 | tr '\n' ', ')
  echo "" >> "$LOG_FILE"
  echo "Suggested: Changes to ${CHANGES%,}" >> "$LOG_FILE"
else
  echo "Working directory clean." >> "$LOG_FILE"
fi

exit 0
