# Infrastructure as Code - Spec Automation

## Purpose

This directory contains Terraform configuration for provisioning the Azure Function infrastructure that powers the Azure DevOps → GitHub spec generation automation.

## Architecture

- **Azure Function App** (Linux, Python 3.11, Consumption plan)
- **Storage Account** (required for Azure Functions runtime)
- **Service Plan** (Consumption tier for cost efficiency)
- **Resource Group** (reusable or new)

## Prerequisites

1. **Azure CLI** installed and authenticated:
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Terraform** >= 1.6.0:
   ```bash
   terraform version
   ```

3. **VPN Access**: Required for managing and accessing resources (all resources are network-isolated)

4. **Required secrets** (set after deployment):
   - `GH_WORKFLOW_DISPATCH_PAT` - GitHub fine-grained PAT (Actions: RW, Contents: R)
   - `ADO_WORK_ITEM_PAT` - Azure DevOps PAT (Work Items: Read)

## Security Architecture

**CRITICAL: All resources are network-isolated and NOT publicly accessible.**

**Premium Plan (EP1) - Full Network Isolation:**
- ✅ **Function App**: VNet integrated, public access DISABLED
- ✅ **Storage Account**: Private endpoints only, no public access
- ✅ **Access Method**: VPN gateway required for all access
- ✅ **Inbound Traffic**: Only via VPN (public_network_access_enabled = false)
- ✅ **Outbound Traffic**: Routed through VNet (vnet_route_all_enabled = true)

**Network Security Controls:**
- **Private Endpoints**: Storage blob + file accessible only within VNet
- **Private DNS**: Automatic resolution within VNet
- **VNet Integration**: Function integrated with existing VNet subnet
- **Default Deny**: All public access blocked by default

