# Quickstart: Preserve Clarification Questions in Workflow Mode

**Feature**: 003-preserve-clarification-markers  
**Prerequisites**: Completion of 001-ado-github-spec deployment  
**Estimated Time**: 15 minutes

---

## Overview

This feature extends the existing specification workflow to conditionally preserve `[NEEDS CLARIFICATION]` markers and auto-create ADO Issues for human resolution.

**When to use**: Automatically triggers when Feature descriptions are ambiguous and Copilot generates clarification questions.

---

## Prerequisites

Before starting, ensure:

- ✅ 001-ado-github-spec is deployed and functional
- ✅ GitHub Actions workflow `spec-kit-specify.yml` exists
- ✅ Azure DevOps PAT with Work Items (Write) scope configured
- ✅ ADO project supports Issue work item type (or fallback to Task)

---

## Step 1: Update Workflow YAML

Modify `.github/workflows/spec-kit-specify.yml` to add marker detection and extraction steps.

### Add after "Step 3-6 - Generate Specification" step:

```yaml
- name: Detect Clarification Markers
  id: detect_markers
  run: |
    SPEC_FILE="${{ steps.create_feature.outputs.spec_file }}"
    
    if grep -q '\[NEEDS CLARIFICATION:' "$SPEC_FILE"; then
      echo "markers_found=true" >> $GITHUB_OUTPUT
      MARKER_COUNT=$(grep -c '\[NEEDS CLARIFICATION:' "$SPEC_FILE" || echo "0")
      echo "marker_count=$MARKER_COUNT" >> $GITHUB_OUTPUT
      echo "✅ Found $MARKER_COUNT clarification markers"
    else
      echo "markers_found=false" >> $GITHUB_OUTPUT
      echo "marker_count=0" >> $GITHUB_OUTPUT
      echo "ℹ️  No clarification markers found - clear requirements"
    fi

- name: Extract Clarifications
  if: steps.detect_markers.outputs.markers_found == 'true'
  run: |
    SPEC_FILE="${{ steps.create_feature.outputs.spec_file }}"
    FEATURE_DIR="${{ steps.create_feature.outputs.feature_dir }}"
    
    echo "📝 Extracting clarification questions..."
    python3 .github/scripts/extract-clarifications.py \
      --spec-file "$SPEC_FILE" \
      --output "$FEATURE_DIR/clarifications.md" \
      --feature-name "$(basename $FEATURE_DIR)"

- name: Create ADO Issues for Clarifications
  if: steps.detect_markers.outputs.markers_found == 'true' && github.event.inputs.work_item_id != ''
  env:
    ADO_WORKITEM_RW_PAT: ${{ secrets.ADO_WORKITEM_RW_PAT }}
    ADO_ORG: ${{ vars.ADO_ORG }}
    ADO_PROJECT: ${{ vars.ADO_PROJECT }}
    FEATURE_ID: ${{ github.event.inputs.work_item_id }}
    BRANCH_NAME: ${{ steps.create_feature.outputs.branch_name }}
  run: |
    CLARIFICATIONS_FILE="${{ steps.create_feature.outputs.feature_dir }}/clarifications.md"
    
    if [ ! -f "$CLARIFICATIONS_FILE" ]; then
      echo "⚠️ Clarifications file not found, skipping Issue creation"
      exit 0
    fi
    
    echo "🎫 Creating ADO Issues for clarification questions..."
    .github/scripts/create-ado-issues.sh \
      --clarifications-file "$CLARIFICATIONS_FILE" \
      --feature-id "$FEATURE_ID" \
      --branch "$BRANCH_NAME" \
      --org "$ADO_ORG" \
      --project "$ADO_PROJECT"
```

---

## Step 2: Add Extraction Script

Create `.github/scripts/extract-clarifications.py`:

