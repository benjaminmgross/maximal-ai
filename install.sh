#!/bin/bash

# Install/Update the maximal-ai command
# Run this after pulling changes to update the installed binary

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_PATH="${HOME}/.local/bin"

echo "🔧 Installing maximal-ai command..."
echo ""

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_PATH"

# Generate the installation script
cat > "$INSTALL_PATH/maximal-ai" << 'EOF'
#!/bin/bash

# Maximal-AI: Advanced Context Engineering Setup
# Run this from any project directory to install the three-phase workflow

set -e

INSTALL_DIR="${MAXIMAL_AI_HOME:-$HOME/dev/maximal-ai}"
PROJECT_ROOT=$(pwd)

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "maximal-ai - Advanced Context Engineering Setup"
    echo ""
    echo "Usage: maximal-ai [command]"
    echo ""
    echo "Commands:"
    echo "  install    Install the three-phase workflow in current directory (default)"
    echo "  --help     Show this help message"
    echo "  --version  Show version information"
    echo ""
    echo "Examples:"
    echo "  maximal-ai           # Install in current directory"
    echo "  maximal-ai install   # Same as above"
    echo ""
    echo "After installation, use these commands in Claude:"
    echo "  /research        - Conduct comprehensive research"
    echo "  /plan            - Create implementation plan"
    echo "  /implement       - Execute the plan"
    echo "  /epic-oneshot    - Run all three phases in one session"
    echo "  /standup         - Generate progress report"
    echo "  /blocked         - Analyze blockers"
    echo "  /create_handoff  - Create handoff documentation for session transfer"
    echo "  /resume_handoff  - Resume work from handoff document"
    exit 0
fi

if [ "$1" = "--version" ]; then
    echo "maximal-ai version 1.1.0"
    echo "Advanced Context Engineering System"
    echo "Based on: github.com/humanlayer/humanlayer"
    exit 0
fi

echo "🚀 Advanced Context Engineering Setup"
echo "======================================"
echo ""
echo "📁 Installing in: $PROJECT_ROOT"
echo ""

# Verify source directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Error: MAXIMAL_AI_HOME directory not found: $INSTALL_DIR"
    echo ""
    echo "Please ensure:"
    echo "1. The maximal-ai repo is cloned"
    echo "2. MAXIMAL_AI_HOME is set correctly in your ~/.zshrc"
    echo "   export MAXIMAL_AI_HOME=\"\$HOME/dev/maximal-ai\""
    exit 1
fi

# Create necessary directories
echo "Creating directory structure..."
mkdir -p "$PROJECT_ROOT/.claude/commands"
mkdir -p "$PROJECT_ROOT/.claude/agents"
mkdir -p "$PROJECT_ROOT/research"
mkdir -p "$PROJECT_ROOT/plans"
mkdir -p "$PROJECT_ROOT/handoffs"

# Optional: Create docs directory for repo-specific documentation
if [ ! -d "$PROJECT_ROOT/docs" ]; then
    echo ""
    echo "Would you like to create a docs/ directory for repo-specific documentation?"
    echo "This enables the RPI workflow to suggest documentation updates after implementation."
    echo -n "(y/N): "
    read CREATE_DOCS
    if [ "$CREATE_DOCS" = "y" ] || [ "$CREATE_DOCS" = "Y" ]; then
        mkdir -p "$PROJECT_ROOT/docs"
        echo "Created docs/ directory"
    else
        echo "Skipping docs/ directory (can be created later)"
    fi
fi

# Username detection and configuration
echo ""
echo "Configuring username for RPI file naming..."

# Check if config.yaml exists and has username
CONFIG_FILE="$PROJECT_ROOT/.claude/config.yaml"
CONFIG_USERNAME=""

