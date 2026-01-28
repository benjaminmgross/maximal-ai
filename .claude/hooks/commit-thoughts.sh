#!/bin/bash
set -e

# commit-thoughts.sh - Commit a thoughts document to GitHub and create a discussion
#
# Usage: commit-thoughts.sh [--no-discussion] <type> <file_path>
#   --no-discussion: Skip GitHub Discussion creation (commit only)
#   type: "research" or "plan"
#   file_path: Path to the document (relative to consumer repo, e.g., "thoughts/research/2026.01.27-bmg-topic.md")
#
# Environment variables required:
#   THOUGHTS_PATH: Path to minty-thoughts repo
#   CLAUDE_PROJECT_DIR: Path to the consumer repo (set by Claude Code)
#
# Exit codes:
#   0: Full success (commit + discussion, or commit only if --no-discussion)
#   1: Partial success (commit succeeded, discussion failed)
#   2: Failure (commit failed)

# Parse optional flags
SKIP_DISCUSSION=false
if [ "$1" = "--no-discussion" ]; then
    SKIP_DISCUSSION=true
    shift
fi

DOC_TYPE="${1:-}"
FILE_PATH="${2:-}"

# Validate inputs
if [ -z "$DOC_TYPE" ] || [ -z "$FILE_PATH" ]; then
    echo "ERROR: Usage: commit-thoughts.sh <type> <file_path>" >&2
    exit 2
fi

if [ "$DOC_TYPE" != "research" ] && [ "$DOC_TYPE" != "plan" ]; then
    echo "ERROR: type must be 'research' or 'plan', got: $DOC_TYPE" >&2
    exit 2
fi

# Validate environment
if [ -z "$THOUGHTS_PATH" ]; then
    echo "ERROR: THOUGHTS_PATH environment variable not set" >&2
    echo "Please add to your shell config: export THOUGHTS_PATH=\"/path/to/minty-thoughts\"" >&2
    exit 2
fi

if [ ! -d "$THOUGHTS_PATH" ]; then
    echo "ERROR: THOUGHTS_PATH does not exist: $THOUGHTS_PATH" >&2
    exit 2
fi

if [ -z "$CLAUDE_PROJECT_DIR" ]; then
    echo "ERROR: CLAUDE_PROJECT_DIR not set (should be set by Claude Code)" >&2
    exit 2
fi

# Extract repo name from CLAUDE_PROJECT_DIR
REPO_NAME=$(basename "$CLAUDE_PROJECT_DIR")
REPO_NAME=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_-]/-/g')

# Extract filename from path
FILENAME=$(basename "$FILE_PATH")

# Determine directory name based on doc type
# "research" stays singular, "plan" becomes "plans"
if [ "$DOC_TYPE" = "research" ]; then
    DIR_NAME="research"
else
    DIR_NAME="plans"
fi

# Resolve the actual file path in minty-thoughts
# The file_path is relative to consumer repo, symlinks point to $THOUGHTS_PATH/repos/{repo}/
RESOLVED_PATH="$THOUGHTS_PATH/repos/$REPO_NAME/$DIR_NAME/$FILENAME"

if [ ! -f "$RESOLVED_PATH" ]; then
    echo "ERROR: File not found: $RESOLVED_PATH" >&2
    echo "Expected file at: $RESOLVED_PATH" >&2
    exit 2
fi

# Check for uncommitted changes in minty-thoughts (excluding our file)
cd "$THOUGHTS_PATH"
OTHER_CHANGES=$(git status --porcelain | grep -v "$FILENAME" || true)
if [ -n "$OTHER_CHANGES" ]; then
    echo "WARNING: minty-thoughts has other uncommitted changes:" >&2
    echo "$OTHER_CHANGES" >&2
    echo "Proceeding with commit anyway..." >&2
fi

# Stage and commit the file
RELATIVE_PATH="repos/$REPO_NAME/$DIR_NAME/$FILENAME"
COMMIT_MSG="${DOC_TYPE}($REPO_NAME): $FILENAME"

git add "$RELATIVE_PATH"

# Check if there's anything to commit
if git diff --cached --quiet; then
    echo "File already committed, no changes to commit"
    COMMIT_SHA="(already committed)"
else
    if git commit -m "$COMMIT_MSG"; then
        COMMIT_SHA=$(git rev-parse --short HEAD)
        echo "Committed: $COMMIT_MSG ($COMMIT_SHA)"
    else
        echo "ERROR: Git commit failed" >&2
        exit 2
    fi
fi

# Push to remote
if git push; then
    echo "Pushed to remote"
else
    echo "ERROR: Git push failed (commit succeeded locally)" >&2
    echo "Run 'cd $THOUGHTS_PATH && git push' to complete" >&2
    exit 1  # Partial success - commit worked, push failed
