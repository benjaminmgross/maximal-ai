#!/bin/bash
# Test installer with various project structures
#
# Usage: ./tests/scripts/test-installer.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR/../.."
TEST_DIR="/tmp/maximal-ai-installer-test-$$"
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

log_pass() {
    echo -e "  ${GREEN}PASS:${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
    echo -e "  ${RED}FAIL:${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_info() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

echo "Testing Maximal-AI Installer"
echo "============================"
echo ""
echo "Test directory: $TEST_DIR"
echo ""

mkdir -p "$TEST_DIR"

# ============================================
# Test 1: RPI Workflow on JavaScript project
# ============================================
log_info "RPI Workflow on JavaScript project (src/)"

mkdir -p "$TEST_DIR/js-project/src/components"
cd "$TEST_DIR/js-project"
git init -q
git config user.email "test@example.com"
git config user.name "Test User"
echo '{"name": "test-js-project", "version": "1.0.0"}' > package.json

export MAXIMAL_AI_HOME="$REPO_ROOT"
bash "$REPO_ROOT/installers/rpi-workflow.sh" > /dev/null 2>&1

if [ -f ".claude/commands/research.md" ]; then
    log_pass "Commands installed"
else
    log_fail "Missing .claude/commands/research.md"
fi

if [ -d "thoughts/research" ] && [ -d "thoughts/plans" ] && [ -d "thoughts/handoffs" ]; then
    log_pass "thoughts/ directories created"
else
    log_fail "Missing thoughts/ directories"
fi

if [ -f ".claude/agents/codebase-analyzer.md" ]; then
    log_pass "Agents installed"
else
    log_fail "Missing .claude/agents/codebase-analyzer.md"
fi

if [ -f "CLAUDE.md" ]; then
    log_pass "CLAUDE.md created"
else
    log_fail "Missing CLAUDE.md"
fi

echo ""

# ============================================
# Test 2: RPI Workflow on Python project
# ============================================
log_info "RPI Workflow on Python project (app/)"

mkdir -p "$TEST_DIR/py-project/app/models"
cd "$TEST_DIR/py-project"
git init -q
git config user.email "test@example.com"
git config user.name "Test User"
echo "flask>=2.0.0" > requirements.txt
touch app/__init__.py

bash "$REPO_ROOT/installers/rpi-workflow.sh" > /dev/null 2>&1

if [ -f ".claude/commands/research.md" ]; then
    log_pass "Commands installed for Python project"
else
    log_fail "Missing commands for Python project"
fi

if [ -f "CLAUDE.md" ]; then
    log_pass "CLAUDE.md created for Python project"
else
    log_fail "Missing CLAUDE.md for Python project"
fi

echo ""

# ============================================
# Test 3: Idempotency - running twice
# ============================================
log_info "Idempotency test (running installer twice)"

cd "$TEST_DIR/js-project"
output=$(bash "$REPO_ROOT/installers/rpi-workflow.sh" 2>&1)

if echo "$output" | grep -q -i "skip\|exist"; then
    log_pass "Installer recognizes existing files"
else
    log_fail "Installer should skip existing files"
fi

echo ""

# ============================================
# Test 4: Command files have valid frontmatter
# ============================================
log_info "Command files have valid YAML frontmatter"

valid_frontmatter=true
for cmd in "$TEST_DIR/js-project/.claude/commands"/*.md; do
    [ -f "$cmd" ] || continue
    if ! head -1 "$cmd" | grep -q "^---$"; then
        log_fail "$(basename "$cmd") missing YAML frontmatter"
        valid_frontmatter=false
        break
    fi
done

if $valid_frontmatter; then
    log_pass "All command files have YAML frontmatter"
fi

echo ""

# ============================================
# Test 5: Empty project (no src/ or app/)
# ============================================
log_info "Empty project (no src/ or app/)"

mkdir -p "$TEST_DIR/empty-project"
cd "$TEST_DIR/empty-project"
git init -q
git config user.email "test@example.com"
git config user.name "Test User"

bash "$REPO_ROOT/installers/rpi-workflow.sh" > /dev/null 2>&1

if [ -f ".claude/commands/research.md" ]; then
    log_pass "Commands installed for empty project"
else
    log_fail "Commands should install even without src/ or app/"
fi

echo ""

# ============================================
# Summary
# ============================================
echo "=========================================="
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "=========================================="

if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
fi

exit 0
