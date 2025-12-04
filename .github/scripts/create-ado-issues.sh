#!/usr/bin/env bash
# Create ADO Issue work items from LLM-extracted questions (JSON format)

set -euo pipefail

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

# For each question, create Issue via Python ADO client
python3 <<EOF
import sys
import os
import json
import hashlib
sys.path.insert(0, '${GITHUB_WORKSPACE}/function_app')
from ado_client import create_issue_workitem

# Set environment variables for ado_client
os.environ['ADO_ORG_URL'] = '${ADO_ORG_URL}'
os.environ['ADO_PROJECT'] = '${ADO_PROJECT}'
os.environ['ADO_WORK_ITEM_PAT'] = '${ADO_WORK_ITEM_PAT}'

# Load questions from JSON
with open('${QUESTIONS_JSON}', 'r') as f:
    questions = json.load(f)

print(f"📋 Loaded {len(questions)} questions from JSON")

# Process each question
for i, q in enumerate(questions, 1):
    topic = q.get('topic', f'Question {i}')
    question_text = q.get('question', '')
    context = q.get('context', '')
    answer_options = q.get('answer_options', '').strip()
    
    print(f"\n📝 Creating Issue for Question {i}: {topic}")
    
    # Generate idempotency key
    question_hash = hashlib.sha256(question_text.encode()).hexdigest()[:8]
    idempotency_key = f"${FEATURE_ID}-{question_hash}"
    
    # Build description in markdown format (ADO accepts markdown)
    description_parts = [
        f"## Question {i}: {topic}\n",
    ]
    
    if context:
        description_parts.append(f"**Context**: {context}\n\n")
    
    if question_text:
        description_parts.append(f"**What we need to know**: {question_text}\n\n")
    
    if answer_options:
        description_parts.append(f"**Suggested Answers**:\n\n{answer_options}\n\n")
    
    description_parts.append(f"**Your choice**: _[Awaiting response]_\n\n")
    description_parts.append(f"---\n\n")
    description_parts.append(f"**Branch**: ${BRANCH_NAME}\n")
    description_parts.append(f"**Idempotency Key**: `{idempotency_key}`\n")
    
    description = ''.join(description_parts)
    
    # Create Issue with clean title (topic only)
    result = create_issue_workitem(
        parent_feature_id=int("${FEATURE_ID}"),
        title=f"Q{i}: {topic}",
        description=description,
        tags="clarification; auto-generated",
        idempotency_key=idempotency_key
    )
    
    if result:
        print(f"✅ Created Issue {result['id']}")
    else:
        print(f"⚠️ Issue creation failed for Question {i}", file=sys.stderr)

print(f"\n✅ Issue creation complete - processed {len(questions)} questions")
EOF

echo "✅ Issue creation complete"
