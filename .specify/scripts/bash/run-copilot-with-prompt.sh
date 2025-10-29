#!/usr/bin/env bash
set -euo pipefail

# Script: run-copilot-with-prompt.sh
# Purpose: Load Spec Kit prompts and run Copilot CLI with proper context
# Usage: ./run-copilot-with-prompt.sh <prompt-name> [key=value...]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PROMPTS_DIR="$REPO_ROOT/.github/prompts"

# Parse arguments
if [ $# -lt 1 ]; then
  echo "Usage: $0 <prompt-name> [key=value...]"
  echo ""
  echo "Examples:"
  echo "  $0 speckit.specify FEATURE_DESC_FILE='path/to/desc.txt' BRANCH_NAME='001-calculator'"
  echo "  $0 speckit.clarify SPEC_FILE='/path/to/spec.md'"
  exit 1
fi

PROMPT_NAME="$1"
shift

# Find prompt file
PROMPT_FILE="$PROMPTS_DIR/${PROMPT_NAME}.prompt.md"
if [ ! -f "$PROMPT_FILE" ]; then
  echo "❌ ERROR: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

echo "📄 Loading prompt: $PROMPT_NAME"
echo "📂 From: $PROMPT_FILE"
echo ""

# Parse arguments and export as environment variables
# These will be available in the prompt template (e.g., $FEATURE_DESC_FILE)
for arg in "$@"; do
  if [[ "$arg" =~ ^([A-Z_]+)=(.*)$ ]]; then
    KEY="${BASH_REMATCH[1]}"
    VALUE="${BASH_REMATCH[2]}"
    echo "� Setting \$$KEY (value: ${VALUE:0:50}...)"
    export "$KEY=$VALUE"
  else
    echo "⚠️  WARNING: Invalid argument format: $arg (expected KEY=value)"
  fi
done

echo ""
echo "🤖 Running Copilot CLI with prompt..."
echo "   Copilot can access environment variables and read files directly"
echo ""

# Run Copilot CLI with the prompt template
# Copilot can access environment variables like $FEATURE_DESC_FILE
# and read files directly using file operations
npx @github/copilot --allow-all-tools --allow-all-paths -p "$(cat "$PROMPT_FILE")"

echo ""
echo "✅ Copilot CLI execution completed"

