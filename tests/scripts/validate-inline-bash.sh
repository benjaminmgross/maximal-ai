#!/bin/bash
# Validate inline bash syntax in Claude Code command files
#
# This script extracts all inline bash commands (!\`...\`) from .md files
# and validates they parse correctly in both bash and zsh.
#
# Usage: ./tests/scripts/validate-inline-bash.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR/../.."
ERRORS=0
WARNINGS=0
CHECKED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

log_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}WARN:${NC} $1"
}

log_ok() {
    echo -e "${GREEN}OK:${NC} $1"
}

echo "Validating inline bash syntax in command files..."
echo "=================================================="
echo ""

# Check if zsh is available
ZSH_AVAILABLE=false
if command -v zsh &>/dev/null; then
    ZSH_AVAILABLE=true
    echo "zsh available - will test both bash and zsh"
else
    echo "zsh not available - will only test bash"
fi
echo ""

# Find all command files
COMMAND_DIR="$REPO_ROOT/.claude/commands"
if [ ! -d "$COMMAND_DIR" ]; then
    echo "No commands directory found at $COMMAND_DIR"
    exit 0
fi

for file in "$COMMAND_DIR"/*.md; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    file_errors=0

    # Extract inline bash commands
    # Pattern: lines starting with !` containing command between backticks
    # Format: !`command here` optional text after
    # These are Claude Code's inline bash execution markers
    while IFS= read -r line; do
        [ -z "$line" ] && continue

        # Extract just the command between !` and the closing `
        # Handle format: !`command` optional trailing text
        bash_cmd="${line#!\`}"

        # Find the first backtick and remove everything from there
        # This handles cases like: command` text after
        if [[ "$bash_cmd" == *"\`"* ]]; then
            bash_cmd="${bash_cmd%%\`*}"
        fi

        # Skip if empty after trimming
        [ -z "$bash_cmd" ] && continue

        CHECKED=$((CHECKED + 1))

        # Validate syntax with bash -n (parse only, don't execute)
        bash_error=$(bash -n <<< "$bash_cmd" 2>&1) || true
        if [ -n "$bash_error" ]; then
            if [ $file_errors -eq 0 ]; then
                echo "File: $filename"
            fi
            log_error "Bash parse error"
            echo "  Command: $bash_cmd"
            echo "  Error: $bash_error"
            echo ""
            ERRORS=$((ERRORS + 1))
            file_errors=$((file_errors + 1))
        fi

        # Also validate with zsh -n if available
        if $ZSH_AVAILABLE; then
            zsh_error=$(zsh -n <<< "$bash_cmd" 2>&1) || true
            if [ -n "$zsh_error" ]; then
                if [ $file_errors -eq 0 ]; then
                    echo "File: $filename"
                fi
                log_error "Zsh parse error"
                echo "  Command: $bash_cmd"
                echo "  Error: $zsh_error"
                echo ""
                ERRORS=$((ERRORS + 1))
                file_errors=$((file_errors + 1))
            fi
        fi

        # Check for known problematic patterns
        # Pattern 1: Variable assignment with $() followed by using that variable
        if [[ "$bash_cmd" =~ [A-Z_]+=\"?\$\( ]]; then
            if [ $file_errors -eq 0 ]; then
                echo "File: $filename"
            fi
            log_warn "Potentially problematic pattern: variable assignment with \$()"
            echo "  Command: $bash_cmd"
            echo "  Suggestion: Simplify to avoid intermediate variable assignment"
            echo ""
            WARNINGS=$((WARNINGS + 1))
        fi

    done < <(grep "^\!\`" "$file" 2>/dev/null || true)

done

echo ""
echo "=================================================="
echo "Summary:"
echo "  Files checked: $(ls -1 "$COMMAND_DIR"/*.md 2>/dev/null | wc -l)"
echo "  Commands checked: $CHECKED"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    log_error "FAILED: $ERRORS syntax errors found"
    echo ""
    echo "To fix:"
    echo "  1. Simplify complex commands (avoid variable assignment with \$())"
    echo "  2. Test manually: bash -n <<< 'your command'"
    echo "  3. See templates/testing.md for patterns to avoid"
    exit 1
else
    log_ok "PASSED: All inline bash commands are syntactically valid"
    if [ $WARNINGS -gt 0 ]; then
        echo "  (but $WARNINGS warnings - consider simplifying)"
    fi
    exit 0
fi
