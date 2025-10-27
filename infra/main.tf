# Azure DevOps → GitHub Spec Generation - Infrastructure
# Terraform configuration for Azure Function deployment

terraform {
  required_version = ">= 1.6.0"
  
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Resource Group (reuse existing or create new)
resource "azurerm_resource_group" "spec_automation" {
  count    = var.use_existing_resource_group ? 0 : 1
  name     = var.resource_group_name
  location = var.location
}

data "azurerm_resource_group" "existing" {
  count = var.use_existing_resource_group ? 1 : 0
  name  = var.resource_group_name
}

locals {
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.spec_automation[0].name
  resource_group_location = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.spec_automation[0].location
}

# Storage Account (required for Azure Functions)
resource "azurerm_storage_account" "function_storage" {
  name                     = var.storage_account_name
  resource_group_name      = local.resource_group_name
  location                 = local.resource_group_location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "SpecAutomation"
  }
}

# Service Plan (Consumption tier for cost efficiency)
resource "azurerm_service_plan" "function_plan" {
  name                = var.service_plan_name
  resource_group_name = local.resource_group_name
  location            = local.resource_group_location
  os_type             = "Linux"
  sku_name            = "Y1"  # Consumption plan
  
  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Linux Function App
resource "azurerm_linux_function_app" "spec_dispatcher" {
  name                       = var.function_app_name
  resource_group_name        = local.resource_group_name
  location                   = local.resource_group_location
  service_plan_id            = azurerm_service_plan.function_plan.id
  storage_account_name       = azurerm_storage_account.function_storage.name
  storage_account_access_key = azurerm_storage_account.function_storage.primary_access_key
  
  site_config {
    application_stack {
      python_version = "3.11"
    }
  }
  
  app_settings = {
    # GitHub configuration
    GITHUB_OWNER               = var.github_owner
    GITHUB_REPO                = var.github_repo
    GITHUB_WORKFLOW_FILENAME   = "spec-kit-specify.yml"
    
    # Azure DevOps configuration
    SPEC_COLUMN_NAME           = var.spec_column_name
    AI_USER_MATCH              = var.ai_user_match
    
    # Application configuration
    FUNCTIONS_WORKER_RUNTIME   = "python"
    LOG_LEVEL                  = var.log_level
    FUNCTION_TIMEOUT_SECONDS   = "30"
    
    # Secrets (placeholder - set via portal or Key Vault reference)
    # GH_WORKFLOW_DISPATCH_PAT = "@Microsoft.KeyVault(SecretUri=...)" # Set manually
    # ADO_WORK_ITEM_PAT        = "@Microsoft.KeyVault(SecretUri=...)" # Set manually
  }
  
  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "SpecAutomation"
  }
}
