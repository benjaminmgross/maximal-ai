---
description: "[DEPRECATED — see /review-fix-loop] Run adversarial review-fix loop on a PR"
---

# Review-Fix PR Loop — DEPRECATED

This command has been **renamed to `/review-fix-loop`** as of T0.HARN-013. The new command operates on a **local diff** (`git diff <base>...HEAD`) instead of a GitHub PR, so it can run BEFORE `gh pr create` — keeping PR history clean and closing the "PR shipped, review never ran" failure mode.

**Migration:**

| Old | New |
|---|---|
| `/review-fix-pr-loop 42` | `/review-fix-loop` (auto-detects base) |
| `/review-fix-pr-loop 42 --max-rounds 5` | `/review-fix-loop --num-rounds 5` |
| `/review-fix-pr-loop https://github.com/user/repo/pull/42` | `/review-fix-loop --base <ref-the-PR-targets>` |

**Retirement timeline:** this wrapper exists for one quarter (per ADR-003 quarterly harness review) to absorb muscle-memory invocations. At the next quarterly review (≥ 2026-08-13), this file will be deleted.

## Coordinator Instructions

This wrapper exists for one-quarter backward compatibility. When invoked:

1. Print the deprecation notice to the user: "**`/review-fix-pr-loop` is deprecated** — invoking `/review-fix-loop` instead. Update your muscle memory: this wrapper will be removed at the next quarterly harness review (≥ 2026-08-13)."

2. Translate the user's `$ARGUMENTS` from PR-flavored to base-branch-flavored:
   - If a PR number is given: `gh pr view <N> --json baseRefName --jq '.baseRefName'` → use as `--base origin/<base>`. Then `gh pr checkout <N>` to land on the PR branch locally (so `HEAD` is the PR head).
   - If `--max-rounds N` was passed, translate to `--num-rounds N`.

3. Then invoke `/review-fix-loop` with the translated arguments. Hand control to that command's coordinator flow.

If the user provided no arguments (bare `/review-fix-pr-loop`), invoke `/review-fix-loop` with no arguments — it will auto-detect the base branch.

See `roadmap/initiatives/T0.HARN-013-review-fix-loop-rename-and-chain.md` (in `minty-docs`) for the full rename rationale.
