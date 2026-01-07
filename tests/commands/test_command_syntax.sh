#!/bin/bash
# Validate slash command files for known Claude Code inline bash limitations
# Run with: ./tests/commands/test_command_syntax.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

echo "=== Validating Slash Command Syntax ==="
echo ""

# Unsafe patterns that cause Claude Code inline bash to fail
# These patterns use command substitution $() which gets over-escaped
UNSAFE_PATTERNS=(
    'VAR=\$\('           # Variable assignment with command substitution
    '\$\(\('             # Arithmetic expansion $(())
    '\[\['               # Bash conditionals [[
)

for cmd_file in "$COMMANDS_DIR"/*.md; do
    filename=$(basename "$cmd_file")
    TESTS_RUN=$((TESTS_RUN + 1))

    has_issues=false

    for pattern in "${UNSAFE_PATTERNS[@]}"; do
        # Only check within inline bash patterns !`...`
        if grep -E "!\`[^\`]*${pattern}" "$cmd_file" >/dev/null 2>&1; then
            if [ "$has_issues" = false ]; then
                echo -e "${RED}✗ FAIL${NC}: $filename"
                has_issues=true
            fi
            echo "  - Contains unsafe pattern: $pattern"
            # Show the matching line
            grep -n -E "!\`[^\`]*${pattern}" "$cmd_file" | head -2 | sed 's/^/    /'
        fi
    done

    if [ "$has_issues" = false ]; then
        echo -e "${GREEN}✓ PASS${NC}: $filename"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
done

echo ""
echo "=========================================="
echo "Tests run: $TESTS_RUN"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "=========================================="

if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
fi

exit 0
