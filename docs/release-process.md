# Release Process

Use this checklist when preparing a Maximal AI release. For normal feature PRs, update the `[Unreleased]` section in `CHANGELOG.md`; do not bump versions or create tags unless the PR is explicitly preparing a release.

## Release Notes

Maximal AI follows Keep a Changelog and Semantic Versioning.

1. Move relevant entries from `[Unreleased]` into a new version section:

   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   ```

2. Keep entries grouped by the existing categories:

   - `Breaking Changes`
   - `Added`
   - `Changed`
   - `Fixed`
   - `Removed`
   - `Security`

3. Include upgrade notes when users need to change install commands, configuration, environment variables, or workflow habits.
4. Add comparison links at the bottom of `CHANGELOG.md` for the new version.
5. For large releases, use the Hermes Agent v0.13.0 release style as a reference for structure: version/date header, concise summary, highlights, categorized details, docs notes, and PR/issue references.

## Version Sources

When publishing a release, update every version source in the same commit:

| File | What to update |
| --- | --- |
| `pyproject.toml` | `[project] version` for the `rdf` package |
| `src/rdf/__init__.py` | `__version__` used by the RDF CLI |
| `uv.lock` | Locked `rdf` package version, if the lockfile changes |
| `install.sh` | Generated `maximal-ai` command comment and `VERSION` variable |
| `tests/integration/test_cli.py` | Expected CLI version output |
| `CHANGELOG.md` | New release section and compare links |

The version bump is the file change. A Git tag only marks the release commit.

## README And Docs

Before tagging, review user-facing docs touched by the release:

- `README.md` install, update, command, and troubleshooting sections
- `.claude/commands/*.md` command behavior
- templates under `templates/`
- docs under `docs/`
- examples or generated output shown in tests

If users need the information to install, upgrade, configure, or operate the toolkit, update it before the release commit.

## Verification

Run the relevant checks before tagging:

```bash
pytest
bash tests/commands/test_command_syntax.sh
bash tests/scripts/test-installer.sh
bash install.sh
maximal-ai --version
```

For documentation-only releases, run the command syntax test and any targeted tests for files changed.

## Tagging

Create tags only after verification passes and the release commit exists.

```bash
git status --short
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

If publishing a GitHub release, use the matching `CHANGELOG.md` section as the release body and include any migration notes near the top.
