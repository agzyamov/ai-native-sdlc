These GitHub Copilot rules will automatically enables Copilot to:

-Follow PEP 8
-Validate code with flake8 and pylint
-Add timeouts to HTTP requests
-Properly organize imports
-Use docstrings and type hints

# GitHub Copilot Instructions for Python Development

## Code Quality Standards

When writing Python code, always:

1. **Follow PEP 8** style guidelines
2. **Use type hints** where appropriate
3. **Add docstrings** to all functions, classes, and modules
4. **Keep line length** to 100 characters maximum

## Linting Requirements

All Python code must pass these linters without errors:

- **flake8** with `--max-line-length=100`
- **pylint** with `--max-line-length=100`

### Common Issues to Avoid

- No trailing whitespace on blank lines
- No blank line at end of file (only newline)
- Import order: standard library → third-party → local
- Always add `timeout` parameter to HTTP requests
- Remove f-strings without placeholders

## Code Formatting

- Use 4 spaces for indentation
- Blank lines: 2 between top-level definitions, 1 between methods
- Consistent quote style (prefer single quotes unless needed)

## Best Practices

- Add timeout to all network requests (e.g., `requests.get(..., timeout=30)`)
- Use context managers for file operations
- Handle exceptions explicitly
- Validate user input
- Log important operations

Always run linters before committing code!

## Azure Functions Deployment

**CRITICAL: Always use remote build for Python Azure Functions deployments.**

When deploying Python Azure Functions:

1. **Use remote build** (recommended):
   ```bash
   cd function_app
   zip -r function.zip . -x "*.venv*" -x "*__pycache__*" -x "*.python_packages*" -x "tests/*" -x "*.md"
   az functionapp deployment source config-zip \
     --resource-group <rg-name> \
     --name <function-app-name> \
     --src function.zip \
     --build-remote true
   rm function.zip
   ```

