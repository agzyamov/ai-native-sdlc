# Implementation Plan: Azure DevOps → GitHub Spec Generation (MVP)

**Branch**: `001-ado-github-spec` | **Date**: 2025-10-27 | **Spec**: `specs/001-ado-github-spec/spec.md`
**Input**: Feature specification from `specs/001-ado-github-spec/spec.md`

**Note**: MVP reuses existing `spec-kit-specify.yml` workflow; no new workflow authoring in scope.

## Summary

Automate initial specification generation when an Azure DevOps Feature (Assigned To = AI Teammate) enters the "Specification – Doing" column. Detection triggers the existing reusable GitHub Actions workflow (`.github/workflows/spec-kit-specify.yml`) which runs Spec Kit to create (or reuse) a feature branch and generate the structured spec. The spec content overwrites the ADO Feature Description (authoritative spec-in-description principle). MVP excludes regeneration, advanced resilience, concurrency hardening, and performance SLO enforcement—all deferred in Backlog.

## Technical Context

**Language/Version**: GitHub Actions composite environment (YAML) + Bash; Spec Kit CLI (Python runtime 3.11 in workflow).  
**Primary Dependencies**: Existing `spec-kit-specify.yml` workflow (checkout, setup-node, setup-python, specify-cli via uv); Azure DevOps Service Hook (Work Item Updated) → Azure Function (HTTP trigger) → GitHub `workflow_dispatch`; Azure DevOps Work Item Update REST endpoint `PATCH https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{id}?api-version=7.0` (JSON Patch replace `/fields/System.Description`); secrets/app settings: `ADO_WORKITEM_RW_PAT` (Description overwrite), `GH_WORKFLOW_DISPATCH_PAT` (GitHub fine‑grained PAT: Actions RW, Contents R), `ADO_WORK_ITEM_PAT` (Work Items Read) used only inside Function for validation fetch.  
**Storage**: None (stateless; spec stored in Git + ADO work item Description).  
**Testing**: Minimal pilot checklist: (1) trigger via real Service Hook event, (2) confirm branch + `spec.md`, (3) verify Description overwrite, (4) second save in same column produces no duplicate branch. No automated harness in MVP (deferred).  
**Target Platform**: Cloud CI (GitHub Actions Ubuntu runners) & Azure DevOps Boards.  
**Project Type**: Single repository automation enhancement (no new runtime service).  
**Performance Goals**: Deferred (latency SLO in Backlog).  
**Constraints**: MUST not introduce new workflow states; MUST preserve Description-as-spec; MUST avoid partial Description merges (full overwrite).  
**Scale/Scope**: Pilot scale (<20 Features) initial; Backlog criteria for scale resilience.
**Infrastructure Provisioning (Principle 7)**: Terraform IaC REQUIRED before production for Azure Function + associated storage/plan; scaffold is PENDING (acceptable for pilot, blocks production hardening gate).

### Integration Flow (MVP) — Azure Function Variant (Pipeline Removed)
1. Azure DevOps Service Hook (Work Item Updated) POSTs raw event JSON to an Azure Function HTTPS endpoint secured by a function key (future: HMAC shared secret header).
2. Function extracts `resource.workItemId`; validates `eventType == workitem.updated`; 400 on malformed payload.
3. Function (if required) performs ADO REST fetch for full work item to obtain board column / assignee (GET work item). Validation rules:
  - Type == Feature
  - Assigned To matches configured AI teammate display name (case-insensitive)
  - Column/State == `Specification – Doing` (env configurable `SPEC_COLUMN_NAME`)
  - On any rule failure → 403 (no dispatch)
4. Derive `branch_hint = feature/wi-{id}` (title slug deferred) and invoke GitHub `workflow_dispatch` with inputs: `work_item_id`, `branch_hint`, `feature_description` placeholder.
5. GitHub workflow executes unchanged (generation + Description overwrite via `ADO_WORKITEM_RW_PAT` with retry on transient 5xx).
6. Function returns 204 on success (future: 202 for debounce short‑circuit). Structured log written (item id, validation result, dispatch status, latency ms).
7. Deprecated pipeline `.azure-pipelines/spec-dispatch.yml` retained temporarily for rollback but no longer part of active flow.
8. Debounce hashing, metrics export, and failure comment surfacing intentionally deferred to backlog.

