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
  resource_group_name     = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.spec_automation[0].name
  resource_group_location = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.spec_automation[0].location
}

# Data source for existing VNet
data "azurerm_virtual_network" "existing" {
  name                = var.vnet_name
  resource_group_name = var.vnet_resource_group
}

data "azurerm_subnet" "function_subnet" {
  name                 = var.function_subnet_name
  virtual_network_name = var.vnet_name
  resource_group_name  = var.vnet_resource_group
}

data "azurerm_subnet" "private_endpoint_subnet" {
  name                 = var.private_endpoint_subnet_name
  virtual_network_name = var.vnet_name
  resource_group_name  = var.vnet_resource_group
}

# Storage Account (required for Azure Functions)
# SECURITY: Public access disabled, private endpoint required
resource "azurerm_storage_account" "function_storage" {
  name                     = var.storage_account_name
  resource_group_name      = local.resource_group_name
  location                 = local.resource_group_location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # CRITICAL: Disable public access
  public_network_access_enabled = var.enable_public_access

  # Network ACLs - deny by default, allow Azure services
  network_rules {
    default_action = "Deny"
    bypass         = ["AzureServices"]
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "SpecAutomation"
  }
}

# Service Plan (Elastic Premium for VNet integration and network isolation)
resource "azurerm_service_plan" "function_plan" {
  name                = var.service_plan_name
  resource_group_name = local.resource_group_name
  location            = local.resource_group_location
  os_type             = "Linux"
  sku_name            = var.service_plan_sku # Controlled by variable with validation

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Linux Function App
# SECURITY: VNet integrated, public access DISABLED (VPN-only)
resource "azurerm_linux_function_app" "spec_dispatcher" {
  name                       = var.function_app_name
  resource_group_name        = local.resource_group_name
  location                   = local.resource_group_location
  service_plan_id            = azurerm_service_plan.function_plan.id
  storage_account_name       = azurerm_storage_account.function_storage.name
  storage_account_access_key = azurerm_storage_account.function_storage.primary_access_key

  # CRITICAL: Disable public access (VPN-only)
  public_network_access_enabled = var.enable_public_access

  # VNet integration for outbound and inbound traffic
  virtual_network_subnet_id = data.azurerm_subnet.function_subnet.id

  site_config {
    # Route all traffic through VNet
    vnet_route_all_enabled = true

    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    # GitHub configuration
    GITHUB_OWNER             = var.github_owner
    GITHUB_REPO              = var.github_repo
    GITHUB_WORKFLOW_FILENAME = "spec-kit-specify.yml"

    # Azure DevOps configuration
    SPEC_COLUMN_NAME = var.spec_column_name
    AI_USER_MATCH    = var.ai_user_match

    # Application configuration
    FUNCTIONS_WORKER_RUNTIME = "python"
    LOG_LEVEL                = var.log_level
    FUNCTION_TIMEOUT_SECONDS = "30"

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

# Private Endpoint for Storage Account (blob)
# Allows Function to access storage via private network
resource "azurerm_private_endpoint" "storage_blob" {
  name                = "${var.storage_account_name}-blob-pe"
  resource_group_name = local.resource_group_name
  location            = local.resource_group_location
  subnet_id           = data.azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "${var.storage_account_name}-blob-psc"
    private_connection_resource_id = azurerm_storage_account.function_storage.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private Endpoint for Storage Account (file)
resource "azurerm_private_endpoint" "storage_file" {
  name                = "${var.storage_account_name}-file-pe"
  resource_group_name = local.resource_group_name
  location            = local.resource_group_location
  subnet_id           = data.azurerm_subnet.private_endpoint_subnet.id

  private_service_connection {
    name                           = "${var.storage_account_name}-file-psc"
    private_connection_resource_id = azurerm_storage_account.function_storage.id
    subresource_names              = ["file"]
    is_manual_connection           = false
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private DNS Zone for Storage Blob
resource "azurerm_private_dns_zone" "blob" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = local.resource_group_name

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private DNS Zone VNet Link
resource "azurerm_private_dns_zone_virtual_network_link" "blob" {
  name                  = "${var.vnet_name}-blob-link"
  resource_group_name   = local.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.blob.name
  virtual_network_id    = data.azurerm_virtual_network.existing.id

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private DNS Zone for Storage File
resource "azurerm_private_dns_zone" "file" {
  name                = "privatelink.file.core.windows.net"
  resource_group_name = local.resource_group_name

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Private DNS Zone VNet Link for File
resource "azurerm_private_dns_zone_virtual_network_link" "file" {
  name                  = "${var.vnet_name}-file-link"
  resource_group_name   = local.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.file.name
  virtual_network_id    = data.azurerm_virtual_network.existing.id

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
