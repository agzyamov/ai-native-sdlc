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
  
  # Extract question block from clarifications.md (from Question X to next Question or end)
  QUESTION_BLOCK=$(sed -n "/^## Question $i:/,/^## Question $((i+1)):/p" "$CLARIFICATIONS_FILE")
  
  # Extract components
  QUESTION_TEXT=$(echo "$QUESTION_BLOCK" | grep "^\*\*Question\*\*:" | sed 's/^\*\*Question\*\*: //')
  QUESTION_TOPIC=$(echo "$QUESTION_BLOCK" | head -1 | sed 's/^## Question [0-9]*: //')
  
  # Extract answer options (everything between **Answer Options**: and **Answer**:)
  ANSWER_OPTIONS=$(echo "$QUESTION_BLOCK" | sed -n '/^\*\*Answer Options\*\*:/,/^\*\*Answer\*\*:/p' | sed '1d;$d' | sed '/^$/d')
  
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

# Extract question and answer options from clarifications.md
question = """${QUESTION_TEXT}"""
topic = """${QUESTION_TOPIC}"""
answer_options = """${ANSWER_OPTIONS}"""

# Generate idempotency key
question_hash = hashlib.sha256(question.encode()).hexdigest()[:8]
idempotency_key = f"${FEATURE_ID}-{question_hash}"

# Build description with answer options (convert markdown table to HTML)
description_parts = [
    f"<p><strong>Question:</strong> {question}</p>",
]

if answer_options.strip():
    # Convert markdown table to HTML (simple conversion for ADO)
    html_table = "<table border='1' cellpadding='5'>"
    for line in answer_options.split('\n'):
        if line.strip().startswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and not all(c.replace('-', '').strip() == '' for c in cells):
                html_table += "<tr>"
                for cell in cells:
                    html_table += f"<td>{cell}</td>"
                html_table += "</tr>"
    html_table += "</table>"
    description_parts.append(f"<p><strong>Answer Options:</strong></p>{html_table}")

description_parts.extend([
    f"<p><strong>Branch:</strong> ${BRANCH_NAME}</p>",
    f"<p><strong>Idempotency Key:</strong> <code>{idempotency_key}</code></p>"
])

description = ''.join(description_parts)

# Create Issue with clean title (topic only, no truncated question text)
result = create_issue_workitem(
    parent_feature_id=int("${FEATURE_ID}"),
    title=f"Q${i}: {topic}",
    description=description,
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
