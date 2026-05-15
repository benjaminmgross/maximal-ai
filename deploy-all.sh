#!/bin/bash

# deploy-all.sh — Deploy maximal-ai to all configured repositories
#
# Usage:
#   ./deploy-all.sh               # Full workflow: pull + install + deploy
#   ./deploy-all.sh --skip-update # Skip git pull + install.sh, just deploy
#   ./deploy-all.sh --skip-codex  # Skip Codex skill refresh

# Prevent running via 'source' — set -e and exit will kill the terminal
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "Error: Do not run this script with 'source'. Use one of:"
    echo "  ./deploy-all.sh"
    echo "  bash deploy-all.sh"
    return 1 2>/dev/null || true
fi

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/deploy.yaml"
SKIP_UPDATE=false
SKIP_CODEX=false

# Parse flags
for arg in "$@"; do
    case "$arg" in
        --skip-update)
            SKIP_UPDATE=true
            ;;
        --skip-codex)
            SKIP_CODEX=true
            ;;
        --help|-h)
            echo "Usage: ./deploy-all.sh [--skip-update] [--skip-codex]"
            echo ""
            echo "Deploy maximal-ai to all repositories listed in deploy.yaml."
            echo ""
            echo "Options:"
            echo "  --skip-update  Skip git pull and install.sh (just deploy to repos)"
            echo "  --skip-codex   Skip user-level Codex skill refresh"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Run './deploy-all.sh --help' for usage."
            exit 1
            ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}$1${NC}"; }
warn()  { echo -e "${YELLOW}$1${NC}"; }
error() { echo -e "${RED}$1${NC}"; }

# Check config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    error "Config file not found: $CONFIG_FILE"
    echo ""
    echo "Create deploy.yaml with your target repos:"
    echo ""
    echo "  base_dir: ~/dev"
    echo "  command: rpi-workflow"
    echo "  repos:"
    echo "    - my-repo-1"
    echo "    - my-repo-2"
    exit 1
fi

# Parse deploy.yaml
BASE_DIR=$(grep '^base_dir:' "$CONFIG_FILE" | sed 's/^base_dir: *//' | sed "s|~|$HOME|")
COMMAND=$(grep '^command:' "$CONFIG_FILE" | sed 's/^command: *//')
REPOS=$(grep '^  - ' "$CONFIG_FILE" | sed 's/^  - //')

if [ -z "$BASE_DIR" ]; then
    error "base_dir not set in deploy.yaml"
    exit 1
fi

if [ -z "$COMMAND" ]; then
    error "command not set in deploy.yaml"
    exit 1
fi

if [ -z "$REPOS" ]; then
    error "No repos listed in deploy.yaml"
    exit 1
fi

REPO_COUNT=$(echo "$REPOS" | wc -l | tr -d ' ')

echo ""
info "Maximal-AI Multi-Repo Deploy"
echo "=============================="
echo "Base directory: $BASE_DIR"
echo "Command:        maximal-ai $COMMAND"
echo "Target repos:   $REPO_COUNT"
echo ""

# Step 1: Self-update (unless skipped)
if [ "$SKIP_UPDATE" = false ]; then
    info "Step 1: Updating maximal-ai..."
    echo ""

    cd "$SCRIPT_DIR"

    echo "Pulling latest from dev..."
    if ! git pull origin dev; then
        error "git pull failed. Fix conflicts and try again."
        exit 1
    fi
    echo ""

    echo "Running install.sh..."
    bash "$SCRIPT_DIR/install.sh"
    echo ""
else
    info "Step 1: Skipped (--skip-update)"
    echo ""
fi

# Step 2: Refresh user-level Codex skills
if [ "$SKIP_CODEX" = false ]; then
    info "Step 2: Refreshing Codex skills..."
    echo ""
    bash "$SCRIPT_DIR/installers/codex-skills.sh"
    echo ""
else
    info "Step 2: Skipped Codex skills (--skip-codex)"
    echo ""
fi

# Step 3: Deploy to repos
info "Step 3: Deploying Claude Code commands to $REPO_COUNT repositories..."
echo ""

SUCCEEDED=0
FAILED=0
SKIPPED=0
FAILED_REPOS=""
SKIPPED_REPOS=""

while IFS= read -r repo; do
    repo_path="$BASE_DIR/$repo"

    if [ ! -d "$repo_path" ]; then
        warn "  ⊘ $repo (directory not found)"
        SKIPPED=$((SKIPPED + 1))
        SKIPPED_REPOS="$SKIPPED_REPOS  ⊘ $repo\n"
        continue
    fi

    echo -n "  Deploying to $repo... "

    # Redirect stdin from /dev/null so any interactive `read` prompts in the
    # installer see EOF instead of consuming the outer `while read` loop's
    # stdin (which is $REPOS). Before this guard, installer prompts silently
    # ate the next repo name as a y/N answer, causing repos to vanish from
    # the deploy output.
    if (cd "$repo_path" && maximal-ai "$COMMAND" < /dev/null) > /dev/null 2>&1; then
        info "✓"
        SUCCEEDED=$((SUCCEEDED + 1))
    else
        error "✗"
        FAILED=$((FAILED + 1))
        FAILED_REPOS="$FAILED_REPOS  ✗ $repo\n"
    fi
done <<< "$REPOS"

# Step 3: Summary
echo ""
echo "=============================="
info "Deploy Complete"
echo ""
if [ "$SKIP_CODEX" = false ]; then
    echo "  Codex skills: refreshed"
else
    warn "  Codex skills: skipped"
fi
echo "  Succeeded: $SUCCEEDED"

if [ "$FAILED" -gt 0 ]; then
    error "  Failed:    $FAILED"
    echo -e "$FAILED_REPOS"
fi

if [ "$SKIPPED" -gt 0 ]; then
    warn "  Skipped:   $SKIPPED"
    echo -e "$SKIPPED_REPOS"
fi

echo ""

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi
