#!/bin/bash
# Shared username detection script for RPI workflow commands
# This script outputs the detected username to stdout
#
# Usage in markdown commands:
#   ```bash
#   source .claude/hooks/detect-username.sh
#   # Now RPI_USERNAME and CURRENT_DATE are available
#   ```
#
# Priority order:
# 1. .claude/config.yaml (recommended - per repository)
# 2. RPI_USERNAME environment variable (global default)
# 3. git config user.name (automatic fallback)
# 4. "user" (last resort default)

# Check for config file first
if [ -f ".claude/config.yaml" ]; then
    CONFIG_USERNAME=$(grep "^username:" .claude/config.yaml 2>/dev/null | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
fi

# Apply priority order
RPI_USERNAME="${CONFIG_USERNAME:-${RPI_USERNAME:-$(git config user.name 2>/dev/null | tr ' ' '-' | tr '[:upper:]' '[:lower:]')}}"
RPI_USERNAME="${RPI_USERNAME:-user}"

# Set current date
CURRENT_DATE=$(date +%Y.%m.%d)

# Export for use in calling script
export RPI_USERNAME
export CURRENT_DATE
