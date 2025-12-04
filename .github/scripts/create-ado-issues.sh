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
    topic = q.get('topic', f'Question {i}').strip()
    question_text = q.get('question', '').strip()
    context = q.get('context', '').strip()
    answer_options = q.get('answer_options', '').strip()
    
    print(f"\n📝 Processing Question {i}: {topic}")
    
    # Generate idempotency key (needed for function call, but not shown in description)
    question_hash = hashlib.sha256(question_text.encode()).hexdigest()[:8]
    idempotency_key = f"${FEATURE_ID}-{question_hash}"
    
    # Use LLM to clean topic and fix all formatting issues
    import os
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://ruste-mhinjxi0-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-5-nano",
                api_key=api_key,
                default_headers={'api-key': api_key}
            )
            
            # Build raw description first
            raw_description_parts = [
                f"## Question {i}: {topic}\n\n",
            ]
            
            if context:
                raw_description_parts.append(f"**Context**: {context}\n\n")
            
            if question_text:
                raw_description_parts.append(f"**What we need to know**: {question_text}\n\n")
            
            if answer_options:
                raw_description_parts.append(f"**Suggested Answers**:\n\n{answer_options}\n\n")
            
            raw_description_parts.append(f"**Your choice**: _[Awaiting response]_\n\n")
            raw_description_parts.append(f"---\n\n")
            raw_description_parts.append(f"**Branch**: ${BRANCH_NAME}\n")
            # Note: idempotency key is used for deduplication but not shown in description
            
            raw_description = ''.join(raw_description_parts)
            
            # Use LLM to clean and fix markdown
            fix_prompt = f"""Clean and fix this ADO work item description markdown. Requirements:
1. Remove duplicate "Question N:" text from the heading (e.g., "Question 2: Question 2: Topic" should become "Question 2: Topic")
2. Ensure all markdown syntax is correct and will render properly in Azure DevOps
3. Fix any broken markdown tables - ensure proper pipe alignment and formatting
4. Ensure proper spacing between sections (blank lines where needed)
5. Keep all content intact, just fix formatting

Raw description:
{raw_description}

Return ONLY the cleaned and fixed markdown description, no code blocks, no explanation."""
            
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "You are a markdown formatter for Azure DevOps. Clean and fix markdown syntax, remove duplicates, and ensure proper formatting. Return only the fixed markdown text."},
                    {"role": "user", "content": fix_prompt}
                ],
                max_completion_tokens=4000,
                extra_query={'api-version': '2025-01-01-preview'}
            )
            
            description = response.choices[0].message.content.strip()
            
            # Remove markdown code fences if LLM added them
            if description.startswith("```"):
                lines = description.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                description = '\n'.join(lines).strip()
            
            # Idempotency key is used for deduplication but not shown in description
            print(f"✅ Cleaned and fixed markdown using LLM")
            
        except Exception as e:
            print(f"⚠️  Could not fix markdown with LLM: {e}, using original")
            # Fallback: build description without LLM
            description_parts = [
                f"## Question {i}: {topic}\n\n",
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
            # Idempotency key is used for deduplication but not shown in description
            description = ''.join(description_parts)
    else:
        # No API key, build description without LLM
        description_parts = [
            f"## Question {i}: {topic}\n\n",
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
        # Idempotency key is used for deduplication but not shown in description
        description = ''.join(description_parts)
    
    # Extract clean topic for title (use LLM if available, otherwise use original)
    if api_key and 'client' in locals():
        try:
            title_prompt = f"""Extract a clean, concise topic from this text. Remove any "Question N:" prefix. Return only the topic text, nothing else.

Text: {topic}

Topic:"""
            title_response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "Extract clean topic text. Remove 'Question N:' prefixes. Return only the topic."},
                    {"role": "user", "content": title_prompt}
                ],
                max_completion_tokens=100,
                extra_query={'api-version': '2025-01-01-preview'}
            )
            clean_topic = title_response.choices[0].message.content.strip()
            if not clean_topic:
                clean_topic = topic
        except:
            clean_topic = topic
    else:
        clean_topic = topic
    
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
