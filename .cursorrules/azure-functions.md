# Azure Functions Deployment

## Critical: Remote Build

**CRITICAL: Always use remote build for Python Azure Functions deployments.**

### Quick Deployment Steps

For `function_app/` to Azure Functions:

```bash
cd function_app
zip -r function.zip . -x "*.venv*" -x "*__pycache__*" -x "*.python_packages*" -x "tests/*" -x "*.md"
az functionapp deployment source config-zip \
  --resource-group rg-func-dev \
  --name func-dev-dispatch \
  --src function.zip \
  --build-remote true
rm function.zip
```

### Detailed Guidelines

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
   - `ENABLE_ORYX_BUILD` defaults to `true` for Linux (per Microsoft docs)
   - Installs dependencies on Azure (not from local venv)
   - Ensures proper function discovery and loading

3. **Never deploy with local virtual environment**:
   - ❌ Don't include `.venv`, `.venv311`, or `.python_packages` in deployment zip
   - ❌ Don't set `WEBSITE_RUN_FROM_PACKAGE=1` with remote build
   - ✅ Always exclude virtual environments from zip
   - ✅ Let Azure build environment on server

4. **Premium Plan File Share Pitfall** ⚠️:
   - Premium plans use Azure Files share for content by default
   - Deployment with `config-zip --build-remote true` deploys to `/site/wwwroot/`
   - **BUT** function runtime reads from Azure Files share (if configured)
   - Result: Deployments succeed but code never updates!
   
   **Solution**: Remove file share settings from app configuration:
   - ❌ Remove `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING`
   - ❌ Remove `WEBSITE_CONTENTSHARE`
   - ❌ Remove `WEBSITE_CONTENTOVERVNET`
   - ✅ Function will run from `/site/wwwroot/` where deployments actually go
   - ✅ Deployment updates will work correctly

5. **Troubleshooting "0 functions found" or "Code not updating"**:
   - Check if deployment didn't use remote build
   - Redeploy with `--build-remote true` flag
   - Check logs show "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
   - **Check file timestamps** in `/site/wwwroot/` vs deployment time
   - If timestamps don't match, remove file share settings (Premium plan issue)

**Reference**: [Microsoft Docs - Deployment technologies](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-technologies)

## Function App Configuration

### Required App Settings

```bash
FUNCTIONS_EXTENSION_VERSION=~4
WEBSITE_RUN_FROM_PACKAGE=1
AzureWebJobsStorage__accountName=<storage-account-name>
```

### Managed Identity

Always use Managed Identity for storage connections:
- Set `storage_uses_managed_identity = true` in Terraform
- Assign RBAC roles: `Storage Blob Data Owner`, `Storage Queue Data Contributor`, `Storage Table Data Contributor`, `Storage File Data Privileged Contributor`
- Use `AzureWebJobsStorage__accountName` instead of connection string

### Key Vault References

Use Key Vault references for secrets:

```bash
GITHUB_TOKEN=@Microsoft.KeyVault(SecretUri=https://kv-name.vault.azure.net/secrets/secret-name/)
```

## Function Code Structure

### Entry Point

```python
import azure.functions as func

app = func.FunctionApp()

@app.route(route="endpoint-name", auth_level=func.AuthLevel.FUNCTION)
def function_name(req: func.HttpRequest) -> func.HttpResponse:
    """Function docstring."""
    # Implementation
    return func.HttpResponse("Response", status_code=200)
```

### Error Handling

Always return appropriate HTTP status codes:
- `200`: Success (or `204` for no content)
- `400`: Bad request (malformed payload)
- `403`: Forbidden (validation failed)
- `500`: Internal server error

### Logging

Use structured logging with correlation IDs:

```python
import logging
import uuid
from datetime import datetime

correlation_id = str(uuid.uuid4())
logger = logging.getLogger(__name__)
logger.info(f"Request started - correlation_id={correlation_id}")
```

## Testing

### Local Testing

```bash
cd function_app
func start
```

### Test with Sample Payload

```bash
curl -X POST http://localhost:7071/api/endpoint-name \
  -H "Content-Type: application/json" \
  -d @sample-payload.json
```

## Related Rules

- See [python.md](python.md) for Python coding standards
- See [azure-infrastructure.md](azure-infrastructure.md) for security requirements
- See [terraform.md](terraform.md) for infrastructure configuration

