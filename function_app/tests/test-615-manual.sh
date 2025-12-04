#!/bin/bash
# Test function manually with work item 615 payload

FUNCTION_URL="${1:-http://localhost:7071/api/spec-dispatch}"
FUNCTION_KEY="${2:-}"

echo "=== Manual Test: Work Item 615 ==="
echo ""
echo "Function URL: $FUNCTION_URL"
echo ""

# Create the exact payload from the user's request
PAYLOAD_FILE=$(mktemp)
cat > "$PAYLOAD_FILE" << 'EOF'
{
  "subscriptionId": "20eeb007-3451-4aad-a749-4f069e36b67c",
  "notificationId": 79,
  "id": "efcf962e-c686-48d5-b6d7-2f6470ab275c",
  "eventType": "workitem.updated",
  "publisherId": "tfs",
  "resource": {
    "workItemId": 615,
    "revision": {
      "fields": {
        "System.WorkItemType": "Feature",
        "System.State": "Specification",
        "System.AssignedTo": "AI Teammate <Bot_AI_Teammate_ai-teammate@epam.com>",
        "System.Title": "hockey simulator game",
        "System.BoardColumn": "Specification",
        "System.BoardColumnDone": false,
        "System.Description": "create a hockey simulator game using unreal engine"
      }
    }
  }
}
EOF

echo "📤 Sending request..."
echo ""

if [ -n "$FUNCTION_KEY" ]; then
    URL="${FUNCTION_URL}?code=${FUNCTION_KEY}"
else
    URL="$FUNCTION_URL"
fi

RESPONSE=$(curl -s -w "\n---STATS---\nHTTP_CODE: %{http_code}\n" \
  -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d @"$PAYLOAD_FILE")

echo "$RESPONSE"
echo ""

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2 | tr -d ' ')

echo "📊 Result: HTTP $HTTP_CODE"
echo ""

case "$HTTP_CODE" in
  204)
    echo "✅ SUCCESS - Function processed the request!"
    ;;
  500)
    echo "❌ SERVER ERROR - This is the issue!"
    echo ""
    echo "The function is failing because:"
    echo "  1. It tries to call ADO API (line 105 in function_app.py)"
    echo "  2. Security settings block the call"
    echo "  3. ADO API returns None"
    echo "  4. Code raises ValueError (line 108)"
    echo "  5. Exception handler returns 500 (line 117-124)"
    echo ""
    echo "BUT the payload already has the data in resource.revision.fields!"
    echo "The ADO API call is unnecessary."
    ;;
  *)
    echo "Response: $(echo "$RESPONSE" | grep -v "HTTP_CODE\|---STATS---")"
    ;;
esac

rm -f "$PAYLOAD_FILE"



