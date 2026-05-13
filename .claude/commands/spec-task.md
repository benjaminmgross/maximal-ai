---
description: Author or audit an implementation spec before RPI planning
---

# Spec Task

Authors or audits an implementation spec before it enters the Research -> Plan -> Implement workflow. A spec is the contract between product/technical intent and execution; this command is the quality gate before `/plan`, `/implement`, or `/epic-oneshot`.

<task_args>
$ARGUMENTS
</task_args>

## Pre-computed Context

### Existing Spec-Like Files
!`find . -path './.git' -prune -o -type f \( -path './specs/*.md' -o -path './docs/specs/*.md' -o -path './roadmap/initiatives/*.md' -o -path './plans/*.md' -o -path './thoughts/plans/*.md' \) -print 2>/dev/null | head -40`

### Local Spec Templates
!`find . -path './.git' -prune -o -type f \( -iname '*spec*template*.md' -o -iname '*initiative*template*.md' -o -path './roadmap/templates/*.md' -o -path './docs/templates/*.md' \) -print 2>/dev/null | head -40`

### Decision Records
!`find . -path './.git' -prune -o -type f \( -path './docs/adr/*.md' -o -path './docs/adrs/*.md' -o -path './docs/architecture/decisions/*.md' -o -path './roadmap/decisions/*.md' -o -path './.context/decisions/*.md' \) -print 2>/dev/null | head -60`

### Current Branch
!`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"`

## When To Use

Use `/spec-task` when intent is still being shaped and the next useful artifact is a spec, not code:

- prepare an implementation brief from a rough prompt,
- convert research or notes into an executable spec,
- audit an existing spec before `/plan`,
- migrate an older freeform brief into a stricter template,
- review acceptance criteria and risks before assigning work to an agent.

If the user already provided an approved implementation plan, use `/implement` instead. If the user wants codebase discovery, use `/research` first.

## Process

### Step 1: Resolve The Argument

Parse `<task_args>` into one of these modes:

| Input shape | Mode | Examples |
| --- | --- | --- |
| Existing Markdown file under a likely spec directory | **audit-in-place** | `specs/search-index.md`, `roadmap/initiatives/T1.CORE-004-foo.md` |
| Existing Markdown file outside a likely spec directory | **source-mode** | `thoughts/research/2026.05.13-rough-notes.md` |
| Existing ticket/task ID and local project docs explain tracker commands | **tracker-mode** | `PROJ-123`, `repo-abc` |
| Freeform text or no matching file | **greenfield** | `"Add OAuth refresh token rotation"` |

Prefer interpretation in this order when ambiguous:

1. tracker-mode if local project instructions define the tracker and the ID shape matches,
2. audit-in-place if the path is already a spec,
3. source-mode if the path is source material,
4. greenfield.

Ask one concise clarification only if choosing the wrong mode would cause file writes in the wrong place.

### Step 2: Load Local Spec Conventions

Read project instructions and local spec materials before drafting or reviewing:

1. `AGENTS.md` and `CLAUDE.md` when present.
2. The first applicable spec template in this priority order:
   - project-local path named by `CLAUDE.md` or `AGENTS.md`,
   - `specs/template.md`,
   - `docs/specs/template.md`,
   - `roadmap/templates/initiative-brief.md`,
   - `docs/templates/*spec*.md`.
3. Roadmap, architecture, and decision context when present:
   - `README.md`,
   - `.context/substrate.md`,
   - `.repomap.yaml` or `REPOMAP.yaml`,
   - `docs/architecture/**`,
   - `docs/adr/**` or `docs/adrs/**`,
   - `docs/architecture/decisions/**`,
   - `roadmap/**`.
4. Risk, testing, and standards docs when present:
   - `docs/risk*`,
   - `roadmap/risk-register.md`,
   - `docs/testing*`,
   - `.context/testing.md`,
   - `docs/coding-standards/**`.

If none of these exist, continue with the generic schema in Step 4.

### Step 3: Resolve The Working Spec

#### audit-in-place

- Read the spec fully.
- Parse its title, status, dependencies, acceptance criteria, risks, and any source artifact links.
- Read source artifacts and dependent specs if the spec references them.

#### source-mode

- Read the source file fully.
- Choose a target path using local conventions. If none exist, use `specs/<slug>.md`.
- Draft a new spec from the source, preserving concrete claims, numbers, file paths, and constraints.
- Add the source path in a `Source` or `source_artifact` field if the local template supports it.

