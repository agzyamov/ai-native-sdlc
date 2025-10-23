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
  echo "  $0 speckit.specify ARGUMENTS='create calculator' BRANCH_NAME='001-calculator'"
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

# Load prompt content
PROMPT_CONTENT=$(cat "$PROMPT_FILE")

# Replace placeholders with provided variables
for arg in "$@"; do
  if [[ "$arg" =~ ^([A-Z_]+)=(.*)$ ]]; then
    KEY="${BASH_REMATCH[1]}"
    VALUE="${BASH_REMATCH[2]}"
    echo "🔄 Replacing \$$KEY with: $VALUE"
    # Escape special characters for sed
    ESCAPED_VALUE=$(printf '%s\n' "$VALUE" | sed 's/[\/&]/\\&/g')
    PROMPT_CONTENT=$(echo "$PROMPT_CONTENT" | sed "s/\\\$$KEY/$ESCAPED_VALUE/g")
  else
    echo "⚠️  WARNING: Invalid argument format: $arg (expected KEY=value)"
  fi
done

echo ""
echo "🤖 Running Copilot CLI with prepared prompt..."
echo ""

# Save prepared prompt to temp file
TEMP_PROMPT=$(mktemp)
echo "$PROMPT_CONTENT" > "$TEMP_PROMPT"

# Run Copilot CLI
npx @github/copilot --allow-all-tools --allow-all-paths -p "$(cat "$TEMP_PROMPT")"

# Cleanup
rm -f "$TEMP_PROMPT"
