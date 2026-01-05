#!/bin/bash
# RDF Framework Installer
# Installs the Repo Documentation Framework with layer-based selection

INSTALL_DIR="${MAXIMAL_AI_HOME:-$HOME/dev/maximal-ai}"
PROJECT_ROOT=$(pwd)

# Source common functions
source "$INSTALL_DIR/installers/common.sh"

# Verify install directory exists
verify_install_dir

show_rdf_help() {
    echo "RDF Framework Installer"
    echo ""
    echo "Usage: maximal-ai rdf-framework [options]"
    echo ""
    echo "Options:"
    echo "  -l, --layers LAYERS   Comma-separated layer numbers (1-5)"
    echo "  --global              Install rdf CLI globally (default)"
    echo "  --local               Copy rdf scripts to project's scripts/"
    echo "  --help                Show this help message"
    echo ""
    echo "Layers:"
    echo "  1 - Entry Points (AGENTS.md, CLAUDE.md, .repomap.yaml)"
    echo "  2 - Code Docs (.folder.md generator, scaffolding)"
    echo "  3 - Extended Docs (protocols/, checklists/, guides/)"
    echo "  4 - Cross-Repo (minty-docs linkage via \$MINTY_DOCS_PATH)"
    echo "  5 - Tooling (rdf CLI, linters)"
    echo ""
    echo "Examples:"
    echo "  maximal-ai rdf-framework             # Interactive selection"
    echo "  maximal-ai rdf-framework -l 1       # Layer 1 only"
    echo "  maximal-ai rdf-framework -l 1,2,3  # Layers 1-3"
    echo "  maximal-ai rdf-framework -l 1,2,3,4,5 --local  # All layers, local install"
}

# Parse arguments
LAYERS=""
INSTALL_MODE="global"

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--layers)
            LAYERS="$2"
            shift 2
            ;;
        --local)
            INSTALL_MODE="local"
            shift
            ;;
        --global)
            INSTALL_MODE="global"
            shift
            ;;
        --help|-h)
            show_rdf_help
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Interactive layer selection if not specified
if [ -z "$LAYERS" ]; then
    echo ""
    info "RDF Framework - Layer Selection"
    echo "================================"
    echo ""
    echo "RDF has 5 layers. Select which to install:"
    echo ""
    echo "Layer 1: Entry Points (AGENTS.md, CLAUDE.md, .repomap.yaml)"
    echo "Layer 2: Code Docs (.folder.md generator, REPOMAP.yaml config)"
    echo "Layer 3: Extended Docs (protocols/, checklists/, guides/)"
    echo "Layer 4: Cross-Repo (minty-docs linkage)"
    echo "Layer 5: Tooling (rdf CLI, linters)"
    echo ""
    echo "Options:"
    echo "  1) Layer 1 only (minimal)"
    echo "  2) Layers 1-2 (basic documentation)"
    echo "  3) Layers 1-3 (full single-repo)"
    echo "  4) Layers 1-4 (with cross-repo)"
    echo "  5) All layers (full toolkit)"
    echo "  c) Custom selection"
    echo ""
    read -p "Enter choice [1-5/c]: " choice

    case $choice in
        1) LAYERS="1" ;;
        2) LAYERS="1,2" ;;
        3) LAYERS="1,2,3" ;;
        4) LAYERS="1,2,3,4" ;;
        5) LAYERS="1,2,3,4,5" ;;
        c)
            echo "Enter layers (comma-separated, e.g., 1,2,5): "
            read LAYERS
            ;;
        *)
            error "Invalid choice"
            exit 1
            ;;
    esac
fi

# Installation mode selection for Layer 5
if [[ "$LAYERS" == *"5"* ]]; then
    echo ""
    echo "Layer 5 includes the rdf CLI tool."
    echo "How would you like to install it?"
    echo ""
    echo "1) Global (pip install to ~/.local/bin/rdf)"
    echo "2) Local (copy scripts to project's scripts/)"
    echo ""
    read -p "Enter choice [1-2]: " mode_choice
    case $mode_choice in
        1) INSTALL_MODE="global" ;;
        2) INSTALL_MODE="local" ;;
    esac
