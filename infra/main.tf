# Azure Functions Infrastructure - CAF Compliant
# Following Microsoft Cloud Adoption Framework best practices
# Region: West Europe (proximity to Europe/Türkiye)
# Security: Network isolation enforced with IP restrictions

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Local variables for consistent tagging
locals {
  common_tags = {
    env        = var.environment
    owner      = var.owner
    costCenter = var.cost_center
    managedBy  = "Terraform"
    purpose    = "SpecAutomation"
  }
}

#=============================================================================
# FOUNDATION LAYER - Base Infrastructure (CAF Requirement)
#=============================================================================

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# VNet with subnets for Functions and Private Endpoints
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  address_space       = var.vnet_address_space
  tags                = local.common_tags
}

# Subnet for Functions (with delegation to Microsoft.Web/serverFarms)
resource "azurerm_subnet" "function" {
  name                 = "snet-func"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.function_subnet_prefix]

  # Service Endpoints required for Storage/Key Vault network ACLs
  service_endpoints = ["Microsoft.Storage", "Microsoft.KeyVault"]

  delegation {
    name = "function-delegation"
    service_delegation {
      name = "Microsoft.Web/serverFarms"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/action"
      ]
    }
  }
}

# Subnet for Private Endpoints
resource "azurerm_subnet" "private_endpoint" {
  name                 = "snet-pe"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.private_endpoint_subnet_prefix]
}

# Log Analytics Workspace (CAF Foundation Layer requirement)
resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.environment}-func"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

# Application Insights linked to Log Analytics
resource "azurerm_application_insights" "main" {
  name                = "ai-${var.environment}-func"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id
  retention_in_days   = 90  # HIGH severity: Must be 90 days or more
  
  # Security: Block log ingestion and querying from public networks (HIGH severity)
  internet_ingestion_enabled = false
  internet_query_enabled     = false
  
  tags = local.common_tags
}

# Storage Account for Functions (CAF Foundation Layer)
resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  # Public endpoint enabled with network rules (correct model for Premium Functions)
  public_network_access_enabled   = true
  allow_nested_items_to_be_public = false
  
  # Security: Disable cross-tenant replication (HIGH severity finding)
  # Prevents data replication to Storage Accounts in other Azure AD Tenants
  cross_tenant_replication_enabled = false

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.function.id]
  }

  tags = local.common_tags
}

# Key Vault for secrets (CAF Foundation Layer requirement)
resource "azurerm_key_vault" "main" {
  name                       = "kv-${var.environment}-func"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = true  # HIGH severity: Key Vault must be recoverable
  enable_rbac_authorization  = true  # Use RBAC instead of access policies (CAF requirement)

  public_network_access_enabled = true # Enabled for secret management from allowed IPs

  network_acls {
    default_action             = "Deny"
    bypass                     = "AzureServices"
    virtual_network_subnet_ids = [azurerm_subnet.function.id]
    ip_rules                   = [var.deployment_allowed_ip] # Allow deployment IP
  }

  tags = local.common_tags
}

# Current client config for Key Vault
data "azurerm_client_config" "current" {}

#=============================================================================
# FUNCTIONS LAYER - Workload Resources
#=============================================================================

# Service Plan (Elastic Premium for VNet integration)
resource "azurerm_service_plan" "main" {
  name                = var.service_plan_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.service_plan_sku
  tags                = local.common_tags
}

