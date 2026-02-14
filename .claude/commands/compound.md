---
description: Document solved problems to compound team knowledge
---

# Compound

You are tasked with capturing a solved problem, pattern, or insight as a searchable learning document in `thoughts/learnings/`. This closes the feedback loop: Research → Plan → Implement → Review → **Compound**.

<learning_context>
$ARGUMENTS
</learning_context>

## Username & Environment Detection

!`source .claude/hooks/detect-username.sh && echo "Username: $RPI_USERNAME" && echo "Date: $CURRENT_DATE"`

!`echo "Repository: $(basename $(pwd))" && echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')" && echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"`

## Process

### Step 1: Determine Learning Context

**If arguments were provided** (the `<learning_context>` above is not empty):
- Use the provided context as the starting point
- Proceed to Step 2

**If no arguments provided**:
- Respond with:
```
What did you learn? Describe the problem you solved, pattern you discovered, or insight you gained.

Examples:
- "Fixed N+1 query in user loading by eager loading associations"
- "Discovered that EventBridge rules need explicit IAM permissions for cross-account targets"
- "Found that pytest fixtures with module scope can cause test pollution"
```
- Wait for the user's response before continuing

### Step 2: Search for Duplicate/Related Learnings

Before creating a new document, check if this learning already exists:

Spawn a **thoughts-locator** agent:
```
Search for existing learnings related to: [learning context]
Focus on:
1. Files in thoughts/learnings/ directory
2. Files matching *-learnings-* in the searchable index
3. Similar topics in research and plans that may already cover this

Return: Any duplicates or highly related prior work.
```

**If a duplicate is found**:
- Show the existing document to the user
- Ask: "A similar learning already exists. Would you like to (A) Update the existing document, (B) Create a new one anyway, (C) Skip?"

**If no duplicate found**: Continue to Step 3.

### Step 3: Gather Details

Use AskUserQuestion to fill in any gaps. Ask up to 3 questions, adapting based on context already provided:

1. **Category** (if not obvious from context):
   ```
   question: "What category best fits this learning?"
   header: "Category"
   options:
     - label: "Debugging", description: "Bug fixes, error resolution, root cause analysis"
     - label: "Pattern", description: "Code patterns, design approaches, best practices"
     - label: "Architecture", description: "System design, infrastructure, scaling decisions"
     - label: "Tooling", description: "Developer tools, CI/CD, build systems, IDE config (also: workflow, performance, testing, integration via Other)"
   ```

2. **Severity** (if not obvious):
   ```
   question: "How critical is this learning for future work?"
   header: "Severity"
   options:
     - label: "Critical", description: "Would cause outage, data loss, or security issue if repeated"
     - label: "High", description: "Significant time waste or quality impact if not known"
     - label: "Medium", description: "Useful to know, moderate time savings"
     - label: "Low", description: "Nice to know, minor convenience"
   ```

3. **Prevention** (if not already described):
   - "How can this be prevented in the future? (tests, linting rules, documentation, patterns)"

**Skip questions** when the context already provides clear answers.

### Step 4: Create Learning Document

Create the document at `thoughts/learnings/{CURRENT_DATE}-{RPI_USERNAME}-{description}.md`:

```markdown
---
date: [Current ISO datetime with timezone]
author: [RPI_USERNAME]
repository: [repo name]
branch: [current branch]
category: [debugging|pattern|architecture|tooling|workflow|performance|testing|integration]
severity: [critical|high|medium|low]
tags: [searchable, relevant, tags]
related_files: [file paths involved in the learning]
status: complete
---

# Learning: [Descriptive Title]

## Problem
[What went wrong or what needed solving]

## Root Cause
[Why it happened — the underlying issue]

## Solution
[How it was fixed, with code examples if applicable]

## Prevention
[How to avoid recurrence — tests, patterns, checks]

## Key Takeaway
[One-sentence summary for quick scanning]
```

**Guidelines**:
- The title should be specific and scannable (e.g., "EventBridge cross-account rules require explicit IAM trust policy")
- Include code snippets in Solution when they clarify the fix
- Tags should be terms someone would search for when hitting the same problem
- related_files should list actual file paths from the codebase
- Keep it concise — this is a reference document, not a research paper

### Step 5: Present and Confirm

Show the user a summary:
```
Learning documented: thoughts/learnings/{filename}

Title: [title]
Category: [category] | Severity: [severity]
Tags: [tags]

Key Takeaway: [one-sentence summary]
```

### Step 6: Offer to Commit

Check if THOUGHTS_PATH is configured:

```bash
if [ -z "$THOUGHTS_PATH" ]; then
    exit 0
fi
```

Use AskUserQuestion:
```
question: "Commit this learning to GitHub?"
header: "Commit"
options:
  - label: "Yes", description: "Commit to minty-thoughts and create discussion"
  - label: "Commit only", description: "Commit to minty-thoughts without creating discussion"
  - label: "No", description: "Keep document local only"
```

**If "Yes"**:
```bash
"$MAXIMAL_AI_HOME/.claude/hooks/commit-thoughts.sh" learning "thoughts/learnings/{filename}"
```

**If "Commit only"**:
```bash
"$MAXIMAL_AI_HOME/.claude/hooks/commit-thoughts.sh" --no-discussion learning "thoughts/learnings/{filename}"
```

**If "No"**:
- Respond: "Learning saved locally at `thoughts/learnings/{filename}`"

## Important Notes

- Learning documents should be **self-contained** — someone hitting the same problem should be able to fix it from this document alone
- Prefer **specific** over **general** — "pytest module-scoped fixtures cause DB state pollution" is better than "be careful with test fixtures"
- Include **code examples** when they make the solution clearer
- **Tags matter** — they're how future sessions find this learning
- Keep it **concise** — if the learning needs more than a page, consider splitting into a learning + a research document
