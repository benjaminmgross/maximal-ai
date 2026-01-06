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
mkdir -p "$PROJECT_ROOT/.claude/commands"
mkdir -p "$PROJECT_ROOT/.claude/agents"
mkdir -p "$PROJECT_ROOT/thoughts/research"
mkdir -p "$PROJECT_ROOT/thoughts/plans"
mkdir -p "$PROJECT_ROOT/thoughts/handoffs"
mkdir -p "$PROJECT_ROOT/thoughts/reviews"

# Optional: Create docs directory
if [ ! -d "$PROJECT_ROOT/docs" ]; then
    echo ""
    echo "Would you like to create a docs/ directory for repo-specific documentation?"
    echo "This enables the RPI workflow to suggest documentation updates after implementation."
    echo -n "(y/N): "
    read create_docs
    if [ "$create_docs" = "y" ] || [ "$create_docs" = "Y" ]; then
        mkdir -p "$PROJECT_ROOT/docs"
        echo "Created docs/ directory"
    else
        echo "Skipping docs/ directory (can be created later)"
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

# Core RPI workflow commands
cp "$INSTALL_DIR/.claude/commands/research.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/plan.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/implement.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/epic-oneshot.md" "$PROJECT_ROOT/.claude/commands/"

# Session management commands
cp "$INSTALL_DIR/.claude/commands/standup.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/blocked.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/create_handoff.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/resume_handoff.md" "$PROJECT_ROOT/.claude/commands/"

# Inner-loop commands (pre-computed context)
cp "$INSTALL_DIR/.claude/commands/commit-push-pr.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/review.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/test-and-fix.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/verify.md" "$PROJECT_ROOT/.claude/commands/"

# Multi-session PR review commands
cp "$INSTALL_DIR/.claude/commands/review-pr.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/address-review.md" "$PROJECT_ROOT/.claude/commands/"

# Automation commands
cp "$INSTALL_DIR/.claude/commands/observe-docstrings.md" "$PROJECT_ROOT/.claude/commands/"

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
if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
    echo ""
    warn "CLAUDE.md already exists in your project."
    echo "   The new configuration has been saved as CLAUDE.md.new"
    echo "   Please merge the configurations manually."
    cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md.new"
else
    echo "Installing CLAUDE.md configuration..."
    cp "$INSTALL_DIR/CLAUDE.md" "$PROJECT_ROOT/"
fi

# Update .gitignore
add_to_gitignore "thoughts/" "# AI Context Engineering artifacts"
add_to_gitignore ".claude/config.yaml" "# AI Context Engineering"

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
echo "   🔍 Multi-Session PR Review (2) - Adversarial code review:"
echo "      review-pr, address-review"
echo ""
echo "   📊 Session Management (4):"
echo "      standup, blocked, create_handoff, resume_handoff"
echo ""
echo "   🤖 Automation Commands (1):"
echo "      observe-docstrings"
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