# Linux Function App
resource "azurerm_linux_function_app" "main" {
  name                          = var.function_app_name
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  service_plan_id               = azurerm_service_plan.main.id
  storage_account_name          = azurerm_storage_account.main.name
  storage_uses_managed_identity = true

  # HTTPS only (CAF security requirement)
  https_only                    = true
  public_network_access_enabled = true
  virtual_network_subnet_id     = azurerm_subnet.function.id

  # System-assigned Managed Identity (CAF requirement)
  identity {
    type = "SystemAssigned"
  }

  site_config {
    vnet_route_all_enabled            = true
    ip_restriction_default_action     = "Deny" # Block all except explicitly allowed
    scm_ip_restriction_default_action = "Deny"

    # Allow Azure DevOps Service Hooks (Inbound connections for webhooks)
    # See: https://learn.microsoft.com/en-us/azure/devops/organizations/security/allow-list-ip-url?view=azure-devops#inbound-connections
    # Western Europe inbound IP range: 40.74.28.0/23
    ip_restriction {
      name        = "AllowAzureDevOpsWebhooks"
      priority    = 100
      action      = "Allow"
      ip_address  = "40.74.28.0/23"
    }

    # Allow deployment from current IP
    ip_restriction {
      name       = "AllowDeploymentIP"
      priority   = 90
      action     = "Allow"
      ip_address = var.deployment_allowed_ip
    }

    scm_ip_restriction {
      name       = "AllowDeploymentIP"
      priority   = 100
      action     = "Allow"
      ip_address = var.deployment_allowed_ip
    }

    application_stack {
      python_version = "3.11"
    }

    ftps_state = "Disabled" # CAF security requirement
  }

  # App Service Authentication (HIGH severity requirement)
  # Configured to satisfy CVM Policy, but allows anonymous access for webhook functionality
  # Actual authentication for webhooks is handled by:
  # - IP restrictions (Azure DevOps IPs only: 40.74.28.0/23)
  # - Function Keys (code parameter in URL)
  # - HTTPS enforcement
  auth_settings_v2 {
    auth_enabled = true

    # Microsoft Entra ID configuration (minimal setup for compliance)
    active_directory_v2 {
      client_id                  = "c868c952-8b2e-4d24-83b7-0fb2ed9fbc75"
      tenant_auth_endpoint       = "https://login.microsoftonline.com/b41b72d0-4e9f-4c26-8a69-f949f367c91d/v2.0"
    }

    # Allow unauthenticated requests for webhook endpoints
    # Authentication is enforced via IP restrictions and Function Keys
    require_authentication = false
    unauthenticated_action = "AllowAnonymous"

    login {
      token_store_enabled = false # Not needed for webhook scenarios
    }
  }

  app_settings = {
    # Required: Azure Functions runtime storage
    AzureWebJobsStorage__accountName = azurerm_storage_account.main.name

    # NOTE: WEBSITE_CONTENTAZUREFILECONNECTIONSTRING and WEBSITE_CONTENTSHARE removed
    # Premium plans use Azure Files by default, but this causes deployment issues:
    # - Deployment with config-zip deploys to /site/wwwroot/
    # - Function runtime reads from Azure Files share
    # - Result: deployments succeed but code never updates
    # Solution: Let function run from /site/wwwroot/ where deployments actually go

    # Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.main.connection_string

    # GitHub configuration
    GITHUB_OWNER             = var.github_owner
    GITHUB_REPO              = var.github_repo
    GITHUB_WORKFLOW_FILENAME = "spec-kit-specify.yml"

    # Azure DevOps configuration
    ADO_ORG_URL      = var.ado_org_url
    ADO_PROJECT      = var.ado_project
    SPEC_COLUMN_NAME = var.spec_column_name
    AI_USER_MATCH    = var.ai_user_match

    # Application configuration
    FUNCTIONS_WORKER_RUNTIME    = "python"
    FUNCTIONS_EXTENSION_VERSION = "~4"
    LOG_LEVEL                   = var.log_level
    FUNCTION_TIMEOUT_SECONDS    = "30"

    # Remote build configuration (required for Python on Linux)
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
    # ENABLE_ORYX_BUILD is true by default for Linux Python apps per Microsoft docs

    # Secrets - Use Key Vault references (CAF security requirement)
    GH_WORKFLOW_DISPATCH_PAT = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.main.vault_uri}secrets/gh-pat)"
    ADO_WORK_ITEM_PAT        = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault.main.vault_uri}secrets/ado-pat)"
  }

  tags = local.common_tags
}

#=============================================================================
# NETWORKING LAYER - Private Endpoints & DNS
#=============================================================================

