# Terraform Conventions

## Overview

Terraform code must follow Microsoft Cloud Adoption Framework (CAF) best practices and support a modular Azure sandbox structure that can evolve into a production landing zone.

## Structure

Organize IaC into three layers:

- **foundation/** — base infra: Resource Group, VNet, Key Vault, Storage, Logging
- **functions/** — Azure Function App, Service Plan, App Insights integration
- **ai-foundry/** — future module for Azure AI Foundry workspace and private networking

All modules accept variables `env` and `location`.
Every resource must have consistent tags: `env`, `owner`, `costCenter`.

## Region Policy

- Default region → `"westeurope"`
- If not provided, define:
  ```hcl
  variable "location" {
    description = "Azure region"
    type        = string
    default     = "westeurope"
  }
  ```
- Alternate regions for proximity to Türkiye → `swedencentral` or `northeurope`
- Disaster-recovery pairing → `westeurope` + `northeurope`
- Verify service availability; fall back to `westeurope` if missing
- Never hard-code regions; always use `var.location`
- Each README must note region choice and link to [CAF Region Pairs](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-setup-guide/regions)

## Foundation Layer

Terraform must create:
- **Resource Group** `rg-func-${var.env}`
- **VNet** `vnet-${var.env}` with subnets:
  - `snet-func` for Functions/App Service Plan
  - `snet-pe` for Private Endpoints
- **Log Analytics Workspace** + Application Insights
- **Storage Account** for Functions (`stfunc${var.env}...`)
- **Key Vault** (`kv-func-${var.env}`) with RBAC authorization
- **Diagnostic settings** forwarding logs to Log Analytics
- **TLS ≥ 1.2** on all services

## Functions Layer

- **Linux Function App** (Consumption by default; Premium if VNet required)
- **System-assigned Managed Identity**
- **HTTPS only**, FTPS disabled
- **Secrets via Key Vault** references (`@Microsoft.KeyVault(...)`)
- **App settings**:
  - `FUNCTIONS_EXTENSION_VERSION = "~4"`
  - `WEBSITE_RUN_FROM_PACKAGE = "1"`
  - `AzureWebJobsStorage` from Storage Account
- **Outputs**: Function App name, hostname, Key Vault URI

## Security Rules

- **No plaintext secrets** in Terraform
- **Public network access disabled** for Key Vault and Storage (except pure sandbox)
- Always enable **Managed Identity**; use RBAC, not access policies
- Enable **diagnostic settings** for all resources
- Enforce **HTTPS** and **TLS ≥ 1.2**

## Terraform Style

- **Variables**: `env`, `location`
- **Idempotent**, minimal modules
- No `.tfstate` in repo; use remote backend if needed
- **Outputs**: Function App hostname, Key Vault URI, Log Analytics Workspace ID
- **Naming**: `<type>-<env>-<suffix>` (e.g., `func-sbx-core`)

## Naming Convention

```
rg-func-dev           # Resource Group
st<env><random>       # Storage Account (e.g., stdev5kcj)
kv-<env>-<suffix>     # Key Vault (e.g., kv-dev-secrets)
func-<env>-<name>     # Function App (e.g., func-dev-api)
asp-<env>-<name>      # App Service Plan (e.g., asp-dev-premium)
ai-<env>-<name>       # Application Insights (e.g., ai-dev-monitoring)
law-<env>-<name>      # Log Analytics Workspace (e.g., law-dev-logs)
```

## Terraform Validation Requirements

**CRITICAL: Before generating or modifying Terraform code, ALWAYS:**

1. **Verify resource capabilities** using `microsoft_docs_search` MCP tool:
   - Search for "Azure [resource type] [feature] Terraform azurerm"
   - Example: "Azure Functions VNet integration Premium plan Terraform azurerm"
   - Verify resource arguments/properties exist in current azurerm provider

2. **Check SKU/tier availability**:
   - Search "Azure [resource] pricing tiers [region]"
   - Verify SKU supports required features (e.g., EP1 Premium supports VNet integration)
   - Confirm feature availability in target region (westeurope)

3. **Validate network security model**:
   - Search "Azure [resource] network isolation private endpoint"
   - Verify `public_network_access_enabled` behavior for specific resource type
   - Confirm correct combination of network rules

4. **Common validation queries**:
   - "Azure Storage Account network rules VNet integration"
   - "Azure Key Vault RBAC authorization network isolation"
   - "Azure Functions Premium plan file share access"
   - "Azure Private Endpoint subnet requirements"

5. **After generating Terraform**:
   - Run `terraform validate` to check syntax
   - Run `terraform plan` to verify resource arguments
   - Search Microsoft Docs if plan shows unknown arguments/deprecated properties

**Never assume Terraform resource arguments without verification in Microsoft Docs.**

## Provider Requirements

- Use `azurerm` provider version 3.x or higher
- Add `description` to all variables and outputs
- Use `default` values for non-sensitive variables where appropriate
- Add `depends_on` where implicit dependencies aren't clear
- Use `lifecycle` blocks for ignore_changes when needed (e.g., tags managed externally)

## Documentation

Each module must include:
- Deployment order (`foundation → functions → ai-foundry`)
- Chosen region and rationale
- How to evolve sandbox into production landing zone
- Links to [Microsoft CAF](https://learn.microsoft.com/azure/cloud-adoption-framework/) and [Azure Landing Zone Terraform](https://registry.terraform.io/modules/Azure/caf-enterprise-scale/azurerm/latest) docs

All pull requests must be reviewed by a platform engineer for compliance.

## Related Rules

- See [azure-infrastructure.md](azure-infrastructure.md) for security and networking requirements
- See [azure-functions.md](azure-functions.md) for Function App configuration

