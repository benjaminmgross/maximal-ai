# Research

You are tasked with conducting comprehensive research across the codebase to answer user questions by spawning parallel sub-agents and synthesizing their findings.

<research_query>
$ARGUMENTS
</research_query>

## Initial Setup

When this command is invoked:

1. **Check if a research query was provided**:
   - If a query was provided as a parameter, skip the default message
   - Immediately proceed to Step 1 with the provided query
   - Begin the research process

2. **If no query provided**, respond with:
```
I'm ready to research the codebase. Please provide your research question or area of interest, and I'll analyze it thoroughly by exploring relevant components and connections.
```

Then wait for the user's research query.

## Process Steps

### Step 1: Read Directly Mentioned Files
- If the user mentions specific files (tickets, docs, JSON), read them FULLY first
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

### Step 1.5: Load Coding Standards (If Present)

Before decomposing the research query, check for repository coding standards:

1. **Check for coding standards directory**:
   - Use Bash to check if `docs/coding-standards/` exists
   - If the directory doesn't exist, continue normally (graceful degradation)

2. **If standards directory exists**:
   - Spawn a **codebase-analyzer** sub-agent with this prompt:
     ```
     Read and synthesize all markdown files in docs/coding-standards/ directory.

     Extract and return:
     1. Key architectural patterns (e.g., package structure, file organization)
     2. Critical anti-patterns to avoid
     3. Technology-specific guidelines (e.g., async usage, dependency management)
     4. Code quality standards (formatting, testing, imports)

     Format as a concise summary with specific file:line references for each guideline.
     Limit response to essential patterns only - focus on what would impact development decisions.
     ```

   - Wait for the sub-agent to complete before proceeding
   - Store the synthesized standards in context for reference during analysis

3. **If standards directory does not exist**:
   - Continue normally without standards (graceful degradation)
   - No need to mention absence to the user

**IMPORTANT**: Standards loading should happen BEFORE decomposing the research query, so architectural patterns can inform which components to investigate.

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
- **If coding standards were loaded**: Cross-reference findings with established patterns
  - Note where current implementation follows standards
  - Highlight any deviations from documented patterns
  - Reference specific standards when applicable (e.g., "Uses async pattern contrary to docs/coding-standards/repo-standards.md:240")
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

## Coding Standards Adherence
[**Only include this section if coding standards were loaded**]

**Standards Location**: `docs/coding-standards/*.md`

### Patterns Followed:
- [Pattern from standards that current code follows] - Reference: repo-standards.md:123
- [Another pattern that's being used correctly]

### Deviations Found:
- [Deviation from documented standards] - Reference: repo-standards.md:240
  - Current implementation: [what exists]
  - Expected per standards: [what standards recommend]
  - Impact: [Low/Medium/High]

### Recommendations:
- [Suggestion for aligning with standards, if relevant to research query]

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
