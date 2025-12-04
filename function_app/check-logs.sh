#!/bin/bash
# Check Azure Function logs for dispatch errors

FUNCTION_NAME="${1:-func-dev-dispatch}"
RESOURCE_GROUP="${2:-rg-spec-automation}"

echo "=== Checking Azure Function Logs ==="
echo "Function: $FUNCTION_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo ""

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "📋 Recent function execution logs (last 50 lines):"
echo "---"
az functionapp log tail \
    --name "$FUNCTION_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --output table 2>/dev/null || \
az webapp log tail \
    --name "$FUNCTION_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --output table 2>/dev/null || \
echo "⚠️  Could not tail logs. Try checking Application Insights instead."
echo ""

echo "📊 Checking Application Insights logs..."
echo "   Go to: https://portal.azure.com → Application Insights → $FUNCTION_NAME → Logs"
echo ""

echo "🔍 Quick check - Recent errors:"
az monitor app-insights query \
    --app "$FUNCTION_NAME" \
    --analytics-query "traces | where timestamp > ago(1h) | where severityLevel >= 3 | project timestamp, message | order by timestamp desc | take 10" \
    --output table 2>/dev/null || \
echo "   (Application Insights query requires app ID. Check portal manually)"
echo ""

echo "💡 To view logs manually:"
echo "   1. Azure Portal → Function App → $FUNCTION_NAME → Log stream"
echo "   2. Azure Portal → Application Insights → Query logs"
echo "   3. Search for: 'Dispatch failed' or 'Failed to dispatch workflow'"
echo ""