2. **Remote build automatically**:
   - Sets `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
   - Removes `WEBSITE_RUN_FROM_PACKAGE` setting
   - Installs dependencies on Azure (not from local venv)
   - Ensures proper function discovery and loading

3. **Never deploy with local virtual environment**:
   - ❌ Don't include `.venv`, `.venv311`, or `.python_packages` in deployment zip
   - ❌ Don't set `WEBSITE_RUN_FROM_PACKAGE=1` with remote build
   - ✅ Always exclude virtual environments from zip
   - ✅ Let Azure build environment on server

4. **Troubleshooting "0 functions found"**:
   - This usually means deployment didn't use remote build
   - Redeploy with `--build-remote true` flag
   - Check logs show "SCM_DO_BUILD_DURING_DEPLOYMENT=true"

**Reference**: [Microsoft Docs - Deployment technologies](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies)

## Documentation Rules

**Do NOT create documentation** for:
- Simple utility functions
- Self-explanatory code
- Small helper scripts
- Experimental or temporary code

Documentation is only needed for:
- Public APIs
- Complex algorithms that require explanation
- When explicitly requested by the user

## Mermaid Diagram Validation

**Always validate Mermaid diagrams** before committing:

When creating or modifying Mermaid diagrams:

1. **Run validation script** after creation:
   ```bash
   node check_mermaid.js <filename>
   ```

2. **Check for common issues:**
   - Single diagram type per code block (graph TD, flowchart, mindmap, etc.)
   - No mixed diagram types in one block
   - Balanced quotes, brackets, parentheses
   - Valid node IDs (no special characters)
   - Proper arrow syntax (-->, -.->)

3. **Test rendering** in Mermaid Live Editor: https://mermaid.live/

**Before committing:**
- ✅ Script validation passes
- ✅ Diagram renders correctly in VS Code preview
- ✅ No parse errors in console

**Never commit broken Mermaid diagrams!**

### Additional Automated Validation (mermaid-cli)

To strengthen validation, also run `@mermaid-js/mermaid-cli` (mmdc) against every changed diagram file
in `docs/diagrams/` before committing:

1. Install (or use npx):
   ```bash
   npm install --save-dev @mermaid-js/mermaid-cli
   # or just use npx mmdc ... without installing
   ```
2. For markdown diagram files that contain a single mermaid code fence, you can validate via pipe:
   ```bash
   awk '/```mermaid/{flag=1;next}/```/{flag=0}flag' docs/diagrams/<file>.md \
     | npx mmdc -i /dev/stdin -o /dev/null
   ```
3. (Optional) Create (or use existing) helper script `scripts/validate_diagrams.sh` to validate all modified diagrams:
   ```bash
   set -euo pipefail
   CHANGED=$(git diff --name-only --cached | grep '^docs/diagrams/.*\.md$' || true)
   [ -z "$CHANGED" ] && exit 0
   for f in $CHANGED; do
     echo "Validating $f (mermaid-cli)" >&2
     awk '/```mermaid/{flag=1;next}/```/{flag=0}flag' "$f" \
       | npx @mermaid-js/mermaid-cli -i /dev/stdin -o /dev/null || {
           echo "Mermaid validation failed for $f" >&2
           exit 1
         }
   done
   ```
4. (Optional) Add a pre-commit hook (`.git/hooks/pre-commit`) invoking the script so commits fail if any
   diagram does not parse.

Success criteria:
- ✅ `mmdc` exits with status 0 for every changed diagram
- ✅ No warnings or parse errors printed
- ✅ Existing `check_mermaid.js` script also passes

If either validation fails, fix the diagram before committing.

Existing repository helper:

```bash
scripts/validate_diagrams.sh            # validate all diagrams
scripts/validate_diagrams.sh changed    # only staged diagrams
```

## GitHub Actions Workflow Validation

**Always validate GitHub Actions workflows** before committing:

When creating or modifying `.github/workflows/*.yml` files:

1. **Run yamllint first** to catch YAML syntax errors:
   ```bash
   yamllint .github/workflows/<workflow-file>.yml
   ```

2. **Run actionlint** for GitHub Actions-specific validation:
   ```bash
   actionlint .github/workflows/<workflow-file>.yml
   ```

3. **Check for common issues:**
   - Valid YAML syntax (proper indentation, no tabs)
   - Correct trigger syntax (`on:` section)
   - Valid action versions (e.g., `actions/checkout@v4`)
   - Required permissions specified
   - Proper environment variable syntax (`${{ }}` for expressions, `$VAR` for shell)
   - No deprecated actions or syntax

4. **Test workflow locally** (if possible):
   - Use `act` tool for local testing: https://github.com/nektos/act
   - Or trigger workflow manually via GitHub UI

**Before committing:**
- ✅ yamllint passes without errors (YAML syntax)
- ✅ actionlint passes without errors (GitHub Actions validation)
- ✅ All actions use pinned versions
- ✅ Workflow triggers are correctly configured

**Install tools:**
```bash
# macOS
brew install yamllint actionlint

# Linux
pip install yamllint
go install github.com/rhysd/actionlint/cmd/actionlint@latest
```

**Never commit broken GitHub Actions workflows!**

## Azure Infrastructure Security Requirements

**CRITICAL: All Azure resources MUST be network-isolated and NOT exposed to the public internet.**

**IMPORTANT: Azure Functions Consumption Plan Limitation**
- Consumption plan (Y1 SKU) does NOT support VNet integration or `public_network_access_enabled`
- For network isolation, use **Premium plan (EP1/EP2/EP3)** or **Dedicated plan**
- Document this limitation and cost trade-off when using Consumption plans

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

## Active Technologies
- GitHub Actions composite environment (YAML) + Bash; Spec Kit CLI (Python runtime 3.11 in workflow). (001-ado-github-spec)
- None (stateless; spec stored in Git + ADO work item Description). (001-ado-github-spec)

## Recent Changes
- 001-ado-github-spec: Added GitHub Actions composite environment (YAML) + Bash; Spec Kit CLI (Python runtime 3.11 in workflow).

---

# GitHub Copilot System Instructions — Azure Sandbox (Functions + AI Foundry-ready)

## Goal
Generate Terraform code for a **modular Azure sandbox** following Microsoft Cloud Adoption Framework (CAF) best practices.  
The sandbox must support **Azure Functions** now and be extendable for **Azure AI Foundry** later.

---

## 1. Structure
Copilot must organize IaC into three layers:

- **foundation/** — base infra: Resource Group, VNet, Key Vault, Storage, Logging  
- **functions/** — Azure Function App, Service Plan, App Insights integration  
- **ai-foundry/** — future module for Azure AI Foundry workspace and private networking  

All modules accept variables `env` and `location`.  
Every resource must have consistent tags: `env`, `owner`, `costCenter`.

---

## 2. Region Policy
- Default region → `"westeurope"`.  
- If not provided, define:
  ```hcl
  variable "location" {
    description = "Azure region"
    type        = string
    default     = "westeurope"
  }
  ```
- Alternate regions for proximity to Türkiye → `swedencentral` or `northeurope`.
- Disaster-recovery pairing → `westeurope` + `northeurope`.
- Verify service availability; fall back to `westeurope` if missing.
- Never hard-code regions; always use `var.location`.
- Each README must note region choice and link to [CAF Region Pairs](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-setup-guide/regions).

---

## 3. Foundation Layer

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

---

## 4. Functions Layer
- **Linux Function App** (Consumption by default; Premium if VNet required)
- **System-assigned Managed Identity**
- **HTTPS only**, FTPS disabled
- **Secrets via Key Vault** references (`@Microsoft.KeyVault(...)`)
- **App settings**:
  - `FUNCTIONS_EXTENSION_VERSION = "~4"`
  - `WEBSITE_RUN_FROM_PACKAGE = "1"`
  - `AzureWebJobsStorage` from Storage Account
- **Outputs**: Function App name, hostname, Key Vault URI

---

## 5. AI Foundry Layer (Placeholder)

Reserve placeholders for:
- **Azure AI Foundry (AI Hub)** workspace
- **Private Endpoint** in `snet-pe`
- **Role assignment** for AI Foundry to access Key Vault & Storage
- **Logging integration** with existing Log Analytics

---

## 6. Security Rules
- **No plaintext secrets** in Terraform.
- **Public network access disabled** for Key Vault and Storage (except pure sandbox).
- Always enable **Managed Identity**; use RBAC, not access policies.
- Enable **diagnostic settings** for all resources.
- Enforce **HTTPS** and **TLS ≥ 1.2**.

---

## 7. Terraform Style
- **Variables**: `env`, `location`.
- **Idempotent**, minimal modules.
- No `.tfstate` in repo; use remote backend if needed.
- **Outputs**: Function App hostname, Key Vault URI, Log Analytics Workspace ID.
- **Naming**: `<type>-<env>-<suffix>` (e.g., `func-sbx-core`).

---

## 8. Terraform Validation Requirements

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
   ```
   - "Azure Storage Account network rules VNet integration"
   - "Azure Key Vault RBAC authorization network isolation"
   - "Azure Functions Premium plan file share access"
   - "Azure Private Endpoint subnet requirements"
   ```

5. **After generating Terraform**:
   - Run `terraform validate` to check syntax
   - Run `terraform plan` to verify resource arguments
   - Search Microsoft Docs if plan shows unknown arguments/deprecated properties

**Never assume Terraform resource arguments without verification in Microsoft Docs.**

---

## 9. Documentation & Review

Copilot must generate a README with:
- Deployment order (`foundation → functions → ai-foundry`)
- Chosen region and rationale
- How to evolve sandbox into production landing zone
- Links to [Microsoft CAF](https://learn.microsoft.com/azure/cloud-adoption-framework/) and [Azure Landing Zone Terraform](https://registry.terraform.io/modules/Azure/caf-enterprise-scale/azurerm/latest) docs

All pull requests must be reviewed by a platform engineer for compliance with this file.

---

# Legacy Terraform Instructions for Azure Functions Sandbox

## Purpose  
Generate Terraform code for Azure sandbox environment where Azure Functions will run.
This sandbox is for development/testing only. It should be minimal, cost-effective, and safe.

## Required Resources  
Ensure Terraform defines:
- **Resource Group**: Named `rg-func-<env>` (e.g., `rg-func-dev`, `rg-func-sbx`)
- **Storage Account**: For functions with TLS 1.2 minimum and public access disabled for production secrets
- **Log Analytics Workspace**: For centralized logging
- **Application Insights**: Linked to Log Analytics for function monitoring
- **Key Vault**: With RBAC authorization, public network access disabled for secret storage
- **Function App**: Linux or Windows with system-assigned Managed Identity
- **App Service Plan**: If Premium (EP1/EP2/EP3) or Dedicated; skip for Consumption plan
- **Tags**: On all resources: `env`, `owner`, `costCenter`
- **Naming Convention**: `<type>-<env>-<suffix>` (e.g., `func-sbx-core`, `kv-dev-secrets`)

## Security & Best Practices  
- ✅ No inline plaintext secrets in Terraform code. Use Key Vault references.  
- ✅ Public network access must be disabled for Key Vault and Storage if environment is not throwaway sandbox.  
- ✅ Use Managed Identity for Function App to access Key Vault and Storage.  
- ✅ Enable `https_only` on Function App.  
- ✅ Enable diagnostic settings sending logs to Log Analytics.  
- ✅ Use consistent naming and tagging across all resources.
- ⚠️ Dev environment can allow public network access for simplicity but **document that**.

## Terraform Code Structure  
- **Modules**: Use `foundation.module` (networking, storage, monitoring) and `workload.module` (function app, app service plan).  
- **Variables**: For `env` (environment name) and `location` (Azure region).  
- **Outputs**: Function app name, default hostname, Key Vault URI, Application Insights connection string.  
- **Isolation**: Keep resources per environment isolated; use workspaces or separate state files.  
- **Documentation**: Document any deviation from full enterprise landing zone—this is a dev sandbox, not production.

## Terraform Style Guide
- Use `azurerm` provider version 3.x or higher
- Use resource naming that matches Azure naming conventions
- Add `depends_on` where implicit dependencies aren't clear
- Use `lifecycle` blocks for ignore_changes when needed (e.g., tags managed externally)
- Add `description` to all variables and outputs
- Use `default` values for non-sensitive variables where appropriate

## Review / Approval  
Each pull request must be reviewed by at least one platform engineer to verify compliance with these instructions before merge.

## Example Naming Pattern
```
rg-func-dev           # Resource Group
st<env><random>       # Storage Account (e.g., stdev5kcj)
kv-<env>-<suffix>     # Key Vault (e.g., kv-dev-secrets)
func-<env>-<name>     # Function App (e.g., func-dev-api)
asp-<env>-<name>      # App Service Plan (e.g., asp-dev-premium)
ai-<env>-<name>       # Application Insights (e.g., ai-dev-monitoring)
law-<env>-<name>      # Log Analytics Workspace (e.g., law-dev-logs)
```
