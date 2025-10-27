# Research & Resolution: Azure DevOps → GitHub Spec Generation (Phase 0)

## Overview
This document resolves (or establishes resolution paths for) all NEEDS CLARIFICATION items in the plan's Technical Context. Critical items (must decide before implementation) are prioritized over deferrable items.

## Decision Log Format
Each entry:
- Decision: Final or Provisional
- Rationale: Why chosen
- Alternatives Considered: Summary
- Follow-up: Action if provisional

## Decisions

### 1. Trigger Transport (ADO → GitHub)
- Decision: Provisional – Azure DevOps Service Hook (Work Item Updated) directly starts dedicated Azure DevOps YAML pipeline via Pipeline Run REST API (Web Hook using PAT) which then invokes GitHub workflow_dispatch.
- Rationale: Removes Azure Function dependency per updated requirement; keeps validation logic in pipeline script.
- Alternatives Considered: (a) Azure Function proxy (removed to reduce dependencies); (b) Direct Service Hook → GitHub dispatch (harder to extend for future debounce); (c) Self-hosted relay (unnecessary ops overhead).
- Follow-up: Validate feasibility of Service Hook → Pipeline Run API without intermediary; if infeasible, fall back to direct GitHub dispatch (update docs accordingly).

### 2. Authentication (ADO Pipeline → GitHub Dispatch)
- Decision: Final – Store a single GitHub PAT `GH_WORKFLOW_DISPATCH_PAT` directly as a secret pipeline variable (no variable group, no Key Vault). Use only for `workflow_dispatch` call. Keep the existing GitHub secret `ADO_WORKITEM_RW_PAT` for the Description PATCH inside the workflow.
- Rationale: Lowest effort: two minimal tokens in their native execution contexts (GitHub needs ADO PAT; ADO pipeline needs GitHub PAT). Avoids extra indirection (no Key Vault wiring, no variable-group governance upfront). Meets MVP needs with smallest setup surface.
- Alternatives Considered: Variable group (more clicks, not needed yet); Key Vault reference (overhead); GitHub App (higher initial complexity); Reusing one PAT for both directions (not possible—different platforms & scopes).
- Follow-up: None (upgrade path to GitHub App + service principal tracked in Backlog; only trigger is security hardening request or scale-out).

### 3. GitHub → ADO Description Overwrite Placement
- Decision: Final – Implement overwrite inside existing `spec-kit-specify.yml` workflow as a new step after spec file commit.
- Rationale: Workflow already has spec context (branch, path). Avoids separate integration job. Simplifies debugging.
- Alternatives: External post-commit service (adds latency); separate workflow triggered by `workflow_run` (longer chain).
- Follow-up: Add step guarded by presence of ADO credentials.

### 4. ADO Authentication for Description PATCH
- Decision: Provisional – Use an ADO PAT stored as GitHub Actions secret `ADO_WORKITEM_RW_PAT` with minimal scope (Work Items Read & Write).
- Rationale: Simple; fast to implement. Service Principal alternative overkill for MVP.
- Alternatives: OAuth app (longer setup); Service connection with pipeline (complicates reuse).
- Follow-up: Create secret pre-merge; document rotation process in quickstart.

### 5. Description PATCH Mechanism
- Decision: Final – Direct REST call: `PATCH https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{id}?api-version=7.0` with JSON Patch operation replacing `/fields/System.Description` with full markdown body.
- Rationale: Aligns with ADO API standard; full overwrite requirement satisfied.
- Alternatives: Partial field merge (violates overwrite principle); UI automation (fragile).
- Follow-up: Provide sample curl in quickstart.

### 6. Idempotency / Debounce Strategy
- Decision: Provisional – Phase 0: Rely on column + assignee change uniqueness. No explicit debounce window. Document risk of rapid toggles producing duplicate dispatches.
- Rationale: Avoid premature complexity; low pilot volume.
- Alternatives: Hash of prior Description stored in tag (needs extra ADO field); time-based suppression cache (needs storage).
- Follow-up: Backlog FR-008 activation can introduce hash-based guard.

### 7. Automated Testing Approach (Workflow)
- Decision: Provisional – Live Service Hook E2E validation only; optional `act` for spec generation. No formal harness in MVP.
- Rationale: Keeps scope minimal; real event path validated directly.
- Alternatives: Dedicated integration harness (overhead), pipeline simulation (latency, complexity).
- Follow-up: Promote harness once >10 Features processed.

### 8. Error Handling (Failure Visibility)
- Decision: Provisional – Rely on GitHub Actions run status + ADO revision history. No automatic comment or status posted back.
- Rationale: Deferred per Backlog FR-005.
- Alternatives: Post failure note to ADO Discussion; create child Issue automatically.
- Follow-up: Activate with FR-005.

### 9. Security Review Scope
- Decision: Final – Limit tokens to least privilege; no storing tokens in code; rotate every 90 days (policy note only).
- Rationale: Aligns with standard minimal exposure practice.
- Alternatives: GitHub App (deferred) provides finer scopes but time cost now.
- Follow-up: Track migration pathway in Backlog narrative.

## Open Items After Phase 0
| Item | Status | Deferral Justification | Promotion Trigger |
|------|--------|------------------------|-------------------|
| Debounce mechanism | Deferred | Low volume pilot | Duplicate trigger observed |
| Automated workflow tests | Deferred | Pilot manual suffices | >10 features onboarded |
| Failure surfaced to ADO | Deferred | Non-critical MVP | Stakeholder request or >1 failure |

## Summary
Critical unknowns resolved (transport pattern flexible via intermediary, in-workflow overwrite, token handling). Remaining items are intentionally deferred with clear triggers. Proceed to Phase 1.
