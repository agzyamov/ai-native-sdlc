# Terraform Outputs for Spec Automation Infrastructure

output "function_name" {
  description = "Name of the deployed Azure Function App"
  value       = azurerm_linux_function_app.spec_dispatcher.name
}

output "function_default_hostname" {
  description = "Default hostname for the Azure Function (HTTPS URL)"
  value       = azurerm_linux_function_app.spec_dispatcher.default_hostname
}

output "function_url" {
  description = "Full HTTPS URL for the Azure Function"
  value       = "https://${azurerm_linux_function_app.spec_dispatcher.default_hostname}"
}

output "resource_group_name" {
  description = "Name of the resource group containing all resources"
  value       = local.resource_group_name
}

output "storage_account_name" {
  description = "Name of the storage account used by the function"
  value       = azurerm_storage_account.function_storage.name
}

output "function_identity_principal_id" {
  description = "Principal ID of the function's managed identity (if enabled)"
  value       = try(azurerm_linux_function_app.spec_dispatcher.identity[0].principal_id, null)
}
