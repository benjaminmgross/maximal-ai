---
description: Conduct comprehensive codebase research by spawning parallel sub-agents
---

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

### Step 1.25: Pre-Research Clarifying Questions

Before spawning agents, ask **minimal clarifying questions** to ensure you understand what to research:

**IMPORTANT**:
- Ask questions **ONE AT A TIME** (serial, not parallel)
- Prefer **multiple choice** when possible
- Focus on **MINIMAL information needed**, not exhaustive discovery
- Only ask 2-4 questions maximum
- Goal: Ensure agents research the RIGHT thing, not everything

**Question Framework** (adapt to context, don't ask all):

1. **Feature Type**:
   - "What type of work is this? (A) New feature, (B) Bug fix, (C) Refactoring, (D) Investigation"

2. **Expected Scope** (if unclear from initial query):
   - "Which repos do you expect this to touch? (A) Single repo: [name], (B) Multiple repos: [list], (C) Unknown - please investigate"

3. **Integration Concerns** (if feature spans repos):
   - "Does this feature involve: (A) API calls between services, (B) Shared data models, (C) Database changes, (D) All of the above, (E) None - isolated feature"

4. **Acceptance Criteria** (if not provided):
   - "How will we know this works? (A) Specific test passes, (B) User can perform action X, (C) System behaves as Y, (D) Not sure - help me define this"

**When to Skip Questions**:
- User provided a detailed research document or spec → Skip, read the doc
- Query is clearly scoped investigation ("How does X work?") → Skip, research is the answer
- User explicitly said "just investigate" → Skip, open-ended research

**Output Format**:
```
I have a few quick questions before I start researching:

1. [First question with multiple choice options]

[Wait for response, then ask next question if needed]
```

Only proceed to Step 1.5 (Load Coding Standards) after getting answers or determining questions aren't needed.

### Step 1.5: Load Coding Standards (If Present)

Before decomposing the research query, check for repository coding standards:

1. **Check for coding standards using priority order**:
   ```bash
   # Priority 1: External standards via EXTERNAL_DOCS_PATH environment variable
   if [ -n "$EXTERNAL_DOCS_PATH" ] && [ -d "$EXTERNAL_DOCS_PATH/cross-cutting/coding-standards/" ]; then
       STANDARDS_PATH="$EXTERNAL_DOCS_PATH/cross-cutting/coding-standards/"
       echo "Found external coding standards (via EXTERNAL_DOCS_PATH)"
   # Priority 2: Local repository standards
   elif [ -d "docs/coding-standards/" ]; then
       STANDARDS_PATH="docs/coding-standards/"
       echo "Found local coding standards"
   else
       STANDARDS_PATH=""
   fi
   ```

2. **If standards found** (`STANDARDS_PATH` is not empty):
   - Spawn a **codebase-analyzer** sub-agent with this prompt:
     ```
     Read and synthesize all markdown files in [STANDARDS_PATH] directory.

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

3. **If no standards found**:
   - Continue normally without standards (graceful degradation)
   - No need to mention absence to the user

**IMPORTANT**: Standards loading should happen BEFORE decomposing the research query, so architectural patterns can inform which components to investigate.

### Step 1.75: Detect Architecture-Relevant Queries

Before decomposing the query, determine if the research involves architectural analysis. This enables specialized system-design agents to be spawned alongside standard research agents.

**Detection Triggers** - Check if the query contains any of these signals:

**Keywords** (case-insensitive):
- "architecture", "architectural", "design", "system design"
- "scalability", "scalable", "scale", "scaling"
- "bottleneck", "performance", "latency"
- "pattern", "anti-pattern", "best practice"
- "tradeoff", "trade-off", "decision"
- "microservices", "monolith", "event-driven"
- "coupling", "cohesion", "dependency"

**Question Types**:
- Questions about system structure: "How is X organized?"
- Questions about component interactions: "How do X and Y communicate?"
- Questions about data flow: "How does data flow from X to Y?"
- Scaling questions: "How would we scale X?"
- Review requests: "Review the architecture of X"
- Decision questions: "Should we use X or Y?"

**Examples**:
```
"How does the authentication system work?"
    → Standard research (no architecture focus)

"What are the scalability concerns in our payment system?"
    → Architecture-relevant (spawn scalability-assessor)

"Should we use SQL or NoSQL for the new feature?"
    → Architecture-relevant (spawn tradeoff-researcher)

"Review the architecture of the API layer"
    → Architecture-relevant (spawn architecture-pattern-detector)

"What patterns are used in the codebase?"
    → Architecture-relevant (spawn architecture-pattern-detector)
```

**If Architecture-Relevant**:
1. Set `ARCHITECTURE_RESEARCH=true` for later reference
2. Load system design reference materials:
   ```
   Read: .claude/docs/system-design/patterns-catalog.md
   Read: .claude/docs/system-design/anti-patterns-catalog.md
   Read: .claude/docs/system-design/scalability-checklist.md
   ```
3. Note which specialized agents to spawn in Step 3 based on query type:
   - **Pattern/structure questions** → `architecture-pattern-detector`
   - **Scalability/bottleneck questions** → `scalability-assessor`
   - **Decision/tradeoff questions** → `tradeoff-researcher`

**If NOT Architecture-Relevant**:
- Continue with standard research flow
- No additional agents needed

**IMPORTANT**: Architecture detection should be quick - don't over-analyze. When in doubt, default to standard research.

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
- Use the **thoughts-locator** agent to search prior research, plans, and handoffs (requires $THOUGHTS_PATH)

**For architecture-relevant research** (if `ARCHITECTURE_RESEARCH=true` from Step 1.75):
- Use the **architecture-pattern-detector** agent to identify patterns and anti-patterns
- Use the **scalability-assessor** agent for bottleneck and capacity analysis
- Use the **tradeoff-researcher** agent for decision evaluation (if tradeoff question)

**Architecture Agent Prompts:**

For pattern detection:
```
Analyze the codebase [scope if specified] to identify:
1. Primary architectural pattern(s) in use
2. Anti-patterns and code smells
3. Layer violations or inconsistencies

Reference patterns from .claude/docs/system-design/patterns-catalog.md
Provide file:line evidence for all findings.
Focus on: [specific area from user query]
```

For scalability assessment:
```
Analyze the codebase [scope if specified] for scalability:
1. Database patterns and potential bottlenecks
2. Connection pool and resource configurations
3. Single points of failure
4. Horizontal scaling blockers

Reference .claude/docs/system-design/scalability-checklist.md
Provide file:line evidence for all findings.
Focus on: [specific concern from user query]
```

For tradeoff research:
```
Research the tradeoff between [Option A] and [Option B] for [context from query].
Load and apply decision framework from .claude/docs/system-design/tradeoff-decision-trees.md
Include external best practices if relevant.
Return: Recommendation with clear rationale.
```

**For web research (only if user explicitly asks):**
- Use the **web-search-researcher** agent for external documentation and resources
- IF you use web-research agents, instruct them to return LINKS with their findings

The key is to use these agents intelligently:
- Start with locator agents to find what exists
- Then use analyzer agents on the most promising findings
- Run multiple agents in parallel when they're searching for different things
- Each agent knows its job - just tell it what you're looking for
- Don't write detailed prompts about HOW to search - the agents already know
- **For architecture queries**: Spawn system-design agents IN PARALLEL with standard agents

### Step 4: Wait and Synthesize
- **IMPORTANT**: Wait for ALL sub-agent tasks to complete before proceeding
- Compile all sub-agent results
- Connect findings across different components
- **If coding standards were loaded**: Cross-reference findings with established patterns
  - Note where current implementation follows standards
  - Highlight any deviations from documented patterns
  - Reference specific standards when applicable (e.g., "Uses async pattern contrary to docs/coding-standards/repo-standards.md:240")
- **If architecture agents were spawned** (`ARCHITECTURE_RESEARCH=true`):
  - Synthesize pattern detection findings into "Architecture Insights" section
  - Include scalability assessment results with severity ratings
  - Present tradeoff analysis with clear recommendation (if applicable)
  - Cross-reference findings with system design reference materials
  - Prioritize issues by impact (Critical > High > Medium > Low)
- Include specific file paths and line numbers for reference
- Highlight patterns, connections, and architectural decisions
- Answer the user's specific questions with concrete evidence

### Step 5: Generate Research Document

**IMPORTANT**: After generating the research document, complete the "Research Validation Checks" section at the end to ensure no hallucinations or placeholders remain.

### Username Detection for File Naming

Before creating the research document, detect the username to use in the filename:

1. **Detect username with priority order**:
   ```bash
   # Priority 1: Check .claude/config.yaml for username
   if [ -f ".claude/config.yaml" ]; then
       CONFIG_USERNAME=$(grep "^username:" .claude/config.yaml | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
   fi

   # Priority 2: Check RPI_USERNAME environment variable
   # Priority 3: Fallback to git config user.name
   # Priority 4: Default to "user"
   RPI_USERNAME="${CONFIG_USERNAME:-${RPI_USERNAME:-$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')}}"
   RPI_USERNAME="${RPI_USERNAME:-user}"

   echo "Using username: $RPI_USERNAME"
```

2. **Format the date with dots**: Use `YYYY.MM.DD` format instead of `YYYY-MM-DD`
   ```bash
   CURRENT_DATE=$(date +%Y.%m.%d)
   ```

3. **Construct filename**: `{CURRENT_DATE}-{RPI_USERNAME}-{description}.md`
   - Example: `2025.11.13-benjamin-authentication-flow.md`
   - Example: `2025.11.13-shared-api-documentation.md`

Create the document at `thoughts/research/YYYY.MM.DD-{username}-description.md` with this structure:

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

## Expected Repos Involved

**Primary Repository**: [repo name where main changes occur]

**Secondary Repositories**:
- [repo name]: [why it's involved - API consumer, shared model, etc.]
- [repo name]: [why it's involved]

**Rationale**: [Brief explanation of why these repos are involved based on research findings]

**Cross-Repo Dependencies**:
- [Repo A] → [Repo B]: [nature of dependency - API call, shared model, etc.]

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

## Architecture Assessment
[**Only include this section if architecture agents were spawned (ARCHITECTURE_RESEARCH=true)**]

### Architectural Patterns Detected
| Pattern | Location | Confidence | Notes |
|---------|----------|------------|-------|
| [Pattern name] | `path/to/dir/` | High/Med/Low | [Brief description] |

### Anti-Patterns Identified
| Anti-Pattern | Severity | Location | Impact |
|--------------|----------|----------|--------|
| [Anti-pattern] | Critical/High/Med/Low | `file:line` | [Impact description] |

### Scalability Concerns
| Concern | Severity | Component | Recommendation |
|---------|----------|-----------|----------------|
| [Issue] | Critical/High/Med/Low | [Component] | [Fix suggestion] |

### Single Points of Failure
- [ ] [SPOF 1]: `location` - [impact if fails]
- [ ] [SPOF 2]: `location` - [impact if fails]

### Tradeoff Analysis
[**Only include if tradeoff question was asked**]

**Decision:** [What needs to be decided]
**Recommendation:** [Recommended option]
**Rationale:** [Why this option]
**Reversibility:** [How hard to change later]

### Architecture Recommendations
| Priority | Issue | Solution | Effort |
|----------|-------|----------|--------|
| 1 | [Issue] | [Solution] | Low/Med/High |
| 2 | [Issue] | [Solution] | Low/Med/High |

## Integration Points

[**Only include this section if the feature spans multiple repos or services**]

### API Calls Between Services:
- **[Service A] → [Service B]**:
  - Endpoint: `[HTTP method] /path/to/endpoint`
  - Purpose: [what data is exchanged]
  - File reference: `service-a/file.py:123`
  - OpenAPI client used: [yes/no, which client]

### Shared Data Models/Schemas:
- **[Model Name]**:
  - Defined in: `repo/path/to/model.py:45`
  - Used by: [list repos/services]
  - Schema validation: [where defined]

### Database Changes Required:
- **[Table name]**:
  - Changes: [new columns, indices, etc.]
  - Migration location: [path to migration]
  - Affects repos: [list]

### External Dependencies:
- **[Library/Service name]**:
  - Purpose: [why needed]
  - Integration pattern: [how it's used]
  - Configuration: [where config lives]

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

## Questions for Hardened Requirements

**These questions MUST be answered before implementation begins. If research couldn't answer them, flag them explicitly.**

### Integration Questions:
- [ ] Have all API contracts between services been identified?
- [ ] Are OpenAPI client versions compatible across repos?
- [ ] Are shared data model schemas aligned?
- [ ] Have database migration dependencies been mapped?

### Data Flow Questions:
- [ ] How does data move between [Component A] and [Component B]?
- [ ] What happens if [Service X] is unavailable?
- [ ] Are there race conditions in the data flow?
- [ ] What validation happens at each boundary?

### Edge Case Questions:
- [ ] What happens when [expected condition] fails?
- [ ] How are errors propagated across service boundaries?
- [ ] What are the rollback procedures if deployment fails?
- [ ] Are there backwards compatibility concerns?

### Testing Questions:
- [ ] Can this be tested in isolation or does it require full integration?
- [ ] What test data is needed?
- [ ] Are there existing test patterns to follow?
- [ ] What's the acceptance test that proves this works?

**Unanswered Questions**:
[List any questions above that research could not answer and require CTO input or further investigation]

## Research Validation Checks

**Before finalizing this research document, verify:**

- [ ] **File Verification**: All mentioned file paths have been confirmed to exist using Read tool
- [ ] **Code Reference Verification**: All `file:line` references have been verified against actual code
- [ ] **Test Execution**: If claiming functionality works, tests were run and output verified
- [ ] **No Placeholders**: No sections contain placeholder text like "[TODO]" or "[TBD]"

**If any checks fail, update the research document before marking as complete.**

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

### Step 8: Offer to Commit Document

After the research document is finalized (either initial creation or after follow-ups):

1. **Check if THOUGHTS_PATH is configured**:
   ```bash
   if [ -z "$THOUGHTS_PATH" ]; then
       # Silently skip - user hasn't set up thoughts repo
       exit 0
   fi
   ```

2. **Prompt user for approval** using AskUserQuestion:
   ```
   Use AskUserQuestion with:
   - question: "Commit this research to GitHub?"
   - header: "Commit"
   - options:
     - label: "Yes", description: "Commit to minty-thoughts and create discussion"
     - label: "Commit only", description: "Commit to minty-thoughts without creating discussion"
     - label: "No", description: "Keep document local only"
   ```

3. **If user selects "Yes"**:
   - Execute the commit script:
     ```bash
     "$MAXIMAL_AI_HOME/.claude/hooks/commit-thoughts.sh" research "thoughts/research/{filename}"
     ```
   - Parse the output:
     - If exit code 0: Report full success with discussion URL
     - If exit code 1: Report partial success (committed but discussion failed)
     - If exit code 2: Report failure

4. **If user selects "Commit only"**:
   - Execute the commit script with --no-discussion flag:
     ```bash
     "$MAXIMAL_AI_HOME/.claude/hooks/commit-thoughts.sh" --no-discussion research "thoughts/research/{filename}"
     ```
   - Report commit success (discussion is intentionally skipped)

5. **If user selects "No"**:
   - Respond: "Document saved locally at `thoughts/research/{filename}`"

6. **Output format for full success** (commit + discussion):
   ```
   Committed to minty-thoughts!
   - Commit: {commit_sha}
   - Discussion: {url}
   ```

7. **Output format for commit only**:
   ```
   Committed to minty-thoughts!
   - Commit: {commit_sha}
   - Discussion: Skipped
   ```

8. **Output format for partial success** (discussion failed):
   ```
   Committed to minty-thoughts!
   - Commit: {commit_sha}
   - Discussion: Failed to create (commit still succeeded)
   ```

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