#### greenfield

- Treat the prompt as the source.
- Choose a target path using local conventions. If none exist, use `specs/<slug>.md`.
- Draft a new spec, marking unknowns explicitly instead of inventing facts.

#### tracker-mode

- Use only tracker commands documented by the local project.
- Resolve linked design/spec paths from tracker metadata if available.
- If no linked spec exists, draft one using the tracker title/description as source material.
- Do not assume any specific tracker such as GitHub Issues, Linear, Jira, or `bd`; project docs own that integration.

### Step 4: Generic Spec Schema

If the project has no template, draft or normalize to this structure:

```markdown
# <Spec Title>

Status: Draft
Owner: <person or unknown>
Source: <prompt, source file, ticket, or unknown>
Updated: YYYY-MM-DD

## Problem
<Observable problem, affected users/systems, cost, and why now. Avoid solution-only framing.>

## Goals
- <Outcome 1>
- <Outcome 2>

## Non-Goals
- <Explicitly excluded scope>

## Context
<Relevant architecture, existing behavior, decisions, and constraints. Include file/doc references where available.>

## Approach
<Proposed implementation strategy at enough detail for /plan to decompose safely.>

## Acceptance Criteria
- [ ] <Machine-checkable or named-human-checkable criterion> -- verified by: <test/query/dashboard/reviewer>
- [ ] <Criterion> -- verified by: <path or manual verification owner>
- [ ] <Criterion> -- verified by: <path or manual verification owner>

## Risks
- <Concrete technical/product risk> -- mitigation: <specific mitigation>

## Dependencies
- <Upstream dependency or "None">

## Open Questions
- <Question, owner, and unblock condition>
```

### Step 5: Invoke Or Apply `spec-reviewer`

Review every draft or existing spec with the `spec-reviewer` agent. If subagents are unavailable in the current environment, perform the same review locally using the agent rubric.

Use a prompt like:

```text
Review the implementation spec at <path>.

Mode: <audit-in-place | source-mode | greenfield | tracker-mode>
Source material: <source path, tracker id, prompt summary, or none>
Local template: <path or none>

Walk every review dimension. Emit the required verdict, findings, roadmap/context cross-check, and proposed patches when patchable.
```

### Step 6: Process The Verdict

The reviewer must emit exactly one verdict:

- `COMPLIANT`
- `PATCHABLE`
- `NON-COMPLIANT`

If the output does not contain `## Verdict: COMPLIANT`, `## Verdict: PATCHABLE`, or `## Verdict: NON-COMPLIANT`, stop and show the malformed report. Do not mark the spec ready.

#### COMPLIANT

- Update the spec status/date if the local template supports it.
- Report that the spec is ready for RPI.
- If a local tracker integration exists, update only the metadata documented by the project.

#### PATCHABLE

- Show findings grouped by severity: `CRITICAL`, `IMPORTANT`, `SUGGESTION`, `NIT`.
- Apply only patches that are directly supported by the spec, source, or local context.
- Re-run `spec-reviewer` after patching.
- Limit to two patch rounds. If the spec is still not `COMPLIANT`, stop and summarize remaining blockers.

#### NON-COMPLIANT

- Do not send the spec to RPI.
- If the reviewer emitted an author-mode skeleton, ask before replacing the current spec.
- Otherwise, report the blocking findings and the minimum rewrite needed.

### Step 7: Final Report

When the spec is compliant, report:

```text
Spec ready for RPI: <spec_path>
Verdict: COMPLIANT
Findings resolved: <summary>
Next step: /plan <spec_path>
```

If the user asked for a full one-session workflow and the spec is compliant, `/epic-oneshot <spec_path>` is also a valid next step.

## Idempotency

The command must be safe to re-run:

- A compliant spec should stay compliant with no unnecessary rewrites.
- Existing source links and tracker metadata should be preserved unless wrong.
- Never create duplicate spec files for the same title or ID.
- Never create or modify tracker items unless the local project explicitly documents how.

## Key Rules

- The reviewer is the gate. A spec does not enter RPI until it reaches `COMPLIANT`.
- Cite local files and line numbers for findings when possible.
- Do not invent facts, metrics, decisions, dependencies, or acceptance tests.
- Keep project-specific tracker and release lifecycle behavior in project-local commands.
- Prefer improving the spec over explaining why it is imperfect.
