#!/bin/bash
# Debug script to test function with detailed output

set -e

FUNCTION_URL="http://localhost:7071/api/spec-dispatch"
SAMPLE="../specs/001-ado-github-spec/contracts/sample-ado-hook.json"

echo "=== Azure Function Debug Test ==="
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

# Check sample payload
if [ ! -f "$SAMPLE" ]; then
    echo "❌ Sample payload not found: $SAMPLE"
    exit 1
fi

echo "📋 Environment Configuration:"
echo "  GITHUB_OWNER: agzyamov"
echo "  GITHUB_REPO: ai-native-sdlc"
echo "  GITHUB_WORKFLOW_FILENAME: spec-kit-specify.yml"
echo "  AI_USER_MATCH: AI Teammate"
echo "  SPEC_COLUMN_NAME: Specification – Doing"
echo ""

echo "📝 Sample Payload Summary:"
jq -r '. | {
  eventType: .eventType,
  workItemId: .resource.workItemId,
  workItemType: .resource.fields."System.WorkItemType",
  assignee: .resource.fields."System.AssignedTo".displayName,
  column: .resource.fields."System.BoardColumn",
  title: .resource.fields."System.Title"
}' "$SAMPLE"
echo ""

echo "🧪 Sending request to function..."
echo ""

# Make the request with full output
RESPONSE=$(curl -s -w "\n---STATS---\nHTTP_CODE: %{http_code}\nTIME: %{time_total}s\n" \
  -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d @"$SAMPLE")

echo "$RESPONSE"
echo ""

# Parse response
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2 | tr -d ' ')

echo "📊 Result Analysis:"
case "$HTTP_CODE" in
  204)
    echo "  ✅ SUCCESS - Workflow dispatched!"
    echo "  Check GitHub Actions: https://github.com/agzyamov/ai-native-sdlc/actions"
    ;;
  400)
    echo "  ❌ BAD REQUEST - Malformed payload"
    echo "  Response: $(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")"
    ;;
  403)
    echo "  ⚠️  FORBIDDEN - Validation failed"
    echo "  Response: $(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")"
    echo ""
    echo "  Common reasons:"
    echo "  - Event type is not 'workitem.updated'"
    echo "  - Work item type is not 'Feature'"
    echo "  - Assignee is not 'AI Teammate'"
    echo "  - Board column is not 'Specification – Doing'"
    ;;
  500)
    echo "  ❌ SERVER ERROR - Internal failure or dispatch error"
    ERROR_MSG=$(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")
    echo "  Response: $ERROR_MSG"
    echo ""
    
    # Check for specific error patterns
    if echo "$ERROR_MSG" | grep -q "401\|403"; then
        echo "  🔑 Authentication issue detected!"
        echo ""
        echo "  GitHub PAT troubleshooting:"
        echo "  1. Verify PAT has 'actions:write' and 'contents:read' permissions"
        echo "  2. Check PAT hasn't expired"
        echo "  3. Test PAT manually:"
        echo "     curl -H 'Authorization: Bearer YOUR_PAT' \\"
        echo "       https://api.github.com/repos/agzyamov/ai-native-sdlc/actions/workflows"
        echo ""
        echo "  ADO PAT troubleshooting:"
        echo "  1. Verify PAT has 'Work Items: Read' permission"
        echo "  2. Check PAT hasn't expired"
        echo "  3. Verify organization URL is correct"
    elif echo "$ERROR_MSG" | grep -q "404"; then
        echo "  🔍 Resource not found!"
        echo ""
        echo "  Check:"
        echo "  1. Workflow file exists: .github/workflows/spec-kit-specify.yml"
        echo "  2. Repository is accessible: agzyamov/ai-native-sdlc"
        echo "  3. Workflow filename in local.settings.json matches exactly"
    elif echo "$ERROR_MSG" | grep -q "422"; then
        echo "  ⚠️  Validation error from GitHub API!"
        echo ""
        echo "  Check:"
        echo "  1. Workflow has workflow_dispatch trigger"
        echo "  2. Input parameters match workflow definition"
        echo "  3. Branch 'main' exists in repository"
    elif echo "$ERROR_MSG" | grep -q "Missing required"; then
        echo "  ⚙️  Configuration error!"
        echo ""
        echo "  Verify local.settings.json has:"
        echo "  - GH_WORKFLOW_DISPATCH_PAT"
        echo "  - GITHUB_OWNER"
        echo "  - GITHUB_REPO"
    fi
    ;;
  *)
    echo "  ❓ UNEXPECTED - HTTP $HTTP_CODE"
    echo "  Response: $(echo "$RESPONSE" | grep -v "HTTP_CODE\|TIME\|---STATS---")"
    ;;
esac
echo ""

echo "📋 Next Steps:"
if [ "$HTTP_CODE" == "204" ]; then
    echo "  1. Check GitHub Actions logs for workflow execution"
    echo "  2. Verify branch was created"
    echo "  3. Check for specification generation output"
elif [ "$HTTP_CODE" == "500" ]; then
    echo "  1. Check function logs in the terminal running 'func start'"
    echo "  2. Verify PAT credentials in local.settings.json"
    echo "  3. Test PATs manually with curl commands above"
else
    echo "  1. Review validation rules in function_app/validation.py"
    echo "  2. Check sample payload matches requirements"
    echo "  3. Review function logs for details"
fi
