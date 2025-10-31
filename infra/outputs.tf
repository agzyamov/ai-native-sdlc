# Terraform Outputs for Azure Functions Infrastructure (CAF Compliant)

output "function_name" {
  description = "Name of the deployed Azure Function App"
  value       = azurerm_linux_function_app.main.name
}

output "function_default_hostname" {
  description = "Default hostname of the Function App"
  value       = azurerm_linux_function_app.main.default_hostname
}

output "function_url" {
  description = "URL of the Function App"
  value       = "https://${azurerm_linux_function_app.main.default_hostname}"
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "function_identity_principal_id" {
  description = "Principal ID of the Function App's managed identity"
  value       = try(azurerm_linux_function_app.main.identity[0].principal_id, null)
  sensitive   = true
}

output "application_insights_name" {
  description = "Name of the Application Insights resource"
  value       = azurerm_application_insights.main.name
}

output "application_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_app_id" {
  description = "Application ID of Application Insights"
  value       = azurerm_application_insights.main.app_id
}

output "key_vault_uri" {
  description = "URI of the Key Vault for secrets management"
  value       = azurerm_key_vault.main.vault_uri
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics Workspace"
  value       = azurerm_log_analytics_workspace.main.id
}

output "vnet_id" {
  description = "ID of the Virtual Network"
  value       = azurerm_virtual_network.main.id
}

output "app_registration_client_id" {
  description = "Client ID of the Azure AD application for Teams Chat Agent"
  value       = azuread_application.teams_agent.client_id
}

output "app_registration_object_id" {
  description = "Object ID of the Azure AD application"
  value       = azuread_application.teams_agent.object_id
}

output "app_service_principal_object_id" {
  description = "Object ID of the service principal for the application"
  value       = azuread_service_principal.teams_agent_sp.object_id
}
