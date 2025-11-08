---
description: Create handoff document for transferring work to another session
---

# Create Handoff

You are tasked with writing a handoff document to hand off your work to another agent in a new session. You will create a handoff document that is thorough, but also **concise**. The goal is to compact and summarize your context without losing any of the key details of what you're working on.


## Process
### 1. Filepath & Metadata
Use the following information to understand how to create your document:

>  **File Naming:** create your file under `handoffs/YYYY-MM-DD_description.md`, where:
>
> * YYYY-MM-DD is today's date
> * Description is a brief kebab-case description
>
> **Frontmatter:** Create the following frontmatter, use standard commands to identify information that isn't readily available in the session. 
>
> ```
> ---
> date: [Current date and time with timezone in ISO format]
> researcher: [Researcher name from session]
> git_commit: [Current commit hash if applicable]
> branch: [Current branch name if applicable]
> repository: [Repository name if applicable]
> topic: [10 word description of the session toipc]
> tags: [5 - 10 tags that describe the session]
> description: [50 words summarizing the session]
> ---
> ```

### 2. Handoff writing
using the above conventions, write your document. use the defined filepath, and the following YAML frontmatter pattern (derived above). Use the front matter gathered in step 1, Structure the document with YAML frontmatter followed by content:

Use the following template structure:
```markdown
---
date: [Current date and time with timezone in ISO format]
researcher: [Researcher name from session]
git_commit: [Current commit hash if applicable]
branch: [Current branch name if applicable]
repository: [Repository name if applicable]
topic: [10 word description of the session toipc]
tags: [5 - 10 tags that describe the session]
description: [20 words summarizing the session]
---

# Handoff: {very concise description}

## Task(s)
{description of the task(s) that you were working on, along with the status of each (completed, work in progress, planned/discussed). If you are working on an implementation plan, make sure to call out which phase you are on. Make sure to reference the plan document and/or research document(s) you are working from that were provided to you at the beginning of the session, if applicable.}

## Critical References
{List any critical specification documents, architectural decisions, or design docs that must be followed. Include only 2-3 most important file paths. Leave blank if none.}

## Recent changes
{describe recent changes made to the codebase that you made in line:file syntax}

## Learnings
{describe important things that you learned - e.g. patterns, root causes of bugs, or other important pieces of information someone that is picking up your work after you should know. Consider listing explicit file paths.}

## Unsolved Issues
{If there are any, describe specific issues that were not resolved and what was attempted. List explicit file paths if appropriate}

## Artifacts
{an exhaustive list of artifacts you produced or updated as filepaths and/or file:line references - e.g. paths to feature documents, implementation plans, etc that should be read in order to resume your work.}

## Action Items & Next Steps
{a list of action items and next steps for the next agent to accomplish based on your tasks and their statuses}

## Other Notes
{other notes, references, or useful information - e.g. where relevant sections of the codebase are, where relevant documents are, or other important things you leanrned that you want to pass on but that don't fall into the above categories}
```
---
##  Additional Notes & Instructions

- **more information, not less**. This is a guideline that defines the minimum of what a handoff should be. Always feel free to include more information if necessary.
- **be thorough and precise**. include both top-level objectives, and lower-level details as necessary.
- **avoid excessive code snippets**. While a brief snippet to describe some key change is important, avoid large code blocks or diffs; do not include one unless it's necessary (e.g. pertains to an error you're debugging). Prefer using `/path/to/file.ext:line` references that an agent can follow later when it's ready, e.g. `packages/dashboard/src/app/dashboard/page.tsx:12-24`
