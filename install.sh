#!/bin/bash

# Install/Update the maximal-ai command
# Run this after pulling changes to update the installed binary

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_PATH="${HOME}/.local/bin"

echo "Installing maximal-ai command..."
echo ""

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_PATH"

# Generate the installation script
cat > "$INSTALL_PATH/maximal-ai" << 'EOF'
#!/bin/bash

# Maximal-AI: Modular AI Development Toolkit
# Version 2.0.0

set -e

INSTALL_DIR="${MAXIMAL_AI_HOME:-$HOME/dev/maximal-ai}"
VERSION="2.0.0"

show_help() {
    echo "maximal-ai - Modular AI Development Toolkit"
    echo ""
    echo "Usage: maximal-ai [command] [options]"
    echo ""
    echo "Commands:"
    echo "  rpi-workflow     Install the three-phase Research/Plan/Implement workflow"
    echo "  rdf-framework    Install the Repo Documentation Framework"
    echo "  complete         Install both RPI workflow and RDF framework"
    echo "  (no command)     Interactive mode - choose what to install"
    echo ""
    echo "Options:"
    echo "  --help, -h       Show this help message"
    echo "  --version, -v    Show version information"
    echo ""
    echo "Examples:"
    echo "  maximal-ai                    # Interactive mode"
    echo "  maximal-ai rpi-workflow       # Install RPI workflow"
    echo "  maximal-ai rdf-framework      # Install RDF framework"
    echo "  maximal-ai rdf-framework -l 1 # Install RDF Layer 1 only"
    echo "  maximal-ai complete           # Install both frameworks"
    echo ""
    echo "After installation, use these commands in Claude:"
    echo "  /research        - Conduct comprehensive research"
    echo "  /plan            - Create implementation plan"
    echo "  /implement       - Execute the plan"
    echo "  /epic-oneshot    - Run all three phases in one session"
    echo "  /standup         - Generate progress report"
    echo "  /blocked         - Analyze blockers"
    echo "  /create_handoff  - Create handoff documentation"
    echo "  /resume_handoff  - Resume work from handoff document"
    echo ""
    echo "RDF CLI (if Layer 5 installed):"
    echo "  rdf --help       - Show RDF CLI commands"
    echo "  rdf init         - Initialize RDF in repository"
    echo "  rdf scaffold-folders src/  - Create .folder.md files"
    echo "  rdf validate     - Check RDF compliance"
}

# Command routing
case "${1:-interactive}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --version|-v)
        echo "maximal-ai version $VERSION"
        echo "Modular AI Development Toolkit"
        echo ""
        echo "Components:"
        echo "  - RPI Workflow (Research/Plan/Implement)"
        echo "  - RDF Framework (Repo Documentation Framework)"
        exit 0
        ;;
    rpi-workflow)
        shift
        source "$INSTALL_DIR/installers/rpi-workflow.sh" "$@"
        ;;
    rdf-framework)
        shift
        source "$INSTALL_DIR/installers/rdf-framework.sh" "$@"
        ;;
    complete)
        shift
        echo ""
        echo "Installing complete Maximal-AI toolkit..."
        echo ""
        source "$INSTALL_DIR/installers/rpi-workflow.sh" "$@"
        echo ""
        echo "---"
        echo ""
        source "$INSTALL_DIR/installers/rdf-framework.sh" "$@"
        ;;
    interactive|"")
        echo ""
        echo "Maximal-AI: Modular AI Development Toolkit"
        echo "=============================================="
        echo ""
        echo "What would you like to install?"
        echo ""
        echo "1) RPI Workflow - Research -> Plan -> Implement workflow"
        echo "2) RDF Framework - Repo Documentation Framework"
        echo "3) Both - Full AI development toolkit"
        echo "4) Cancel"
        echo ""
        read -p "Enter choice [1-4]: " choice

        case $choice in
            1)
                source "$INSTALL_DIR/installers/rpi-workflow.sh"
                ;;
            2)
                source "$INSTALL_DIR/installers/rdf-framework.sh"
                ;;
            3)
                source "$INSTALL_DIR/installers/rpi-workflow.sh"
                echo ""
                echo "---"
                echo ""
                source "$INSTALL_DIR/installers/rdf-framework.sh"
                ;;
            4)
                echo "Cancelled."
                exit 0
                ;;
            *)
                echo "Invalid choice"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run 'maximal-ai --help' for usage."
        exit 1
        ;;
esac
EOF

# Make the script executable
chmod +x "$INSTALL_PATH/maximal-ai"

echo "maximal-ai command installed to $INSTALL_PATH/maximal-ai"
echo ""
echo "Make sure your PATH includes $INSTALL_PATH"
echo "   Add to ~/.zshrc: export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Test the installation:"
echo "   maximal-ai --version"
echo "   maximal-ai --help"
echo ""
echo "Use it in any project:"
echo "   cd /path/to/your/project"
echo "   maximal-ai"
echo ""
