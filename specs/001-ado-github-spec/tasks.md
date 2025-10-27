---
description: "Implementation task list for Azure DevOps → GitHub Spec Generation (MVP)"
---

# Tasks: Azure DevOps → GitHub Spec Generation (MVP)

**Feature Directory**: `specs/001-ado-github-spec/`
**Primary User Story (P1)**: Automatic Spec Generation on Column Placement (US1)
**MVP Scope**: Only US1 (automatic generation + Description overwrite)
**Deferred**: Regen, debounce, failure surfacing, performance, telemetry

## Phase 1: Setup (Shared Infrastructure)
Purpose: Ensure repo + baseline tooling ready for integration changes.

- [X] T001 Create placeholder pipeline design note in `specs/001-ado-github-spec/plan.md` (already present – verify, no edit if consistent)
- [ ] T002 Add secret `ADO_WORKITEM_RW_PAT` to GitHub repository settings (external action; document completion in `quickstart.md`)
- [X] T003 Add rotation note for tokens in `specs/001-ado-github-spec/quickstart.md` (verify existing text; adjust if missing interval)
- [X] T004 [P] Validate `.github/workflows/spec-kit-specify.yml` exists and is syntactically valid (actionlint) (no content change yet)
- [X] T005 [P] Add local developer note in `README.md` referencing feature quickstart (documentation cross-link)

## Phase 2: Foundational (Blocking Prerequisites)
Purpose: Core modifications required before story logic executes.

- [X] T006 Insert new workflow inputs (`work_item_id`, `branch_hint`) scaffold into `.github/workflows/spec-kit-specify.yml` (commented / no-op until dispatch path finalized)
- [X] T007 Implement ADO Description PATCH step in `.github/workflows/spec-kit-specify.yml` after spec generation commit (uses `ADO_WORKITEM_RW_PAT`)
- [X] T008 [P] Add minimal retry (x2 exponential) around PATCH step (inline shell or composite action) in `.github/workflows/spec-kit-specify.yml`
- [X] T009 [P] Document PATCH contract reference link inside workflow as comment (maintainability)
- [X] T010 Remove residual intermediary (Azure Function) language from `plan.md` (if any stray references remain)

**Checkpoint**: Workflow can be manually triggered with manual inputs (temporary) and successfully overwrites an ADO work item Description in a dry run (using test ID).

## Phase 3: User Story 1 - Automatic Spec Generation (Priority: P1) 🎯 MVP
**Goal**: Trigger generation & overwrite automatically when Feature enters `Specification – Doing` with assignee AI Teammate.
**Independent Test**: Move qualifying Feature → verify spec commit + Description overwrite without manual workflow dispatch.

### Implementation (US1)
- [X] T011 [US1] Author pipeline YAML `.azure-pipelines/spec-dispatch.yml` (reintroduced from design) with clearly marked STUB validation
- [ ] T012 [P] [US1] Add `GH_WORKFLOW_DISPATCH_PAT` as secret pipeline variable (⚠️ **EXTERNAL ACTION** - document completion in `quickstart.md`)
- [ ] T013 [P] [US1] Add Service Hook (Work Item Updated) → pipeline run (⚠️ **EXTERNAL ACTION** - record pipeline ID in `quickstart.md`)
- [X] T014 [P] [US1] Enhance pipeline to attempt payload capture (log raw environment for diagnosis)
- [X] T015 [US1] Add fallback path in pipeline: if payload missing, require `WORK_ITEM_ID` variable (documented in quickstart)
- [X] T016 [US1] Add branch hint slugification (sanitized: lowercase, alnum + hyphen) inside pipeline dispatch step
- [X] T017 [US1] Update workflow to use `branch_hint` if supplied, else compute default (comment guarding existing logic)
- [X] T018 [US1] Add commit message enhancement including ADO Feature ID placeholder
- [X] T019 [P] [US1] Add minimal logging (echo lines) around spec generation to surface debugging context
- [ ] T020 [US1] Manual end-to-end test: move test Feature → confirm pipeline triggers, workflow runs, Description overwritten (⚠️ **BLOCKED** - requires T012 & T013 completion; record test evidence in `responses/` directory)

