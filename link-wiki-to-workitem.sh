#!/bin/bash

# Azure DevOps API to link Wiki page to Work Item
# Organization: RustemAgziamov
# Project: ai-native-sdlc-blueprint
# Work Item ID: 810
# Wiki Page ID: 55

ORG="RustemAgziamov"
PROJECT="ai-native-sdlc-blueprint"
WORK_ITEM_ID="810"
WIKI_NAME="ai-native-sdlc-blueprint.wiki"
WIKI_PAGE_ID="55"

# Construct the wiki artifact URI
# Format: vstfs:///Wiki/WikiPage/{project-id}/{wiki-name}/{page-id}
# We need to get the project ID first, or use the alternative URL format

WIKI_URL="https://dev.azure.com/${ORG}/${PROJECT}/_wiki/wikis/${WIKI_NAME}/${WIKI_PAGE_ID}/ADO-Process-Change-Alert"

# API endpoint
API_URL="https://dev.azure.com/${ORG}/${PROJECT}/_apis/wit/workitems/${WORK_ITEM_ID}?api-version=7.1"

# JSON Patch body to add wiki link
# Using ArtifactLink with Wiki link type
BODY='[
  {
    "op": "add",
    "path": "/relations/-",
    "value": {
      "rel": "ArtifactLink",
      "url": "'"${WIKI_URL}"'",
      "attributes": {
        "name": "Wiki",
        "comment": "Architecture Diagram for ADO Process Change Alert"
      }
    }
  }
]'

echo "Linking wiki page to work item..."
echo "Wiki URL: ${WIKI_URL}"
echo "Work Item: ${WORK_ITEM_ID}"
echo ""
echo "API URL: ${API_URL}"
echo ""
echo "Request body:"
echo "${BODY}" | jq .
echo ""
echo "Run with your PAT token:"
echo 'curl -X PATCH "'${API_URL}'" \'
echo '  -H "Content-Type: application/json-patch+json" \'
echo '  -u ":YOUR_PAT_TOKEN" \'
echo '  -d '"'"'${BODY}'"'"

