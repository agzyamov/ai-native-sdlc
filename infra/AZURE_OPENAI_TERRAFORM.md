# Azure OpenAI Network ACLs - Terraform Management

## Overview

The Azure OpenAI Cognitive Services account (`ruste-mhinjxi0-eastus2`) is now managed via Terraform for network ACLs. This allows GitHub Actions to access Azure OpenAI without managing 5000+ IP ranges.

## Configuration

The configuration is in `infra/ai-foundry.tf`:
- **Network ACLs**: `default_action = "Allow"` (all IPs allowed, protected by API key)
- **Lifecycle**: Ignores changes to properties that would cause resource recreation

## First-Time Setup

### Step 1: Import Existing Resource

Before first apply, import the existing Azure OpenAI account into Terraform state:

```bash
cd infra

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Import the existing resource
terraform import azurerm_cognitive_account.openai_network \
  /subscriptions/$SUBSCRIPTION_ID/resourceGroups/aifoundry/providers/Microsoft.CognitiveServices/accounts/ruste-mhinjxi0-eastus2
```

### Step 2: Review Plan

```bash
terraform plan
```

Verify that Terraform will only update `network_acls` and not recreate the resource.

### Step 3: Apply Changes

```bash
terraform apply
```

This will update the network ACLs to allow all IPs (default_action = "Allow").

## Verification

After applying, verify the change:

```bash
az cognitiveservices account show \
  --name ruste-mhinjxi0-eastus2 \
  --resource-group aifoundry \
  --query "{defaultAction:properties.networkAcls.defaultAction, publicNetworkAccess:properties.publicNetworkAccess}" \
  -o json
```

Expected output:
```json
{
  "defaultAction": "Allow",
  "publicNetworkAccess": "Enabled"
}
```

## Security Note

The service is still protected by **API key authentication**. Allowing all IPs only removes the network firewall restriction - API keys are still required for access.

## Future Updates

To change network ACLs in the future, simply update `infra/ai-foundry.tf` and run:

```bash
cd infra
terraform plan
terraform apply
```

