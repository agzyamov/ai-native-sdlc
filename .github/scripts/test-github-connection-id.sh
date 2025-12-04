#!/bin/bash
# Test script to retrieve GitHub Connection ID from Azure DevOps API
# Usage: ./test-github-connection-id.sh

set -e

# Configuration - set these or export as environment variables
ADO_ORG="${ADO_ORG:-RustemAgziamov}"
ADO_PROJECT="${ADO_PROJECT:-ai-native-sdlc-blueprint}"
GITHUB_REPO="${GITHUB_REPO:-agzyamov/ai-native-sdlc}"
ADO_WORKITEM_RW_PAT="${ADO_WORKITEM_RW_PAT}"

if [ -z "$ADO_WORKITEM_RW_PAT" ]; then
  echo "❌ ERROR: ADO_WORKITEM_RW_PAT environment variable not set"
  echo "Please export it: export ADO_WORKITEM_RW_PAT='your-pat-token'"
  exit 1
fi

echo "🔍 Querying Azure DevOps API for GitHub connection ID..."
echo "ADO_ORG: $ADO_ORG"
echo "ADO_PROJECT: $ADO_PROJECT"
echo "GITHUB_REPO: $GITHUB_REPO"
echo ""

# Try Boards External Connections API first
echo "📡 Trying Boards External Connections API..."
ENDPOINT="https://dev.azure.com/${ADO_ORG}/${ADO_PROJECT}/_apis/work/boards/externalconnections?api-version=7.0-preview.1"

RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  --http1.1 \
  --max-time 30 \
  --connect-timeout 10 \
  -H "Authorization: Basic $(echo -n ":${ADO_WORKITEM_RW_PAT}" | base64 | tr -d '\n')" \
  "$ENDPOINT" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
  echo "📋 Full API Response:"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  echo ""
  
  # Extract connection ID from response
  CONNECTION_ID=$(echo "$BODY" | jq -r --arg repo "$GITHUB_REPO" '.value[]? | select(.type == "GitHub" and ((.repositoryName // .name // "") | ascii_downcase | contains($repo | ascii_downcase))) | .id' 2>/dev/null | head -1)
  
  if [ -n "$CONNECTION_ID" ] && [ "$CONNECTION_ID" != "null" ] && [ "$CONNECTION_ID" != "" ]; then
    echo "✅ Found GitHub connection ID (matched repo): $CONNECTION_ID"
    exit 0
  fi
  
  # If no match found, try to get the first GitHub connection
  CONNECTION_ID=$(echo "$BODY" | jq -r '.value[]? | select(.type == "GitHub") | .id' 2>/dev/null | head -1)
  
  if [ -n "$CONNECTION_ID" ] && [ "$CONNECTION_ID" != "null" ] && [ "$CONNECTION_ID" != "" ]; then
    echo "✅ Found GitHub connection ID (first available): $CONNECTION_ID"
    exit 0
  fi
  
  echo "ℹ️  No GitHub connections found in Boards External Connections API response"
else
  echo "⚠️  Boards External Connections API returned HTTP $HTTP_CODE"
  echo "Response: $BODY"
fi

# Fallback: Try Service Endpoints API
echo ""
echo "📡 Trying Service Endpoints API (fallback)..."
ENDPOINT="https://dev.azure.com/${ADO_ORG}/${ADO_PROJECT}/_apis/serviceendpoint/endpoints?api-version=6.0-preview.4&type=github"

RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  --http1.1 \
  --max-time 30 \
  --connect-timeout 10 \
  -H "Authorization: Basic $(echo -n ":${ADO_WORKITEM_RW_PAT}" | base64 | tr -d '\n')" \
  "$ENDPOINT" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
  echo "📋 Full API Response:"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  echo ""
  
  # Extract first GitHub service endpoint ID
  CONNECTION_ID=$(echo "$BODY" | jq -r '.value[0].id // empty' 2>/dev/null | head -1)
  
  if [ -n "$CONNECTION_ID" ] && [ "$CONNECTION_ID" != "null" ] && [ "$CONNECTION_ID" != "" ]; then
    echo "✅ Found GitHub service endpoint ID: $CONNECTION_ID"
    exit 0
  fi
  
  echo "ℹ️  No GitHub service endpoints found in response"
else
  echo "⚠️  Service Endpoints API returned HTTP $HTTP_CODE"
  echo "Response: $BODY"
fi

echo ""
echo "❌ Could not find GitHub connection ID"
exit 1

