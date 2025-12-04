#!/usr/bin/env bash
# Create ADO Issue work items from LLM-extracted questions (JSON format)

set -uo pipefail  # Remove -e to allow manual error handling

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --questions-json) QUESTIONS_JSON="$2"; shift 2 ;;
    --feature-id) FEATURE_ID="$2"; shift 2 ;;
    --branch) BRANCH_NAME="$2"; shift 2 ;;
    --org-url) ADO_ORG_URL="$2"; shift 2 ;;
    --project) ADO_PROJECT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Validate environment
echo "=== ADO Issue Creation Debug Info ==="
echo "ADO_ORG_URL: ${ADO_ORG_URL:-not set}"
echo "ADO_PROJECT: ${ADO_PROJECT:-not set}"
echo "FEATURE_ID: ${FEATURE_ID:-not set}"
echo "ADO_WORK_ITEM_PAT length: ${#ADO_WORK_ITEM_PAT}"
echo "QUESTIONS_JSON: ${QUESTIONS_JSON:-not set}"
echo ""

if [ -z "${ADO_WORK_ITEM_PAT:-}" ]; then
  echo "❌ Error: ADO_WORK_ITEM_PAT not set" >&2
  exit 1
fi

if [ -z "${ADO_ORG_URL:-}" ] || [ -z "${ADO_PROJECT:-}" ]; then
  echo "❌ Error: ADO_ORG_URL or ADO_PROJECT not set" >&2
  exit 1
fi

if [ "$ADO_ORG_URL" = "https://dev.azure.com/your-org" ] || [ "$ADO_PROJECT" = "your-project" ]; then
  echo "❌ Error: ADO_ORG or ADO_PROJECT using default values!" >&2
  echo "Please set GitHub repository variables:" >&2
  echo "  - ADO_ORG: Your Azure DevOps organization name" >&2
  echo "  - ADO_PROJECT: Your Azure DevOps project name" >&2
  exit 1
fi

if [ ! -f "$QUESTIONS_JSON" ]; then
  echo "❌ Error: Questions JSON file not found: $QUESTIONS_JSON" >&2
  exit 1
fi

# Count questions in JSON
QUESTION_COUNT=$(python3 -c "import json; print(len(json.load(open('$QUESTIONS_JSON'))))" 2>/dev/null || echo "0")

if [ "$QUESTION_COUNT" -eq 0 ]; then
  echo "ℹ️  No questions found in JSON file"
  exit 0
fi

echo "📋 Found $QUESTION_COUNT questions to create Issues for"

# Call Python script to create issues
set +e  # Temporarily disable exit on error to capture exit code
python3 .github/scripts/create-ado-issues.py \
  --questions-json "$QUESTIONS_JSON" \
  --feature-id "$FEATURE_ID" \
  --branch "$BRANCH_NAME" \
  --org-url "$ADO_ORG_URL" \
  --project "$ADO_PROJECT"

EXIT_CODE=$?
set -e  # Re-enable exit on error

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Issue creation complete"
else
  echo "❌ Issue creation failed with exit code $EXIT_CODE" >&2
  exit $EXIT_CODE
fi
