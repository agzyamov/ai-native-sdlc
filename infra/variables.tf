# Terraform Variables for Spec Automation Infrastructure

variable "resource_group_name" {
  description = "Name of the Azure resource group (new or existing). Used to organize all spec automation resources."
  type        = string
  default     = "rg-spec-automation"
}

variable "use_existing_resource_group" {
  description = "Whether to use an existing resource group instead of creating new one. Set to true if resource group already exists."
  type        = bool
  default     = false
}

variable "location" {
  description = "Azure region for resources. Choose region closest to your team for best performance."
  type        = string
  default     = "eastus"
}

variable "storage_account_name" {
  description = "Name of the storage account (must be globally unique, 3-24 lowercase alphanumeric). Required for Azure Functions runtime."
  type        = string
  default     = "stspecauto001"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "service_plan_name" {
  description = "Name of the Azure Service Plan. Defines the compute resources for the function."
  type        = string
  default     = "asp-spec-automation"
}

variable "function_app_name" {
  description = "Name of the Azure Function App (must be globally unique). This will be part of the function URL."
  type        = string
  default     = "func-spec-dispatch-001"

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

variable "spec_column_name" {
  description = "Azure DevOps board column name that triggers spec generation. Must match board configuration exactly."
  type        = string
  default     = "Specification – Doing"
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

variable "environment" {
  description = "Environment tag (dev, staging, prod). Used for resource tagging and cost tracking."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}