**Cost:**
- Premium (EP1): ~$150/month (always-on, required for network isolation)
- See [Azure Functions pricing](https://azure.microsoft.com/pricing/details/functions/) for details.

## Usage

### 1. Initialize Terraform

```bash
cd infra
terraform init
```

### 2. Review and customize variables

Create `terraform.tfvars`:

```hcl
# Required
github_owner = "agzyamov"
github_repo  = "ai-native-sdlc"

# Network Configuration (use existing VPN-connected VNet)
vnet_name                    = "vnet-ai-agents-infra-dev"
vnet_resource_group          = "rg-ai-agents-infra-dev"
function_subnet_name         = "subnet-ai-dev"
private_endpoint_subnet_name = "subnet-ai-dev"

# SECURITY: Keep public access disabled for production
enable_public_access = false

# Optional (override defaults)
resource_group_name          = "rg-spec-automation"
use_existing_resource_group  = false
location                     = "eastus"
storage_account_name         = "stspecautorustem001"  # Must be globally unique
function_app_name            = "func-spec-rustem-001" # Must be globally unique
environment                  = "dev"
log_level                    = "INFO"
```

**Important Security Settings:**
- `enable_public_access = false` - Resources only accessible via VPN (REQUIRED for production)
- `enable_public_access = true` - Temporary flag for initial testing only (NOT recommended)

### 3. Plan deployment

```bash
terraform plan -out=tfplan
```

**Review the plan output carefully** before applying. Verify:
- Resource names are unique (storage account, function app)
- Region matches your preference
- No unexpected deletions

### 4. Apply configuration

```bash
terraform apply tfplan
```

### 5. Configure secrets (manual step)

After deployment, set secrets via Azure Portal or CLI:

**Option A: Azure Portal**
1. Navigate to Function App → Configuration → Application settings
2. Add new settings:
   - `GH_WORKFLOW_DISPATCH_PAT` = `<your-github-pat>`
   - `ADO_WORK_ITEM_PAT` = `<your-ado-pat>`
3. Click **Save**

**Option B: Azure CLI**
```bash
FUNCTION_NAME=$(terraform output -raw function_name)
RG_NAME=$(terraform output -raw resource_group_name)

az functionapp config appsettings set \
  --name $FUNCTION_NAME \
  --resource-group $RG_NAME \
  --settings \
    "GH_WORKFLOW_DISPATCH_PAT=<your-github-pat>" \
    "ADO_WORK_ITEM_PAT=<your-ado-pat>"
```

### 6. Deploy function code

See `function_app/README.md` for deployment instructions.

## Outputs

After successful deployment, Terraform exports these outputs:

| Output | Description | Usage |
|--------|-------------|-------|
| `function_name` | Name of the deployed Function App | Use with Azure CLI: `az functionapp show -n <name> -g <rg>` |
| `function_url` | Complete HTTPS URL to function endpoint | Service Hook URL (append function key as query param) |
| `function_default_hostname` | Function App hostname only | For custom domain configuration |
| `resource_group_name` | Resource group containing all resources | Use for resource management commands |

**Retrieve outputs**:
```bash
terraform output
terraform output -raw function_url  # Get specific output without quotes
```

**Use outputs in CI/CD**:
```bash
# Export for subsequent steps
export FUNCTION_URL=$(terraform output -raw function_url)
export FUNCTION_NAME=$(terraform output -raw function_name)
```

## Terraform Plan Artifact Guidance

For production deployments with approval workflows:

**Generate plan artifact**:
```bash
# In CI pipeline or pre-deployment
terraform plan -out=tfplan.binary

# Convert to human-readable for review
terraform show -no-color tfplan.binary > tfplan.txt

# Optional: JSON format for automated policy checks
terraform show -json tfplan.binary > tfplan.json
```

**Store plan securely**:
```bash
# Option 1: GitHub Actions artifact (ephemeral, 7 days retention)
- uses: actions/upload-artifact@v4
  with:
    name: terraform-plan
    path: infra/tfplan.binary
    retention-days: 7

# Option 2: Azure Storage (persistent)
az storage blob upload \
  --account-name <storage> \
  --container tfplans \
  --name "plan-$(date +%Y%m%d-%H%M%S).binary" \
  --file tfplan.binary
```

**Apply from plan**:
```bash
# In approval/apply stage
terraform apply tfplan.binary
```

**Plan validation in CI**:
```yaml
# Add to .github/workflows/ci-infra-validation.yml
- name: Terraform Plan
  run: terraform plan -input=false -no-color
  env:
    TF_VAR_github_owner: ${{ github.repository_owner }}
    TF_VAR_github_repo: ${{ github.event.repository.name }}
```

**Best practices**:
- Always review `tfplan.txt` before approval
- Store plan artifacts for audit trail
- Use `-lock-timeout=5m` for concurrent deployment protection
- Verify resource_group_name output matches expectations

## Maintenance

### Update infrastructure

```bash
terraform plan
terraform apply
```

### Destroy resources (cleanup)

```bash
terraform destroy
```

**Warning:** This will delete all resources including storage. Ensure backups if needed.

## State Management

Currently using **local state** (`terraform.tfstate`). For team collaboration, migrate to remote backend:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "sttfstate001"
    container_name       = "tfstate"
    key                  = "spec-automation.tfstate"
  }
}
```

## Security Notes

- **Network Isolation**: All resources deployed with `public_network_access_enabled = false` by default
- **VPN Required**: Access function and storage only via existing VPN gateway connection
- **Private Endpoints**: Storage accessible via private endpoints within VNet
- **VNet Integration**: Function App routes all traffic through VNet
- **Never commit** `terraform.tfvars` or `.tfstate` files containing secrets
- **Key Vault**: Production secrets should use Key Vault references:
  ```hcl
  "@Microsoft.KeyVault(SecretUri=https://vault.vault.azure.net/secrets/secret-name)"
  ```
- **PAT Rotation**: Rotate PATs every 90 days (policy)
- **Access Control**: Review function app settings periodically for unused variables

**To access deployed function:**
1. Connect to VPN
2. Use private function URL (not publicly routable)
3. Configure ADO Service Hook from VPN-accessible endpoint

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Storage account name already taken` | Change `storage_account_name` to a unique value |
| `Function app name already exists` | Change `function_app_name` to a unique value |
| `Authentication failed` | Run `az login` and set correct subscription |
| `Provider registry.terraform.io/hashicorp/azurerm not found` | Run `terraform init` |

## Cost Estimation

**Consumption Plan** (pay-per-execution):
- First 1M executions/month: Free
- Storage: ~$0.10/month (minimal data)
- Estimated monthly cost for pilot (<100 executions): **< $1**

For production scale estimations, use [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/).
