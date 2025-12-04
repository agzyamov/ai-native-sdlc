# AI Foundry Layer - Future Expansion (CAF Requirement)
# This file contains placeholders for Azure AI Foundry (AI Hub) workspace
# 
# NOTE: Cognitive Services accounts (AIServices kind) are NOT managed by Terraform
# because they cannot be imported without recreation (kind change forces replacement).
# They must be configured manually via Azure Portal for network restrictions.
# 
# Existing Cognitive Services accounts:
# - ruste-mhinjxi0-eastus2 (eastus2, aifoundry RG)
# - aifoundry275872280917-resource (germanywestcentral, AIFoundry RG)
# 
# HIGH SEVERITY: Configure network restrictions manually via Azure Portal:
# 1. Go to Azure Portal → Cognitive Services account
# 2. Navigate to "Networking" in left menu
# 3. Under "Firewalls and virtual networks":
#    - Select "Selected networks and private endpoints"
#    - Add your IP address to "Firewall" section
#    - Set "Allow access from selected networks" (default action Deny)
# 4. Save changes
#
# Or use Azure CLI:
# 1. Add IP rule:
#    az cognitiveservices account network-rule add \
#      --name ruste-mhinjxi0-eastus2 \
#      --resource-group aifoundry \
#      --ip-address 176.233.30.114
#
# 2. Set default action (via az resource):
#    az resource update \
#      --ids /subscriptions/.../Microsoft.CognitiveServices/accounts/ruste-mhinjxi0-eastus2 \
#      --set properties.networkAcls.defaultAction=Deny
#
# NOTE: Network ACLs may cause errors with apiProperties. Configure via Portal if CLI fails.

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
