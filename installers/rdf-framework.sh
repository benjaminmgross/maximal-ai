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
    echo "  1 - Entry Points (CLAUDE.md bootstrap, .context/, docs/AGENTS.md, .repomap.yaml)"
    echo "  2 - Directory Docs (.context.md files in source directories)"
    echo "  3 - AI Guidance (protocols/, checklists/, guides/)"
    echo "  4 - Cross-Repo (external docs linkage via \$EXTERNAL_DOCS_PATH)"
    echo "  5 - Tooling (rdf CLI, linters, observe system)"
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
    echo "Layer 1: Entry Points (CLAUDE.md bootstrap, .context/, docs/AGENTS.md, .repomap.yaml)"
    echo "Layer 2: Directory Docs (.context.md files in source directories)"
    echo "Layer 3: AI Guidance (protocols/, checklists/, guides/)"
    echo "Layer 4: Cross-Repo (external docs linkage via \$EXTERNAL_DOCS_PATH)"
    echo "Layer 5: Tooling (rdf CLI, linters, observe system)"
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

# ============================================
# RDF Bootstrap Injection
# ============================================

inject_rdf_bootstrap() {
    local target="$PROJECT_ROOT/CLAUDE.md"
    local bootstrap_template="$INSTALL_DIR/templates/rdf/rdf-bootstrap.md.template"
    local marker="## Repository Documentation Framework (RDF)"

    if [ ! -f "$bootstrap_template" ]; then
        warn "  RDF bootstrap template not found"
        return 0
    fi

    if [ -f "$target" ]; then
        # Check if bootstrap already injected
        if grep -q "$marker" "$target"; then
            echo "  CLAUDE.md already has RDF bootstrap section"
            return 0
        fi
        # Append to existing CLAUDE.md
        echo "" >> "$target"
        cat "$bootstrap_template" >> "$target"
        echo "  Appended RDF bootstrap section to CLAUDE.md"
    else
        # Create minimal CLAUDE.md with bootstrap
        cat > "$target" << 'EOFCLAUDEMD'
# CLAUDE.md

> This file provides Claude with context about this repository.

## Project Overview

<!-- TODO: Replace with your project description -->

## Quick Start

```bash
# TODO: Add your setup commands
```

## Code Standards

Follow existing patterns in the codebase.
EOFCLAUDEMD
        echo "" >> "$target"
        cat "$bootstrap_template" >> "$target"
        echo "  Created CLAUDE.md with RDF bootstrap section"
    fi
}

# ============================================
# .context/ Directory Scaffolding
# ============================================

