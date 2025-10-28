#!/bin/bash
# Test with real Azure DevOps work item

set -e

FUNCTION_URL="http://localhost:7071/api/spec-dispatch"
WORK_ITEM_ID="444"

echo "=== Testing with Real ADO Work Item ==="
echo ""
echo "📋 Configuration:"
echo "  ADO Org: https://dev.azure.com/RustemAgziamov"
echo "  Project: ai-native-sdlc-blueprint"
echo "  Work Item ID: $WORK_ITEM_ID"
echo ""

# Check if function is running
echo "🔍 Checking if function is running..."
if ! curl -s --max-time 2 "$FUNCTION_URL" > /dev/null 2>&1; then
    echo "❌ Function is not running at $FUNCTION_URL"
    echo ""
    echo "Start it with:"
    echo "  cd function_app"
    echo "  func start"
    exit 1
fi
echo "✅ Function is responding"
echo ""

# First, let's fetch the real work item to see its current state
echo "🔍 Fetching work item $WORK_ITEM_ID from ADO..."
ADO_ORG_URL="https://dev.azure.com/RustemAgziamov"
ADO_PROJECT="ai-native-sdlc-blueprint"
ADO_PAT="CT3dNvWwrwR6r1V8OaDNBLzHoGJMfVsWK5HoUP9Fykf8uBAbeEKNJQQJ99BJACAAAAAc0or1AAASAZDOaUC8"

WORK_ITEM_DATA=$(curl -s -u ":$ADO_PAT" \
  "$ADO_ORG_URL/$ADO_PROJECT/_apis/wit/workitems/$WORK_ITEM_ID?api-version=7.1")

echo "📝 Work Item Details:"
echo "$WORK_ITEM_DATA" | jq -r '{
  id: .id,
  type: .fields."System.WorkItemType",
  title: .fields."System.Title",
  assignee: .fields."System.AssignedTo".displayName,
  state: .fields."System.State",
  column: .fields."System.BoardColumn"
}'
echo ""

# Extract fields for payload
WORK_ITEM_TYPE=$(echo "$WORK_ITEM_DATA" | jq -r '.fields."System.WorkItemType"')
TITLE=$(echo "$WORK_ITEM_DATA" | jq -r '.fields."System.Title"')
ASSIGNEE=$(echo "$WORK_ITEM_DATA" | jq -r '.fields."System.AssignedTo".displayName // "Unassigned"')
BOARD_COLUMN=$(echo "$WORK_ITEM_DATA" | jq -r '.fields."System.BoardColumn" // "Unknown"')

echo "🧪 Validation Check:"
echo "  ✓ Event Type: workitem.updated (will send)"
echo "  ✓ Work Item Type: $WORK_ITEM_TYPE (expecting: Feature)"
echo "  ✓ Assignee: $ASSIGNEE (expecting: AI Teammate)"
echo "  ✓ Board Column: $BOARD_COLUMN (expecting: Specification – Doing)"
echo ""

# Create realistic ADO Service Hook payload
PAYLOAD=$(cat <<EOF
{
  "subscriptionId": "test-subscription-id",
  "notificationId": 1,
  "id": "test-event-id",
  "eventType": "workitem.updated",
  "publisherId": "tfs",
  "message": {
    "text": "$WORK_ITEM_TYPE #$WORK_ITEM_ID updated",
    "html": "$WORK_ITEM_TYPE <a href=\\\"$ADO_ORG_URL/$ADO_PROJECT/_workitems/edit/$WORK_ITEM_ID\\\">$WORK_ITEM_ID</a> updated"
  },
  "detailedMessage": {
    "text": "$WORK_ITEM_TYPE #$WORK_ITEM_ID ($TITLE) updated\\r\\n($ADO_ORG_URL/$ADO_PROJECT/_workitems/edit/$WORK_ITEM_ID)"
  },
  "resource": {
    "id": $WORK_ITEM_ID,
    "workItemId": $WORK_ITEM_ID,
    "rev": 1,
    "fields": {
      "System.WorkItemType": "$WORK_ITEM_TYPE",
      "System.Title": "$TITLE",
      "System.AssignedTo": {
        "displayName": "$ASSIGNEE"
      },
      "System.BoardColumn": "$BOARD_COLUMN",
      "System.State": "Active"
    },
    "_links": {
      "html": {
        "href": "$ADO_ORG_URL/$ADO_PROJECT/_workitems/edit/$WORK_ITEM_ID"
      }
    }
  },
  "createdDate": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
)

echo "📤 Sending payload to function..."
echo ""

RESPONSE=$(curl -s -w "\n---STATS---\nHTTP_CODE: %{http_code}\nTIME: %{time_total}s\n" \
  -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESPONSE"
echo ""

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2 | tr -d ' ')

echo "📊 Result Analysis:"
case "$HTTP_CODE" in
  204)
    echo "  ✅ SUCCESS - Workflow dispatched!"
    echo ""
    echo "  🎯 Next Steps:"
    echo "  1. Check GitHub Actions: https://github.com/agzyamov/ai-native-sdlc/actions"
    echo "  2. Verify branch feature/wi-$WORK_ITEM_ID was created"
    echo "  3. Check specs/ directory for generated specification"
    echo "  4. Verify ADO work item Description was updated"
    ;;
  400)
    echo "  ❌ BAD REQUEST - Malformed payload"
    BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")
    echo "  Response: $BODY"
    ;;
  403)
    echo "  ⚠️  FORBIDDEN - Validation failed"
    BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")
    echo "  Response: $BODY"
    echo ""
    echo "  Current work item state:"
    echo "    Work Item Type: $WORK_ITEM_TYPE (expected: Feature)"
    echo "    Assignee: $ASSIGNEE (expected: AI Teammate)"
    echo "    Board Column: $BOARD_COLUMN (expected: Specification – Doing)"
    echo ""
    echo "  💡 To fix:"
    echo "  1. Ensure work item is a Feature"
    echo "  2. Assign to 'AI Teammate'"
    echo "  3. Move to 'Specification – Doing' column"
    ;;
  500)
    echo "  ❌ SERVER ERROR - Internal failure"
    BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")
    echo "  Response: $BODY"
    ;;
  *)
    echo "  ❓ UNEXPECTED - HTTP $HTTP_CODE"
    BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")
    echo "  Response: $BODY"
    ;;
esac