fi

# Create GitHub Discussion (unless --no-discussion flag)
DISCUSSION_SUCCESS=false
DISCUSSION_URL=""

if [ "$SKIP_DISCUSSION" = true ]; then
    echo "Skipping discussion creation (--no-discussion flag)"
    DISCUSSION_SUCCESS=true  # Treat as success since it was intentionally skipped
    DISCUSSION_URL="(skipped)"
else
    # Parse GitHub owner/repo from git remote (supports HTTPS and SSH URLs)
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo "WARNING: No origin remote found in $THOUGHTS_PATH, skipping discussion" >&2
else
    # Extract owner/repo from URL formats:
    # - https://github.com/owner/repo.git
    # - git@github.com:owner/repo.git
    GH_OWNER=$(echo "$REMOTE_URL" | sed -E 's#.*[:/]([^/]+)/([^/]+)(\.git)?$#\1#')
    GH_REPO=$(echo "$REMOTE_URL" | sed -E 's#.*[:/]([^/]+)/([^/]+)(\.git)?$#\2#' | sed 's/\.git$//')
fi

# Check for cached IDs in consumer repo's config.yaml
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/config.yaml"
CACHE_HIT=false
REPO_ID=""
RESEARCH_CATEGORY_ID=""
PLANS_CATEGORY_ID=""

if [ -f "$CONFIG_FILE" ] && [ -n "$REMOTE_URL" ]; then
    # Check if cache exists and matches current remote
    CACHED_REMOTE=$(grep '^  remote_url:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *"\?\([^"]*\)"\?/\1/' || echo "")
    if [ "$CACHED_REMOTE" = "$REMOTE_URL" ]; then
        REPO_ID=$(grep '^  repo_id:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *//' || echo "")
        RESEARCH_CATEGORY_ID=$(grep '^  research_category_id:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *//' || echo "")
        PLANS_CATEGORY_ID=$(grep '^  plans_category_id:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *//' || echo "")
        if [ -n "$REPO_ID" ] && [ -n "$RESEARCH_CATEGORY_ID" ] && [ -n "$PLANS_CATEGORY_ID" ]; then
            CACHE_HIT=true
            echo "Using cached GitHub IDs from config.yaml"
        fi
    fi
fi

