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
   8. **Record pipeline ID** (visible in URL after save): `____________`
      - URL format: `https://dev.azure.com/{org}/{project}/_build?definitionId={pipelineId}`
   
   **Note:** This connects the pipeline to your GitHub repo for source code. The Service Hook (step 6) is what triggers the pipeline when work items update.

5. ⚠️ **ACTION REQUIRED**: Configure Azure DevOps pipeline variables (T012)
   
   **Step-by-step:**
   1. Go to **Pipelines** → select your newly created pipeline
   2. Click **Edit** → **Variables** (top right) → **New variable**
   3. Add the following variables:
      
      **Secret variable:**
      - Name: `GH_WORKFLOW_DISPATCH_PAT`
      - Value: `<your-github-pat>` (scopes: `repo`, `workflow`)
      - ✅ Check "Keep this value secret"
      - Click **OK**
      
      **Regular variables:**
      - Name: `GITHUB_OWNER`, Value: `agzyamov` (your GitHub username/org)
      - Name: `GITHUB_REPO`, Value: `ai-native-sdlc` (your repo name)
      - (Temporary for testing) Name: `WORK_ITEM_ID`, Value: `<test-feature-id>`
   
   4. Click **Save** (top right)

6. ⚠️ **ACTION REQUIRED**: Create Service Hook (Work Item Updated) (T013)
   
   **Step-by-step:**
   1. Navigate to **Project Settings** (bottom left gear icon)
   2. Under **General**, select **Service hooks**
   3. Click **+ Create subscription**
   4. Select **Web Hooks** → **Next**
   
   **Trigger configuration:**
   - Event: **Work item updated**
   - Filters:
     - Area path: `{your-project}` (or leave blank for all)
     - Work item type: `Feature`
     - (Optional) Changed by: `AI Teammate` (to reduce noise)
   - Click **Next**
   
   **Action configuration:**
   - URL: `https://dev.azure.com/{org}/{project}/_apis/pipelines/{pipelineId}/runs?api-version=7.0`
     - Replace `{org}`, `{project}`, and `{pipelineId}` with your values
   - HTTP headers:
     ```
     Content-Type: application/json
     Authorization: Basic {base64-encoded-PAT}
     ```
     - To generate Base64 PAT: `echo -n ":{your-ado-pat}" | base64`
     - PAT scopes needed: **Build (read and execute)**
   - Resource details to send: **All**
   - Messages to send: **All**
   - Detailed messages to send: **All**
   
   5. Click **Test** to verify connection
   6. Click **Finish**
   
   **Troubleshooting:**
   - If test fails with 401: Check PAT is valid and has Build execute permission
   - If test fails with 404: Verify pipeline ID is correct
   - Check Service Hook history: Project Settings → Service hooks → select hook → History
6. ✅ Validate mermaid & workflow tooling (T004):
   - `./scripts/validate_diagrams.sh changed` (if diagrams modified)
   - `actionlint .github/workflows/spec-kit-specify.yml` (shellcheck warnings acceptable)## Automatic Trigger (Pipeline Variant – Planned)
1. Assign Feature to AI Teammate and move to `Specification – Doing`.
2. (Post-implementation) Service Hook will start Azure DevOps pipeline.
3. Pipeline will validate event and dispatch GitHub workflow.
4. GitHub workflow overwrites Description.

## Manual Fallback (Pre-Pipeline / Failure Scenario)
1. Run GitHub Action manually providing required inputs (as implemented at runtime).
2. Ensure `ADO_WORKITEM_RW_PAT` secret exists.

## Expected Outcomes
| Step | Outcome |
|------|---------|
| Workflow completes | New or existing feature branch contains `spec.md` |
| Overwrite step | ADO Feature Description replaced with structured spec |
| Re-run (no changes) | No duplicate branch; spec remains stable |

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

## Security Notes
- Two trust planes: ADO (dispatch PAT) and GitHub (ADO write PAT). Keep scopes minimal.
- Rotate both PATs every 90 days.
- If adopting GitHub App later: remove `GH_WORKFLOW_DISPATCH_PAT` and map pipeline to App token exchange.

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
