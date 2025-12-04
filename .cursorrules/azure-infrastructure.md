# Azure Infrastructure Security

## Critical Requirements

**CRITICAL: All Azure resources MUST be network-isolated and NOT exposed to the public internet.**

**IMPORTANT: Azure Functions Consumption Plan Limitation**
- Consumption plan (Y1 SKU) does NOT support VNet integration or `public_network_access_enabled`
- For network isolation, use **Premium plan (EP1/EP2/EP3)** or **Dedicated plan**
- Document this limitation and cost trade-off when using Consumption plans

## Network Security

When creating or modifying Azure infrastructure:

1. **Network Security**:
   - ✅ Use existing VPN gateway for secure access
   - ✅ Configure Private Endpoints for all services (Storage, Key Vault, etc.)
   - ✅ Disable public network access on Storage Accounts
   - ❌ NEVER expose resources directly to the internet (0.0.0.0/0)
   - ✅ Use Network Security Groups (NSGs) with least-privilege rules
   - ✅ Enable VNet integration for Azure Functions **Premium/Dedicated plans only**

2. **Terraform/IaC Requirements**:
   ```hcl
   # Required patterns for Azure resources:
   
   # Storage Account - disable public access (ALL plans)
   public_network_access_enabled = false
   network_rules {
     default_action = "Deny"
     bypass         = ["AzureServices"]
   }
   
   # Function App - VNet integration (Premium/Dedicated ONLY, not Consumption)
   # For Premium plan (EP1/EP2/EP3):
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

3. **Access Patterns**:
   - Use VPN gateway for administrative access
   - Use Private Endpoints for service-to-service communication
   - **ALWAYS use Managed Identity for storage connections** (never connection strings)
   - Store secrets in Key Vault with network restrictions
   
   **Storage Connection Best Practices:**
   - ✅ Use `AzureWebJobsStorage__accountName` with Managed Identity
   - ✅ Set `storage_uses_managed_identity = true` on Function Apps
   - ✅ Assign proper RBAC roles: `Storage Blob Data Owner`, `Storage Queue Data Contributor`, `Storage Table Data Contributor`, `Storage File Data Privileged Contributor`
   - ❌ NEVER use `AzureWebJobsStorage` with connection strings in production
   - ⚠️ Exception: `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING` requires connection string (Azure Files doesn't support managed identity for file shares yet)

4. **Validation Checklist**:
   - ✅ Storage accounts have `public_network_access_enabled = false`
   - ✅ Function plan is Premium/Dedicated (not Consumption Y1) for VNet integration
   - ✅ All resources have `network_acls` or NSG configuration
   - ✅ VNet integration configured for compute resources (Premium+ only)
   - ✅ Private DNS zones configured for private endpoints
   - ✅ Firewall rules documented and justified
   - ⚠️ Document if Consumption plan used (cannot enforce full network isolation)

**Before committing infrastructure code:**
- ✅ Verify Storage accounts have no public endpoints
- ✅ Confirm plan SKU supports required network features
- ✅ Confirm VPN/Private Endpoint access path documented
- ✅ Security review checklist completed
- ✅ Run `terraform plan` and review network configuration
- ✅ Document any limitations (e.g., Consumption plan public access)

**Never deploy publicly accessible Azure Storage without explicit security exception!**

## Managed Identity

Always use Managed Identity instead of connection strings:

### Function App Managed Identity

```hcl
resource "azurerm_linux_function_app" "main" {
  # ... other configuration ...
  
  identity {
    type = "SystemAssigned"
  }
  
  storage_uses_managed_identity = true
  storage_account_access_key    = null
}
```

### RBAC Role Assignments

```hcl
resource "azurerm_role_assignment" "storage_blob" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id
}
```

## Key Vault Integration

### RBAC Authorization

Use RBAC instead of access policies:

```hcl
resource "azurerm_key_vault" "main" {
  # ... other configuration ...
  
  enable_rbac_authorization = true
  public_network_access_enabled = false
}
```

### Private Endpoint

```hcl
resource "azurerm_private_endpoint" "kv" {
  name                = "pe-kv-${var.env}"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id

  private_service_connection {
    name                           = "psc-kv-${var.env}"
    private_connection_resource_id = azurerm_key_vault.main.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }
}
```

## Diagnostic Settings

Enable diagnostic settings for all resources:

```hcl
resource "azurerm_monitor_diagnostic_setting" "function_app" {
  name                       = "diag-func-${var.env}"
  target_resource_id         = azurerm_linux_function_app.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "FunctionAppLogs"
  }

  metric {
    category = "AllMetrics"
  }
}
```

## TLS Requirements

Enforce HTTPS and TLS ≥ 1.2:

```hcl
resource "azurerm_linux_function_app" "main" {
  # ... other configuration ...
  
  https_only = true
  
  site_config {
    minimum_tls_version = "1.2"
    ftps_state          = "Disabled"
  }
}
```

## Related Rules

- See [terraform.md](terraform.md) for Terraform conventions
- See [azure-functions.md](azure-functions.md) for Function App configuration

