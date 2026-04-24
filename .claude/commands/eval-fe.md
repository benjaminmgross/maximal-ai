---
description: Browser-driven evaluator for frontend work (Playwright-powered)
---

# /eval-fe — Frontend Evaluator

Browser-driven evaluator for frontend changes. Complements static code review by inspecting the rendered page — the layer tests and linters don't see. Part of the inferential feedback loop in modern harness engineering.

## Status

**STUB.** First real implementation expected once Playwright integration is wired into your project.

## Intent

After `/implement` ships a frontend feature with acceptance criteria that reference a route, `/eval-fe <route>` should:

1. Boot the dev server (project-specific — `npm run dev`, `vite dev`, `rails s`, etc.)
2. Wait for the ready signal (poll the local URL until 200)
3. Navigate to the route with Playwright, auth'd as a test user
4. Screenshot the rendered page (full-page + viewport)
5. Capture console errors and network failures
6. Extract DOM text content and interactive structure
7. Spawn a sub-agent with the screenshot + DOM + acceptance criteria and task it:
   > "For each acceptance criterion, answer pass/fail with one concrete piece of evidence (a DOM element, a screenshot region, a network response). Do not summarize. Do not rationalize failures."
8. Return a structured report
9. If your project has a feature progress tracker (e.g. a `features.json` convention), flip passing features on success

## Usage (when implemented)

```bash
/eval-fe /path/to/route
/eval-fe --feature <feature-id>          # if your project has a feature registry
/eval-fe --all                            # every failing frontend feature in the current scope
```

## Current Interim: Manual Evaluation

Until this is built:

1. Boot the dev server
2. Open each route listed in the plan's acceptance criteria
3. Walk through each verification item manually
4. If all pass, mark the feature done in your project's tracker and commit
5. If any fail, file a bug referencing the unmet criterion

## Implementation Notes

- Playwright MCP is the cleanest integration path (`mcp__playwright__*` tool family)
- Store screenshots under your project's review-artifact directory (e.g. `thoughts/reviews/screenshots/`)
- **Skeptical tuning matters.** The sub-agent must start from *"I default to fail; I must find concrete evidence to pass."* Evaluators without explicit skepticism prompts self-rationalize — this is the central Anthropic finding.
- Auth bootstrap is often the gating blocker — have a reusable test-user fixture ready before building this command

## Why This Is a Separate Command

Diff-level code review catches implementation gaps. Browser-level evaluation catches rendering, interaction, and integration gaps. A function that compiles and passes unit tests can still render a blank page, have a broken form, or silently 401. Different failure modes → different evaluator.

## Sources

- Anthropic, ["Effective Harnesses for Long-Running Agents"](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Playwright Docs — https://playwright.dev/
