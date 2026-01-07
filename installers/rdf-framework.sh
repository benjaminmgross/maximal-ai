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
    echo "  4 - Cross-Repo (external docs linkage via \$EXTERNAL_DOCS_PATH)"
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

    # Discover source directories by looking for code files
    echo ""
    echo "Discovering source directories..."
    echo ""

    # Find all directories containing source files, excluding common non-source dirs
    # This creates a list of potential source roots
    DISCOVERED_DIRS=$(find "$PROJECT_ROOT" -type f \( \
        -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
        -o -name "*.go" -o -name "*.rs" -o -name "*.rb" -o -name "*.java" \
    \) 2>/dev/null | \
        grep -v -E "(node_modules|\.git|__pycache__|\.venv|venv|\.tox|build|dist|\.egg-info|\.mypy_cache|\.pytest_cache|\.ruff_cache)" | \
        xargs -I {} dirname {} 2>/dev/null | \
        sort -u | \
        # Get relative paths from PROJECT_ROOT
        sed "s|^$PROJECT_ROOT/||" | \
        # Filter to top-level source directories (first component)
        cut -d'/' -f1 | \
        sort -u | \
        # Exclude hidden directories and common non-source dirs
        grep -v -E "^(\.|node_modules|docs|tests?|spec|fixtures|coverage|htmlcov)$" || true)

    if [ -z "$DISCOVERED_DIRS" ]; then
        warn "No source directories found with code files."
        echo ""
        echo "You can manually specify directories later with:"
        echo "  rdf scaffold-folders <directory>"
        return 0
    fi

    # Count files and subdirs for each discovered directory
    echo "Found the following source directories:"
    echo ""
    echo "┌─────────────────────────────────────────────────────────────────┐"
    printf "│ %-3s %-25s %10s %10s │\n" "#" "Directory" "Files" "Subdirs"
    echo "├─────────────────────────────────────────────────────────────────┤"

    COUNTER=1
    DIR_ARRAY=()
    for dir in $DISCOVERED_DIRS; do
        if [ -d "$PROJECT_ROOT/$dir" ]; then
            # Count source files
            FILE_COUNT=$(find "$PROJECT_ROOT/$dir" -type f \( \
                -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
                -o -name "*.go" -o -name "*.rs" -o -name "*.rb" -o -name "*.java" \
            \) 2>/dev/null | wc -l)

            # Count subdirectories (excluding hidden and __pycache__)
            SUBDIR_COUNT=$(find "$PROJECT_ROOT/$dir" -type d 2>/dev/null | \
                grep -v -E "(__pycache__|\.)" | wc -l)
            SUBDIR_COUNT=$((SUBDIR_COUNT - 1))  # Exclude the dir itself

            printf "│ %-3s %-25s %10s %10s │\n" "$COUNTER" "$dir/" "$FILE_COUNT" "$SUBDIR_COUNT"
            DIR_ARRAY+=("$dir")
            COUNTER=$((COUNTER + 1))
        fi
    done

    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""

    # Selection prompt
    echo "Select directories to add .folder.md files (including all subdirectories):"
    echo ""
    echo "  a) All listed directories"
    echo "  n) None (skip for now)"
    echo "  1,2,3) Specific numbers (comma-separated)"
    echo "  custom) Enter custom directory path"
    echo ""
    read -p "Your choice [a/n/numbers/custom]: " choice

    SELECTED_DIRS=()

    case "$choice" in
        a|A)
            SELECTED_DIRS=("${DIR_ARRAY[@]}")
            ;;
        n|N|"")
            echo "  Skipping .folder.md creation."
            echo "  Run later with: rdf scaffold-folders <directory>"
            return 0
            ;;
        custom)
            echo ""
            read -p "Enter directory path (relative to project root): " custom_dir
            if [ -d "$PROJECT_ROOT/$custom_dir" ]; then
                SELECTED_DIRS=("$custom_dir")
            else
                error "Directory not found: $custom_dir"
                return 1
            fi
            ;;
        *)
            # Parse comma-separated numbers
            IFS=',' read -ra NUMS <<< "$choice"
            for num in "${NUMS[@]}"; do
                num=$(echo "$num" | tr -d ' ')  # Trim whitespace
                if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#DIR_ARRAY[@]}" ]; then
                    SELECTED_DIRS+=("${DIR_ARRAY[$((num-1))]}")
                else
                    warn "Invalid selection: $num (skipping)"
                fi
            done
            ;;
    esac

    if [ ${#SELECTED_DIRS[@]} -eq 0 ]; then
        echo "  No valid directories selected."
        return 0
    fi

    # Create .folder.md files
    echo ""
    info "Creating .folder.md files..."

    TEMPLATE="$INSTALL_DIR/templates/rdf/layer2/.folder.md.template"
    CREATED=0
    SKIPPED=0

    for dir in "${SELECTED_DIRS[@]}"; do
        # Find all subdirectories (excluding hidden, __pycache__, etc.)
        while IFS= read -r subdir; do
            [ -z "$subdir" ] && continue
            rel_path="${subdir#$PROJECT_ROOT/}"

            if [ -f "$subdir/.folder.md" ]; then
                SKIPPED=$((SKIPPED + 1))
            else
                if [ -f "$TEMPLATE" ]; then
                    # Create .folder.md with directory name substituted
                    dir_name=$(basename "$subdir")
                    sed "s/{{FOLDER_NAME}}/$dir_name/g" "$TEMPLATE" > "$subdir/.folder.md" 2>/dev/null || \
                        cp "$TEMPLATE" "$subdir/.folder.md"
                    echo "  ✓ $rel_path/.folder.md"
                    CREATED=$((CREATED + 1))
                else
                    # Create minimal .folder.md if template not found
                    dir_name=$(basename "$subdir")
                    cat > "$subdir/.folder.md" << EOFMD
# $dir_name/

> **Purpose:** TODO: Describe the purpose of this directory
> **Owner:** TODO: Team or individual responsible

## Contents

TODO: List key files and their purposes

## Dependencies

TODO: What this directory depends on

## Dependents

TODO: What depends on this directory
EOFMD
                    echo "  ✓ $rel_path/.folder.md (minimal template)"
                    CREATED=$((CREATED + 1))
                fi
            fi
        done < <(find "$PROJECT_ROOT/$dir" -type d 2>/dev/null | \
            grep -v -E "(__pycache__|\.git|node_modules|\.venv|venv|\.tox|\.egg-info|\.mypy_cache)")
    done

    echo ""
    echo "  Created: $CREATED .folder.md files"
    [ $SKIPPED -gt 0 ] && echo "  Skipped: $SKIPPED (already exist)"
    echo ""
    echo "  Next: Edit the .folder.md files to describe each directory's purpose."
    echo "  Tip: Use 'rdf validate' to check for missing documentation."
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

    if [ -n "$EXTERNAL_DOCS_PATH" ]; then
        echo "  EXTERNAL_DOCS_PATH detected: $EXTERNAL_DOCS_PATH"
        echo "  Cross-cutting standards available at: $EXTERNAL_DOCS_PATH/cross-cutting/"

        # Add reference to AGENTS.md
        if [ -f "$PROJECT_ROOT/docs/AGENTS.md" ]; then
            if ! grep -q "EXTERNAL_DOCS_PATH" "$PROJECT_ROOT/docs/AGENTS.md"; then
                cat >> "$PROJECT_ROOT/docs/AGENTS.md" << 'EOFAGENTS'

## Company-Wide Standards

For organization-wide coding standards, see:
- **$EXTERNAL_DOCS_PATH/cross-cutting/coding-standards/** - Python style, docstrings, testing
- **$EXTERNAL_DOCS_PATH/cross-cutting/ai/** - Shared AI protocols and checklists
EOFAGENTS
                echo "  Updated docs/AGENTS.md with external-docs reference"
            fi
        fi
    else
        warn "  EXTERNAL_DOCS_PATH not set - skipping cross-repo integration"
        echo "  Set EXTERNAL_DOCS_PATH in ~/.zshrc to enable cross-repo docs"
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