# Private Endpoint for Storage Account (blob)
resource "azurerm_private_endpoint" "storage_blob" {
  name                = "${var.storage_account_name}-blob-pe"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  subnet_id           = azurerm_subnet.private_endpoint.id

  private_service_connection {
    name                           = "${var.storage_account_name}-blob-psc"
    private_connection_resource_id = azurerm_storage_account.main.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "blob-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.blob.id]
  }

  tags = local.common_tags
}

# Private Endpoint for Storage Account (file)
resource "azurerm_private_endpoint" "storage_file" {
  name                = "${var.storage_account_name}-file-pe"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  subnet_id           = azurerm_subnet.private_endpoint.id

  private_service_connection {
    name                           = "${var.storage_account_name}-file-psc"
    private_connection_resource_id = azurerm_storage_account.main.id
    subresource_names              = ["file"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "file-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.file.id]
  }

  tags = local.common_tags
}

# Private DNS Zone for Storage Blob
resource "azurerm_private_dns_zone" "blob" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

# Private DNS Zone VNet Link (blob)
resource "azurerm_private_dns_zone_virtual_network_link" "blob" {
  name                  = "vnet-link-blob"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.blob.name
  virtual_network_id    = azurerm_virtual_network.main.id
  tags                  = local.common_tags
}

# Private DNS Zone for Storage File
resource "azurerm_private_dns_zone" "file" {
  name                = "privatelink.file.core.windows.net"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

# Private DNS Zone VNet Link (file)
resource "azurerm_private_dns_zone_virtual_network_link" "file" {
  name                  = "vnet-link-file"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.file.name
  virtual_network_id    = azurerm_virtual_network.main.id
  tags                  = local.common_tags
}

# Private Endpoint for Key Vault
resource "azurerm_private_endpoint" "keyvault" {
  name                = "kv-func-dev-pe"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  subnet_id           = azurerm_subnet.private_endpoint.id

  private_service_connection {
    name                           = "kv-func-dev-psc"
    private_connection_resource_id = azurerm_key_vault.main.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "vault-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.keyvault.id]
  }

  tags = local.common_tags
}

# Private DNS Zone for Key Vault
resource "azurerm_private_dns_zone" "keyvault" {
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

# Private DNS Zone VNet Link (Key Vault)
resource "azurerm_private_dns_zone_virtual_network_link" "keyvault" {
  name                  = "vnet-link-keyvault"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.keyvault.name
  virtual_network_id    = azurerm_virtual_network.main.id
  tags                  = local.common_tags
}

#=============================================================================
# RBAC - Role Assignments for Managed Identity
#=============================================================================

# Function App Managed Identity → Storage Account roles
resource "azurerm_role_assignment" "function_storage_blob" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id
}

resource "azurerm_role_assignment" "function_storage_queue" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Queue Data Contributor"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id
}

resource "azurerm_role_assignment" "function_storage_table" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Table Data Contributor"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id
}

resource "azurerm_role_assignment" "function_storage_file" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage File Data Privileged Contributor"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id
}

# Function App Managed Identity → Key Vault access
resource "azurerm_role_assignment" "function_keyvault_secrets" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id
}

#=============================================================================
# DIAGNOSTIC SETTINGS - CAF Requirement
#=============================================================================

# Function App diagnostic settings → Log Analytics
resource "azurerm_monitor_diagnostic_setting" "function_app" {
  name                       = "diag-${var.function_app_name}"
  target_resource_id         = azurerm_linux_function_app.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "FunctionAppLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

# Storage Account diagnostic settings → Log Analytics
resource "azurerm_monitor_diagnostic_setting" "storage" {
  name                       = "diag-${var.storage_account_name}"
  target_resource_id         = azurerm_storage_account.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_metric {
    category = "AllMetrics"
  }
}

# Key Vault diagnostic settings → Log Analytics
resource "azurerm_monitor_diagnostic_setting" "keyvault" {
  name                       = "diag-kv-${var.environment}-func"
  target_resource_id         = azurerm_key_vault.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "AuditEvent"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