scaffold_context_dir() {
    local context_dir="$PROJECT_ROOT/.context"
    local template_dir="$INSTALL_DIR/templates/rdf/context"

    if [ ! -d "$template_dir" ]; then
        warn "  Context templates not found at $template_dir"
        return 0
    fi

    echo "  Scaffolding .context/ directory..."

    # Create directory structure
    mkdir -p "$context_dir"
    mkdir -p "$context_dir/architecture"
    mkdir -p "$context_dir/decisions"
    mkdir -p "$context_dir/prompts"

    # Copy top-level context files
    local CREATED=0
    local SKIPPED=0

    for template_file in "$template_dir"/*.template; do
        [ ! -f "$template_file" ] && continue
        local filename
        filename=$(basename "$template_file" .template)
        local target_file="$context_dir/$filename"

        if [ ! -f "$target_file" ]; then
            cp "$template_file" "$target_file"
            echo "    Created .context/$filename"
            CREATED=$((CREATED + 1))
        else
            SKIPPED=$((SKIPPED + 1))
        fi
    done

    # Copy subdirectory files
    for subdir in architecture decisions prompts; do
        if [ -d "$template_dir/$subdir" ]; then
            for template_file in "$template_dir/$subdir"/*.template; do
                [ ! -f "$template_file" ] && continue
                local filename
                filename=$(basename "$template_file" .template)
                local target_file="$context_dir/$subdir/$filename"

                if [ ! -f "$target_file" ]; then
                    cp "$template_file" "$target_file"
                    echo "    Created .context/$subdir/$filename"
                    CREATED=$((CREATED + 1))
                else
                    SKIPPED=$((SKIPPED + 1))
                fi
            done
        fi
    done

    echo "  .context/: $CREATED created, $SKIPPED skipped (already exist)"
}

# ============================================
# Layer Installation Functions
# ============================================

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

    # Scaffold .context/ directory
    scaffold_context_dir

    # Inject RDF bootstrap section into root CLAUDE.md
    inject_rdf_bootstrap

    # Auto-generate REPOMAP.yaml if rdf CLI is available
    if command -v rdf &> /dev/null; then
        for src_dir in src lib app; do
            if [ -d "$PROJECT_ROOT/$src_dir" ]; then
                echo "  Generating REPOMAP.yaml from $src_dir/..."
                (cd "$PROJECT_ROOT" && rdf generate-repomap --source "$src_dir") 2>/dev/null || true
                break
            fi
        done
    fi
}

install_layer2() {
    info "Installing Layer 2: Directory Docs..."

    # Discover source directories by looking for code files
    echo ""
    echo "Discovering source directories..."
    echo ""

    # Find all directories containing source files, excluding common non-source dirs
    DISCOVERED_DIRS=$(find "$PROJECT_ROOT" -type f \( \
        -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
        -o -name "*.go" -o -name "*.rs" -o -name "*.rb" -o -name "*.java" \
    \) 2>/dev/null | \
        grep -v -E "(node_modules|\.git|__pycache__|\.venv|venv|\.tox|build|dist|\.egg-info|\.mypy_cache|\.pytest_cache|\.ruff_cache)" | \
        xargs -I {} dirname {} 2>/dev/null | \
        sort -u | \
        sed "s|^$PROJECT_ROOT/||" | \
        cut -d'/' -f1 | \
        sort -u | \
        grep -v -E "^(\.|node_modules|docs|tests?|spec|fixtures|coverage|htmlcov)$" || true)

    if [ -z "$DISCOVERED_DIRS" ]; then
        warn "No source directories found with code files."
        echo ""
        echo "You can manually specify directories later with:"
        echo "  rdf scaffold-context-files <directory>"
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
            FILE_COUNT=$(find "$PROJECT_ROOT/$dir" -type f \( \
                -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
                -o -name "*.go" -o -name "*.rs" -o -name "*.rb" -o -name "*.java" \
            \) 2>/dev/null | wc -l)

            SUBDIR_COUNT=$(find "$PROJECT_ROOT/$dir" -type d 2>/dev/null | \
                grep -v -E "(__pycache__|\.)" | wc -l)
            SUBDIR_COUNT=$((SUBDIR_COUNT - 1))

            printf "│ %-3s %-25s %10s %10s │\n" "$COUNTER" "$dir/" "$FILE_COUNT" "$SUBDIR_COUNT"
            DIR_ARRAY+=("$dir")
            COUNTER=$((COUNTER + 1))
        fi
    done

    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""

    # Selection prompt
    echo "Select directories to add .context.md files (including all subdirectories):"
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
            echo "  Skipping .context.md creation."
            echo "  Run later with: rdf scaffold-context-files <directory>"
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
            IFS=',' read -ra NUMS <<< "$choice"
            for num in "${NUMS[@]}"; do
                num=$(echo "$num" | tr -d ' ')
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

    # Create .context.md files
    echo ""
    info "Creating .context.md files..."

    CONTEXT_TEMPLATE="$INSTALL_DIR/templates/rdf/layer2/.context.md.template"
    FOLDER_TEMPLATE="$INSTALL_DIR/templates/rdf/layer2/.folder.md.template"
    CREATED=0
    SKIPPED=0

    for dir in "${SELECTED_DIRS[@]}"; do
        while IFS= read -r subdir; do
            [ -z "$subdir" ] && continue
            rel_path="${subdir#$PROJECT_ROOT/}"

            # Check for either .context.md or .folder.md (backward compat)
            if [ -f "$subdir/.context.md" ] || [ -f "$subdir/.folder.md" ]; then
                SKIPPED=$((SKIPPED + 1))
            else
                # Prefer .context.md template, fall back to .folder.md template
                if [ -f "$CONTEXT_TEMPLATE" ]; then
                    dir_name=$(basename "$subdir")
                    awk -v name="$dir_name" '{gsub(/\{\{FOLDER_NAME\}\}/, name)}1' "$CONTEXT_TEMPLATE" > "$subdir/.context.md" 2>/dev/null || \
                        cp "$CONTEXT_TEMPLATE" "$subdir/.context.md"
                    echo "  Created $rel_path/.context.md"
                    CREATED=$((CREATED + 1))
                elif [ -f "$FOLDER_TEMPLATE" ]; then
                    dir_name=$(basename "$subdir")
                    awk -v name="$dir_name" '{gsub(/\{\{FOLDER_NAME\}\}/, name)}1' "$FOLDER_TEMPLATE" > "$subdir/.context.md" 2>/dev/null || \
                        cp "$FOLDER_TEMPLATE" "$subdir/.context.md"
                    echo "  Created $rel_path/.context.md"
                    CREATED=$((CREATED + 1))
                else
                    dir_name=$(basename "$subdir")
                    cat > "$subdir/.context.md" << EOFMD
# $dir_name/

> **Purpose:** TODO: Describe the purpose of this directory
> **Update Trigger:** Update when files added/removed or responsibilities change.

## Architecture

<!-- HUMAN-AUTHORED - DO NOT AUTO-GENERATE -->
TODO: Describe this directory's responsibility, boundaries, and invariants.

---

<!-- AUTO-GENERATED BELOW - DO NOT EDIT MANUALLY -->

## Files

TODO: Auto-generated file listing will appear here.
EOFMD
                    echo "  Created $rel_path/.context.md (minimal template)"
                    CREATED=$((CREATED + 1))
                fi
            fi
        done < <(find "$PROJECT_ROOT/$dir" -type d 2>/dev/null | \
            grep -v -E "(__pycache__|\.git|node_modules|\.venv|venv|\.tox|\.egg-info|\.mypy_cache)")
    done

    echo ""
    echo "  Created: $CREATED .context.md files"
    [ $SKIPPED -gt 0 ] && echo "  Skipped: $SKIPPED (already exist)"

    # Auto-generate populated .context.md if rdf CLI available
    if command -v rdf &> /dev/null; then
        echo ""
        info "  Running documentation generators..."
        for dir in "${SELECTED_DIRS[@]}"; do
            echo "    Generating populated .context.md files in $dir/..."
            (cd "$PROJECT_ROOT" && rdf scaffold-context-files "$dir") 2>/dev/null || true
        done
    fi

    echo ""
    echo "  Next: Edit .context.md files to describe each directory's purpose."
    echo "  Tip: Use 'rdf validate' to check for missing documentation."
}

install_layer3() {
    info "Installing Layer 3: AI Guidance..."

    mkdir -p "$PROJECT_ROOT/docs/ai/protocols"
    mkdir -p "$PROJECT_ROOT/docs/ai/checklists"
    mkdir -p "$PROJECT_ROOT/docs/ai/prompts"
    mkdir -p "$PROJECT_ROOT/docs/guides"
    mkdir -p "$PROJECT_ROOT/docs/templates"
    mkdir -p "$PROJECT_ROOT/docs/architecture/decisions"

    # Copy protocol templates
    local TEMPLATE_DIR="$INSTALL_DIR/templates/rdf/layer3"
    local CREATED=0

    for subdir in protocols checklists guides; do
        if [ -d "$TEMPLATE_DIR/$subdir" ]; then
            for template_file in "$TEMPLATE_DIR/$subdir"/*.template; do
                [ ! -f "$template_file" ] && continue
                local filename
                filename=$(basename "$template_file" .template)
                local target_dir_map=""

                case "$subdir" in
                    protocols) target_dir_map="$PROJECT_ROOT/docs/ai/protocols" ;;
                    checklists) target_dir_map="$PROJECT_ROOT/docs/ai/checklists" ;;
                    guides) target_dir_map="$PROJECT_ROOT/docs/guides" ;;
                esac

                if [ -n "$target_dir_map" ] && [ ! -f "$target_dir_map/$filename" ]; then
                    cp "$template_file" "$target_dir_map/$filename"
                    echo "  Created $subdir/$filename"
                    CREATED=$((CREATED + 1))
                fi
            done
        fi
    done

    echo "  Created $CREATED AI guidance files"
    echo "  Directories: docs/ai/{protocols,checklists,prompts}/, docs/{guides,templates,architecture/decisions}/"
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

# ============================================
# Execute Installation
# ============================================

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

# ============================================
# Post-Install Summary
# ============================================

echo ""
info "RDF Framework installation complete!"
echo ""
echo "Installed layers: $LAYERS"
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│              What Happens Next                          │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│                                                         │"
echo "│  1. FILL IN THE TEMPLATES                               │"
echo "│     Edit these files with your project details:         │"
echo "│     - .context/substrate.md   (project overview)        │"
echo "│     - .context/ai-rules.md    (code generation rules)   │"
echo "│     - .context/glossary.md    (domain terminology)      │"
echo "│                                                         │"
echo "│  2. GENERATE DOCUMENTATION                              │"
if command -v rdf &> /dev/null; then
echo "│     rdf CLI detected! Run:                              │"
echo "│     - rdf generate-repomap --source src/                │"
echo "│     - rdf scaffold-context-files src/                   │"
echo "│     - rdf status                                        │"
else
echo "│     Install rdf CLI for auto-generation:                │"
echo "│     - pip install -e \$MAXIMAL_AI_HOME                   │"
echo "│     Then: rdf generate-repomap && rdf status            │"
fi
echo "│                                                         │"
echo "│  3. ENRICH WITH OBSERVATION (Python projects)           │"
echo "│     In Claude: /observe-docstrings tests/               │"
echo "│     Or CLI:    rdf observe src/main.py -e main          │"
echo "│     Generates complete docstrings from runtime data.    │"
echo "│                                                         │"
echo "│  4. CHECK STATUS                                        │"
if command -v rdf &> /dev/null; then
echo "│     rdf status          (documentation health check)    │"
echo "│     rdf validate        (lint docstrings & coverage)    │"
else
echo "│     Install rdf CLI, then run: rdf status               │"
fi
echo "│                                                         │"
echo "└─────────────────────────────────────────────────────────┘"
