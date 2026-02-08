# Extension Guide: Adding Commands & Adapting to New Domains

> v2.0 — Updated to cover the full command registration workflow and domain adaptation.

This guide covers two things:

1. **Adding a new command** to the maximal-ai toolkit (the checklist you need every time)
2. **Adapting the RPI pattern** to new domains (product management, data science, etc.)

---

## Part 1: Adding a New Command

### Command Categories

Commands live in `.claude/commands/` and fall into these categories:

| Category | Commands | Count |
|----------|----------|-------|
| Core RPI | `research`, `plan`, `implement`, `epic-oneshot` | 4 |
| Inner-Loop | `commit-push-pr`, `review`, `test-and-fix`, `verify` | 4 |
| PR Review | `review-pr`, `address-review`, `review-fix-pr-loop` | 3 |
| Session Management | `standup`, `blocked`, `create_handoff`, `resume_handoff` | 4 |
| System Design | `architecture-review`, `design-system`, `tradeoff-analysis` | 3 |
| Automation | `observe-docstrings` | 1 |

When adding a command, decide which category it belongs to. This determines where it appears in documentation and the installer.

### Registration Checklist

Every new command must be registered in **all** of the following locations. Missing any one of them is a bug (the `/review-fix-pr-loop` command was merged without the installer update — this checklist exists because of that).

#### Critical (command won't work in other repos without these)

- [ ] **Create the command file** — `.claude/commands/your-command.md`
- [ ] **Add to installer** — `installers/rpi-workflow.sh`
  - Add a `cp` line in the appropriate category section (~lines 66-89)
  - Update the echo summary count and list (~lines 152-170)
  - Add usage example to "Next steps" section if user-facing (~lines 189+)
- [ ] **Add to installation test** — `test-installation.sh`
  - Add command name to the verification for-loop (~lines 45-51)

#### High Priority (users won't discover the command without these)

- [ ] **Document in CLAUDE.md** — four separate locations:
  1. "Commands Available" section — add bullet with description
  2. "Usage Examples" section — add a code example if user-facing
  3. "Slash Command Quick Reference" table — add a row
  4. "File Organization" tree — add the filename under `.claude/commands/`
- [ ] **Document in README.md** — two locations:
  1. Command count in installation section (~line 112)
  2. Project structure tree (~lines 259-275)

#### Medium Priority

- [ ] **Update install.sh help text** — `install.sh` lines 51-66
  - Add to the "After installation, use these commands" list
- [ ] **Update HOWTO.md** — if the command involves agents, add to the agent reference section

#### Low Priority

- [ ] **Update CHANGELOG.md** — document in the "Added" section for the current version
- [ ] **Update this guide** — update the command category table above

### Command File Structure

Commands use two patterns depending on whether they need pre-computed context.

#### Simple command (no pre-computation)

```markdown
# Command Name

You are tasked with [what Claude should do].

$ARGUMENTS

## Instructions
[Step-by-step instructions for Claude]

## Output Format
[What the output should look like]
```

#### Command with inline bash pre-computation

Pre-computed context eliminates tool-call round-trips. Use `!` backtick syntax:

```markdown
# Command Name

[Description]

## Pre-computed Context

### Git Branch
!`git branch --show-current`

### Recent Commits
!`git log --oneline -10`

### Diff
!`git diff HEAD | head -600`

## Instructions
[Claude sees the pre-computed values above and can act immediately]
```

**Important constraints for inline bash:**
- Do NOT use `VAR=$(...)` command substitution — the inline parser doesn't support it
- Use `xargs -I{}` piping instead: `echo "value" | xargs -I{} some-command {}`
- Test patterns with `./tests/commands/validate_bash_patterns.sh`

### Testing a New Command

1. **Run static validation** before committing:
   ```bash
   ./tests/commands/validate_bash_patterns.sh
   ```

2. **Test inline bash locally** (if applicable):
   ```bash
   grep -oE '!\`[^`]+\`' .claude/commands/new-command.md | while read line; do
       pattern="${line:2:-1}"
       echo "Testing: $pattern"
       bash -c "${pattern//\$ARGUMENTS/test}" && echo "OK" || echo "FAILED"
   done
   ```

3. **Verify installation** in a test project:
   ```bash
   cd /tmp && mkdir test-project && cd test-project
   git init && maximal-ai rpi-workflow
   ls .claude/commands/your-command.md  # Should exist
   ```

### Real Example: Adding `review-fix-pr-loop`

Here's what was required when this command was added:

