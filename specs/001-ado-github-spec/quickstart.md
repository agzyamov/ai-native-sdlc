# Quickstart: Azure DevOps → GitHub Spec Generation (MVP)

## Purpose
Run and validate the automatic spec generation loop for a pilot Feature.

## Prerequisites
- GitHub secrets:
  - `COPILOT_TOKEN` (existing)
  - `ADO_WORKITEM_RW_PAT` (Work Items Read/Write scope) ✅ **ACTION REQUIRED**: Add to GitHub repository settings
- Azure DevOps pipeline variables (T012 – **ACTION REQUIRED**):
  - `GH_WORKFLOW_DISPATCH_PAT` (scopes: repo workflows + contents:read) – Add as secret variable
  - `GITHUB_OWNER` – Your GitHub org/user (e.g., `agzyamov`)
  - `GITHUB_REPO` – Repository name (e.g., `ai-native-sdlc`)
  - `WORK_ITEM_ID` – (Temporary) Manual injection for testing until Service Hook payload forwarding resolved
- Pipeline YAML (`.azure-pipelines/spec-dispatch.yml`) ✅ **IMPLEMENTED** (T011 complete)
- Service Hook configuration (T013 – **ACTION REQUIRED** – see setup checklist below)
- Feature exists in Azure DevOps; AI machine user ("AI Teammate") identity present.

## One-Time Setup Checklist
1. ✅ Confirm workflow file: `.github/workflows/spec-kit-specify.yml` present (validated T004)
2. ✅ Add GitHub secret `ADO_WORKITEM_RW_PAT` (T002) - **COMPLETED**
   ```bash
   # Navigate to: Settings → Secrets and variables → Actions → New repository secret
   # Name: ADO_WORKITEM_RW_PAT
   # Value: <your-ado-pat-with-work-items-rw-scope>
   ```
3. ✅ Pipeline file `.azure-pipelines/spec-dispatch.yml` added to proper directory structure (T011)

4. ⚠️ **ACTION REQUIRED**: Create Azure DevOps pipeline from YAML file (T012 prerequisite)
   
   **Step-by-step:**
   1. Navigate to Azure DevOps: `https://dev.azure.com/{your-org}/{your-project}`
   2. Go to **Pipelines** → **Pipelines** → **New pipeline**
   3. Select **GitHub** (recommended - connects directly to your GitHub repo)
      - Authorize Azure Pipelines to access your GitHub account if prompted
      - Select repository: `agzyamov/ai-native-sdlc`
   4. Choose **Existing Azure Pipelines YAML file**
   5. Select branch: `001-ado-github-spec` (or your feature branch)
   6. Path: `/.azure-pipelines/spec-dispatch.yml`
   7. Click **Continue**, then **Save** (do not run yet)
   8. **Record pipeline ID** (visible in URL after save): `3` ✅
      - URL: `https://dev.azure.com/RustemAgziamov/ai-native-sdlc-blueprint/_build?definitionId=3`
   
   **Note:** This connects the pipeline to your GitHub repo for source code. The Service Hook (step 6) is what triggers the pipeline when work items update.

5. ✅ Configure Azure DevOps pipeline variables (T012) - **COMPLETED**
   
   **Step-by-step:**
   1. Go to **Pipelines** → select your newly created pipeline
   2. Click **Edit** → **Variables** (top right) → **New variable**
   3. Add the following variables:
      
      **Secret variable:**
      - Name: `GH_WORKFLOW_DISPATCH_PAT`
      - Value: `<your-github-pat>` (Fine-grained PAT repository permissions: **Actions: Read and write**, **Contents: Read**)
      - ✅ Check "Keep this value secret"
      - Click **OK**
      
      **Regular variables:**
      - Name: `GITHUB_OWNER`, Value: `agzyamov` (your GitHub username/org)
      - Name: `GITHUB_REPO`, Value: `ai-native-sdlc` (your repo name)
      - (Temporary for testing) Name: `WORK_ITEM_ID`, Value: `<test-feature-id>`
   
   4. Click **Save** (top right)

## Azure Function Deployment (Recommended Path)

**Status**: ✅ **IMPLEMENTED** - Replaces deprecated pipeline approach

The Azure Function directly handles Service Hook events and dispatches GitHub workflows without intermediary hops.

### Deploy Infrastructure

1. **Prerequisites**: Azure CLI authenticated, Terraform >= 1.6.0 installed

2. **Deploy via Terraform**:
   ```bash
   cd infra
   terraform init
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

3. **Set secrets** (via Azure Portal or CLI):
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

4. **Deploy function code**:
   ```bash
   cd ../function_app
   func azure functionapp publish $FUNCTION_NAME
   ```

5. **Get function URL**:
   ```bash
   terraform output function_url
   ```

### Configure Service Hook

1. Navigate to Azure DevOps: **Project Settings** → **Service Hooks**
2. Click **Create Subscription** → **Web Hooks**
3. Configure trigger:
   - Event Type: **Work item updated**
   - Filters: (Optional) Work Item Type = Feature
4. Configure action:
   - URL: `<function_url>/api/spec-dispatch?code=<function_key>`
   - HTTP Headers: (none required)
5. Test and finish

### Manual Test

```bash
curl -X POST "<function_url>/api/spec-dispatch?code=<key>" \
  -H "Content-Type: application/json" \
  -d @specs/001-ado-github-spec/contracts/sample-ado-hook.json