```python
#!/usr/bin/env python3
"""Extract [NEEDS CLARIFICATION] markers from spec.md and create clarifications.md"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

MARKER_PATTERN = r'\[NEEDS CLARIFICATION:\s*([^\]]+)\]'

def extract_markers(spec_content: str) -> list[dict]:
    """Extract all clarification markers with context"""
    markers = []
    
    for match in re.finditer(MARKER_PATTERN, spec_content):
        question = match.group(1).strip()
        pos = match.start()
        
        # Extract context (200 chars before/after)
        start = max(0, pos - 200)
        end = min(len(spec_content), pos + 200)
        context = spec_content[start:end].strip()
        
        # Find section header (search backwards for ##)
        before_marker = spec_content[:pos]
        section_match = re.findall(r'^#{1,6}\s+(.+)$', before_marker, re.MULTILINE)
        section = section_match[-1] if section_match else "Unknown Section"
        
        # Generate topic (first 50 chars of question)
        topic = question[:50] + ("..." if len(question) > 50 else "")
        
        markers.append({
            'question': question,
            'context': context,
            'section': section,
            'topic': topic
        })
    
    return markers

def generate_clarifications_md(markers: list[dict], feature_name: str, spec_link: str = "./spec.md") -> str:
    """Generate clarifications.md content"""
    created_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    content = f"""# Clarification Questions: {feature_name}

**Feature**: [{spec_link}]({spec_link})  
**Created**: {created_date}  
**Status**: Open  
**Total Questions**: {len(markers)}

---

"""
    
    for i, marker in enumerate(markers, 1):
        content += f"""## Question {i}: {marker['topic']}

**Spec Section**: {marker['section']}

**Context**: {marker['context']}

**Question**: {marker['question']}

**Answer**: _Pending_

**ADO Issue**: _To be created_

---

"""
    
    content += """## Resolution Notes

_This section will be populated when questions are answered (manual or automated)._

"""
    
    return content

def main():
    parser = argparse.ArgumentParser(description="Extract clarification markers from spec.md")
    parser.add_argument("--spec-file", required=True, help="Path to spec.md")
    parser.add_argument("--output", required=True, help="Path to output clarifications.md")
    parser.add_argument("--feature-name", required=True, help="Feature name for header")
    
    args = parser.parse_args()
    
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        print(f"❌ Error: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    spec_content = spec_path.read_text()
    markers = extract_markers(spec_content)
    
    if not markers:
        print("ℹ️  No clarification markers found")
        sys.exit(0)
    
    print(f"✅ Extracted {len(markers)} clarification markers")
    
    clarifications_content = generate_clarifications_md(markers, args.feature_name)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clarifications_content)
    
    print(f"✅ Created clarifications file: {output_path}")

if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x .github/scripts/extract-clarifications.py
```

---

## Step 3: Add Issue Creation Script

Create `.github/scripts/create-ado-issues.sh`:

```bash
#!/usr/bin/env bash
"""Create ADO Issue work items from clarifications.md"""

set -euo pipefail

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --clarifications-file) CLARIFICATIONS_FILE="$2"; shift 2 ;;
    --feature-id) FEATURE_ID="$2"; shift 2 ;;
    --branch) BRANCH_NAME="$2"; shift 2 ;;
    --org) ADO_ORG="$2"; shift 2 ;;
    --project) ADO_PROJECT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Validate environment
if [ -z "${ADO_WORKITEM_RW_PAT:-}" ]; then
  echo "❌ Error: ADO_WORKITEM_RW_PAT not set" >&2
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
  
  # Call Python function to create Issue (extend ado_client.py)
  python3 <<EOF
import sys
sys.path.insert(0, '${GITHUB_WORKSPACE}/function_app')
from ado_client import create_issue_workitem
import hashlib

# Extract question from clarifications.md (simplified - real implementation parses markdown properly)
question = "Question $i from clarifications"  # TODO: Parse from file
topic = question[:50]

# Generate idempotency key
question_hash = hashlib.sha256(question.encode()).hexdigest()[:8]
idempotency_key = f"${FEATURE_ID}-{question_hash}"

# Create Issue
result = create_issue_workitem(
    parent_feature_id=int("${FEATURE_ID}"),
    title=f"Clarification Q$i: {topic}",
    description=f"<p><strong>Question:</strong> {question}</p><p><strong>Idempotency Key:</strong> <code>{idempotency_key}</code></p>",
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
```

