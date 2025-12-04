#!/bin/bash
# Test script to assign work item 615 to the user found in revisedBy
# Usage: ADO_WORK_ITEM_PAT='your-pat' ./test-assign-615.sh

set -e

WORK_ITEM_ID=615
USER_ID="8ec6f80d-0ef1-6357-9fe4-e09eca72d843"  # From revisedBy.id in payload
ADO_ORG="${ADO_ORG:-RustemAgziamov}"
ADO_PROJECT="${ADO_PROJECT:-ai-native-sdlc-blueprint}"

if [ -z "$ADO_WORK_ITEM_PAT" ]; then
  echo "❌ ADO_WORK_ITEM_PAT environment variable not set"
  echo "Usage: ADO_WORK_ITEM_PAT='your-pat' ./test-assign-615.sh"
  exit 1
fi

echo "🧪 Testing Work Item Assignment"
echo "============================================================"
echo "Work Item ID: $WORK_ITEM_ID"
echo "User ID (GUID): $USER_ID"
echo "Org: $ADO_ORG"
echo "Project: $ADO_PROJECT"
echo ""

# Step 1: Fetch current state
echo "📋 Step 1: Fetching current work item state..."
CURRENT_URL="https://dev.azure.com/${ADO_ORG}/${ADO_PROJECT}/_apis/wit/workitems/${WORK_ITEM_ID}?api-version=7.0"

CURRENT_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  -H "Authorization: Basic $(echo -n ":${ADO_WORK_ITEM_PAT}" | base64 | tr -d '\n')" \
  -H "Content-Type: application/json" \
  "$CURRENT_URL" 2>&1)

CURRENT_HTTP=$(echo "$CURRENT_RESPONSE" | tail -1)
CURRENT_BODY=$(echo "$CURRENT_RESPONSE" | sed '$d')

if [ "$CURRENT_HTTP" = "200" ]; then
  CURRENT_ASSIGNED=$(echo "$CURRENT_BODY" | jq -r '.fields."System.AssignedTo".displayName // .fields."System.AssignedTo" // "Unassigned"' 2>/dev/null || echo "N/A")
  CURRENT_ID=$(echo "$CURRENT_BODY" | jq -r '.fields."System.AssignedTo".id // "N/A"' 2>/dev/null || echo "N/A")
  echo "✅ Current assignment:"
  echo "   Display Name: $CURRENT_ASSIGNED"
  echo "   User ID: $CURRENT_ID"
  echo ""
else
  echo "❌ Failed to fetch: HTTP $CURRENT_HTTP"
  echo "$CURRENT_BODY" | head -20
  exit 1
fi

# Step 2: Assign to user
echo "🔄 Step 2: Assigning work item to user..."
ASSIGN_URL="https://dev.azure.com/${ADO_ORG}/${ADO_PROJECT}/_apis/wit/workitems/${WORK_ITEM_ID}?api-version=7.0"

PAYLOAD=$(cat <<EOF
[
  {
    "op": "replace",
    "path": "/fields/System.AssignedTo",
    "value": "$USER_ID"
  }
]
EOF
)

echo "   Payload:"
echo "$PAYLOAD" | jq '.'
echo ""

ASSIGN_RESPONSE=$(curl -s -w "\n%{http_code}" -X PATCH \
  -H "Authorization: Basic $(echo -n ":${ADO_WORK_ITEM_PAT}" | base64 | tr -d '\n')" \
  -H "Content-Type: application/json-patch+json" \
  -d "$PAYLOAD" \
  "$ASSIGN_URL" 2>&1)

ASSIGN_HTTP=$(echo "$ASSIGN_RESPONSE" | tail -1)
ASSIGN_BODY=$(echo "$ASSIGN_RESPONSE" | sed '$d')

echo "   HTTP Status: $ASSIGN_HTTP"

if [ "$ASSIGN_HTTP" = "200" ] || [ "$ASSIGN_HTTP" = "204" ]; then
  echo "✅ Work item assigned successfully!"
  echo ""
  
  # Step 3: Verify
  echo "📋 Step 3: Verifying assignment..."
  VERIFY_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Authorization: Basic $(echo -n ":${ADO_WORK_ITEM_PAT}" | base64 | tr -d '\n')" \
    -H "Content-Type: application/json" \
    "$CURRENT_URL" 2>&1)
  
  VERIFY_HTTP=$(echo "$VERIFY_RESPONSE" | tail -1)
  VERIFY_BODY=$(echo "$VERIFY_RESPONSE" | sed '$d')
  
  if [ "$VERIFY_HTTP" = "200" ]; then
    VERIFY_ASSIGNED=$(echo "$VERIFY_BODY" | jq -r '.fields."System.AssignedTo".displayName // .fields."System.AssignedTo" // "N/A"' 2>/dev/null || echo "N/A")
    VERIFY_ID=$(echo "$VERIFY_BODY" | jq -r '.fields."System.AssignedTo".id // "N/A"' 2>/dev/null || echo "N/A")
    
    echo "✅ Verified assignment:"
    echo "   Display Name: $VERIFY_ASSIGNED"
    echo "   User ID: $VERIFY_ID"
    
    if [ "$VERIFY_ID" = "$USER_ID" ]; then
      echo "   ✅ User ID matches!"
    else
      echo "   ⚠️  User ID mismatch"
      echo "      Expected: $USER_ID"
      echo "      Got: $VERIFY_ID"
    fi
  else
    echo "⚠️  Could not verify (HTTP $VERIFY_HTTP)"
  fi
else
  echo "❌ Assignment failed"
  echo ""
  echo "Response body:"
  echo "$ASSIGN_BODY" | jq '.' 2>/dev/null || echo "$ASSIGN_BODY" | head -20
  echo ""
  echo "💡 Note: If you get HTTP 400, Azure DevOps might require the user's email (uniqueName) instead of GUID"
fi

echo ""
echo "============================================================"

