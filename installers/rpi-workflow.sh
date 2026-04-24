#!/bin/bash
# RPI Workflow Installer
# Installs the three-phase Research -> Plan -> Implement workflow

INSTALL_DIR="${MAXIMAL_AI_HOME:-$HOME/dev/maximal-ai}"
PROJECT_ROOT=$(pwd)

# Source common functions
source "$INSTALL_DIR/installers/common.sh"

# Verify install directory exists
verify_install_dir

echo ""
info "Installing RPI Workflow in: $PROJECT_ROOT"
echo ""

# Create necessary directories
echo "Creating directory structure..."

# Helper: mkdir -p that survives broken symlinks by creating the symlink's target.
# Motivation: thoughts/{handoffs,plans,research,...} are commonly symlinks into
# a sibling minty-thoughts/repos/<repo>/ hub. If the hub subdir was never
# created, plain `mkdir -p <path-through-broken-symlink>` fails with
# "No such file or directory" because mkdir resolves the symlink first.
safe_mkdir() {
    local path="$1"
    if [ -L "$path" ] && [ ! -e "$path" ]; then
        local target
        target=$(readlink "$path")
        # Relative symlink → resolve against the symlink's containing directory
        if [[ "$target" != /* ]]; then
            target="$(cd "$(dirname "$path")" && pwd -P)/$target"
        fi
        mkdir -p "$target"
    else
        mkdir -p "$path"
    fi
}

safe_mkdir "$PROJECT_ROOT/.claude/commands"
safe_mkdir "$PROJECT_ROOT/.claude/agents"
safe_mkdir "$PROJECT_ROOT/thoughts/research"
safe_mkdir "$PROJECT_ROOT/thoughts/plans"
safe_mkdir "$PROJECT_ROOT/thoughts/handoffs"
safe_mkdir "$PROJECT_ROOT/thoughts/reviews"
safe_mkdir "$PROJECT_ROOT/thoughts/learnings"

# Optional: Create docs directory.
# Only prompt when stdin is a TTY — non-interactive runs (e.g. deploy-all.sh)
# used to inherit the loop's stdin and silently consume the next repo name
# as the y/N answer. Set RPI_CREATE_DOCS=1 to auto-create in CI / batch mode.
if [ ! -d "$PROJECT_ROOT/docs" ]; then
    if [ -t 0 ]; then
        echo ""
        echo "Would you like to create a docs/ directory for repo-specific documentation?"
        echo "This enables the RPI workflow to suggest documentation updates after implementation."
        read -p "(y/N): " create_docs
        if [ "$create_docs" = "y" ] || [ "$create_docs" = "Y" ]; then
            mkdir -p "$PROJECT_ROOT/docs"
            echo "Created docs/ directory"
        else
            echo "Skipping docs/ directory (can be created later)"
        fi
    elif [ "${RPI_CREATE_DOCS:-}" = "1" ]; then
        mkdir -p "$PROJECT_ROOT/docs"
        echo "Created docs/ directory (RPI_CREATE_DOCS=1)"
    else
        echo "Skipping docs/ directory (non-interactive; set RPI_CREATE_DOCS=1 to auto-create)"
    fi
fi

# Username configuration
echo ""
echo "Configuring username for RPI file naming..."

config_file="$PROJECT_ROOT/.claude/config.yaml"
if [ -f "$config_file" ]; then
    existing_username=$(grep "^username:" "$config_file" 2>/dev/null | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
    if [ -n "$existing_username" ]; then
        echo "Using existing username from config: $existing_username"
        final_username="$existing_username"
    else
        final_username=$(get_username)
        save_username "$final_username"
    fi
else
    final_username=$(get_username)
    save_username "$final_username"
fi

echo ""

# Copy command files
echo "Installing commands..."

# Multi-session PR review commands are SYMLINKED (single source of truth across
# consumer repos — edits in maximal-ai propagate instantly). Everything else
# is COPIED so consuming projects can optionally force-track project-specific
# overrides (cf. tackle-next.md pattern in minty-docs).
SYMLINKED_CMDS=(review.md review-pr.md address-review.md review-fix-pr-loop.md)

is_symlinked_cmd() {
    local name="$1"
    for s in "${SYMLINKED_CMDS[@]}"; do
        [ "$name" = "$s" ] && return 0
    done
    return 1
}

# Copy every *.md in .claude/commands/ that isn't part of the symlink set.
# Globbed rather than enumerated so new commands added upstream auto-propagate.
for cmd_file in "$INSTALL_DIR"/.claude/commands/*.md; do
    cmd_name=$(basename "$cmd_file")
    if is_symlinked_cmd "$cmd_name"; then
        continue
    fi
    cp "$cmd_file" "$PROJECT_ROOT/.claude/commands/"
done

# Symlink the review family (single source of truth — edits propagate instantly)
echo "Symlinking review commands..."
symlink_failures=0
for sc in "${SYMLINKED_CMDS[@]}"; do
    symlink_command "$sc" || { error "Failed to symlink $sc"; symlink_failures=$((symlink_failures + 1)); }
done
if [ "$symlink_failures" -gt 0 ]; then
    warn "Warning: $symlink_failures symlink(s) failed — review commands may be incomplete"
fi

# Copy agent files
echo "Installing agents..."
cp "$INSTALL_DIR/.claude/agents/codebase-locator.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/codebase-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/codebase-pattern-finder.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/web-search-researcher.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/file-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/bug-hunter.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/test-runner.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/code-simplifier.md" "$PROJECT_ROOT/.claude/agents/"

# ============================================
# Install Hooks
# ============================================
echo "Installing Claude Code hooks..."

HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# Copy hook scripts
for hook in post-edit.sh pre-commit-check.sh session-complete.sh auto-format.sh; do
  if [ -f "$INSTALL_DIR/.claude/hooks/$hook" ]; then
    cp "$INSTALL_DIR/.claude/hooks/$hook" "$HOOKS_DIR/$hook"
    chmod +x "$HOOKS_DIR/$hook"
    echo "  ✓ Installed $hook"
  fi
done

# Copy project settings.json (hooks config)
if [ -f "$INSTALL_DIR/.claude/settings.json" ]; then
  # Merge with existing settings.json if present, otherwise copy
  if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
    echo "  ⚠ .claude/settings.json already exists - manual merge may be needed"
  else
    cp "$INSTALL_DIR/.claude/settings.json" "$PROJECT_ROOT/.claude/settings.json"
    echo "  ✓ Installed hooks configuration"
  fi
fi

echo "Hooks installation complete."
echo ""

# Copy or merge CLAUDE.md
# Smart merge: preserve RDF bootstrap section if present
RDF_MARKER="## Repository Documentation Framework (RDF)"

if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
    if grep -q "$RDF_MARKER" "$PROJECT_ROOT/CLAUDE.md"; then
        # CLAUDE.md has RDF bootstrap — preserve it, save RPI config as .new for merge
        echo ""
        warn "CLAUDE.md already exists with RDF bootstrap section."
        echo "   The RPI configuration has been saved as CLAUDE.md.rpi-new"
        echo "   Please merge the RPI commands/workflow sections manually."
        cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md.rpi-new"
    else
        echo ""
        warn "CLAUDE.md already exists in your project."
        echo "   The new configuration has been saved as CLAUDE.md.new"
        echo "   Please merge the configurations manually."
        cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md.new"
    fi
else
    echo "Installing CLAUDE.md configuration..."
    cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/"
fi

# Update .gitignore
add_to_gitignore "thoughts/" "# AI Context Engineering artifacts"
add_to_gitignore ".claude/config.yaml" "# AI Context Engineering"

# Symlinked review commands are machine-local and must not be committed
add_to_gitignore ".claude/commands/review.md" "# Symlinked review commands (machine-local)"
add_to_gitignore ".claude/commands/review-pr.md"
add_to_gitignore ".claude/commands/address-review.md"
add_to_gitignore ".claude/commands/review-fix-pr-loop.md"

echo ""
info "RPI Workflow installation complete!"
echo ""
echo "Installed:"
echo ""
echo "   📋 Core RPI Commands (4):"
echo "      research, plan, implement, epic-oneshot"
echo ""
echo "   🔄 Inner-Loop Commands (4) - Pre-computed context for speed:"
echo "      commit-push-pr, review, test-and-fix, verify"
echo ""
echo "   🔍 Multi-Session PR Review (3) - Adversarial code review:"
echo "      review-pr, address-review, review-fix-pr-loop"
echo ""
echo "   📊 Session Management (4):"
echo "      standup, blocked, create_handoff, resume_handoff"
echo ""
echo "   🧠 Knowledge Compounding (1):"
echo "      compound"
echo ""
echo "   🤖 Automation Commands (2):"
echo "      observe-docstrings, map-to-standards"
echo ""
echo "   🧠 Sub-Agents (8) - Spawned automatically by Claude:"
echo "      locator, analyzer, pattern-finder, researcher,"
echo "      file-analyzer, bug-hunter, test-runner, code-simplifier"
echo ""
echo "   ⚡ Hooks (4):"
echo "      auto-format, post-edit (background tests),"
echo "      pre-commit-check, session-complete"
echo ""
echo "Documentation destinations:"
if [ -n "$EXTERNAL_DOCS_PATH" ]; then
    echo "   - Cross-cutting: $EXTERNAL_DOCS_PATH"
else
    echo "   - Cross-cutting: Not configured (set EXTERNAL_DOCS_PATH for cross-cutting docs)"
fi
if [ -d "$PROJECT_ROOT/docs" ]; then
    echo "   - Repo-specific: docs/"
else
    echo "   - Repo-specific: Not configured (create docs/ for repo-specific docs)"
fi
echo ""
echo "Next steps:"
echo "1. Open this project in Claude"
echo "2. Try: /research [your question]"
echo "3. Create a plan: /plan [topic or research file]"
echo "4. Implement: /implement [plan file]"
echo "5. Create PR: /commit-push-pr"
echo ""
echo "Multi-session PR review workflow:"
echo "   Session 1: /implement → /commit-push-pr → PR created"
echo "   Session 2: /review-pr [PR#] → creates thoughts/reviews/..."
echo "   Session 1: /clear → /address-review [plan] [review]"
echo "   Session 2: /review-pr [PR#] → APPROVED → merge"
echo ""
echo "Automated review-fix loop (single session):"
echo "   /review-fix-pr-loop [PR#]              # Default 3 rounds"
echo "   /review-fix-pr-loop [PR#] --max-rounds 5"
echo ""