Rationale: Service Hook payload shape incompatible with Pipelines Run API (`RunPipelineParameters`), causing 400 errors; Function provides flexible transformation + validation without extra CI hop (Principle 6: Direct Event Path).

### Known Reusable Assets
- `spec-kit-specify.yml` (short-name + generation + commit logic)
- Spec template + constitution (validated)

### Deferred / Provisional Items (Tracked in research.md)
| Item | Current Stance | Promotion Trigger |
|------|----------------|-------------------|
| ADO pipeline dispatch (Service Hook trigger) | Provisional (payload forwarding TBD) | Evolves with debounce/metrics |
| Debounce logic | Deferred | Observed duplicate dispatch noise |
| Automated test harness | Deferred | >10 pilot Features executed |
| Failure surfacing to ADO comment | Deferred | First meaningful failure or stakeholder request |
| Performance SLO enforcement | Deferred | Scale beyond pilot / Backlog activation |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The plan MUST explicitly confirm each gate below (FAIL any → plan not approvable):

| Gate | Pass Criteria | Status |
|------|---------------|--------|
| Spec Exit Integrity | No open clarification issues; acceptance checklist passed | OK |
| Story Independence | All listed user stories independently testable & prioritized (P1..N) | OK (single P1) |
| Minimal State Model | No added workflow states; only New→Specification→Planning→Validation→Ready referenced | OK |
| Quality Automation | Diagram + workflow validation steps documented (mermaid-cli, actionlint) | OK (steps in quickstart) |
| Complexity Justification | Any structural deviations justified in Complexity Tracking section | OK (none) |
| Direct Event Path (Principle 6) | No unnecessary intermediary hops in automation path | OK (pipeline removed) |
| IaC Declaration (Principle 7) | Durable infra declared via Terraform prior to production usage | PENDING (Terraform scaffold not yet created) |

Remediation: IaC Declaration gate PENDING — create `infra/` Terraform scaffold (Function App, Storage, Plan) before moving beyond pilot. Schedule: within current branch prior to enabling production secrets. Owner: AI Teammate.

Add a brief note if any gate is FAIL with remediation path and responsible owner.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
.github/workflows/
  spec-kit-specify.yml   # Existing reusable workflow (invoked by dispatch)
specs/
  001-ado-github-spec/
    spec.md
    plan.md
    research.md          # (to be generated Phase 0)
    data-model.md        # (to be generated Phase 1)
    quickstart.md        # (to be generated Phase 1)
    contracts/           # (to be generated Phase 1)
scripts/
  validate_diagrams.sh   # Mermaid validation (already present)
```

**Structure Decision**: Single-repo automation; reuse existing workflow; no new service code.

## Complexity Tracking

Current Deviation: Removed YAML pipeline hop; reinstated Azure Function to align payload format & enable richer validation before dispatch.

| Aspect | Previous (Pipeline) | Current (Function) | Risk | Mitigation |
|--------|---------------------|--------------------|------|------------|
| Event Validation | Stub (limited fields) | Full (fetch + rules) | Slight latency increase | Use short HTTP timeouts; skip redundant fetch if data present |
| Secret Distribution | Split (pipeline vars + GH secrets) | Consolidated (Function app settings) | Central secret compromise | Rotate PATs; future GitHub App integration |
| Debounce Implementation | Awkward (state external) | Straightforward (hash + store) | Not yet implemented | Backlog FR; design hash schema now |
| Observability | Minimal job logs | Structured JSON logs | Log noise | Introduce sampling / severity levels |
| Rollback | Hard (recreate function) | Simple (invoke manual workflow or resurrect pipeline) | Stale pipeline drift | Schedule deletion after Function GA |
| Infrastructure as Code | Not applicable (no runtime) | Required Terraform not yet authored | Drift / manual config risk | Add infra/ Terraform early; enforce plan in CI |

Status: Accepted; pipeline marked deprecated (scheduled removal by 2025-11-26); function path is prerequisite for future debounce & metrics enhancements; IaC compliance pending.
