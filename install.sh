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
    echo "  /research      - Conduct comprehensive research"
    echo "  /plan          - Create implementation plan"
    echo "  /implement     - Execute the plan"
    echo "  /epic-oneshot  - Run all three phases in one session"
    echo "  /standup       - Generate progress report"
    echo "  /blocked       - Analyze blockers"
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

# Copy command files
echo "Installing commands..."
cp "$INSTALL_DIR/.claude/commands/research.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/plan.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/implement.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/epic-oneshot.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/standup.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/blocked.md" "$PROJECT_ROOT/.claude/commands/"

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
        echo "Added research/ and plans/ to .gitignore"
    fi
fi

echo ""
echo "✅ Installation Complete!"
echo ""
echo "📦 Installed:"
echo "   • 6 commands: research, plan, implement, epic-oneshot, standup, blocked"
echo "   • 7 agents: locator, analyzer, pattern-finder, researcher, file-analyzer, bug-hunter, test-runner"
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
