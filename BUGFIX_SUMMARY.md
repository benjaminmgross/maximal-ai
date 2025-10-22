# Installation Script Bugfix Summary

## Problem Identified

The `maximal-ai` command was only installing 3 out of 6 commands and 4 out of 7 agents, resulting in an incomplete installation.

### What Was Missing

**Commands Not Being Installed:**
- `epic-oneshot.md` - Complete RPI workflow in one session
- `standup.md` - Generate progress reports
- `blocked.md` - Identify and analyze implementation blockers

**Agents Not Being Installed:**
- `file-analyzer.md` - Reduces large files by 80-90%
- `bug-hunter.md` - Elite bug detection specialist
- `test-runner.md` - Executes tests without polluting context

## Root Cause

The installed script at `/Users/benjamingross/.local/bin/maximal-ai` was outdated and didn't include all the files that exist in the source repository's `setup.sh`.

## Solution Implemented

Created a new `install.sh` script that:

1. **Generates the complete `maximal-ai` command** with all files included
2. **Installs it to `~/.local/bin/maximal-ai`** for global access
3. **Makes the installation process reproducible** - just run `./install.sh` after pulling updates
4. **Provides clear feedback** showing what was installed

### Files Modified/Created

1. **`install.sh`** (new) - Installation script that generates the complete maximal-ai command
2. **`README.md`** (modified) - Updated with new installation instructions

## Verification

Tested the fix by:
1. Running `./install.sh` in maximal-ai repo
2. Verifying version bump to 1.1.0
3. Running `maximal-ai` in a test project (minty_revamp)
4. Confirming all 6 commands and 7 agents are installed

### Before Fix
```bash
$ ls .claude/commands/
implement.md  plan.md  research.md
```

### After Fix
```bash
$ ls .claude/commands/
blocked.md       epic-oneshot.md  implement.md     plan.md          research.md      standup.md
```

## How to Use the Fix

### For Users

1. **Pull the latest changes:**
   ```bash
   cd ~/dev/maximal-ai
   git checkout bugfix/install-error  # Or after merge: git pull
   ```

2. **Run the installer:**
   ```bash
   ./install.sh
   ```

3. **Verify the update:**
   ```bash
   maximal-ai --version  # Should show 1.1.0
   ```

4. **Re-install in your projects:**
   ```bash
   cd /path/to/your/project
   maximal-ai
   ```

### For Future Updates

When maximal-ai is updated with new commands or agents:

```bash
cd ~/dev/maximal-ai
git pull
./install.sh  # Updates the global command
```

Then reinstall in each project to get the latest files.

## Technical Details

### The Complete Installation Command

The fixed script now copies all files:

**Commands (6 total):**
```bash
cp "$INSTALL_DIR/.claude/commands/research.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/plan.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/implement.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/epic-oneshot.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/standup.md" "$PROJECT_ROOT/.claude/commands/"
cp "$INSTALL_DIR/.claude/commands/blocked.md" "$PROJECT_ROOT/.claude/commands/"
```

**Agents (7 total):**
```bash
cp "$INSTALL_DIR/.claude/agents/codebase-locator.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/codebase-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/codebase-pattern-finder.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/web-search-researcher.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/file-analyzer.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/bug-hunter.md" "$PROJECT_ROOT/.claude/agents/"
cp "$INSTALL_DIR/.claude/agents/test-runner.md" "$PROJECT_ROOT/.claude/agents/"
```

## Benefits

✅ Complete installation of all workflow components
✅ Reproducible installation process
✅ Easy updates when new commands/agents are added
✅ Clear feedback during installation
✅ Version tracking (now at 1.1.0)

## Next Steps

1. Merge this bugfix branch into dev/main
2. Tag the release as v1.1.0
3. Update any documentation that references the old installation method
4. Notify users to run the update process

---

**Branch:** `bugfix/install-error`
**Commit:** fix: Complete installation script that installs all commands and agents
**Date:** October 22, 2025