```

Expected response: HTTP 204 (success) or 403 (validation failed)

---

## ⚠️ DEPRECATED: Azure Pipelines Approach

**Status**: Deprecated (scheduled removal 2025-11-26). Retained for rollback only.

The Pipeline Run API requires a specific JSON format (`{"resources": {...}}`) that doesn't match the Service Hook payload structure, causing 400 errors. Use the Azure Function approach above instead.

<details>
<summary>View deprecated pipeline instructions (click to expand)</summary>

6. ⚠️ **DEFERRED**: Automatic Service Hook triggering (T013)
   
   **Status**: The Pipeline Run API requires a specific JSON format (`{"resources": {...}}`) that doesn't match the Service Hook payload structure. Service Hooks send the full work item event payload, causing 400 Bad Request errors.
   
   **MVP Approach**: Manual pipeline testing
   - Go to **Pipelines** → select **spec-dispatch** pipeline → **Run pipeline**
   - Uses `WORK_ITEM_ID` variable configured in step 5
   - Validates full integration: Pipeline → GitHub workflow → ADO Description update
   
   **Future Options** (requires additional dependencies):
   - **Azure Function**: Transform Service Hook payload to Pipeline API format
   - **Logic App**: Same transformation via low-code workflow
   - **Azure Pipelines Service Hook**: Native integration (not available in your org)

</details>

---

## Automatic Trigger (Function Variant)
1. Assign Feature to AI Teammate and move to `Specification – Doing`.
2. Service Hook POSTs event to Azure Function.
3. Function validates (type, assignee, column) and dispatches GitHub workflow.
4. GitHub workflow generates spec and overwrites ADO Description.

## Manual Fallback
1. Run GitHub Action manually providing required inputs (work_item_id, branch_hint).
2. Ensure `ADO_WORKITEM_RW_PAT` secret exists in GitHub.

## Expected Outcomes
| Step | Outcome |
|------|---------|
| Workflow completes | New or existing feature branch contains `spec.md` |
| Overwrite step | ADO Feature Description replaced with structured spec |
| Re-run (no changes) | No duplicate branch; spec remains stable |

## Performance Measurement

Monitor function execution time via structured logs:

```bash
# Extract latency from Application Insights or function logs
# Example log entry:
# {"correlation_id": "abc123", "work_item_id": 123, "latency_ms": 1250, "event": "dispatch_success"}

# Median latency should be < 3000ms (3 seconds) for MVP
# P95 latency target: < 5000ms (5 seconds)
```

**Log Extraction**:
- Azure Portal → Function App → Log stream
- Application Insights → Logs → Query:
  ```kusto
  traces
  | where message contains "latency_ms"
  | extend latencyMs = toint(parse_json(message).latency_ms)
  | summarize median=percentile(latencyMs, 50), p95=percentile(latencyMs, 95)
  ```

## Verification Commands (Optional Local)
```bash
# List feature branch
git fetch --all
git checkout 001-ado-github-spec
ls specs/001-ado-github-spec/
```

## ADO Description Overwrite (Pseudo Curl)
```bash
curl -X PATCH \
  -H "Content-Type: application/json-patch+json" \
  -H "Authorization: Basic $(echo -n :$ADO_WORKITEM_RW_PAT | base64)" \
  https://dev.azure.com/<org>/<project>/_apis/wit/workitems/<featureId>?api-version=7.0 \
  -d @payload.json
```
`payload.json` contains replacement JSON Patch defined in `contracts/README.md`.

## Failure Triage (MVP)
| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| Pipeline not starting | Service Hook POST auth failure | Re-check PAT & hook URL |
| Workflow not triggered | Dispatch step failed in pipeline | Inspect pipeline logs; validate PAT scopes |
| 401 from GitHub dispatch | `GH_WORKFLOW_DISPATCH_PAT` expired | Rotate PAT in pipeline variables |
| Description unchanged | Missing `ADO_WORKITEM_RW_PAT` or PATCH failure | Check workflow logs for PATCH status |
| Duplicate generation | Rapid column toggles | Backlog debounce item |

## Azure Function Environment Variables

The deployed Azure Function requires the following environment variables (configured via Terraform or Azure Portal):

### Required Configuration
| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_OWNER` | GitHub repository owner | `agzyamov` |
| `GITHUB_REPO` | GitHub repository name | `ai-native-sdlc` |
| `GITHUB_WORKFLOW_FILENAME` | Workflow file name | `spec-kit-specify.yml` |
| `SPEC_COLUMN_NAME` | ADO column that triggers spec generation | `Specification – Doing` |
| `AI_USER_MATCH` | AI teammate display name (case-insensitive) | `AI Teammate` |

### Required Secrets (Set via Azure Portal)
| Secret | Description | Scope |
|--------|-------------|-------|
| `GH_WORKFLOW_DISPATCH_PAT` | GitHub fine-grained PAT | Actions: Read/Write, Contents: Read |
| `ADO_WORK_ITEM_PAT` | Azure DevOps PAT | Work Items: Read |

### Optional Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `FUNCTION_TIMEOUT_SECONDS` | Max execution time | `30` |

## Security Notes
- Two trust planes: ADO (dispatch PAT) and GitHub (ADO write PAT). Keep scopes minimal.
- Rotate both PATs every 90 days.
- If adopting GitHub App later: remove `GH_WORKFLOW_DISPATCH_PAT` and map function to App token exchange.

## Assumptions & Caveats (Design Stage)
| Assumption | Status | Risk | Mitigation |
|------------|--------|------|------------|
| Service Hook → Pipeline Run API feasible | Unverified | Pipeline path blocked | Fallback to direct GitHub dispatch |
| Payload accessible in pipeline | Unverified | Validation stub remains | Introduce relay or ADO REST fetch |
| Column name stable | Likely | Filter breakage | Variable-driven column name |
| Title safe for slug | Variable | Invalid branch | Slugify + fallback to id |

## Next Expansion (Backlog Hooks)
- Debounce hashing
- Regen mode support
- Failure comment posting to ADO

---
MVP loop validated once a Feature transitions and Description reflects generated spec.
