#!/bin/bash
# Common functions shared by installers

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored messages
info() {
    echo -e "${GREEN}$1${NC}"
}

warn() {
    echo -e "${YELLOW}$1${NC}"
}

error() {
    echo -e "${RED}$1${NC}"
}

# Verify MAXIMAL_AI_HOME is set
verify_install_dir() {
    if [ ! -d "$INSTALL_DIR" ]; then
        error "Error: MAXIMAL_AI_HOME directory not found: $INSTALL_DIR"
        echo ""
        echo "Please ensure:"
        echo "1. The maximal-ai repo is cloned"
        echo "2. MAXIMAL_AI_HOME is set correctly in your ~/.zshrc"
        echo "   export MAXIMAL_AI_HOME=\"\$HOME/dev/maximal-ai\""
        exit 1
    fi
}

# Get username from config or prompt user
get_username() {
    local config_file="$PROJECT_ROOT/.claude/config.yaml"
    local config_username=""

    if [ -f "$config_file" ]; then
        config_username=$(grep "^username:" "$config_file" 2>/dev/null | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
    fi

    if [ -n "$config_username" ]; then
        echo "$config_username"
        return
    fi

    # Detect username from environment or git
    local detected="${RPI_USERNAME:-$(git config user.name 2>/dev/null | tr ' ' '-' | tr '[:upper:]' '[:lower:]')}"
    detected="${detected:-user}"

    echo ""
    echo "Detected username: $detected"
    echo -n "Press Enter to use this username, or type a different one: "
    read user_input

    if [ -n "$user_input" ]; then
        echo "$user_input" | tr ' ' '-' | tr '[:upper:]' '[:lower:]'
    else
        echo "$detected"
    fi
}

# Save username to config
save_username() {
    local username="$1"
    local config_file="$PROJECT_ROOT/.claude/config.yaml"

    cat > "$config_file" << EOC
# Maximal-AI Configuration
# Username for RPI file naming (YYYY.MM.DD-{username}-description.md)
username: $username

# Additional settings can be added here
EOC
    info "Created .claude/config.yaml with username: $username"
}

# Add entry to .gitignore if not present
add_to_gitignore() {
    local entry="$1"
    local comment="$2"

    if [ -f "$PROJECT_ROOT/.gitignore" ]; then
        if ! grep -q "^${entry}$" "$PROJECT_ROOT/.gitignore"; then
            if [ -n "$comment" ] && ! grep -q "$comment" "$PROJECT_ROOT/.gitignore"; then
                echo "" >> "$PROJECT_ROOT/.gitignore"
                echo "$comment" >> "$PROJECT_ROOT/.gitignore"
            fi
            echo "$entry" >> "$PROJECT_ROOT/.gitignore"
            echo "Added $entry to .gitignore"
        fi
    fi
}
