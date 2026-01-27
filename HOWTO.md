<!--
  WARNING: This file is managed by maximal-ai and will be overwritten
  when running setup.sh. Do not customize this file in target projects.
  For project-specific guidance, add to CLAUDE.md instead.
-->

# How to Use maximal-ai Effectively

> Quick tips and gotchas for the Research-Plan-Implement workflow.

---

## Context Management

<important if="you are hitting context limits or getting degraded output">
Stay under 40% context usage. Start fresh context windows for each RPI phase. See CLAUDE.md for the three-phase workflow details.
</important>

<important if="you are starting a new task">
Always start with `/research` before writing code. Understanding the codebase prevents thousands of bad lines. See README.md § "Why Three Phases?" for the full workflow.
</important>

<important if="context feels cluttered">
Spawn sub-agents for exploration tasks. Keep the main context for orchestration and synthesis. See CLAUDE.md § "Context Management" for agent spawning patterns.
</important>

---

## Research Phase

<important if="you want research to be thorough">
Use parallel sub-agents: `codebase-locator` finds WHERE, `codebase-analyzer` explains HOW, `codebase-pattern-finder` shows examples. Launch multiple agents in a single message.
</important>

<important if="you have a centralized thoughts repository">
Use the `thoughts-locator` agent to search prior research, plans, and handoffs. Requires `$THOUGHTS_PATH` environment variable. Prevents re-researching solved problems.
</important>

<important if="research documents are too long">
Use the `file-analyzer` agent to summarize verbose outputs. Achieves 80-90% token reduction while preserving critical information.
</important>

---

## Planning Phase

<important if="your plans have open questions">
Stop and resolve questions immediately. Do NOT write plans with unresolved questions. The implementation plan must be complete and actionable.
</important>

<important if="you want plans approved quickly">
Keep plans focused on WHAT changes, not WHY (research covers why). Include specific file:line references. Separate automated vs manual verification steps.
</important>

<important if="you are unsure about approach">
Use `/plan` interactively. Present structure first, get feedback, then write details. Plans are much easier to review than code.
</important>

---

## Implementation Phase

<important if="you are implementing from a plan">
Follow the plan's intent, but adapt to reality. If you discover something the plan missed, note the deviation. Update the plan's checkboxes as you complete phases.
</important>

<important if="implementation is going off-track">
Stop and return to planning. A bad plan line becomes hundreds of bad code lines. It's cheaper to fix the plan than the code.
</important>

<important if="you need to verify your work">
Use `/verify` for quick checks (tests, lint, typecheck). Use `test-runner` agent for comprehensive test execution with result analysis.
</important>

---

## Git Practices

<important if="you are committing changes">
Stage specific files, not `git add .`. Focus commits on single concerns. Follow the commit style shown in recent commits. See CLAUDE.md § "Git Commit Best Practices".
</important>

<important if="unrelated changes crept into your commit">
Use selective staging: `git add <specific-file>`. Track which files you modified during RPI. Never commit files you didn't intentionally change.
</important>

<important if="you need to create a PR">
Use `/commit-push-pr` command. It pre-computes git status, branch info, and existing PR state. Follow the PR template in the command output.
</important>

---

## Agent Usage

<important if="you don't know which agent to use">
- **Finding files**: `codebase-locator`
- **Understanding code**: `codebase-analyzer`
- **Finding patterns**: `codebase-pattern-finder`
- **Running tests**: `test-runner`
- **Summarizing files**: `file-analyzer`
- **Web research**: `web-search-researcher`
- **Prior research**: `thoughts-locator` (requires $THOUGHTS_PATH)

See extension_guide.md for creating new agents.
</important>

<important if="agents are returning incomplete results">
Provide detailed prompts with specific search terms. Spawn multiple agents in parallel for different aspects. Wait for ALL agents to complete before synthesizing.
</important>

---

## Troubleshooting

<important if="setup.sh fails">
Ensure you're running from the maximal-ai directory. Check that target project has `.claude/` directory structure. Run with `bash -x setup.sh` for debug output.
</important>

<important if="commands aren't being discovered">
Commands are discovered by filename in `.claude/commands/`. Verify the file was copied by setup.sh. Check YAML frontmatter has `description` field.
</important>

<important if="agents aren't working as expected">
Verify YAML frontmatter: `name`, `description`, `tools`, `model`. Check that tools listed are available. Review agent output format section.
</important>

<important if="$THOUGHTS_PATH is not set">
Add to your shell profile (~/.zshrc or ~/.bashrc):
```bash
export THOUGHTS_PATH=/path/to/your/thoughts-repository
```
Then restart your terminal or run `source ~/.zshrc`.
</important>

---

*For detailed configuration, see CLAUDE.md. For workflow concepts, see README.md. For extending the system, see extension_guide.md.*
