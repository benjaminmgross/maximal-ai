# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  - `rdf scaffold-folders` - Generate .folder.md files
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

[Unreleased]: https://github.com/benjaminmgross/maximal-ai/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/benjaminmgross/maximal-ai/compare/v0.1.0...v2.0.0
[0.1.0]: https://github.com/benjaminmgross/maximal-ai/releases/tag/v0.1.0
[0.0.1]: https://github.com/benjaminmgross/maximal-ai/releases/tag/v0.0.1