fi

# Layer installation functions
install_layer1() {
    info "Installing Layer 1: Entry Points..."

    mkdir -p "$PROJECT_ROOT/docs"

    # Create AGENTS.md from template
    if [ ! -f "$PROJECT_ROOT/docs/AGENTS.md" ]; then
        if [ -f "$INSTALL_DIR/templates/rdf/layer1/AGENTS.md.template" ]; then
            cp "$INSTALL_DIR/templates/rdf/layer1/AGENTS.md.template" "$PROJECT_ROOT/docs/AGENTS.md"
            echo "  Created docs/AGENTS.md"
        else
            warn "  Template not found: templates/rdf/layer1/AGENTS.md.template"
        fi
    else
        echo "  Skipped docs/AGENTS.md (exists)"
    fi

    # Create CLAUDE.md from template (in docs/ per RDF spec)
    if [ ! -f "$PROJECT_ROOT/docs/CLAUDE.md" ]; then
        if [ -f "$INSTALL_DIR/templates/rdf/layer1/CLAUDE.md.template" ]; then
            cp "$INSTALL_DIR/templates/rdf/layer1/CLAUDE.md.template" "$PROJECT_ROOT/docs/CLAUDE.md"
            echo "  Created docs/CLAUDE.md"
        else
            warn "  Template not found: templates/rdf/layer1/CLAUDE.md.template"
        fi
    else
        echo "  Skipped docs/CLAUDE.md (exists)"
    fi

    # Create .repomap.yaml config
    if [ ! -f "$PROJECT_ROOT/.repomap.yaml" ]; then
        if [ -f "$INSTALL_DIR/templates/rdf/layer1/.repomap.yaml.template" ]; then
            cp "$INSTALL_DIR/templates/rdf/layer1/.repomap.yaml.template" "$PROJECT_ROOT/.repomap.yaml"
            echo "  Created .repomap.yaml"
        else
            warn "  Template not found: templates/rdf/layer1/.repomap.yaml.template"
        fi
    else
        echo "  Skipped .repomap.yaml (exists)"
    fi
}

install_layer2() {
    info "Installing Layer 2: Code Docs..."

    # Create .folder.md template at src/ root if exists
    if [ -d "$PROJECT_ROOT/src" ] && [ ! -f "$PROJECT_ROOT/src/.folder.md" ]; then
        if [ -f "$INSTALL_DIR/templates/rdf/layer2/.folder.md.template" ]; then
            cp "$INSTALL_DIR/templates/rdf/layer2/.folder.md.template" "$PROJECT_ROOT/src/.folder.md"
            echo "  Created src/.folder.md template"
        fi
    fi

    # Prompt for scaffolding
    echo ""
    echo "Would you like to scaffold .folder.md files in all source directories?"
    read -p "(y/N): " scaffold
    if [ "$scaffold" = "y" ] || [ "$scaffold" = "Y" ]; then
        if command -v rdf &> /dev/null; then
            rdf scaffold-folders src/
        else
            warn "  (rdf command not available - install Layer 5 first, then run: rdf scaffold-folders src/)"
        fi
    fi
}

