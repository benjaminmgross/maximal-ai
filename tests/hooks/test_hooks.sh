#!/bin/bash
# Test suite for Claude Code hooks
# Run with: ./tests/hooks/test_hooks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
assert_exit_code() {
  local expected=$1
  local actual=$2
  local test_name=$3

  TESTS_RUN=$((TESTS_RUN + 1))
  if [ "$expected" -eq "$actual" ]; then
    echo -e "${GREEN}✓ PASS${NC}: $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗ FAIL${NC}: $test_name (expected exit $expected, got $actual)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_file_exists() {
  local file=$1
  local test_name=$2

  TESTS_RUN=$((TESTS_RUN + 1))
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓ PASS${NC}: $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗ FAIL${NC}: $test_name (file not found: $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_file_contains() {
  local file=$1
  local pattern=$2
  local test_name=$3

  TESTS_RUN=$((TESTS_RUN + 1))
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}: $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗ FAIL${NC}: $test_name (pattern not found in $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

assert_executable() {
  local file=$1
  local test_name=$2

  TESTS_RUN=$((TESTS_RUN + 1))
  if [ -x "$file" ]; then
    echo -e "${GREEN}✓ PASS${NC}: $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗ FAIL${NC}: $test_name (file not executable: $file)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ============================================
# Test: Hook files exist
# ============================================
echo ""
echo "=== Testing hook file existence ==="

assert_file_exists "$HOOKS_DIR/post-edit.sh" "post-edit.sh exists"
assert_file_exists "$HOOKS_DIR/pre-commit-check.sh" "pre-commit-check.sh exists"
assert_file_exists "$HOOKS_DIR/session-complete.sh" "session-complete.sh exists"
assert_file_exists "$HOOKS_DIR/auto-format.sh" "auto-format.sh exists"

# ============================================
# Test: Hook files are executable
# ============================================
echo ""
echo "=== Testing hook file permissions ==="

assert_executable "$HOOKS_DIR/post-edit.sh" "post-edit.sh is executable"
assert_executable "$HOOKS_DIR/pre-commit-check.sh" "pre-commit-check.sh is executable"
assert_executable "$HOOKS_DIR/session-complete.sh" "session-complete.sh is executable"
assert_executable "$HOOKS_DIR/auto-format.sh" "auto-format.sh is executable"

# ============================================
# Test: post-edit.sh - Skip non-source files
# ============================================
echo ""
echo "=== Testing post-edit.sh ==="

# Create temp log file
TEST_LOG="/tmp/claude-test-results-test.log"
rm -f "$TEST_LOG"

# Test with non-source file (should exit 0, no logging)
export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"
echo '{"tool_input": {"file_path": "/tmp/test.txt"}}' | "$HOOKS_DIR/post-edit.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "post-edit.sh exits 0 for non-source file"

# Test with empty input (should exit 0)
echo '{}' | "$HOOKS_DIR/post-edit.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "post-edit.sh exits 0 for empty input"

# ============================================
# Test: pre-commit-check.sh - Non-commit commands pass through
# ============================================
echo ""
echo "=== Testing pre-commit-check.sh ==="

# Test non-commit command (should pass through)
echo '{"tool_input": {"command": "git status"}}' | "$HOOKS_DIR/pre-commit-check.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "pre-commit-check.sh passes through non-commit commands"

# Test empty input
echo '{}' | "$HOOKS_DIR/pre-commit-check.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "pre-commit-check.sh handles empty input"

# ============================================
# Test: session-complete.sh - Creates log file
# ============================================
echo ""
echo "=== Testing session-complete.sh ==="

SESSION_LOG="/tmp/claude-session-summary.log"
rm -f "$SESSION_LOG"

export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"
"$HOOKS_DIR/session-complete.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "session-complete.sh exits 0"
assert_file_exists "$SESSION_LOG" "session-complete.sh creates log file"
assert_file_contains "$SESSION_LOG" "Session ended" "session-complete.sh logs session end"

# ============================================
# Test: auto-format.sh - Handles missing file gracefully
# ============================================
echo ""
echo "=== Testing auto-format.sh ==="

# Test with non-existent file (should exit 0)
echo '{"tool_input": {"file_path": "/tmp/nonexistent_file_12345.py"}}' | "$HOOKS_DIR/auto-format.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "auto-format.sh exits 0 for missing file"

# Test with empty input
echo '{}' | "$HOOKS_DIR/auto-format.sh"
EXIT_CODE=$?
assert_exit_code 0 $EXIT_CODE "auto-format.sh handles empty input"

# ============================================
# Summary
# ============================================
echo ""
echo "=========================================="
echo -e "Tests run: $TESTS_RUN"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "=========================================="

if [ $TESTS_FAILED -gt 0 ]; then
  exit 1
fi

exit 0