| File | Change |
|------|--------|
| `.claude/commands/review-fix-pr-loop.md` | Created the 437-line command file |
| `installers/rpi-workflow.sh` | Added `cp` line, updated count from (2) to (3), added usage example |
| `CLAUDE.md` | Added to Commands Available, Usage Examples, Quick Reference table, Workflow section, File Organization tree |
| `test-installation.sh` | Added to verification loop |
| `install.sh` | Added to help text |
| `CHANGELOG.md` | Documented in current version |

---

## Part 2: Adapting the RPI Pattern to New Domains

The core system is domain-agnostic. It works for any complex task that benefits from:

1. Understanding before doing
2. Planning before executing
3. Verification during execution

### Step 1: Map Your Domain's Phases

Ask yourself:
- **Research Phase**: What do I need to understand?
- **Planning Phase**: What do I need to design?
- **Implementation Phase**: What do I need to execute?

### Step 2: Create Your Command Structure

Create three new commands in `.claude/commands/`:

#### `[domain]_research.md`
```markdown
# [Domain] Research

You are tasked with researching [domain-specific context].

## Initial Setup
[Greeting and explanation]

## Research Process
1. [Domain-specific research step 1]
2. [Domain-specific research step 2]
3. [Synthesis step]

## Output Format
[Domain-specific research document structure]
```

#### `[domain]_plan.md`
```markdown
# [Domain] Plan

You are tasked with planning [domain-specific objective].

## Planning Process
1. Read research document
2. [Domain-specific planning steps]
3. Create actionable plan

## Output Format
[Domain-specific plan structure]
```

#### `[domain]_implement.md`
```markdown
# [Domain] Implementation

You are tasked with executing [domain-specific plan].

## Implementation Process
1. Read plan document
2. [Domain-specific execution steps]
3. Verify success

## Success Criteria
[Domain-specific verification]
```

### Step 3: Design Domain-Specific Agents

Create specialized agents in `.claude/agents/`:

```markdown
---
name: [domain]-[specialist]
description: [What this agent specializes in]
tools: [Relevant tools]
model: sonnet
---

You are a specialist at [specific domain task].

## Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]

## Search Strategy
[How to find information]

## Output Format
[How to structure findings]
```

**Model Selection:** Use `model: sonnet` (recommended default) for most agents. Available options: `sonnet` (balanced speed/capability), `opus` (maximum capability), `haiku` (fastest, for simple tasks).

### Step 4: Register Everything

Follow the **Registration Checklist** from Part 1. Every command and agent you create needs to be added to the installer, documentation, and tests.

### Concrete Examples

#### Example 1: Product Management

**Phases:**
1. **Market Research** — Understand users, market, competition
2. **Product Planning** — Design features, specifications, roadmap
3. **Launch Execution** — Implement go-to-market strategy

**Commands:** `/market_research`, `/product_plan`, `/launch_execute`

**Agents:** `user-researcher`, `market-analyzer`, `competitor-analyst`, `stakeholder-mapper`

#### Example 2: Data Science

**Phases:**
1. **Data Exploration** — Understand data, patterns, quality
2. **Model Design** — Plan architecture, features, metrics
3. **Model Training** — Implement and validate model

**Commands:** `/explore_data`, `/design_model`, `/train_model`

**Agents:** `data-profiler`, `feature-engineer`, `model-researcher`, `metric-designer`

#### Example 3: Content Creation

**Phases:**
1. **Content Research** — Topic research, audience analysis
2. **Content Planning** — Outline, structure, key points
3. **Content Production** — Writing, editing, publishing

**Commands:** `/content_research`, `/content_plan`, `/content_write`

**Agents:** `topic-researcher`, `audience-analyzer`, `seo-optimizer`, `fact-checker`

---

## Key Principles

Regardless of domain, always maintain:

1. **Context Resets Between Phases** — Each phase starts fresh, only carries forward the MD document
2. **Parallel Agent Architecture** — Research uses multiple specialized agents working in parallel
3. **Reviewable Artifacts** — Each phase outputs a self-contained, reviewable document
4. **Progressive Refinement** — Research reduces uncertainty, planning reduces ambiguity, implementation reduces risk
5. **Clear Success Criteria** — Automated where possible, manual where necessary, measurable always

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Skip phases to save time | Complete each phase fully |
| Combine phases in one context | Reset context between phases |
| Proceed with open questions | Resolve all ambiguities first |
| Create overly complex agents | Keep agents focused and simple |
| Forget the registration checklist | Update all 10+ locations every time |

## Success Indicators

Your extension is working when:
- Research documents answer all key questions
- Plans are approved without major revisions
- Implementation proceeds without blocking
- Context stays under 40% in each phase
- Output quality matches or exceeds manual work

The power isn't in the specific commands or agents — it's in the pattern:

```
UNDERSTAND → DESIGN → EXECUTE
```

With intentional context management at each transition. Start with the pattern. The rest will follow.