# Fetch IDs if not cached (or cache miss)
if [ "$CACHE_HIT" = false ] && [ -n "$REMOTE_URL" ]; then
    echo "Fetching GitHub IDs (will cache for future use)..."

    # Get repository ID
    REPO_ID=$(gh api graphql -F owner="$GH_OWNER" -F name="$GH_REPO" -f query='
      query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) { id }
      }
    ' --jq '.data.repository.id' 2>/dev/null || echo "")

    if [ -n "$REPO_ID" ]; then
        # Fetch both category IDs at once
        CATEGORIES=$(gh api graphql -H 'GraphQL-Features: discussions_api' \
          -F owner="$GH_OWNER" -F name="$GH_REPO" -f query='
            query($owner: String!, $name: String!) {
              repository(owner: $owner, name: $name) {
                discussionCategories(first: 25) {
                  nodes { id name }
                }
              }
            }
          ' 2>/dev/null || echo "")

        RESEARCH_CATEGORY_ID=$(echo "$CATEGORIES" | jq -r '.data.repository.discussionCategories.nodes[] | select(.name=="Research") | .id' 2>/dev/null || echo "")
        PLANS_CATEGORY_ID=$(echo "$CATEGORIES" | jq -r '.data.repository.discussionCategories.nodes[] | select(.name=="Plans") | .id' 2>/dev/null || echo "")

        # Cache the IDs if we got them all
        if [ -n "$REPO_ID" ] && [ -n "$RESEARCH_CATEGORY_ID" ] && [ -n "$PLANS_CATEGORY_ID" ]; then
            # Remove old cache section if exists
            if grep -q '^thoughts_cache:' "$CONFIG_FILE" 2>/dev/null; then
                # Remove existing cache section (from thoughts_cache: to next non-indented line or EOF)
                sed -i '' '/^thoughts_cache:/,/^[^ ]/{/^[^ ]/!d;}' "$CONFIG_FILE"
                sed -i '' '/^thoughts_cache:/d' "$CONFIG_FILE"
            fi

            # Append new cache section
            cat >> "$CONFIG_FILE" << EOF

# Cached GitHub Discussion IDs (auto-generated, do not edit)
thoughts_cache:
  remote_url: $REMOTE_URL
  repo_id: $REPO_ID
  research_category_id: $RESEARCH_CATEGORY_ID
  plans_category_id: $PLANS_CATEGORY_ID
EOF
            echo "Cached GitHub IDs to config.yaml"
        fi
    fi
fi

if [ -z "$REPO_ID" ]; then
    if [ -n "$REMOTE_URL" ]; then
        echo "WARNING: Could not get repository ID for discussions" >&2
    fi
else
    # Determine category ID based on doc type
    if [ "$DOC_TYPE" = "research" ]; then
        CATEGORY_NAME="Research"
        CATEGORY_ID="$RESEARCH_CATEGORY_ID"
    else
        CATEGORY_NAME="Plans"
        CATEGORY_ID="$PLANS_CATEGORY_ID"
    fi

    if [ -z "$CATEGORY_ID" ]; then
        echo "WARNING: Could not find '$CATEGORY_NAME' discussion category" >&2
        echo "Please create it in GitHub: Settings > Discussions > Categories" >&2
    else
        # Read file content with size check (GitHub limit ~65K chars)
        FILE_SIZE=$(wc -c < "$RESOLVED_PATH")
        MAX_BODY_SIZE=60000  # Leave buffer for metadata

        if [ "$FILE_SIZE" -gt "$MAX_BODY_SIZE" ]; then
            FILE_CONTENT="$(head -c $MAX_BODY_SIZE "$RESOLVED_PATH")

---

**[Content truncated - see source file for full document]**"
            echo "WARNING: File content truncated for discussion (${FILE_SIZE} bytes > ${MAX_BODY_SIZE} limit)" >&2
        else
            FILE_CONTENT=$(cat "$RESOLVED_PATH")
        fi

        # Create discussion title from filename
        DISCUSSION_TITLE="[$REPO_NAME] $FILENAME"

        # Check for existing discussion with same title (prevent duplicates)
        EXISTING_DISCUSSION=$(gh api graphql -H 'GraphQL-Features: discussions_api' \
          -F owner="$GH_OWNER" -F name="$GH_REPO" -F query="$DISCUSSION_TITLE" -f query='
            query($owner: String!, $name: String!, $query: String!) {
              repository(owner: $owner, name: $name) {
                discussions(first: 1, filterBy: {query: $query}) {
                  nodes { url title }
                }
              }
            }
          ' --jq '.data.repository.discussions.nodes[0].url // empty' 2>/dev/null || echo "")

        if [ -n "$EXISTING_DISCUSSION" ]; then
            echo "Discussion already exists: $EXISTING_DISCUSSION"
            DISCUSSION_SUCCESS=true
            DISCUSSION_URL="$EXISTING_DISCUSSION"
        else
            # Create discussion body with link to file
            DISCUSSION_BODY="## Source

**Repository:** $REPO_NAME
**File:** [\`$RELATIVE_PATH\`](https://github.com/$GH_OWNER/$GH_REPO/blob/main/$RELATIVE_PATH)
**Commit:** $COMMIT_SHA

---

$FILE_CONTENT"

        # Create discussion
        DISCUSSION_RESULT=$(gh api graphql -H 'GraphQL-Features: discussions_api' \
          -F repositoryId="$REPO_ID" \
          -F categoryId="$CATEGORY_ID" \
          -F title="$DISCUSSION_TITLE" \
          -F body="$DISCUSSION_BODY" \
          -f query='
            mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
              createDiscussion(input: {
                repositoryId: $repositoryId
                categoryId: $categoryId
                title: $title
                body: $body
              }) {
                discussion { url }
              }
            }
          ' 2>/dev/null || echo "")

            DISCUSSION_URL=$(echo "$DISCUSSION_RESULT" | jq -r '.data.createDiscussion.discussion.url // empty' 2>/dev/null || echo "")

            if [ -n "$DISCUSSION_URL" ]; then
                DISCUSSION_SUCCESS=true
                echo "Discussion created: $DISCUSSION_URL"
            else
                echo "WARNING: Failed to create discussion" >&2
            fi
        fi  # end of "create new discussion" block
    fi
fi
fi  # end of SKIP_DISCUSSION check

# Output summary
echo ""
echo "=== Summary ==="
echo "Commit: SUCCESS ($COMMIT_SHA)"
if [ "$DISCUSSION_URL" = "(skipped)" ]; then
    echo "Discussion: SKIPPED (--no-discussion flag)"
    exit 0
elif [ "$DISCUSSION_SUCCESS" = true ]; then
    echo "Discussion: SUCCESS"
    echo "URL: $DISCUSSION_URL"
    exit 0
else
    echo "Discussion: FAILED (commit still succeeded)"
    if [ -n "$GH_OWNER" ] && [ -n "$GH_REPO" ]; then
        echo ""
        echo "To create the discussion manually:"
        echo "  1. Go to: https://github.com/$GH_OWNER/$GH_REPO/discussions/new"
        echo "  2. Select category: $CATEGORY_NAME"
        echo "  3. Copy content from: $RESOLVED_PATH"
    fi
    exit 1
fi
