#!/bin/bash

# Test installation script with multi-language support
set -e

echo "🧪 Testing Maximal-AI Installation"
echo "==================================="
echo "Supporting both Python and JavaScript/TypeScript projects"
echo ""

# Function to detect project type
detect_project_type() {
    if [ -f "package.json" ]; then
        echo "javascript"
    elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
        echo "python"
    else
        echo "unknown"
    fi
}

# Create temp directory
TEST_DIR="/tmp/maximal-ai-test-$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 Test directory: $TEST_DIR"

# Initialize git
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Get the actual path to the maximal-ai directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run setup
echo "🚀 Running setup.sh..."
bash "$SCRIPT_DIR/setup.sh"

# Verify files exist
echo "✓ Checking installation..."

# Check commands
for cmd in research plan implement epic-oneshot standup blocked create_handoff resume_handoff; do
    if [ -f ".claude/commands/$cmd.md" ]; then
        echo "  ✅ Command: $cmd"
    else
        echo "  ❌ Missing command: $cmd"
        exit 1
    fi
done

# Check agents
for agent in codebase-locator codebase-analyzer codebase-pattern-finder web-search-researcher file-analyzer bug-hunter test-runner; do
    if [ -f ".claude/agents/$agent.md" ]; then
        echo "  ✅ Agent: $agent"
    else
        echo "  ❌ Missing agent: $agent"
        exit 1
    fi
done

# Check directories
for dir in research plans handoffs; do
    if [ -d "$dir" ]; then
        echo "  ✅ Directory: $dir"
    else
        echo "  ❌ Missing directory: $dir"
        exit 1
    fi
done

echo ""

# Test language-specific features
PROJECT_TYPE=$(detect_project_type)
echo "📦 Testing for project type: $PROJECT_TYPE"

if [ "$PROJECT_TYPE" = "python" ] || [ "$PROJECT_TYPE" = "unknown" ]; then
    echo "  🐍 Testing Python support..."
    # Create dummy Python test
    mkdir -p tests
    cat > tests/test_sample.py << 'EOF'
def test_dummy():
    """Verify pytest works"""
    assert True
EOF

    # Test if pytest works
    if command -v pytest &> /dev/null; then
        pytest tests/test_sample.py -q && echo "    ✅ pytest verification works"
    else
        echo "    ⚠️ pytest not installed (optional)"
    fi

    # Check Python linters
    if command -v ruff &> /dev/null; then
        echo "    ✅ ruff available"
    elif command -v flake8 &> /dev/null; then
        echo "    ✅ flake8 available"
    else
        echo "    ⚠️ No Python linter found (optional)"
    fi
fi

if [ "$PROJECT_TYPE" = "javascript" ] || [ "$PROJECT_TYPE" = "unknown" ]; then
    echo "  📦 Testing JavaScript/TypeScript support..."
    # Create minimal package.json
    cat > package.json << 'EOF'
{
  "name": "test-project",
  "version": "1.0.0",
  "scripts": {
    "test": "echo 'No tests defined'"
  }
}
EOF

    # Test npm
    if command -v npm &> /dev/null; then
        npm test &> /dev/null && echo "    ✅ npm verification works"
    else
        echo "    ⚠️ npm not installed (optional)"
    fi
fi

echo ""
echo "✅ Installation test passed!"
echo ""
echo "🧹 Cleaning up test directory..."
cd /
rm -rf "$TEST_DIR"

echo "✨ All tests completed successfully!"