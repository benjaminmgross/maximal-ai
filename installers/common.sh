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

# Verify MAXIMAL_AI_HOME is set and directory exists
verify_install_dir() {
    if [ ! -d "$INSTALL_DIR" ]; then
        error "Error: MAXIMAL_AI_HOME directory not found: $INSTALL_DIR"
        echo ""
        echo "To fix this, run the following commands:"
        echo ""
        echo "  # Clone the repository"
        echo "  git clone https://github.com/benjaminmgross/maximal-ai.git \$HOME/dev/maximal-ai"
        echo ""
        echo "  # Add to your shell configuration (~/.zshrc or ~/.bashrc)"
        echo "  export MAXIMAL_AI_HOME=\"\$HOME/dev/maximal-ai\""
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "  # Reload your shell and run the installer"
        echo "  source ~/.zshrc"
        echo "  cd \$MAXIMAL_AI_HOME && ./install.sh"
        echo ""
        echo "Would you like to set up now? (Run this in a new terminal after setup)"
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
    # Only prompt interactively — non-interactive runs (e.g. deploy-all.sh's
    # `while read` loop) would otherwise steal the next line of stdin.
    local user_input=""
    if [ -t 0 ]; then
        read -p "Press Enter to use this username, or type a different one: " user_input
    fi

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

# Symlink a command file from maximal-ai to the target project.
# Provides single-source-of-truth: edits to maximal-ai propagate instantly.
symlink_command() {
    local filename="$1"
    local source="$INSTALL_DIR/.claude/commands/$filename"
    local target="$PROJECT_ROOT/.claude/commands/$filename"

    if [ ! -f "$source" ]; then
        warn "  Source not found: $source"
        return 1
    fi

    # Remove existing file/symlink before creating new symlink
    rm -f "$target"

    # Use relative symlinks so they survive moves and aren't machine-specific
    local rel_path
    rel_path="$(python3 -c "import os.path,sys; print(os.path.relpath(sys.argv[1], os.path.dirname(sys.argv[2])))" "$source" "$target" 2>/dev/null)" || {
        warn "  python3 not available, falling back to absolute symlink"
        rel_path="$source"
    }
    ln -sf "$rel_path" "$target"

    # Verify the symlink actually resolves (catches broken relpath computation)
    if [ ! -e "$target" ]; then
        warn "  Symlink created but does not resolve: $target -> $rel_path"
        return 1
    fi
    echo "  ✓ Linked $filename → maximal-ai (relative)"
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
