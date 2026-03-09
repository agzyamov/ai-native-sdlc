---
applyTo: 'infra/**'
---

# Azure Infrastructure

## Security Requirements

**CRITICAL: All Azure resources MUST be network-isolated and NOT exposed to the public internet.**

**IMPORTANT: Azure Functions Consumption Plan Limitation**
- Consumption plan (Y1 SKU) does NOT support VNet integration or `public_network_access_enabled`
- For network isolation, use **Premium plan (EP1/EP2/EP3)** or **Dedicated plan**
- Document this limitation and cost trade-off when using Consumption plans

### Network Security

- ✅ Use existing VPN gateway for secure access
- ✅ Configure Private Endpoints for all services (Storage, Key Vault, etc.)
- ✅ Disable public network access on Storage Accounts
- ❌ NEVER expose resources directly to the internet (0.0.0.0/0)
- ✅ Use Network Security Groups (NSGs) with least-privilege rules
- ✅ Enable VNet integration for Azure Functions **Premium/Dedicated plans only**

### Terraform/IaC Required Patterns

```hcl
# Storage Account - disable public access (ALL plans)
public_network_access_enabled = false
network_rules {
  default_action = "Deny"
  bypass         = ["AzureServices"]
}

# Function App - VNet integration (Premium/Dedicated ONLY, not Consumption)
virtual_network_subnet_id = var.function_subnet_id
public_network_access_enabled = false
site_config {
  vnet_route_all_enabled = true
}

# Key Vault - use private endpoint
public_network_access_enabled = false
network_acls {
  default_action = "Deny"
  bypass         = "AzureServices"
}
```

### Storage Connection Best Practices

- ✅ Use `AzureWebJobsStorage__accountName` with Managed Identity
- ✅ Set `storage_uses_managed_identity = true` on Function Apps
- ✅ Assign RBAC roles: `Storage Blob Data Owner`, `Storage Queue Data Contributor`, `Storage Table Data Contributor`, `Storage File Data Privileged Contributor`
- ❌ NEVER use `AzureWebJobsStorage` with connection strings in production
- ⚠️ Exception: `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` requires connection string (Azure Files doesn't support managed identity yet)

### Validation Checklist

- ✅ Storage accounts have `public_network_access_enabled = false`
- ✅ Function plan is Premium/Dedicated (not Consumption Y1) for VNet integration
- ✅ All resources have `network_acls` or NSG configuration
- ✅ VNet integration configured for compute resources (Premium+ only)
- ✅ Private DNS zones configured for private endpoints
- ✅ Run `terraform plan` and review network configuration
- ⚠️ Document if Consumption plan used (cannot enforce full network isolation)

**Never deploy publicly accessible Azure Storage without explicit security exception!**

---

## IP Rotation — Mandatory Runbook

**When you see `ForbiddenByFirewall` or HTTP 403 from Azure Function / Key Vault that previously worked:**

Your public IP has rotated. Run this before any `terraform apply`:

```bash
bash scripts/update-deployment-ip.sh   # detects current IP, updates infra/terraform.tfvars
cd infra
ARM_SUBSCRIPTION_ID=<sub-id> terraform apply -auto-approve \
  -target=azurerm_linux_function_app.main \
  -target=azurerm_key_vault.main
```

**Checklist before debugging function errors:**
- ✅ Run `curl -s https://api.ipify.org` and compare to `deployment_allowed_ip` in `terraform.tfvars`
- ✅ If different → run `bash scripts/update-deployment-ip.sh && terraform apply -target=...`
- ✅ Then retest — do not debug KV references or PAT scopes until IP is confirmed correct

---

## Terraform CAF Sandbox — Structure & Standards

### Module Structure

- **foundation/** — Resource Group, VNet, Key Vault, Storage, Logging
- **functions/** — Function App, Service Plan, App Insights integration
- **ai-foundry/** — placeholder for Azure AI Foundry workspace and private networking

All modules accept variables `env` and `location`. Every resource must have tags: `env`, `owner`, `costCenter`.

### Region Policy

- Default region → `"westeurope"`
- Alternate regions for proximity to Türkiye → `swedencentral` or `northeurope`
- DR pairing → `westeurope` + `northeurope`
- Never hard-code regions; always use `var.location`

### Foundation Layer Resources

- **Resource Group** `rg-func-${var.env}`
- **VNet** `vnet-${var.env}` with subnets `snet-func` and `snet-pe`
- **Log Analytics Workspace** + Application Insights
- **Storage Account** `stfunc${var.env}...`
- **Key Vault** `kv-func-${var.env}` with RBAC authorization
- **Diagnostic settings** forwarding to Log Analytics
- **TLS ≥ 1.2** on all services

### Functions Layer

- Linux Function App (Consumption by default; Premium if VNet required)
- System-assigned Managed Identity; HTTPS only; FTPS disabled
- Secrets via Key Vault references (`@Microsoft.KeyVault(...)`)
- App settings: `FUNCTIONS_EXTENSION_VERSION = "~4"`, `WEBSITE_RUN_FROM_PACKAGE = "1"`

### Terraform Validation Requirements

**Before generating or modifying Terraform code, ALWAYS:**

1. Verify resource capabilities using `microsoft_docs_search` MCP tool
2. Check SKU/tier availability for the target region
3. Validate the network security model
4. Run `terraform validate` and `terraform plan` after changes

**Never assume Terraform resource arguments without verification in Microsoft Docs.**

### Naming Convention

```
rg-func-dev           # Resource Group
st<env><random>       # Storage Account (e.g., stdev5kcj)
kv-<env>-<suffix>     # Key Vault (e.g., kv-dev-secrets)
func-<env>-<name>     # Function App (e.g., func-dev-api)
asp-<env>-<name>      # App Service Plan (e.g., asp-dev-premium)
ai-<env>-<name>       # Application Insights (e.g., ai-dev-monitoring)
law-<env>-<name>      # Log Analytics Workspace (e.g., law-dev-logs)
```

All pull requests must be reviewed by a platform engineer for compliance.
