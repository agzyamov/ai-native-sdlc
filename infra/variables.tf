# Terraform Variables for Spec Automation Infrastructure

variable "cleanup_enabled" {
  description = "Enable cleanup of old AI/ML resources. Set to true to allow data sources to query resources for deletion."
  type        = bool
  default     = false
}

variable "resource_group_name" {
  description = "Name of the Azure resource group following CAF naming: rg-func-{env}"
  type        = string
  default     = "rg-func-dev"
}

variable "use_existing_resource_group" {
  description = "Whether to use an existing resource group instead of creating new one. Set to true if resource group already exists."
  type        = bool
  default     = false
}

variable "location" {
  description = "Azure region for resources. Default is westeurope per CAF guidelines for proximity to Europe/Türkiye."
  type        = string
  default     = "westeurope"
}

variable "storage_account_name" {
  description = "Name of the storage account following CAF naming: stfunc<env><random> (must be globally unique, 3-24 lowercase alphanumeric). Required for Azure Functions runtime."
  type        = string
  default     = "stfuncdevspec001"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "service_plan_name" {
  description = "Name of the Azure Service Plan following CAF naming: <type>-<env>-<suffix>"
  type        = string
  default     = "asp-dev-spec"
}

variable "service_plan_sku" {
  description = "SKU for Azure Service Plan. MUST be Premium (EP1/EP2/EP3) for network isolation. Consumption (Y1) is NOT allowed."
  type        = string
  default     = "EP1"

  validation {
    condition     = can(regex("^(EP1|EP2|EP3)$", var.service_plan_sku))
    error_message = "SECURITY POLICY VIOLATION: service_plan_sku must be EP1, EP2, or EP3 (Elastic Premium). Consumption plan (Y1) does NOT support network isolation and is FORBIDDEN."
  }
}

variable "function_app_name" {
  description = "Name of the Azure Function App following CAF naming: func-<env>-<name> (must be globally unique). This will be part of the function URL."
  type        = string
  default     = "func-dev-dispatch"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,60}$", var.function_app_name))
    error_message = "Function app name must be 2-60 lowercase alphanumeric characters or hyphens."
  }
}

variable "github_owner" {
  description = "GitHub repository owner (organization or user). Example: 'agzyamov'"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name. Example: 'ai-native-sdlc'"
  type        = string
}

variable "ado_org_url" {
  description = "Azure DevOps organization URL. Example: 'https://dev.azure.com/yourorg'"
  type        = string
}

variable "ado_project" {
  description = "Azure DevOps project name. Example: 'YourProject'"
  type        = string
}

variable "spec_column_name" {
  description = "Azure DevOps board column name that triggers spec generation. Must match board configuration exactly."
  type        = string
  default     = "Specification"
}

variable "ai_user_match" {
  description = "Azure DevOps user display name for AI Teammate (case-insensitive match). Example: 'AI Teammate'"
  type        = string
  default     = "AI Teammate"
}

variable "log_level" {
  description = "Logging level (DEBUG, INFO, WARNING, ERROR). Use DEBUG for troubleshooting, INFO for normal operation."
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

variable "deployment_allowed_ip" {
  description = "Your current public IP address for deployment access (CIDR format, e.g., 176.233.31.83/32). Run scripts/update-deployment-ip.sh to update."
  type        = string
  default     = "0.0.0.0/32" # Placeholder - run update script
}

variable "environment" {
  description = "Environment tag (dev, staging, prod). Used for resource tagging and cost tracking."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "owner" {
  description = "Owner tag for cost tracking and resource management per CAF guidelines."
  type        = string
  default     = "platform-team"
}

variable "cost_center" {
  description = "Cost center tag for billing allocation per CAF guidelines."
  type        = string
  default     = "engineering"
}

# Network Configuration (CAF Foundation Layer)

variable "vnet_address_space" {
  description = "Address space for VNet following CAF guidelines."
  type        = list(string)
  default     = ["10.1.0.0/16"]
}

variable "function_subnet_prefix" {
  description = "Address prefix for Functions subnet (snet-func)."
  type        = string
  default     = "10.1.1.0/24"
}

variable "private_endpoint_subnet_prefix" {
  description = "Address prefix for Private Endpoints subnet (snet-pe)."
  type        = string
  default     = "10.1.2.0/24"
}

variable "enable_public_access" {
  description = "Enable public network access endpoint. REQUIRED=true for Premium Functions file share with VNet. Security enforced via network_rules.default_action=Deny + VNet allowlist."
  type        = bool
  default     = true

  # Note: publicNetworkAccess=true with defaultAction=Deny is the CORRECT security model
  # for Premium Functions with VNet integration. Setting to false blocks file share access
  # even with VNet integration, causing function startup failures.
  # Actual security is enforced by:
  #  1. network_rules.default_action = "Deny" (blocks all public traffic by default)
  #  2. network_rules.virtualNetworkRules (allow only specific subnets)
  # 3. Private endpoints for blob/file (for additional security)
}

# Application Registration Variables
variable "app_display_name" {
  description = "Display name for Azure AD application registration used by Teams Chat Agent"
  type        = string
  default     = "teams-chat-agent"
}

variable "app_redirect_urls" {
  description = "List of redirect URIs for public client / web auth flows (add http://localhost for dev)"
  type        = list(string)
  default     = ["http://localhost"]
}
