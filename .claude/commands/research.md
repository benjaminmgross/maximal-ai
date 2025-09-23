# Research

You are tasked with conducting comprehensive research across the codebase to answer user questions by spawning parallel sub-agents and synthesizing their findings.

## Initial Setup

When this command is invoked, respond with:
```
I'm ready to research the codebase. Please provide your research question or area of interest, and I'll analyze it thoroughly by exploring relevant components and connections.
```

Then wait for the user's research query.

## Steps to follow after receiving the research query

### Step 1: Read Directly Mentioned Files
- If the user mentions specific files (tickets, docs, JSON), read them FULLY first
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

### Step 2: Analyze and Decompose
- Break down the user's query into composable research areas
- Take time to think deeply about the underlying patterns, connections, and architectural implications
- Identify specific components, patterns, or concepts to investigate
- Create a research plan using TodoWrite to track all subtasks
- Consider which directories, files, or architectural patterns are relevant

### Step 3: Spawn Parallel Sub-Agent Tasks
Create multiple Task agents to research different aspects concurrently:

**For codebase research:**
- Use the **codebase-locator** agent to find WHERE files and components live
- Use the **codebase-analyzer** agent to understand HOW specific code works
- Use the **codebase-pattern-finder** agent if you need examples of similar implementations

**For web research (only if user explicitly asks):**
- Use the **web-search-researcher** agent for external documentation and resources
- IF you use web-research agents, instruct them to return LINKS with their findings

The key is to use these agents intelligently:
- Start with locator agents to find what exists
- Then use analyzer agents on the most promising findings
- Run multiple agents in parallel when they're searching for different things
- Each agent knows its job - just tell it what you're looking for
- Don't write detailed prompts about HOW to search - the agents already know

### Step 4: Wait and Synthesize
- **IMPORTANT**: Wait for ALL sub-agent tasks to complete before proceeding
- Compile all sub-agent results
- Connect findings across different components
- Include specific file paths and line numbers for reference
- Highlight patterns, connections, and architectural decisions
- Answer the user's specific questions with concrete evidence

### Step 5: Generate Research Document

Create the document at `research/YYYY-MM-DD-description.md` with this structure:

```markdown
---
date: [Current ISO datetime with timezone]
researcher: [Your name]
git_commit: [Current commit hash if available]
branch: [Current branch name if available]
repository: [Repository name]
topic: "[User's Question/Topic]"
tags: [research, codebase, relevant-component-names]
status: complete
last_updated: [Current date in YYYY-MM-DD format]
last_updated_by: [Your name]
---

# Research: [User's Question/Topic]

**Date**: [Current ISO datetime]
**Researcher**: [Your name]
**Git Commit**: [If available]
**Branch**: [If available]
**Repository**: [Repository name]

## Research Question
[Original user query]

## Summary
[High-level findings answering the user's question - 2-3 paragraphs]

## Detailed Findings

### [Component/Area 1]
- Finding with reference ([file.ext:line](link))
- Connection to other components
- Implementation details

### [Component/Area 2]
...

## Code References
- `path/to/file.py:123` - Description of what's there
- `another/file.ts:45-67` - Description of the code block

## Architecture Insights
[Patterns, conventions, and design decisions discovered]

## Related Research
[Links to other research documents if available]

## Open Questions
[Any areas that need further investigation]

## Next Steps
[Recommended actions based on the research]
```

### Step 6: Present Findings
- Present a concise summary of findings to the user
- Include key file references for easy navigation
- Provide mermaid charts, when relevant, to facilitate understanding
- Ask if they have follow-up questions or need clarification

### Step 7: Handle Follow-ups
- If the user has follow-up questions, append to the same research document
- Update the frontmatter fields `last_updated` and `last_updated_by`
- Add a new section: `## Follow-up Research [timestamp]`
- Spawn new sub-agents as needed for additional investigation

## Important Notes

- Always use parallel Task agents to maximize efficiency and minimize context usage
- Focus on finding concrete file paths and line numbers for developer reference
- Research documents should be self-contained with all necessary context
- Each sub-agent prompt should be specific and focused on read-only operations
- Consider cross-component connections and architectural patterns
- Include temporal context (when the research was conducted)
- Keep the main agent focused on synthesis, not deep file reading
- Encourage sub-agents to find examples and usage patterns, not just definitions
- **File reading**: Always read mentioned files FULLY (no limit/offset) before spawning sub-tasks
- **Critical ordering**: Follow the numbered steps exactly
- **NEVER** write the research document with placeholder values

## Success Indicators

Good research documents:
- Answer the user's question completely
- Provide concrete code references
- Provide mermaid charts, when relevant, to facilitate understanding
- Identify patterns and connections
- Are immediately actionable
- Include enough context for future reference

## Example Usage

```
User: /research How does the authentication system work in this codebase?