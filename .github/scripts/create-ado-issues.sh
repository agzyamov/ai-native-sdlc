#!/usr/bin/env bash
"""Create ADO Issue work items from clarifications.md"""

set -euo pipefail

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --clarifications-file) CLARIFICATIONS_FILE="$2"; shift 2 ;;
    --feature-id) FEATURE_ID="$2"; shift 2 ;;
    --branch) BRANCH_NAME="$2"; shift 2 ;;
    --org-url) ADO_ORG_URL="$2"; shift 2 ;;
    --project) ADO_PROJECT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Validate environment
if [ -z "${ADO_WORK_ITEM_PAT:-}" ]; then
  echo "❌ Error: ADO_WORK_ITEM_PAT not set" >&2
  exit 1
fi

# Extract questions from clarifications.md (parse markdown)
QUESTION_COUNT=$(grep -c "^## Question" "$CLARIFICATIONS_FILE" || echo "0")

if [ "$QUESTION_COUNT" -eq 0 ]; then
  echo "ℹ️  No questions found in clarifications file"
  exit 0
fi

echo "📋 Found $QUESTION_COUNT questions to create Issues for"

# For each question, create Issue via Python ADO client
for i in $(seq 1 "$QUESTION_COUNT"); do
  echo "Creating Issue for Question $i..."
  
  # Extract question text and topic from clarifications.md
  QUESTION_TEXT=$(sed -n "/^## Question $i:/,/^## Question $((i+1)):/p" "$CLARIFICATIONS_FILE" | grep "^\*\*Question\*\*:" | sed 's/^\*\*Question\*\*: //')
  QUESTION_TOPIC=$(sed -n "/^## Question $i:/p" "$CLARIFICATIONS_FILE" | sed 's/^## Question [0-9]*: //')
  
  # Call Python function to create Issue (extend ado_client.py)
  python3 <<EOF
import sys
import os
import hashlib
sys.path.insert(0, '${GITHUB_WORKSPACE}/function_app')
from ado_client import create_issue_workitem

# Set environment variables for ado_client
os.environ['ADO_ORG_URL'] = '${ADO_ORG_URL}'
os.environ['ADO_PROJECT'] = '${ADO_PROJECT}'
os.environ['ADO_WORK_ITEM_PAT'] = '${ADO_WORK_ITEM_PAT}'

# Extract question from clarifications.md
question = """${QUESTION_TEXT}"""
topic = """${QUESTION_TOPIC}"""

# Generate idempotency key
question_hash = hashlib.sha256(question.encode()).hexdigest()[:8]
idempotency_key = f"${FEATURE_ID}-{question_hash}"

# Create Issue
result = create_issue_workitem(
    parent_feature_id=int("${FEATURE_ID}"),
    title=f"Clarification Q$i: {topic}",
    description=f"<p><strong>Question:</strong> {question}</p><p><strong>Branch:</strong> ${BRANCH_NAME}</p><p><strong>Idempotency Key:</strong> <code>{idempotency_key}</code></p>",
    tags="clarification; auto-generated",
    idempotency_key=idempotency_key
)

if result:
    print(f"✅ Created Issue {result['id']}")
else:
    print(f"⚠️ Issue creation failed for Question $i", file=sys.stderr)
EOF
done

echo "✅ Issue creation complete"
