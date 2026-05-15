# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes
- **Renamed `/review-fix-pr-loop` → `/review-fix-loop`** (T0.HARN-013). Input contract changes from PR identifier (`gh pr view`) to local diff (`git diff <base>...HEAD`). The command now runs BEFORE `gh pr create` rather than after, so PRs carry one coherent post-review diff rather than a multi-commit review-fix audit trail. A thin deprecation wrapper at `.claude/commands/review-fix-pr-loop.md` redirects muscle-memory invocations; retired at the next quarterly harness review.

### Added
- Provider-aware deployment for Codex:
  - New `installers/codex-skills.sh` installer generates Codex skill wrappers from canonical `.claude/commands/*.md` files.
  - New `maximal-ai codex-skills` subcommand refreshes `${CODEX_HOME:-$HOME/.codex}/skills`.
  - `deploy-all.sh` now refreshes Codex skills once before deploying Claude Code commands to target repos, with `--skip-codex` for opt-out.
- `/review-fix-loop` is now **auto-chained** into the three flow commands as a mandatory gate before any commit:
  - `/epic-oneshot`: new "Step 3.5: Adversarial Review" between Implementation and the commit step.
  - `/commit-push-pr`: new "Step 0: Adversarial Review Gate" before staging.
  - `/implement`: new "Final Step 2: Adversarial Review Gate" after the existing Evaluator Pass.
  Each insertion documents the APPROVED / APPROVED_WITH_SUGGESTIONS / REQUEST_CHANGES handling and the bypass mechanism. Empirically motivated by PR #43 (T0.HARN-012 merge driver in minty-docs), which shipped from `/epic-oneshot` with 2 CRITICAL bugs that no upstream gate caught.
- `/map-to-standards` command — map any commit range or PR to all 9 Minty Living coding standards with structured scorecards
- Release closeout guidance for RPI workflows, including changelog entries, version synchronization, README/docs review, and Git tag preparation
- `docs/release-process.md` with the Maximal AI release checklist
- `/spec-task` command and `spec-reviewer` agent for authoring or auditing implementation specs before RPI planning

### Fixed
- Synchronized the generated `maximal-ai` installer command version with the repo's `3.0.0` package/runtime version

## [2.0.1] - 2026-01-05

### Fixed
- Version synchronization between `pyproject.toml` and `install.sh` (both now 2.0.0)
- Hook scripts now use `$TMPDIR` for log files with fallback to `/tmp`

### Changed
- Renamed `MINTY_DOCS_PATH` to `EXTERNAL_DOCS_PATH` for more generic naming
- Improved `verify_install_dir()` with detailed auto-setup instructions
- Added graceful degradation for hook dependencies (prettier, ruff, pytest)
  - Hooks now silently continue if optional tools are not installed

### Added
- Prerequisites section in README with version requirements (Python 3.10+, Git 2.0+, Bash 4.0+, jq 1.5+)
- Documentation for optional tools (Node.js, Ruff, pytest)

## [2.0.0] - 2026-01-04

### Breaking Changes
- Restructured as modular AI development toolkit with subcommands
- Previous single-command install now requires `maximal-ai rpi-workflow` or `maximal-ai complete`

### Added
- **Modular installer architecture** with `installers/` directory
  - `installers/common.sh` - Shared utility functions
  - `installers/rpi-workflow.sh` - RPI workflow installer (existing functionality)
  - `installers/rdf-framework.sh` - New RDF framework installer
- **RDF Framework (Repo Documentation Framework)** - Layer-based documentation system
  - Layer 1: Entry points (AGENTS.md, CLAUDE.md, .repomap.yaml)
  - Layer 2: Folder documentation (.folder.md files)
  - Layer 3: AI guidance (protocols/, checklists/, guides/)
  - Layer 4: Python tooling integration (`rdf` CLI)
  - Layer 5: Full linting enforcement (CI/CD integration)
- **Python package `rdf`** with CLI tools
  - `rdf init` - Initialize RDF structure
  - `rdf scaffold-context-files` - Generate .context.md files
  - `rdf generate-repomap` - Create REPOMAP.yaml
  - `rdf validate` - Lint docstrings with NumPy-style validation
- **New subcommand system** for `maximal-ai`:
  - `maximal-ai rpi-workflow` - Install RPI workflow only
  - `maximal-ai rdf-framework` - Install RDF framework only
  - `maximal-ai complete` - Install both frameworks
  - `maximal-ai` (no args) - Interactive mode
- **Layer templates** in `templates/rdf/`
- **95% test coverage** for Python tooling

### Changed
- `install.sh` now creates modular `maximal-ai` command with subcommand routing
- Version bumped to 2.0.0 (breaking change)
- Renamed `EXTENSION_GUIDE.md` to `extension_guide.md` for consistency

### Removed
- `BUGFIX_SUMMARY.md` - Obsolete documentation from earlier development
- `META_LEARNINGS.md` - Content consolidated into `extension_guide.md`
- `test_improvement_plan.md` - Completed feature planning document

## [0.1.0] - 2025-11-13

### Added
- Integrated `thoughts/` directory structure with username-based file naming
- Session handoff commands (`/create_handoff`, `/resume_handoff`)
- Automatic coding standards integration from `docs/coding-standards/`
- SP-inspired enhancements to Maximal AI RPI workflow
- A/B testing scenario documentation
- Enhanced `/research` command with clarifying questions and requirement artifacts
- Link to 'Advanced Context Engineering for Coding Agents' talk

### Changed
- Updated README.md to reflect `thoughts/` directory structure
- Improved installation process with username configuration

### Fixed
- Installation error handling

## [0.0.1] - 2025-01-08

### Added
- Initial three-phase workflow implementation (Research → Plan → Implement)
- Core commands: `/research`, `/plan`, `/implement`, `/epic-oneshot`, `/standup`, `/blocked`
- Specialized agents: codebase-locator, codebase-analyzer, codebase-pattern-finder, web-search-researcher, file-analyzer, bug-hunter, test-runner
- Installation script (`install.sh`) with global `maximal-ai` command
- Username configuration system via `.claude/config.yaml`
- RPI artifacts directory structure (`thoughts/research/`, `thoughts/plans/`, `thoughts/handoffs/`)
- Comprehensive documentation in README.md and CLAUDE.md

[Unreleased]: https://github.com/benjaminmgross/maximal-ai/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/benjaminmgross/maximal-ai/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/benjaminmgross/maximal-ai/compare/v0.1.0...v2.0.0
[0.1.0]: https://github.com/benjaminmgross/maximal-ai/releases/tag/v0.1.0
[0.0.1]: https://github.com/benjaminmgross/maximal-ai/releases/tag/v0.0.1