Make it executable:
```bash
chmod +x .github/scripts/create-ado-issues.sh
```

---

## Step 4: Extend ADO Client

Add to `function_app/ado_client.py`:

```python
def create_issue_workitem(
    parent_feature_id: int,
    title: str,
    description: str,
    tags: str,
    idempotency_key: str,
    assigned_to: str = None
) -> dict:
    """
    Create ADO Issue work item with Parent-Child link to Feature.
    
    Returns Issue dict if created, None if duplicate detected or error.
    """
    # Check for existing Issue (idempotency)
    query_url = f"https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_apis/wit/wiql?api-version=7.0"
    query_payload = {
        "query": f"""
            SELECT [System.Id] 
            FROM WorkItems 
            WHERE [System.WorkItemType] = 'Issue' 
            AND [System.Parent] = {parent_feature_id}
            AND [System.Description] CONTAINS '{idempotency_key}'
        """
    }
    
    response = requests.post(
        query_url,
        json=query_payload,
        headers={"Authorization": f"Basic {base64_encoded_pat}"},
        timeout=10
    )
    
    if response.ok and response.json().get('workItems'):
        logger.info(f"Issue already exists for idempotency key {idempotency_key}")
        return None  # Duplicate, skip
    
    # Create Issue (JSON Patch format)
    create_url = f"https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workitems/$Issue?api-version=7.0"
    
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description},
        {"op": "add", "path": "/fields/System.Tags", "value": tags},
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": f"https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workitems/{parent_feature_id}",
                "attributes": {"comment": "Auto-generated clarification"}
            }
        }
    ]
    
    if assigned_to:
        payload.append({"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to})
    
    response = requests.post(
        create_url,
        json=payload,
        headers={
            "Content-Type": "application/json-patch+json",
            "Authorization": f"Basic {base64_encoded_pat}"
        },
        timeout=30
    )
    
    if response.ok:
        issue = response.json()
        logger.info(f"Created Issue {issue['id']}: {title}")
        return issue
    else:
        logger.error(f"Failed to create Issue: {response.status_code} {response.text}")
        return None
```

---

## Step 5: Test End-to-End

### 5.1 Trigger Workflow with Ambiguous Feature

In Azure DevOps:
1. Create a Feature: "Add user authentication" (ambiguous)
2. Assign to "AI Teammate"
3. Move to "Specification – Doing"

### 5.2 Verify Outputs

Check GitHub Actions workflow run:
- ✅ Spec file created with `[NEEDS CLARIFICATION: auth method]` marker
- ✅ `clarifications.md` file created with extracted question
- ✅ ADO Issue created linked to Feature
- ✅ Feature Description updated with spec containing marker

### 5.3 Test Happy Path (No Markers)

Create Feature: "Add OAuth2 authentication using PKCE flow" (clear)
- ✅ Spec file created without markers
- ✅ No clarifications.md created
- ✅ No Issues created
- ✅ Feature Description updated with clean spec

---

## Troubleshooting

### Markers Not Detected

**Symptom**: Workflow says "No markers found" but spec contains them

**Fix**: Check marker format exactly matches `[NEEDS CLARIFICATION: question]` (no typos, proper brackets)

### Issue Creation Fails

**Symptom**: "❌ Failed to create Issue: 401"

**Fix**: Verify `ADO_WORKITEM_RW_PAT` has Work Items (Write) scope

### Duplicate Issues Created

**Symptom**: Re-running workflow creates duplicate Issues

**Fix**: Verify idempotency query is working (check for `idempotency_key` in Issue Description)

---

## Next Steps

- Review [contracts/ado-issue-creation.md](./contracts/ado-issue-creation.md) for API details
- Check [data-model.md](./data-model.md) for entity relationships
- See [spec.md](./spec.md) for complete requirements

---

**Deployment Time**: ~15 minutes  
**Dependencies**: 001-ado-github-spec  
**Support**: See repository issues for help
