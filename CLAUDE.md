# CLAUDE.md - Advanced Context Engineering Configuration

This file configures Claude to use the advanced three-phase development workflow: Research → Plan → Implement.

## Repository Overview

This repository implements the advanced context engineering workflow for AI-driven development, based on the principles from the "Advanced Context Engineering for Coding Agents" methodology.

## Core Workflow

### The Three Phases

1. **Research Phase** (`/research`)
   - Understand how the existing system works
   - Identify relevant files and components
   - Pinpoint where changes are needed
   - Prevents misunderstanding that leads to bad code

2. **Planning Phase** (`/plan`)
   - Define every change to be made
   - Include affected files and code snippets
   - Specify verification steps
   - Much shorter than code changes but easier to review

3. **Implementation Phase** (`/implement`)
   - Execute based on the approved plan
   - Follow established patterns
   - Maintain context efficiency
   - Verify at each step

## Commands Available

### Primary Commands
- `/research [query]` - Conduct comprehensive codebase research
- `/plan [research-file or description]` - Create detailed implementation plan
- `/implement [plan-file]` - Execute the implementation plan

### Usage Examples
```bash
# Research how authentication works
/research How does the authentication system work?

# Create a plan based on research
/plan research/2025-01-08-authentication-flow.md

# Implement the plan
/implement plans/2025-01-08-add-oauth-support.md
```

## Key Principles

### Context Management
- **Keep context under 40%** - Maintain efficiency by managing context carefully
- **Intentional compaction** - Actively shrink context to focus on what matters
- **Parallel sub-agents** - Use specialized agents for different research aspects
- **No shouting matches** - Good plans eliminate back-and-forth corrections

### Quality Standards
- **No slop** - Production-ready code only
- **Works in complex codebases** - Handles brownfield development
- **Mental alignment** - Plans are easier to review than PRs
- **Measurable success** - Clear verification criteria

## File Organization

```
project-root/
├── .claude/
│   ├── commands/       # Workflow commands
│   │   ├── research.md
│   │   ├── plan.md
│   │   └── implement.md
│   └── agents/         # Specialized sub-agents
│       ├── codebase-locator.md
│       ├── codebase-analyzer.md
│       ├── codebase-pattern-finder.md
│       └── web-search-researcher.md
├── research/           # Research documents (OUTPUT from phase 1)
│   └── YYYY-MM-DD-topic.md
├── plans/             # Implementation plans (OUTPUT from phase 2)
│   └── YYYY-MM-DD-feature.md
└── CLAUDE.md          # This file
```

## Critical Workflow: Context Resets Between Phases

**IMPORTANT**: Each phase should start with a fresh context window:

1. **Phase 1 (Research)**: Start fresh Claude session
   - Run: `/research How does authentication work?`
   - Output: `research/2025-01-12-authentication.md`
   - Close/clear context

2. **Phase 2 (Planning)**: Start fresh Claude session
   - Run: `/plan research/2025-01-12-authentication.md`
   - Output: `plans/2025-01-12-oauth-support.md`
   - Close/clear context

3. **Phase 3 (Implementation)**: Start fresh Claude session
   - Run: `/implement plans/2025-01-12-oauth-support.md`
   - Execute the plan with verification
   - Complete implementation

This intentional context reset prevents overflow and ensures each phase starts with exactly the information it needs.

## Document Formats

### Research Documents
- Located in `research/` directory
- Named: `YYYY-MM-DD-description.md`
- Include findings, code references, and insights
- Self-contained with all necessary context

### Implementation Plans
- Located in `plans/` directory
- Named: `YYYY-MM-DD-description.md`
- Include phases, specific changes, and success criteria
- Separate automated and manual verification

## Best Practices

### During Research
- Read mentioned files FULLY before spawning sub-tasks
- Use parallel agents for efficiency
- Include specific file:line references
- Think deeply about architectural implications

### During Planning
- Be skeptical and thorough
- Work iteratively with the user
- No open questions in final plan
- Include "What we're NOT doing" section

### During Implementation
- Follow the plan's intent
- Adapt to reality when needed
- Verify continuously
- Update progress tracking

## Context Engineering Tips

1. **Research prevents bad code**
   - Misunderstanding = thousands of bad lines
   - Bad research = hundreds of bad lines
   - Bad plan = tens of bad lines

2. **Review markdown, not code**
   - Research files are easier to review than code
   - Plans show intent clearly
   - Catch problems before implementation

3. **Parallel processing**
   - Spawn multiple research agents simultaneously
   - Each agent focuses on specific aspects
   - Synthesize findings in main context

4. **Progress tracking**
   - Use TodoWrite for task management
   - Update plan checkboxes during implementation
   - Maintain clear status indicators

## Important Reminders

- **Always read files fully** - Never use limit/offset parameters
- **Wait for all agents** - Don't synthesize before agents complete
- **Verify continuously** - Run tests after each phase
- **Document deviations** - Note when reality differs from plan
- **Maintain quality** - No commented code, no TODOs

## Success Metrics

You know the workflow is working when:
- Research documents answer questions completely
- Plans are approved with minimal revisions
- Implementation proceeds without blocking issues
- Tests pass on first run
- Code follows existing patterns
- No back-and-forth corrections needed

## Getting Started

1. Start with `/research` to understand the codebase
2. Use `/plan` to create a detailed implementation plan
3. Execute with `/implement` following the plan
4. Iterate based on verification results

Remember: The goal is not just to write code, but to write the RIGHT code efficiently with minimal context usage and maximum correctness.