if [ -f "$CONFIG_FILE" ]; then
    CONFIG_USERNAME=$(grep "^username:" "$CONFIG_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
fi

if [ -n "$CONFIG_USERNAME" ]; then
    echo "Using existing username from config: $CONFIG_USERNAME"
    FINAL_USERNAME="$CONFIG_USERNAME"
else
    # Detect username from environment or git
    DETECTED_USERNAME="${RPI_USERNAME:-$(git config user.name 2>/dev/null | tr ' ' '-' | tr '[:upper:]' '[:lower:]')}"
    DETECTED_USERNAME="${DETECTED_USERNAME:-user}"

    # Prompt user for username
    echo ""
    echo "Detected username: $DETECTED_USERNAME"
    echo -n "Press Enter to use this username, or type a different one: "
    read USER_INPUT

    # Use input if provided, otherwise use detected
    if [ -n "$USER_INPUT" ]; then
        FINAL_USERNAME=$(echo "$USER_INPUT" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
        echo "Using username: $FINAL_USERNAME"
    else
        FINAL_USERNAME="$DETECTED_USERNAME"
        echo "Using username: $FINAL_USERNAME"
    fi

    # Create config.yaml with username
    cat > "$CONFIG_FILE" << EOC
# Maximal-AI Configuration
# Username for RPI file naming (YYYY.MM.DD-{username}-description.md)
username: $FINAL_USERNAME

# Additional settings can be added here
EOC
    echo "Created .claude/config.yaml with username: $FINAL_USERNAME"
fi

echo ""

# Copy command files
echo "Installing commands..."
cp "$INSTALL_DIR/.claude/commands/research.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/plan.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/implement.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/epic-oneshot.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/standup.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/blocked.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/create_handoff.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/resume_handoff.md" "$PROJECT_ROOT/.claude/commands/"

# Copy agent files
echo "Installing agents..."
cp "$INSTALL_DIR/.claude/agents/codebase-locator.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/codebase-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/codebase-pattern-finder.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/web-search-researcher.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/file-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/bug-hunter.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/test-runner.md" "$PROJECT_ROOT/.claude/agents/"

# Copy or merge CLAUDE.md
if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
    echo ""
    echo "⚠️  CLAUDE.md already exists in your project."
    echo "   The new configuration has been saved as CLAUDE.md.new"
    echo "   Please merge the configurations manually."
    cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md.new"
else
    echo "Installing CLAUDE.md configuration..."
    cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/"
fi

# Create .gitignore entries if needed
if [ -f "$PROJECT_ROOT/.gitignore" ]; then
    # Check if research/ and plans/ are already in gitignore
    if ! grep -q "^research/$" "$PROJECT_ROOT/.gitignore"; then
        echo "" >> "$PROJECT_ROOT/.gitignore"
        echo "# AI Context Engineering artifacts" >> "$PROJECT_ROOT/.gitignore"
        echo "research/" >> "$PROJECT_ROOT/.gitignore"
        echo "plans/" >> "$PROJECT_ROOT/.gitignore"
        echo "handoffs/" >> "$PROJECT_ROOT/.gitignore"
        echo "Added research/, plans/, and handoffs/ to .gitignore"
    fi

    # Add .claude/config.yaml to gitignore (each developer has their own username)
    if ! grep -q "^\.claude/config\.yaml$" "$PROJECT_ROOT/.gitignore"; then
        # Check if AI Context section already exists
        if ! grep -q "# AI Context Engineering" "$PROJECT_ROOT/.gitignore"; then
            echo "" >> "$PROJECT_ROOT/.gitignore"
            echo "# AI Context Engineering" >> "$PROJECT_ROOT/.gitignore"
        fi
        echo ".claude/config.yaml" >> "$PROJECT_ROOT/.gitignore"
        echo "Added .claude/config.yaml to .gitignore"
    fi
fi

echo ""
echo "✅ Installation Complete!"
echo ""
echo "📦 Installed:"
echo "   • 8 commands: research, plan, implement, epic-oneshot, standup, blocked, create_handoff, resume_handoff"
echo "   • 7 agents: locator, analyzer, pattern-finder, researcher, file-analyzer, bug-hunter, test-runner"
echo ""
echo "📄 Documentation destinations:"
if [ -n "$MINTY_DOCS_PATH" ]; then
    echo "   • Cross-cutting: $MINTY_DOCS_PATH"
else
    echo "   • Cross-cutting: Not configured (set MINTY_DOCS_PATH for cross-cutting docs)"
fi
if [ -d "$PROJECT_ROOT/docs" ]; then
    echo "   • Repo-specific: docs/"
else
    echo "   • Repo-specific: Not configured (create docs/ for repo-specific docs)"
fi
echo ""
echo "📚 Next Steps:"
echo "1. Open this project in Claude"
echo "2. Try the research command: /research [your question]"
echo "3. Create a plan: /plan [topic or research file]"
echo "4. Implement: /implement [plan file]"
echo ""
echo "📖 Documentation: $INSTALL_DIR/README.md"
echo ""
echo "Remember: Reset context between phases for best results!"
echo ""
echo "Happy coding with advanced context engineering! 🎉"
echo ""
EOF

# Make the script executable
chmod +x "$INSTALL_PATH/maximal-ai"

echo "✅ maximal-ai command installed to $INSTALL_PATH/maximal-ai"
echo ""
echo "📝 Make sure your PATH includes $INSTALL_PATH"
echo "   Add to ~/.zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "🧪 Test the installation:"
echo "   maximal-ai --version"
echo "   maximal-ai --help"
echo ""
echo "🚀 Use it in any project:"
echo "   cd /path/to/your/project"
echo "   maximal-ai"
echo ""