install_layer3() {
    info "Installing Layer 3: Extended Docs..."

    mkdir -p "$PROJECT_ROOT/docs/ai/protocols"
    mkdir -p "$PROJECT_ROOT/docs/ai/checklists"
    mkdir -p "$PROJECT_ROOT/docs/ai/prompts"
    mkdir -p "$PROJECT_ROOT/docs/guides"
    mkdir -p "$PROJECT_ROOT/docs/templates"
    mkdir -p "$PROJECT_ROOT/docs/architecture/decisions"

    # Create .folder.md files
    if [ -f "$INSTALL_DIR/templates/rdf/layer3/protocols.folder.md" ]; then
        cp "$INSTALL_DIR/templates/rdf/layer3/protocols.folder.md" "$PROJECT_ROOT/docs/ai/protocols/.folder.md"
    fi
    if [ -f "$INSTALL_DIR/templates/rdf/layer3/checklists.folder.md" ]; then
        cp "$INSTALL_DIR/templates/rdf/layer3/checklists.folder.md" "$PROJECT_ROOT/docs/ai/checklists/.folder.md"
    fi
    if [ -f "$INSTALL_DIR/templates/rdf/layer3/guides.folder.md" ]; then
        cp "$INSTALL_DIR/templates/rdf/layer3/guides.folder.md" "$PROJECT_ROOT/docs/guides/.folder.md"
    fi

    echo "  Created docs/ai/{protocols,checklists,prompts}/"
    echo "  Created docs/{guides,templates,architecture/decisions}/"
}

install_layer4() {
    info "Installing Layer 4: Cross-Repo..."

    if [ -n "$MINTY_DOCS_PATH" ]; then
        echo "  MINTY_DOCS_PATH detected: $MINTY_DOCS_PATH"
        echo "  Cross-cutting standards available at: $MINTY_DOCS_PATH/cross-cutting/"

        # Add reference to AGENTS.md
        if [ -f "$PROJECT_ROOT/docs/AGENTS.md" ]; then
            if ! grep -q "MINTY_DOCS_PATH" "$PROJECT_ROOT/docs/AGENTS.md"; then
                cat >> "$PROJECT_ROOT/docs/AGENTS.md" << 'EOFAGENTS'

## Company-Wide Standards

For organization-wide coding standards, see:
- **$MINTY_DOCS_PATH/cross-cutting/coding-standards/** - Python style, docstrings, testing
- **$MINTY_DOCS_PATH/cross-cutting/ai/** - Shared AI protocols and checklists
EOFAGENTS
                echo "  Updated docs/AGENTS.md with minty-docs reference"
            fi
        fi
    else
        warn "  MINTY_DOCS_PATH not set - skipping cross-repo integration"
        echo "  Set MINTY_DOCS_PATH in ~/.zshrc to enable cross-repo docs"
    fi
}

install_layer5() {
    info "Installing Layer 5: Tooling..."

    if [ "$INSTALL_MODE" = "global" ]; then
        echo "  Installing rdf CLI globally..."
        cd "$INSTALL_DIR"
        if command -v uv &> /dev/null; then
            uv pip install -e .
        elif command -v pip &> /dev/null; then
            pip install -e .
        else
            error "  Neither uv nor pip found. Please install Python package manager."
            return 1
        fi
        echo "  rdf CLI installed globally"
    else
        echo "  Installing rdf scripts locally..."
        mkdir -p "$PROJECT_ROOT/scripts"
        cp "$INSTALL_DIR/src/rdf/cli.py" "$PROJECT_ROOT/scripts/rdf_cli.py"
        cp -r "$INSTALL_DIR/src/rdf/generators" "$PROJECT_ROOT/scripts/"
        cp -r "$INSTALL_DIR/src/rdf/linters" "$PROJECT_ROOT/scripts/"
        echo "  Copied rdf scripts to scripts/"
        echo "  Run with: python scripts/rdf_cli.py [command]"
    fi
}

# Execute installation
echo ""
info "Installing RDF Framework (Layers: $LAYERS)"
echo ""

for layer in $(echo $LAYERS | tr ',' ' '); do
    case $layer in
        1) install_layer1 ;;
        2) install_layer2 ;;
        3) install_layer3 ;;
        4) install_layer4 ;;
        5) install_layer5 ;;
        *) warn "Unknown layer: $layer" ;;
    esac
done

echo ""
info "RDF Framework installation complete!"
echo ""
echo "Installed layers: $LAYERS"
echo ""
if [[ "$LAYERS" == *"5"* ]]; then
    echo "Next steps:"
    echo "  rdf --help          # See available commands"
    echo "  rdf init --dry-run  # Preview RDF initialization"
    echo "  rdf validate        # Check RDF compliance"
fi
