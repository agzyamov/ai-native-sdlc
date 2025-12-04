#!/bin/bash
# Diagnose why GitHub Actions workflow is not being triggered

FUNCTION_NAME="${1:-func-dev-dispatch}"
RESOURCE_GROUP="${2:-rg-spec-automation}"

echo "=========================================="
echo "GitHub Dispatch Diagnostic Tool"
echo "=========================================="
echo ""

# 1. Check Azure Function logs
echo "1️⃣  Checking Azure Function Logs..."
echo "---"
echo "Function: $FUNCTION_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo ""

if command -v az &> /dev/null; then
    echo "📋 Recent function logs (searching for dispatch errors):"
    az functionapp log tail \
        --name "$FUNCTION_NAME" \
        --resource-group "$RESOURCE_GROUP" 2>/dev/null | \
        grep -i -E "(dispatch|github|workflow|failed|error)" | tail -n 20 || \
    echo "   (Could not tail logs - check Azure Portal manually)"
    echo ""
    
    echo "💡 To view full logs:"
    echo "   Azure Portal → Function App → $FUNCTION_NAME → Log stream"
    echo "   Or: Azure Portal → Application Insights → Query logs"
    echo ""
else
    echo "⚠️  Azure CLI not installed. Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    echo ""
fi

# 2. Check GitHub configuration
echo "2️⃣  Checking GitHub Configuration..."
echo "---"
echo "Expected values:"
echo "  GITHUB_OWNER: agzyamov"
echo "  GITHUB_REPO: ai-native-sdlc"
echo "  GITHUB_WORKFLOW_FILENAME: spec-kit-specify.yml"
echo "  GITHUB_WORKFLOW_REF: main"
echo "  GH_WORKFLOW_DISPATCH_PAT: (should be set in Azure)"
echo ""

if command -v az &> /dev/null; then
    echo "📋 Current Azure Function settings:"
    az functionapp config appsettings list \
        --name "$FUNCTION_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name=='GITHUB_OWNER' || name=='GITHUB_REPO' || name=='GITHUB_WORKFLOW_FILENAME' || name=='GITHUB_WORKFLOW_REF' || name=='GH_WORKFLOW_DISPATCH_PAT'].{Name:name, Value:value}" \
        --output table 2>/dev/null || echo "   (Could not fetch settings)"
    echo ""
fi

# 3. Test GitHub API directly
echo "3️⃣  Testing GitHub API Access..."
echo "---"
echo "GitHub API URL:"
echo "  https://api.github.com/repos/agzyamov/ai-native-sdlc/actions/workflows/spec-kit-specify.yml/dispatches"
echo ""
echo "To test manually (replace YOUR_PAT):"
echo "  curl -X POST \\"
echo "    -H 'Authorization: Bearer YOUR_PAT' \\"
echo "    -H 'Accept: application/vnd.github+json' \\"
echo "    -H 'X-GitHub-Api-Version: 2022-11-28' \\"
echo "    https://api.github.com/repos/agzyamov/ai-native-sdlc/actions/workflows/spec-kit-specify.yml/dispatches \\"
echo "    -d '{\"ref\":\"main\",\"inputs\":{\"work_item_id\":\"615\",\"feature_description\":\"test\",\"create_branch\":\"true\"}}'"
echo ""

# 4. Common issues checklist
echo "4️⃣  Common Issues Checklist:"
echo "---"
echo "□ GitHub PAT expired or invalid"
echo "□ GitHub PAT missing 'actions:write' permission"
echo "□ GitHub PAT missing 'contents:read' permission"
echo "□ Workflow file 'spec-kit-specify.yml' doesn't exist"
echo "□ Workflow file is in wrong location (.github/workflows/)"
echo "□ Workflow doesn't have 'workflow_dispatch' trigger"
echo "□ Branch 'main' doesn't exist"
echo "□ Workflow inputs don't match (work_item_id, feature_description, create_branch)"
echo "□ Network/firewall blocking outbound calls to api.github.com"
echo ""

# 5. Check workflow file exists
echo "5️⃣  Verifying Workflow File..."
echo "---"
if [ -f ".github/workflows/spec-kit-specify.yml" ]; then
    echo "✅ Workflow file exists locally: .github/workflows/spec-kit-specify.yml"
    if grep -q "workflow_dispatch" .github/workflows/spec-kit-specify.yml; then
        echo "✅ Workflow has 'workflow_dispatch' trigger"
    else
        echo "❌ Workflow MISSING 'workflow_dispatch' trigger!"
        echo "   Add this to the workflow file:"
        echo "   on:"
        echo "     workflow_dispatch:"
        echo "       inputs:"
        echo "         work_item_id:"
        echo "           ..."
    fi
else
    echo "⚠️  Workflow file not found locally (may still exist in GitHub)"
fi
echo ""

# 6. Error codes reference
echo "6️⃣  Error Code Reference:"
echo "---"
echo "HTTP 204 = Success (workflow dispatched)"
echo "HTTP 401 = Unauthorized (PAT expired/invalid)"
echo "HTTP 403 = Forbidden (PAT missing permissions or workflow not found)"
echo "HTTP 404 = Not Found (workflow file doesn't exist)"
echo "HTTP 422 = Validation Error (wrong inputs or branch doesn't exist)"
echo ""

echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Check Azure Portal → Function App → Log stream for recent errors"
echo "2. Check Application Insights for detailed error messages"
echo "3. Verify GitHub PAT has correct permissions"
echo "4. Test GitHub API call manually with curl (see above)"
echo "5. Check GitHub Actions → Workflows → spec-kit-specify.yml exists"
echo ""

