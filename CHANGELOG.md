# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Renamed `EXTENSION_GUIDE.md` to `extension_guide.md` for consistency with lowercase naming conventions

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

[Unreleased]: https://github.com/benjaminmgross/maximal-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/benjaminmgross/maximal-ai/releases/tag/v0.1.0
[0.0.1]: https://github.com/benjaminmgross/maximal-ai/releases/tag/v0.0.1
