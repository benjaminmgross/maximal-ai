# Testing Standard for Maximal-AI Commands

> **Purpose:** Ensure slash commands, installers, and shell scripts work reliably across different environments.
> **Audience:** Contributors adding or modifying commands and scripts.
> **Update Trigger:** Modify when new testing patterns are needed.

## Testing Philosophy

Slash commands execute in user environments with different shells (bash, zsh), OS versions, and tool configurations. Testing must catch issues before users encounter them.

**Key risks:**
- Shell syntax incompatibilities (bash vs zsh)
- Inline bash command parsing failures
- Missing dependencies or assumptions about user environment
- Install script edge cases (different project structures)

---

## Test Categories

### 1. Shell Syntax Validation

**Purpose:** Ensure inline bash commands (`!` backticks) parse correctly in both bash and zsh.

**What to test:**
- All `!` backtick commands in `.claude/commands/*.md` files
- Shell scripts in `installers/`, `.claude/hooks/`

**Anti-patterns to avoid:**

```bash
# BAD: Variable assignment with $() inside inline bash
!`VAR=$(echo "$ARGUMENTS" | grep -oE '[0-9]+'); ls $VAR`
#     ^^^ Parse error in some shells

# GOOD: Simple commands without intermediate variables
!`ls -t thoughts/reviews/*.md 2>/dev/null | head -10 || echo "No files"`

# BAD: Nested command substitution
!`echo "Count: $(ls $(pwd)/src/*.py | wc -l)"`
#              ^^^ Double-nested $() causes issues

# GOOD: Single command substitution or piping
!`ls src/*.py 2>/dev/null | wc -l || echo "0"`

# BAD: Process substitution
!`diff <(cmd1) <(cmd2)`
#      ^^^ Not portable to all shells

# GOOD: Temporary files or sequential commands
!`cmd1 > /tmp/a && cmd2 > /tmp/b && diff /tmp/a /tmp/b; rm -f /tmp/a /tmp/b`
```

**Test command:**

```bash
# Validate all inline bash syntax
./tests/scripts/validate-inline-bash.sh
```

### 2. Command Integration Tests

**Purpose:** Verify slash commands work when invoked with various inputs.

**What to test:**
- Commands work with valid arguments
- Commands fail gracefully with invalid/missing arguments
- Pre-computed context (`!` backticks) returns expected formats
- Output formatting is correct

**Test patterns:**

```bash
# Test that gh commands work (requires gh auth)
gh pr view --help > /dev/null && echo "gh available"

# Test that git commands work
git status --short 2>/dev/null || echo "Not in git repo"

# Test file patterns
ls thoughts/plans/*.md 2>/dev/null | head -1 || echo "No plans"
```

### 3. Installer Tests

**Purpose:** Verify installation scripts create correct files in various project structures.

**What to test:**
- Files created in `src/` projects
- Files created in `app/` projects (Python convention)
- Files created in projects with neither
- Idempotency (running twice doesn't break things)
- Layer combinations (1 only, 1-3, all, etc.)

**Test scenarios:**

| Scenario | Input | Expected |
|----------|-------|----------|
| JS project | `src/` exists | `.folder.md` in `src/` |
| Python project | `app/` exists | `.folder.md` in `app/` |
| Neither exists | No source dir | Warning, graceful skip |
| Run twice | Already installed | "Skipped (exists)" messages |
| Layers 1-3 only | `-l 1,2,3` | No Layer 5 CLI |

### 4. Shell Compatibility Tests

**Purpose:** Verify scripts work in bash and zsh.

**What to test:**
- `set -e` behavior differences
- Array syntax (`$@` vs `$*`)
- `[[` vs `[` conditionals
- POSIX compliance where needed

---

## Test Infrastructure

### Directory Structure

```
tests/
+-- scripts/                    # Shell test scripts
|   +-- validate-inline-bash.sh # Validates command file syntax
|   +-- test-installer.sh       # Tests installer in temp directory
|   +-- test-commands.sh        # Integration tests for commands
+-- unit/                       # Python unit tests
+-- integration/                # Python integration tests
+-- fixtures/                   # Test data
    +-- project-js/             # Simulated JS project
    +-- project-python/         # Simulated Python project
    +-- project-empty/          # Empty project
```

### validate-inline-bash.sh

Extracts and validates all inline bash commands:

```bash
#!/bin/bash
# Extract inline bash from command files and validate syntax

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR/../.."
ERRORS=0

echo "Validating inline bash syntax in command files..."
echo ""

# Find all command files
for file in "$REPO_ROOT"/.claude/commands/*.md; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")

    # Extract inline bash commands (lines starting with !)
    # Format: !`command here`
    grep -oP '!\`[^\`]+\`' "$file" 2>/dev/null | while read -r cmd; do
        # Remove !` prefix and ` suffix
        bash_cmd="${cmd:2:-1}"

        # Validate syntax with bash -n (parse only, don't execute)
        if ! bash -n <<< "$bash_cmd" 2>/dev/null; then
            echo "ERROR in $filename:"
            echo "  Command: $bash_cmd"
            bash -n <<< "$bash_cmd" 2>&1 | sed 's/^/  /'
            ERRORS=$((ERRORS + 1))
        fi

        # Also validate with zsh -n if available
        if command -v zsh &>/dev/null; then
            if ! zsh -n <<< "$bash_cmd" 2>/dev/null; then
                echo "ZSH ERROR in $filename:"
                echo "  Command: $bash_cmd"
                ERRORS=$((ERRORS + 1))
            fi
        fi
    done
done

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "FAILED: $ERRORS syntax errors found"
    exit 1
else
    echo "PASSED: All inline bash commands are syntactically valid"
    exit 0
fi
```

### test-installer.sh

Tests installer in isolated environment:

```bash
#!/bin/bash
# Test installer with various project structures

set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR/../.."
TEST_DIR="/tmp/maximal-ai-installer-test-$$"

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

echo "Testing Maximal-AI installer..."
echo ""

# Test 1: JavaScript project (src/)
echo "Test 1: JavaScript project structure"
mkdir -p "$TEST_DIR/js-project/src/components"
cd "$TEST_DIR/js-project"
git init -q
echo '{"name": "test"}' > package.json

MAXIMAL_AI_HOME="$REPO_ROOT" bash "$REPO_ROOT/installers/rpi-workflow.sh"

# Verify
[ -f ".claude/commands/research.md" ] && echo "  PASS: Commands installed"
[ -d "thoughts/research" ] && echo "  PASS: thoughts/ directories created"

# Test 2: Python project (app/)
echo ""
echo "Test 2: Python project structure"
mkdir -p "$TEST_DIR/py-project/app/models"
cd "$TEST_DIR/py-project"
git init -q
echo "flask" > requirements.txt

MAXIMAL_AI_HOME="$REPO_ROOT" bash "$REPO_ROOT/installers/rpi-workflow.sh"

[ -f ".claude/commands/research.md" ] && echo "  PASS: Commands installed"

# Test 3: Idempotency
echo ""
echo "Test 3: Running installer twice"
cd "$TEST_DIR/js-project"
MAXIMAL_AI_HOME="$REPO_ROOT" bash "$REPO_ROOT/installers/rpi-workflow.sh" 2>&1 | grep -q "exists" && echo "  PASS: Skips existing files"

echo ""
echo "All installer tests passed!"
```

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  shell-syntax:
    name: Shell Syntax Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate inline bash syntax
        run: ./tests/scripts/validate-inline-bash.sh

      - name: ShellCheck shell scripts
        uses: ludeeus/action-shellcheck@master
        with:
          scandir: './installers'
          severity: error

  installer:
    name: Installer Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shell: [bash, zsh]
    steps:
      - uses: actions/checkout@v4

      - name: Install zsh
        if: matrix.shell == 'zsh'
        run: sudo apt-get update && sudo apt-get install -y zsh

      - name: Run installer tests
        shell: ${{ matrix.shell }} {0}
        run: ./tests/scripts/test-installer.sh

  python:
    name: Python Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --dev

      - name: Run tests
        run: uv run pytest -v --tb=short

      - name: Check coverage
        run: uv run pytest --cov=rdf --cov-report=term-missing --cov-fail-under=70
```

### Pre-commit Hook

Add shell syntax validation to pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.6
    hooks:
      - id: shellcheck
        files: \.(sh|bash)$

  - repo: local
    hooks:
      - id: validate-inline-bash
        name: Validate inline bash in commands
        entry: ./tests/scripts/validate-inline-bash.sh
        language: script
        files: \.claude/commands/.*\.md$
        pass_filenames: false
```

---

## Writing Testable Commands

### Guidelines

1. **Keep inline bash simple**
   - Single commands with pipes are fine
   - Avoid variable assignment with `$()`
   - Avoid nested subshells

2. **Use `|| echo "fallback"` for graceful failures**
   ```bash
   !`git status --short 2>/dev/null || echo "Not a git repo"`
   ```

3. **Limit output with `head` or `tail`**
   ```bash
   !`git log --oneline -10 2>/dev/null || echo "No commits"`
   ```

4. **Redirect stderr to avoid noise**
   ```bash
   !`ls thoughts/plans/*.md 2>/dev/null | head -5`
   ```

5. **Test commands manually in both bash and zsh**
   ```bash
   bash -c 'your_command_here'
   zsh -c 'your_command_here'
   ```

### Command Checklist

Before merging a new or modified command:

- [ ] All inline bash commands parse in `bash -n`
- [ ] All inline bash commands parse in `zsh -n`
- [ ] Commands fail gracefully with missing tools (gh, git, etc.)
- [ ] Output doesn't exceed reasonable length
- [ ] No hardcoded paths that won't exist on other machines
- [ ] Tested with at least one realistic input

---

## Debugging Test Failures

### Shell Syntax Errors

```bash
# Test a specific command manually
bash -n <<< 'your command here'
zsh -n <<< 'your command here'

# Get verbose output
bash -x <<< 'your command here'
```

### Installer Failures

```bash
# Run with debug output
MAXIMAL_AI_HOME=/path/to/repo bash -x installers/rpi-workflow.sh

# Check what would be created
MAXIMAL_AI_HOME=/path/to/repo bash installers/rpi-workflow.sh --dry-run
```

### CI/CD Failures

1. Check which job failed in GitHub Actions
2. Read the step output for error messages
3. Reproduce locally using the same shell (bash/zsh)
4. Add `set -x` to scripts for debugging

---

## Adding New Tests

When adding a new command or modifying an existing one:

1. **Update `validate-inline-bash.sh`** if new patterns are used
2. **Add integration test** in `test-commands.sh` if command has complex logic
3. **Test manually** in both bash and zsh before pushing
4. **Run full test suite** locally: `./tests/scripts/validate-inline-bash.sh && pytest`

When modifying installers:

1. **Add test case** to `test-installer.sh` for new files/directories
2. **Test idempotency** - running twice should not break things
3. **Test edge cases** - missing directories, existing files, etc.