**Checkpoint**: US1 end-to-end functional with a real Feature.

---

description: "Task list for Azure DevOps → GitHub Spec Generation feature"

---

# Tasks: Azure DevOps → GitHub Spec Generation

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create `infra/` directory structure (infra/main.tf, infra/providers.tf, infra/variables.tf, infra/outputs.tf)
- [ ] T002 Initialize Terraform local backend (state kept local) in `infra/main.tf`
- [ ] T003 [P] Add Terraform provider block (azurerm + features) in `infra/providers.tf`
- [ ] T004 [P] Define Terraform variables (resource_group_name, function_app_name, github_owner, github_repo) in `infra/variables.tf`
- [ ] T005 Add infrastructure README stub at `infra/README.md` (purpose, apply steps)
- [ ] T006 Update `.gitignore` to include Terraform artifacts (`.terraform/`, `*.tfstate*`)
- [ ] T007 [P] Add mermaid + workflow validation reminder to `specs/001-ado-github-spec/quickstart.md`
- [ ] T008 Capture sample ADO Service Hook payload in `specs/001-ado-github-spec/contracts/sample-ado-hook.json`
- [ ] T009 [P] Document required function environment variables in quickstart (append section)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T010 Define Azure resources in `infra/main.tf` (resource group reuse variable, storage account, service plan, linux function app)
- [ ] T011 Add function app settings (SPEC_COLUMN_NAME, AI_USER_MATCH, GITHUB_REPO, GITHUB_OWNER placeholders) in `infra/main.tf`
- [ ] T012 [P] Add Terraform outputs (`function_name`, `function_default_hostname`) in `infra/outputs.tf`
- [ ] T013 Implement minimal Python Azure Function scaffold at `function_app/__init__.py` (HTTP trigger, parse JSON, 400 on missing resource.workItemId)
- [ ] T014 [P] Create `function_app/validation.py` with stub `validate_event(event: dict)` (checks eventType == workitem.updated)
- [ ] T015 [P] Create `function_app/dispatch.py` with placeholder `dispatch(work_item_id: int, branch_hint: str)` (TODO comment for network)
- [ ] T016 Add `requirements.txt` with pinned `azure-functions`, `requests`
- [ ] T017 Add `function_app/README.md` (env vars, flow overview)
- [ ] T018 Implement GitHub workflow dispatch POST (timeout=15s) in `function_app/dispatch.py`
- [ ] T019 Add structured JSON logging in `function_app/__init__.py` (correlation_id, work_item_id, dispatch_status)
- [ ] T020 Add dataclass `WorkItemEvent` in `function_app/models.py` (fields: work_item_id, event_type)
- [ ] T021 [P] Create `tests/test_validation.py` (happy path + invalid eventType)
- [ ] T022 Add idempotency inline comment in `function_app/__init__.py` (hash-based debounce deferred)
- [ ] T023 Verify plan.md complexity tracking IaC row; adjust if drift detected
- [ ] T024 Add pipeline removal task reference in plan.md Backlog section
- [ ] T025 [P] Add Terraform version constraint (`terraform { required_version = ">= 1.6.0" }`) in providers.tf

## Phase 3: User Story 1 - Automatic Spec Generation (Priority: P1)

Goal: End-to-end automatic spec generation when Feature enters Specification – Doing.
Independent Test: Move test Feature to Specification – Doing and verify: Function receives payload, workflow dispatched (GitHub run visible), `spec.md` committed, Description overwritten.

### Implementation Tasks

