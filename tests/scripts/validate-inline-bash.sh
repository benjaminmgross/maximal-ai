#!/bin/bash
# Validate inline bash syntax in command files for both bash and zsh
#
# Usage: ./tests/scripts/validate-inline-bash.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR/../.."
COMMANDS_DIR="$REPO_ROOT/.claude/commands"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ERRORS=0
COMMANDS_CHECKED=0
PATTERNS_CHECKED=0

echo "Validating inline bash syntax in command files..."
echo ""

# Check if zsh is available
HAS_ZSH=false
if command -v zsh &>/dev/null; then
    HAS_ZSH=true
    echo "✓ zsh detected - will test cross-shell compatibility"
else
    echo "⚠ zsh not found - testing bash only"
fi
echo ""

# Process each command file
for file in "$COMMANDS_DIR"/*.md; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    COMMANDS_CHECKED=$((COMMANDS_CHECKED + 1))
    file_errors=0

    # Extract inline bash commands (!`...`)
    while IFS= read -r line; do
        # Extract the command between !` and `
        cmd=$(echo "$line" | grep -oP '!\`\K[^`]+' 2>/dev/null || true)
        [ -z "$cmd" ] && continue

        PATTERNS_CHECKED=$((PATTERNS_CHECKED + 1))

        # Replace variables with test values
        test_cmd="${cmd//\$ARGUMENTS/123}"
        test_cmd="${test_cmd//\$1/123}"
        test_cmd="${test_cmd//\$2/test}"

        # Test in bash
        if ! bash -n <<< "$test_cmd" 2>/dev/null; then
            echo -e "${RED}BASH ERROR${NC} in $filename:"
            echo "  Command: ${cmd:0:60}..."
            bash -n <<< "$test_cmd" 2>&1 | sed 's/^/  /'
            file_errors=$((file_errors + 1))
            ERRORS=$((ERRORS + 1))
        fi

        # Test in zsh if available
        if $HAS_ZSH; then
            if ! zsh -n <<< "$test_cmd" 2>/dev/null; then
                echo -e "${YELLOW}ZSH ERROR${NC} in $filename:"
                echo "  Command: ${cmd:0:60}..."
                zsh -n <<< "$test_cmd" 2>&1 | sed 's/^/  /'
                file_errors=$((file_errors + 1))
                ERRORS=$((ERRORS + 1))
            fi
        fi
    done < <(grep -E '!\`[^`]+\`' "$file" 2>/dev/null || true)

    if [ $file_errors -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $filename"
    fi
done

echo ""
echo "=========================================="
echo "Commands checked: $COMMANDS_CHECKED"
echo "Patterns checked: $PATTERNS_CHECKED"
if [ $ERRORS -gt 0 ]; then
    echo -e "Errors: ${RED}$ERRORS${NC}"
    exit 1
else
    echo -e "Errors: ${GREEN}0${NC}"
    echo "All inline bash commands are syntactically valid"
    exit 0
fi
