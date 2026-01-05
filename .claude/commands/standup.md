---
description: Generate comprehensive status report from RPI artifacts and git activity
---

# Standup

Generates a comprehensive status report from recent RPI artifacts and git activity.

## Initial Response

When this command is invoked, respond with:
```
I'll generate a standup report from your recent work. Let me analyze your RPI artifacts and git history...
```

## Pre-computed Status (Zero Round-Trips)

### Git Status
!`git status --short 2>/dev/null | head -20 || echo "Not a git repository"`

### Current Branch
!`git branch --show-current 2>/dev/null || echo "unknown"`

### Recent Commits (last 24 hours)
!`git log --oneline --since="24 hours ago" 2>/dev/null | head -10 || echo "No recent commits"`

### All Recent Commits (last 10)
!`git log --oneline -10 2>/dev/null || echo "No commits"`

### Uncommitted Changes Summary
!`git diff --stat 2>/dev/null | tail -5 || echo "No uncommitted changes"`

### Recent Research Documents
!`ls -lt thoughts/research/*.md 2>/dev/null | head -5 | awk '{print $NF}' || echo "No research documents found"`

### Recent Plans
!`ls -lt thoughts/plans/*.md 2>/dev/null | head -5 | awk '{print $NF}' || echo "No plan documents found"`

### Active Handoffs
!`ls -lt thoughts/handoffs/*.md 2>/dev/null | head -3 | awk '{print $NF}' || echo "No handoffs found"`

### TODO/FIXME Comments in Changed Files
!`git diff --name-only HEAD~5 2>/dev/null | xargs grep -l "TODO\|FIXME" 2>/dev/null | head -5 || echo "No TODOs in recently changed files"`

### Test Status (quick check)
!`(npm test 2>&1 || pytest -q 2>&1) 2>/dev/null | tail -5 || echo "Tests not configured or not run"`

## Process Steps

### Step 1: Analyze Pre-computed Data

Using the pre-computed information above:
1. Review git status for uncommitted work
2. Check recent commits for completed work
3. Scan RPI artifacts for context
4. Note any TODOs or blockers

### Step 2: Generate Report

Create a structured standup report:

```markdown
# Daily Standup - [Date]

## 📊 Current Status
- **Branch**: [branch-name]
- **Last Commit**: [time ago] - [commit message]
- **Uncommitted Changes**: [X files]

## ✅ Recently Completed
[Based on recent commits and completed plans]
- [Task/Feature 1] - [Brief description]
  - Files affected: X
  - Tests: ✅ Passing
- [Task/Feature 2] - [Brief description]

## 🚧 In Progress
[Based on uncommitted changes and active plans]
- [Current task] ([X]% complete)
  - Plan: thoughts/plans/[filename].md
  - Next step: [Description]

## 📋 Upcoming
[Based on pending plans and TODOs]
1. [Next priority task]
2. [Following task]
3. [Future consideration]

## 🔬 Recent Research
[From thoughts/research/ directory]
- [Topic] - thoughts/research/[filename].md
  - Key finding: [Brief summary]

## ⚠️ Blockers/Issues
[From blocked items or errors]
- [Issue description] - [What's needed to resolve]

## 📈 Metrics
- **Commits Today**: X
- **Files Changed**: Y
- **Test Coverage**: Z%
- **Active Plans**: N

## 🎯 Today's Focus
Based on current progress, the priorities are:
1. [Primary focus]
2. [Secondary task]
3. [If time permits]
```

### Step 3: Provide Actionable Summary

```
Standup generated! Here's your executive summary:

**Momentum**: [Good/Blocked/Slow]
**Key Achievement**: [Most important recent completion]
**Main Focus**: [What you should work on next]
**Needs Attention**: [Any blockers or issues]

Would you like me to:
1. Share this in a specific format (Slack, email, etc.)?
2. Create action items from blockers?
3. Prioritize the upcoming work?
```

## Data Sources

### Git Information
- Recent commits (last 24-48 hours)
- Current branch and upstream status
- Uncommitted changes
- Stash status

### RPI Artifacts
- Files modified in last 3 days
- Research documents created
- Plans in various states
- Implementation progress

### Code Analysis
- TODO/FIXME comments
- Test results if available
- Coverage reports if available
- Lint status

## Customization Options

If user provides parameters:
- `--days N` - Look back N days (default: 1)
- `--verbose` - Include more detail
- `--metrics` - Focus on quantitative data
- `--blockers` - Emphasize blockers/issues

## Important Guidelines

- **Be concise** - Standups should be scannable
- **Be honest** - Don't hide blockers
- **Be specific** - Use real file names and numbers
- **Be actionable** - Identify clear next steps
- **Be informative** - Provide context for decisions

## Output Formats

Can adapt output for different needs:
- **Slack**: Emoji-rich, formatted for channels
- **Email**: Professional, detailed
- **Terminal**: Concise, command-line friendly
- **Markdown**: Full detail for documentation

Remember: The standup should give a clear picture of progress, current state, and what's next.