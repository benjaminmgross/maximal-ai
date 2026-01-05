#!/bin/bash

# Auto-format hook with graceful degradation
# Formats files using available tools (prettier, ruff, black)
# If tools are not installed, the hook silently continues

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

# Skip if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only format if file exists and is a source file
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# JavaScript/TypeScript: Use Prettier if available
# Gracefully degrades if prettier is not installed
if [[ "$FILE_PATH" =~ \.(js|jsx|ts|tsx|json|md)$ ]]; then
  if command -v npx &> /dev/null && [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
    # Check if prettier is available in the project
    if (cd "$CLAUDE_PROJECT_DIR" && npx prettier --version &>/dev/null 2>&1); then
      (cd "$CLAUDE_PROJECT_DIR" && npx prettier --write "$FILE_PATH" 2>/dev/null) || true
    fi
    # If prettier is not available, silently continue
  fi
fi

# Python: Use Ruff if available, fall back to Black, or silently skip
if [[ "$FILE_PATH" =~ \.py$ ]]; then
  if command -v ruff &> /dev/null; then
    ruff format "$FILE_PATH" 2>/dev/null || true
    ruff check --fix "$FILE_PATH" 2>/dev/null || true
  elif command -v black &> /dev/null; then
    black "$FILE_PATH" 2>/dev/null || true
  fi
  # If neither ruff nor black is available, silently continue
fi

exit 0
