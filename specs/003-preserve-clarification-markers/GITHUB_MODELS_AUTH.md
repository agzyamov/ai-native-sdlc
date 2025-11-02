# GitHub Models API Authentication Fix

## Problem

GitHub Actions workflow failed with authentication error when calling GitHub Models API:
```
Error: 401/403 - Unauthorized access to https://models.inference.ai.azure.com
```

**Root Cause**: The default `GITHUB_TOKEN` provided by GitHub Actions **does not have** the `models: read` permission required to access GitHub Models API.

## Solution

Create a **fine-grained Personal Access Token (PAT)** with `models: read` permission and add it as a repository secret.

### Step 1: Create Fine-Grained PAT

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Click **Generate new token**
3. Configure token:
   - **Token name**: `GitHub Models API Token`
   - **Description**: `Access GitHub Models API for spec clarification extraction`
   - **Expiration**: 90 days (or custom)
   - **Repository access**: Select **Only select repositories** → Choose `ai-native-sdlc`
   - **Permissions** → **Repository permissions**:
     - **Models**: Select **Read-only** ✅
   - **Account permissions**: (none needed)

4. Click **Generate token**
5. **Copy the token** (starts with `github_pat_...`)

**IMPORTANT**: You do NOT need any other permissions! Only `models: read` is required.

### Step 2: Add Token as Repository Secret

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Configure secret:
   - **Name**: `GITHUB_MODELS_TOKEN`
   - **Value**: Paste the PAT from Step 1
4. Click **Add secret**

### Step 3: Workflow Configuration

The workflow has been updated to use the new token:

```yaml
- name: Extract Clarifications
  if: steps.detect_markers.outputs.markers_found == 'true'
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_MODELS_TOKEN || secrets.GITHUB_TOKEN }}
  run: |
    # LLM extraction script uses GITHUB_TOKEN
    python3 .github/scripts/extract-clarifications-llm.py ...
```

**Fallback logic**: If `GITHUB_MODELS_TOKEN` is not set, falls back to `GITHUB_TOKEN` (for backward compatibility, but will fail with auth error).

### Step 4: Test

Re-run the workflow after adding the secret:

```bash
# Trigger workflow manually
gh workflow run spec-kit-specify.yml -f feature_description="create a squid game"
```

Expected result: LLM extraction succeeds, ADO Issues created with proper titles.

## Alternative: Use Azure OpenAI (Not Recommended)

If GitHub Models continues to have issues, you could switch to Azure OpenAI:

1. Create Azure OpenAI resource
2. Deploy `gpt-4o` model
3. Update `extract-clarifications-llm.py`:
   ```python
   client = OpenAI(
       base_url="https://<resource>.openai.azure.com/openai/deployments/<deployment>",
       api_key=os.getenv("AZURE_OPENAI_API_KEY"),
       default_headers={"api-version": "2024-06-01"}
   )
   ```
4. Add `AZURE_OPENAI_API_KEY` secret

**Not recommended because**: GitHub Models is free for GitHub Actions, Azure OpenAI costs money.

## References

- [Microsoft Docs: Aspire GitHub Models Integration](https://learn.microsoft.com/en-us/dotnet/aspire/github/github-models-integration)
- [Microsoft Docs: Azure AI Inference Client Library](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-inference-readme?view=azure-python-preview)
- [GitHub Docs: Fine-grained Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token)

## Status

- ✅ Workflow updated to use `GITHUB_MODELS_TOKEN`
- ⏸️ Waiting for PAT to be created and added as secret
- ⏸️ Re-run workflow to validate fix

## Next Steps

1. **You**: Create fine-grained PAT with `models: read` permission
2. **You**: Add `GITHUB_MODELS_TOKEN` secret to repository
3. **You**: Re-run workflow to validate
4. **Agent**: Monitor workflow logs for successful LLM extraction
