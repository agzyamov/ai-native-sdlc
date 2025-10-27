# Quickstart: Azure DevOps → GitHub Spec Generation (MVP)

## Purpose
Run and validate the automatic spec generation loop for a pilot Feature.

## Prerequisites
- GitHub secrets:
  - `COPILOT_TOKEN` (existing)
  - `ADO_WORKITEM_RW_PAT` (Work Items Read/Write scope)
- Azure DevOps (planned) secure pipeline variables (not yet created until implementation begins):
  - `GH_WORKFLOW_DISPATCH_PAT` (scopes: repo workflows + contents:read)
- Pipeline YAML (`azure-pipelines-spec-dispatch.yml`) is DEFERRED (will be added at implementation start; intentionally removed to keep planning phase artifact-only).
- Service Hook configuration and pipeline binding will occur after pipeline file exists.
- Feature exists in Azure DevOps; AI machine user ("AI Teammate") identity present.

## One-Time Setup Checklist (To Execute During Implementation Phase)
1. Confirm workflow file: `.github/workflows/spec-kit-specify.yml` present.
2. Add GitHub secret `ADO_WORKITEM_RW_PAT`.
3. Add pipeline file `azure-pipelines-spec-dispatch.yml` (from design spec) to repository root.
4. Create Azure DevOps secret variable `GH_WORKFLOW_DISPATCH_PAT`.
5. Create Service Hook (Work Item Updated) → Pipeline Run API binding.
6. Validate mermaid & workflow tooling:
  - `./scripts/validate_diagrams.sh changed`
  - `actionlint .github/workflows/spec-kit-specify.yml`

## Automatic Trigger (Pipeline Variant – Planned)
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
