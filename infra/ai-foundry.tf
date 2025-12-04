# AI Foundry Layer - Azure OpenAI Configuration
# 
# Manages network ACLs for existing Azure OpenAI Cognitive Services account
# NOTE: The account uses kind="AIServices" which Terraform azurerm provider doesn't support
# We use null_resource with Azure REST API to manage network ACLs
# 
# Existing Cognitive Services accounts:
# - ruste-mhinjxi0-eastus2 (eastus2, aifoundry RG) - Azure OpenAI
# - aifoundry275872280917-resource (germanywestcentral, AIFoundry RG)

# Variable for network ACL default action
variable "azure_openai_network_default_action" {
  description = "Default action for Azure OpenAI network ACLs. Use 'Allow' to enable GitHub Actions access."
  type        = string
  default     = "Allow"
  validation {
    condition     = contains(["Allow", "Deny"], var.azure_openai_network_default_action)
    error_message = "default_action must be either 'Allow' or 'Deny'."
  }
}

# Manage network ACLs for Azure OpenAI via Azure REST API
# This allows GitHub Actions and other services to access Azure OpenAI
resource "null_resource" "openai_network_acls" {
  triggers = {
    default_action = var.azure_openai_network_default_action
    # Re-run if subscription or resource changes
    subscription_id = data.azurerm_client_config.current.subscription_id
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -e
      
      RESOURCE_ID="/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/aifoundry/providers/Microsoft.CognitiveServices/accounts/ruste-mhinjxi0-eastus2"
      
      # Get access token
      ACCESS_TOKEN=$(az account get-access-token --query accessToken -o tsv)
      
      # Update network ACLs using PATCH (only updates specified properties)
      PATCH_BODY=$(echo '{}' | jq --arg action "${var.azure_openai_network_default_action}" '.properties.networkAcls = {
        "defaultAction": $action,
        "ipRules": [],
        "virtualNetworkRules": []
      }')
      
      az rest --method PATCH \
        --uri "https://management.azure.com$${RESOURCE_ID}?api-version=2025-06-01" \
        --headers "Authorization=Bearer $ACCESS_TOKEN" \
        --headers "Content-Type=application/json" \
        --body "$PATCH_BODY" \
        -o json > /dev/null
      
      echo "✅ Updated Azure OpenAI network ACLs: defaultAction=${var.azure_openai_network_default_action}"
    EOT
  }
}

#=============================================================================
# AI FOUNDRY WORKSPACE - Future Expansion
#=============================================================================

# Placeholder: Azure AI Foundry (AI Hub) Workspace
# resource "azurerm_machine_learning_workspace" "ai_hub" {
#   name                    = "aihub-${var.environment}-spec"
#   resource_group_name     = azurerm_resource_group.main.name
#   location                = azurerm_resource_group.main.location
#   application_insights_id = azurerm_application_insights.main.id
#   key_vault_id            = azurerm_key_vault.main.id
#   storage_account_id      = azurerm_storage_account.main.id
#   
#   identity {
#     type = "SystemAssigned"
#   }
#   
#   tags = local.common_tags
# }

# Placeholder: Private Endpoint for AI Foundry
# resource "azurerm_private_endpoint" "ai_foundry" {
#   name                = "pe-aihub-${var.environment}"
#   resource_group_name = azurerm_resource_group.main.name
#   location            = azurerm_resource_group.main.location
#   subnet_id           = azurerm_subnet.private_endpoint.id
#   
#   private_service_connection {
#     name                           = "psc-aihub-${var.environment}"
#     private_connection_resource_id = azurerm_machine_learning_workspace.ai_hub.id
#     subresource_names              = ["amlworkspace"]
#     is_manual_connection           = false
#   }
#   
#   tags = local.common_tags
# }

# Placeholder: Role assignment for AI Foundry to access Key Vault
# resource "azurerm_role_assignment" "ai_foundry_keyvault" {
#   scope                = azurerm_key_vault.main.id
#   role_definition_name = "Key Vault Secrets User"
#   principal_id         = azurerm_machine_learning_workspace.ai_hub.identity[0].principal_id
# }

# Placeholder: Role assignment for AI Foundry to access Storage
# resource "azurerm_role_assignment" "ai_foundry_storage" {
#   scope                = azurerm_storage_account.main.id
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = azurerm_machine_learning_workspace.ai_hub.identity[0].principal_id
# }

# Placeholder: Diagnostic settings for AI Foundry
# resource "azurerm_monitor_diagnostic_setting" "ai_foundry" {
#   name                       = "diag-aihub-${var.environment}"
#   target_resource_id         = azurerm_machine_learning_workspace.ai_hub.id
#   log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
#   
#   enabled_log {
#     category = "AmlComputeClusterEvent"
#   }
#   
#   metric {
#     category = "AllMetrics"
#   }
# }
