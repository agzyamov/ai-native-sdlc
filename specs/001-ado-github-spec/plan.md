# Implementation Plan: Azure DevOps → GitHub Spec Generation (MVP)

**Branch**: `001-ado-github-spec` | **Date**: 2025-10-27 | **Spec**: `specs/001-ado-github-spec/spec.md`
**Input**: Feature specification from `specs/001-ado-github-spec/spec.md`

**Note**: MVP reuses existing `spec-kit-specify.yml` workflow; no new workflow authoring in scope.

## Summary

Automate initial specification generation when an Azure DevOps Feature (Assigned To = AI Teammate) enters the "Specification – Doing" column. Detection triggers the existing reusable GitHub Actions workflow (`.github/workflows/spec-kit-specify.yml`) which runs Spec Kit to create (or reuse) a feature branch and generate the structured spec. The spec content overwrites the ADO Feature Description (authoritative spec-in-description principle). MVP excludes regeneration, advanced resilience, concurrency hardening, and performance SLO enforcement—all deferred in Backlog.

## Technical Context

**Language/Version**: GitHub Actions composite environment (YAML) + Bash; Spec Kit CLI (Python runtime 3.11 in workflow).  
**Primary Dependencies**: Existing `spec-kit-specify.yml` workflow (checkout, setup-node, setup-python, specify-cli via uv); Azure DevOps Service Hook (Work Item Updated + board column) → Azure Function proxy; Azure DevOps Work Item Update REST endpoint `PATCH https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{id}?api-version=7.0` (JSON Patch replace `/fields/System.Description`); secrets: `ADO_WORKITEM_RW_PAT` (Description overwrite) and `GH_WORKFLOW_DISPATCH_PAT` (workflow_dispatch PAT stored only in Function config).  
**Storage**: None (stateless; spec stored in Git + ADO work item Description).  
**Testing**: Minimal pilot checklist: (1) trigger via real Service Hook event, (2) confirm branch + `spec.md`, (3) verify Description overwrite, (4) second save in same column produces no duplicate branch. No automated harness in MVP (deferred).  
**Target Platform**: Cloud CI (GitHub Actions Ubuntu runners) & Azure DevOps Boards.  
**Project Type**: Single repository automation enhancement (no new runtime service).  
**Performance Goals**: Deferred (latency SLO in Backlog).  
**Constraints**: MUST not introduce new workflow states; MUST preserve Description-as-spec; MUST avoid partial Description merges (full overwrite).  
**Scale/Scope**: Pilot scale (<20 Features) initial; Backlog criteria for scale resilience.

### Integration Flow (MVP) — Pipeline Variant (No Azure Function)
1. Azure DevOps Service Hook (Work Item Updated) invokes Azure DevOps Pipelines Run REST API (assumption: permitted via Service Hook Web Hook using PAT Basic auth) to start dedicated YAML pipeline `azure-pipelines-spec-dispatch.yml`.
2. Pipeline job downloads the triggering event body (passed verbatim by Service Hook) from predefined file (`event.json`) or environment variable (assumption: service hook POST body is forwarded to pipeline as `SYSTEM_WEBHOOK_PAYLOAD`; if not, a thin relay may be required — documented in assumptions).
3. Pipeline Bash step parses work item id, new board column, work item type, assignee; validates: column == `Specification – Doing`, type == Feature, Assigned To == AI Teammate.
4. On pass, pipeline derives `branch_hint` (slugified Title) and calls GitHub `workflow_dispatch` (PAT: `GH_WORKFLOW_DISPATCH_PAT`) supplying inputs: work_item_id, branch_hint.
5. GitHub Actions workflow: branch create/reuse → Spec Kit generation → PATCH overwrite of ADO Description via `ADO_WORKITEM_RW_PAT` (retry x2 on 5xx) → commit.
6. ADO feature shows updated Description + Development tab branch; human review moves to `Specification – Done` (no further automation in MVP).
7. If validation fails (wrong column/assignee), pipeline exits 0 (no-op) to avoid noise; logging retained for audit.

### Known Reusable Assets
- `spec-kit-specify.yml` (short-name + generation + commit logic)
- Spec template + constitution (validated)

### Deferred / Provisional Items (Tracked in research.md)
| Item | Current Stance | Promotion Trigger |
|------|----------------|-------------------|
| Intermediary function (Azure Function proxy) | Mandatory | Evolves with debounce/metrics |
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

Remediation: None pending for gates; remaining unknowns tracked in research.md.

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

Deviation Introduced (Post-Revision): Replaced earlier planned Azure Function intermediary with Azure DevOps YAML pipeline for validation + dispatch.

| Aspect | Original | Current | Risk | Mitigation |
|--------|----------|---------|------|------------|
| Event Validation | Function (rich payload) | Pipeline (stub validation) | False positives | Add payload relay or revert to direct dispatch if noise high |
| Secret Isolation | Function config | Split: ADO pipeline vs GitHub secrets | Slight sprawl | Consolidate under GitHub App later |
| Extensibility (debounce/metrics) | High (code) | Medium (scripts) | Added effort later | Backlog item to migrate to Function/App if complexity grows |
| Work Item Context Access | Direct re-fetch in Function | Not implemented (would happen in GitHub step only) | Missed pre-dispatch filter | Add ADO REST fetch in pipeline if payload accessible |

Status: Accepted for MVP per user directive (eliminate Azure Function dependency).
