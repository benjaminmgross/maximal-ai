#!/bin/bash

# Advanced Context Engineering Setup Script
# This script helps set up the three-phase workflow in your project

set -e

echo "🚀 Advanced Context Engineering Setup"
echo "======================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we're in a git repository
if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    PROJECT_ROOT=$(pwd)
else
    echo "⚠️  Not in a git repository. Setup will continue but consider initializing git."
    PROJECT_ROOT=$(pwd)
fi

echo "📁 Setting up in: $PROJECT_ROOT"
echo ""

# Create necessary directories
echo "Creating directory structure..."
mkdir -p "$PROJECT_ROOT/.claude/commands"
mkdir -p "$PROJECT_ROOT/.claude/agents"
mkdir -p "$PROJECT_ROOT/research"
mkdir -p "$PROJECT_ROOT/plans"
mkdir -p "$PROJECT_ROOT/handoffs"

# Copy command files
echo "Installing commands..."
cp "$SCRIPT_DIR/.claude/commands/research.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/plan.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/implement.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/epic-oneshot.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/standup.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/blocked.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/create_handoff.md" "$PROJECT_ROOT/.claude/commands/"
cp "$SCRIPT_DIR/.claude/commands/resume_handoff.md" "$PROJECT_ROOT/.claude/commands/"

# Copy agent files
echo "Installing agents..."
cp "$SCRIPT_DIR/.claude/agents/codebase-locator.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/codebase-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/codebase-pattern-finder.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/web-search-researcher.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/file-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/bug-hunter.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/test-runner.md" "$PROJECT_ROOT/.claude/agents/"
cp "$SCRIPT_DIR/.claude/agents/thoughts-locator.md" "$PROJECT_ROOT/.claude/agents/"

# Copy or merge CLAUDE.md
if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
    echo ""
    echo "⚠️  CLAUDE.md already exists in your project."
    echo "   The new configuration has been saved as CLAUDE.md.new"
    echo "   Please merge the configurations manually."
    cp "$SCRIPT_DIR/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md.new"
else
    echo "Installing CLAUDE.md configuration..."
    cp "$SCRIPT_DIR/CLAUDE.md" "$PROJECT_ROOT/"
fi

# Copy HOWTO.md (quick reference guide)
echo "Installing HOWTO.md..."
cp "$SCRIPT_DIR/HOWTO.md" "$PROJECT_ROOT/"

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
fi

# Create example files
echo ""
echo "Creating example templates..."

# Example research template
cat > "$PROJECT_ROOT/research/TEMPLATE.md" << 'EOF'
---
date: [ISO datetime]
researcher: [name]
git_commit: [commit hash]
branch: [branch name]
repository: [repo name]
topic: "[Research Topic]"
tags: [research, codebase]
status: complete
last_updated: [YYYY-MM-DD]
last_updated_by: [name]
---

# Research: [Topic]

## Research Question
[What are we trying to understand?]

## Summary
[High-level findings - 2-3 paragraphs]

## Detailed Findings

### [Component/Area]
- Finding with reference (`file:line`)
- Implementation details
- Connections to other components

## Code References
- `path/to/file:123` - Description
- `another/file:45-67` - Description

## Architecture Insights
[Patterns and decisions discovered]

## Open Questions
[Areas needing further investigation]

## Next Steps
[Recommended actions]
EOF

# Example plan template
cat > "$PROJECT_ROOT/plans/TEMPLATE.md" << 'EOF'
# [Feature] Implementation Plan

## Overview
[What we're implementing and why]

## Current State Analysis
[What exists now, constraints]

## Desired End State
[Specification of end state]

## What We're NOT Doing
[Explicit out-of-scope items]

## Implementation Approach
[High-level strategy]

## Phase 1: [Name]

### Overview
[What this phase accomplishes]

### Changes Required:

#### 1. [Component]
**File**: `path/to/file`
**Changes**: [Summary]

```language
// Code to add/modify
```

### Success Criteria:

#### Automated Verification:
- [ ] Tests pass: `npm test`
- [ ] Lint passes: `npm run lint`

#### Manual Verification:
- [ ] Feature works as expected
- [ ] No regressions

## Testing Strategy
[Test approach]

## References
- Original research: `research/[file].md`
EOF

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📚 Next Steps:"
echo "1. Open your project in Claude"
echo "2. Try the research command: /research [your question]"
echo "3. Create a plan: /plan [topic or research file]"
echo "4. Implement: /implement [plan file]"
echo ""
echo "📖 Documentation: $SCRIPT_DIR/README.md"
echo ""
echo "Happy coding with advanced context engineering! 🎉"