- [ ] T026 [US1] Implement full validation in `function_app/validation.py` (Feature type, assignee match, column match)
- [ ] T027 [US1] Create ADO client in `function_app/ado_client.py` (GET work item by id, timeout=15s)
- [ ] T028 [US1] Integrate ADO fetch fallback in `function_app/__init__.py` when column/assignee absent
- [ ] T029 [US1] Implement retry (3 attempts exponential backoff) for dispatch in `function_app/dispatch.py`
- [ ] T030 [US1] Map validation failure → 403 response in `function_app/__init__.py`
- [ ] T031 [US1] Derive `branch_hint = feature/wi-{id}` in `function_app/__init__.py`
- [ ] T032 [US1] Extract `work_item_id` defensively from payload (`resource.workItemId`) in `function_app/__init__.py`
- [ ] T033 [US1] Return 204 on successful dispatch (log latency ms) in `function_app/__init__.py`
- [ ] T034 [US1] Pass description placeholder to dispatch inputs
- [ ] T035 [US1] Add `function_app/config.py` loader for env vars & defaults
- [ ] T036 [US1] Add error classification (validation vs transport) to log output
- [ ] T037 [US1] Extend `tests/test_validation.py` with column/assignee negatives
- [ ] T038 [US1] Add `tests/test_dispatch.py` (mock `requests.post` success/failure)
- [ ] T039 [US1] Update `quickstart.md` replacing pipeline instructions with Function flow (mark pipeline deprecated)
- [ ] T040 [US1] Remove any pipeline references from `function_app/README.md`

### Completion Criteria
Tasks T026–T040 complete → Automatic generation loop validated via real or simulated event.

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T041 [P] Add debounce design placeholder (hash plan) in `function_app/__init__.py`
- [ ] T042 Implement correlation id utility (UUID4) in `function_app/util.py`
- [ ] T043 [P] Add structured logger abstraction in `function_app/logging.py`
- [ ] T044 Add timeout constants module `function_app/constants.py`
- [ ] T045 Create security review checklist `specs/001-ado-github-spec/security-review.md`
- [ ] T046 [P] Add Terraform variable descriptions & types in `infra/variables.tf`
- [ ] T047 [P] Document outputs usage in `infra/README.md`
- [ ] T048 Remove deprecated pipeline file after grace period (verify Function stability first)
- [ ] T049 Add CI workflow `.github/workflows/ci-infra-validation.yml` (terraform fmt + actionlint)
- [ ] T050 [P] Add retry behavior tests in `tests/test_dispatch.py`
- [ ] T051 Add 403 validation failure test in `tests/test_validation.py`
- [ ] T052 Add performance measurement note (latency log extraction) to `quickstart.md`
- [ ] T053 [P] Add manual curl test section to `function_app/README.md`
- [ ] T054 Add log sampling strategy comment in `function_app/logging.py`
- [ ] T055 [P] Add guidance for capturing Terraform plan artifact/screenshot in `infra/README.md`

## Dependencies & Execution Order

### Phase Dependencies
Setup → Foundational → User Story 1 → Polish

### User Story Dependencies
Only User Story 1 exists; begins after Foundational completion.

### Within User Story 1
Validation & ADO client before dispatch; retry after base dispatch; config before usage; tests may start once modules stubbed.

## Parallel Opportunities
- Setup: T003, T004, T007, T009
- Foundational: T012, T014, T015, T021, T025
- User Story 1: T026 & T027 parallel; T037 & T038 parallel after base modules
- Polish: T041, T043, T046, T047, T050, T053, T055

## Implementation Strategy
1. Finish Setup (T001–T009)
2. Build infra + scaffold (T010–T025)
3. Implement User Story 1 (T026–T040) → Validate E2E
4. Apply Polish selectively based on risk/time

## MVP Scope Recommendation
Complete through T040; optionally defer T049, T041 until stability proven.

## Notes
- All HTTP requests must include explicit `timeout`.
- Idempotency qualitative; hash-based debounce deferred.
- Remove pipeline only after Function reliability confirmed.