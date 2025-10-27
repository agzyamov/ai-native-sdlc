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

3. **Required secrets** (set after deployment):
   - `GH_WORKFLOW_DISPATCH_PAT` - GitHub fine-grained PAT (Actions: RW, Contents: R)
   - `ADO_WORK_ITEM_PAT` - Azure DevOps PAT (Work Items: Read)

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

# Optional (override defaults)
resource_group_name          = "rg-spec-automation"
use_existing_resource_group  = false
location                     = "eastus"
storage_account_name         = "stspecauto001"  # Must be globally unique
function_app_name            = "func-spec-dispatch-001"  # Must be globally unique
environment                  = "dev"
log_level                    = "INFO"
```

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

- **Never commit** `terraform.tfvars` or `.tfstate` files containing secrets
- Use **Key Vault references** for production secrets:
  ```hcl
  "@Microsoft.KeyVault(SecretUri=https://vault.vault.azure.net/secrets/secret-name)"
  ```
- Rotate PATs every 90 days (policy)
- Review function app settings periodically for unused variables

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
