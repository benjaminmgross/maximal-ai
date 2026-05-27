#!/bin/bash
# Codex Skills Installer
# Installs Codex-compatible skill wrappers backed by the canonical Claude commands.

set -e

INSTALL_DIR="${MAXIMAL_AI_HOME:-$HOME/dev/maximal-ai}"
PROJECT_ROOT=$(pwd)
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="$CODEX_HOME/skills"
DRY_RUN=false

# Source common functions
source "$INSTALL_DIR/installers/common.sh"

show_help() {
    echo "Usage: maximal-ai codex-skills [--dry-run]"
    echo ""
    echo "Install Codex skill wrappers for Maximal-AI commands."
    echo "Existing SKILL.md wrappers are preserved; refreshed source references carry command protocol updates."
    echo ""
    echo "Options:"
    echo "  --dry-run   Show what would be installed without writing files"
    echo "  --help, -h  Show this help message"
}

for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $arg"
            echo "Run 'maximal-ai codex-skills --help' for usage."
            exit 1
            ;;
    esac
done

verify_install_dir

COMMANDS_DIR="$INSTALL_DIR/.claude/commands"
if [ ! -d "$COMMANDS_DIR" ]; then
    error "Claude command source directory not found: $COMMANDS_DIR"
    exit 1
fi

extract_description() {
    local file="$1"
    awk '
        NR == 1 && $0 == "---" { in_frontmatter = 1; next }
        in_frontmatter && $0 == "---" { exit }
        in_frontmatter && $0 ~ /^description:/ {
            sub(/^description:[[:space:]]*/, "", $0)
            gsub(/^"/, "", $0)
            gsub(/"$/, "", $0)
            gsub(/^'\''/, "", $0)
            gsub(/'\''$/, "", $0)
            print
            exit
        }
    ' "$file"
}

title_from_name() {
    local name="$1"
    echo "$name" | tr '_-' '  ' | awk '{
        for (i = 1; i <= NF; i++) {
            $i = toupper(substr($i, 1, 1)) substr($i, 2)
        }
        print
    }'
}

write_skill_wrapper() {
    local skill_file="$1"
    local skill_name="$2"
    local command_name="$3"
    local description="$4"
    local title

    title=$(title_from_name "$skill_name")
    if [ -z "$description" ]; then
        description="No description was found in the source command frontmatter."
    fi

    cat > "$skill_file" <<EOF
---
name: $skill_name
description: "Use when the user asks for /$command_name or the equivalent Maximal-AI workflow. Generated Codex wrapper backed by references/source-claude-command.md."
---

# $title

This is a generated Codex wrapper for the Maximal-AI \`/$command_name\` workflow.

Original command description: $description

## Workflow

1. Read local project guidance first: \`AGENTS.md\`, \`CLAUDE.md\`, \`.context/\`, and relevant \`thoughts/\` artifacts when present, especially applicable \`thoughts/learnings\` entries.
2. Use \`references/source-claude-command.md\` as the canonical workflow source for this command.
3. Adapt Claude Code-specific instructions to Codex equivalents:
   - Inline bash pre-computation blocks are reference context, not syntax Codex executes automatically.
   - Claude Task/sub-agent instructions map to Codex subagents only when the user has explicitly authorized delegation in the current request.
   - \`.claude/config.yaml\` remains the RPI username source when present.
4. Preserve the command's RPI artifact conventions under \`thoughts/\` unless the user requests a different output.
5. Make scoped edits, protect unrelated user changes, and run the relevant verification before claiming completion.

## Reference

The canonical Claude Code command source is bundled at \`references/source-claude-command.md\`.
EOF
}

echo ""
info "Installing Codex skills from Maximal-AI commands"
echo ""
echo "Command source: $COMMANDS_DIR"
echo "Codex home:     $CODEX_HOME"
echo "Skills target:  $SKILLS_DIR"
echo "Update model:   Preserve existing SKILL.md files; refresh canonical source references"
if [ "$DRY_RUN" = true ]; then
    warn "Dry run: no files will be written"
fi
echo ""

installed=0
preserved=0
generated=0

for cmd_file in "$COMMANDS_DIR"/*.md; do
    [ -f "$cmd_file" ] || continue

    cmd_filename=$(basename "$cmd_file")
    command_name="${cmd_filename%.md}"
    skill_name="${command_name//_/-}"
    skill_dir="$SKILLS_DIR/$skill_name"
    reference_dir="$skill_dir/references"
    skill_file="$skill_dir/SKILL.md"
    reference_file="$reference_dir/source-claude-command.md"
    description=$(extract_description "$cmd_file")

    if [ "$DRY_RUN" = true ]; then
        if [ -f "$skill_file" ]; then
            echo "  Would refresh $skill_name source reference and preserve SKILL.md"
        else
            echo "  Would create $skill_name SKILL.md and reference"
        fi
        installed=$((installed + 1))
        continue
    fi

    mkdir -p "$reference_dir"
    cp "$cmd_file" "$reference_file"

    if [ -f "$skill_file" ]; then
        echo "  ✓ Refreshed $skill_name source reference (preserved SKILL.md)"
        preserved=$((preserved + 1))
    else
        write_skill_wrapper "$skill_file" "$skill_name" "$command_name" "$description"
        echo "  ✓ Generated $skill_name skill"
        generated=$((generated + 1))
    fi

    installed=$((installed + 1))
done

echo ""
info "Codex skills installation complete!"
echo ""
echo "Installed/updated: $installed"
if [ "$DRY_RUN" = false ]; then
    echo "Generated:         $generated"
    echo "Preserved:         $preserved"
fi
echo ""
echo "Codex will discover these skills from: $SKILLS_DIR"
echo ""
