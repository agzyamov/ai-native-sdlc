#!/bin/bash
# Cleanup Script - Remove Unused AI/ML Resources
# This script deletes resources that are not needed for the Azure Functions landing zone

set -euo pipefail

echo "======================================"
echo "Azure Resources Cleanup Script"
echo "======================================"
echo ""
echo "This script will DELETE the following resources:"
echo ""
echo "Individual Resources in rg-ai-agents-infra-dev:"
echo "  - ai-ai-agents-infra-dev (Application Insights)"
echo "  - kv-aiagents-dev-efee (Key Vault)"
echo "  - staiagentsinfradevgv7x (Storage Account)"
echo "  - craiagentsinfradev5kcj (Container Registry)"
echo "  - ai-aiagentsinfradevq8ry (Cognitive Services)"
echo "  - hub-ai-agents-infra-dev (ML Workspace Hub)"
echo "  - ai-project-ai-agents-infra-dev (ML Workspace Project)"
echo "  - aci-ado-mcp-dev (Container Instance)"
echo "  - id-mcp-dev (Managed Identity)"
echo "  - nsg-ai-dev (Network Security Group)"
echo "  - All related private endpoints and DNS zones"
echo ""
echo "Entire Resource Groups:"
echo "  - ai-agents"
echo "  - myResourceGroup"
echo "  - rustemfuncapp"
echo "  - rg-ado-agent-swedencentral"
echo "  - All rg-Rustem_Agziamov-* groups"
echo "  - All rg-Aleksei_Tolstov-* groups"
echo ""
echo "Resources that will be KEPT:"
echo "  - vnet-ai-agents-infra-dev (VNet)"
echo "  - vpngw-dev (VPN Gateway)"
echo "  - All subnets"
echo "  - Everything in rg-spec-automation"
echo ""

read -p "Are you sure you want to proceed? Type 'DELETE' to confirm: " confirmation

