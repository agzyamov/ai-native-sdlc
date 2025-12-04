#!/bin/bash
# Script to update Azure OpenAI firewall to allow all networks
# This uses Azure REST API to bypass CLI limitations with Cognitive Services

set -e

RESOURCE_GROUP="aifoundry"
ACCOUNT_NAME="ruste-mhinjxi0-eastus2"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo "🔧 Updating Azure OpenAI firewall to allow all networks..."
echo "   Account: $ACCOUNT_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo ""

# Get access token
ACCESS_TOKEN=$(az account get-access-token --query accessToken -o tsv)

# Get current resource
RESOURCE_ID="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$ACCOUNT_NAME"

echo "📡 Fetching current configuration..."
CURRENT_CONFIG=$(az rest --method GET \
  --uri "https://management.azure.com$RESOURCE_ID?api-version=2024-06-01" \
  --headers "Authorization=Bearer $ACCESS_TOKEN" \
  -o json)

# Extract current networkAcls and update defaultAction
echo "✏️  Updating defaultAction to 'Allow'..."

# Use jq to update the configuration
UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | jq --argjson networkAcls '{
  "defaultAction": "Allow",
  "ipRules": [],
  "virtualNetworkRules": []
}' '.properties.networkAcls = $networkAcls')

# Update via REST API
echo "💾 Saving changes..."
az rest --method PATCH \
  --uri "https://management.azure.com$RESOURCE_ID?api-version=2024-06-01" \
  --headers "Authorization=Bearer $ACCESS_TOKEN" \
  --headers "Content-Type=application/json" \
  --body "$UPDATED_CONFIG" \
  -o json > /dev/null

echo ""
echo "✅ Successfully updated firewall to allow all networks!"
echo ""
echo "Verifying change..."
az cognitiveservices account show \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "{defaultAction:properties.networkAcls.defaultAction, publicNetworkAccess:properties.publicNetworkAccess}" \
  -o json

echo ""
echo "🎉 Azure OpenAI is now accessible from GitHub Actions (and all IPs)."
echo "   The service is still protected by API key authentication."