if [ "$confirmation" != "DELETE" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup process..."
echo ""

# Function to check if resource exists
resource_exists() {
    az resource show --ids "$1" &>/dev/null
}

# Function to delete resource with error handling
delete_resource() {
    local resource_id="$1"
    local resource_name="$2"
    
    if resource_exists "$resource_id"; then
        echo "Deleting $resource_name..."
        if az resource delete --ids "$resource_id" --verbose 2>&1 | tee /tmp/cleanup_log.txt; then
            echo "✓ Deleted $resource_name"
        else
            echo "✗ Failed to delete $resource_name - check /tmp/cleanup_log.txt"
        fi
    else
        echo "⊘ $resource_name does not exist (already deleted or not found)"
    fi
}

# 1. Delete Container Instance first (dependencies)
echo "=== Phase 1: Container Instances ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.ContainerInstance/containerGroups/aci-ado-mcp-dev" "Container Instance (aci-ado-mcp-dev)"

# 2. Delete ML Workspaces (must be deleted before dependencies)
echo ""
echo "=== Phase 2: ML Workspaces ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.MachineLearningServices/workspaces/ai-project-ai-agents-infra-dev" "ML Project Workspace"
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.MachineLearningServices/workspaces/hub-ai-agents-infra-dev" "ML Hub Workspace"

# 3. Delete AI Foundry Project (nested in Cognitive Services)
echo ""
echo "=== Phase 3: AI Foundry Project ==="
if az cognitiveservices account show --name ai-aiagentsinfradevq8ry --resource-group rg-ai-agents-infra-dev &>/dev/null; then
    echo "Checking for AI Foundry projects..."
    # List and delete any projects under the Cognitive Services account
    for project in $(az rest --method GET --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.CognitiveServices/accounts/ai-aiagentsinfradevq8ry/projects?api-version=2023-10-01-preview" --query "value[].name" -o tsv 2>/dev/null || echo ""); do
        if [ -n "$project" ]; then
            echo "Deleting AI Foundry project: $project"
            az rest --method DELETE --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.CognitiveServices/accounts/ai-aiagentsinfradevq8ry/projects/$project?api-version=2023-10-01-preview" || echo "Failed to delete project $project"
        fi
    done
else
    echo "⊘ Cognitive Services account does not exist"
fi

# 4. Delete Cognitive Services
echo ""
echo "=== Phase 4: Cognitive Services ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.CognitiveServices/accounts/ai-aiagentsinfradevq8ry" "Cognitive Services Account"

# 5. Delete Private Endpoints (for resources we're deleting)
echo ""
echo "=== Phase 5: Private Endpoints ==="
for pe in $(az network private-endpoint list --resource-group rg-ai-agents-infra-dev --query "[?contains(name, 'search') || contains(name, 'acr')].id" -o tsv); do
    delete_resource "$pe" "Private Endpoint $(basename $pe)"
done

# 6. Delete Container Registry
echo ""
echo "=== Phase 6: Container Registry ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.ContainerRegistry/registries/craiagentsinfradev5kcj" "Container Registry"

# 7. Delete Storage Account (AI/ML)
echo ""
echo "=== Phase 7: Storage Account ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.Storage/storageAccounts/staiagentsinfradevgv7x" "Storage Account (AI/ML)"

# 8. Delete Key Vault (soft-delete protection may apply)
echo ""
echo "=== Phase 8: Key Vault ==="
if az keyvault show --name kv-aiagents-dev-efee &>/dev/null; then
    echo "Deleting Key Vault..."
    az keyvault delete --name kv-aiagents-dev-efee --resource-group rg-ai-agents-infra-dev
    echo "Purging Key Vault (removing soft-delete protection)..."
    az keyvault purge --name kv-aiagents-dev-efee || echo "Note: Purge may require additional permissions or time"
    echo "✓ Deleted Key Vault"
else
    echo "⊘ Key Vault does not exist"
fi

# 9. Delete Application Insights
echo ""
echo "=== Phase 9: Application Insights ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/microsoft.insights/components/ai-ai-agents-infra-dev" "Application Insights"

# 10. Delete Managed Identity
echo ""
echo "=== Phase 10: Managed Identity ==="
delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-mcp-dev" "Managed Identity"

# 11. Delete VNet Links from Private DNS Zones (nested resources)
echo ""
echo "=== Phase 11: Private DNS Zone VNet Links ==="
for zone in "privatelink.api.azureml.ms" "privatelink.notebooks.azure.net" "privatelink.search.windows.net" "privatelink.azurecr.io" "ado-mcp.dev.local" "privatelink.monitor.azure.com"; do
    if az network private-dns zone show --name "$zone" --resource-group rg-ai-agents-infra-dev &>/dev/null; then
        echo "Removing VNet links from DNS Zone: $zone"
        for link in $(az network private-dns link vnet list --zone-name "$zone" --resource-group rg-ai-agents-infra-dev --query "[].name" -o tsv); do
            echo "  Deleting link: $link"
            az network private-dns link vnet delete --name "$link" --zone-name "$zone" --resource-group rg-ai-agents-infra-dev --yes
        done
    fi
done

# 12. Delete Private DNS Zones (for deleted resources)
echo ""
echo "=== Phase 12: Private DNS Zones (ML/Search/ACR) ==="
for zone in "privatelink.api.azureml.ms" "privatelink.notebooks.azure.net" "privatelink.search.windows.net" "privatelink.azurecr.io" "ado-mcp.dev.local" "privatelink.monitor.azure.com"; do
    if az network private-dns zone show --name "$zone" --resource-group rg-ai-agents-infra-dev &>/dev/null; then
        echo "Deleting DNS Zone: $zone"
        az network private-dns zone delete --name "$zone" --resource-group rg-ai-agents-infra-dev --yes
        echo "✓ Deleted $zone"
    else
        echo "⊘ DNS Zone $zone does not exist"
    fi
done

# 11. Delete VNet Links from Private DNS Zones (nested resources)
echo ""
echo "=== Phase 11: Private DNS Zone VNet Links ==="
for zone in "privatelink.api.azureml.ms" "privatelink.notebooks.azure.net" "privatelink.search.windows.net" "privatelink.azurecr.io" "ado-mcp.dev.local" "privatelink.monitor.azure.com"; do
    if az network private-dns zone show --name "$zone" --resource-group rg-ai-agents-infra-dev &>/dev/null; then
        echo "Removing VNet links from DNS Zone: $zone"
        for link in $(az network private-dns link vnet list --zone-name "$zone" --resource-group rg-ai-agents-infra-dev --query "[].name" -o tsv); do
            echo "  Deleting link: $link"
            az network private-dns link vnet delete --name "$link" --zone-name "$zone" --resource-group rg-ai-agents-infra-dev --yes
        done
    fi
done

# 12. Delete Private DNS Zones (for deleted resources)
echo ""
echo "=== Phase 12: Private DNS Zones (ML/Search/ACR) ==="
for zone in "privatelink.api.azureml.ms" "privatelink.notebooks.azure.net" "privatelink.search.windows.net" "privatelink.azurecr.io" "ado-mcp.dev.local" "privatelink.monitor.azure.com"; do
    if az network private-dns zone show --name "$zone" --resource-group rg-ai-agents-infra-dev &>/dev/null; then
        echo "Deleting DNS Zone: $zone"
        az network private-dns zone delete --name "$zone" --resource-group rg-ai-agents-infra-dev --yes
        echo "✓ Deleted $zone"
    else
        echo "⊘ DNS Zone $zone does not exist"
    fi
done

# 13. Delete Network Security Group (if not in use)
echo ""
echo "=== Phase 13: Network Security Group ==="
# First check if NSG is attached to any subnet
nsg_attached=$(az network vnet subnet list --resource-group rg-ai-agents-infra-dev --vnet-name vnet-ai-agents-infra-dev --query "[?networkSecurityGroup.id && contains(networkSecurityGroup.id, 'nsg-ai-dev')].name" -o tsv)
if [ -n "$nsg_attached" ]; then
    echo "⚠ NSG nsg-ai-dev is attached to subnet(s): $nsg_attached"
    echo "  Skipping deletion. Manually detach first if not needed."
else
    delete_resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-ai-agents-infra-dev/providers/Microsoft.Network/networkSecurityGroups/nsg-ai-dev" "Network Security Group"
fi

# 14. Delete entire resource groups
echo ""
echo "=== Phase 14: Resource Groups ==="

delete_group() {
    local group="$1"
    if az group exists --name "$group" | grep -q true; then
        echo "Deleting resource group: $group"
        az group delete --name "$group" --yes --no-wait
        echo "✓ Initiated deletion of $group (running in background)"
    else
        echo "⊘ Resource group $group does not exist"
    fi
}

delete_group "ai-agents"
delete_group "myResourceGroup"
delete_group "rustemfuncapp"
delete_group "rg-ado-agent-swedencentral"

# Find and delete all rg-Rustem_Agziamov-* groups
echo ""
echo "Searching for rg-Rustem_Agziamov-* resource groups..."
for group in $(az group list --query "[?starts_with(name, 'rg-Rustem_Agziamov-')].name" -o tsv); do
    delete_group "$group"
done

# Skip rg-Aleksei_Tolstov-* groups (keeping for other team member)
echo ""
echo "⊘ Skipping rg-Aleksei_Tolstov-* resource groups (preserved for team member)"

echo ""
echo "======================================"
echo "Cleanup Complete!"
echo "======================================"
echo ""
echo "Note: Resource group deletions are running in the background."
echo "To check status, run:"
echo "  az group list --query \"[?properties.provisioningState=='Deleting'].name\" -o table"
echo ""
echo "Kept resources:"
echo "  ✓ vnet-ai-agents-infra-dev"
echo "  ✓ vpngw-dev"
echo "  ✓ All resources in rg-spec-automation"
