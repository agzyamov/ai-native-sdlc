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

- [ ] T001 Create placeholder pipeline design note in `specs/001-ado-github-spec/plan.md` (already present – verify, no edit if consistent)
- [ ] T002 Add secret `ADO_WORKITEM_RW_PAT` to GitHub repository settings (external action; document completion in `quickstart.md`)
- [ ] T003 Add rotation note for tokens in `specs/001-ado-github-spec/quickstart.md` (verify existing text; adjust if missing interval)
- [ ] T004 [P] Validate `.github/workflows/spec-kit-specify.yml` exists and is syntactically valid (actionlint) (no content change yet)
- [ ] T005 [P] Add local developer note in `README.md` referencing feature quickstart (documentation cross-link)

## Phase 2: Foundational (Blocking Prerequisites)
Purpose: Core modifications required before story logic executes.

- [ ] T006 Insert new workflow inputs (`work_item_id`, `branch_hint`) scaffold into `.github/workflows/spec-kit-specify.yml` (commented / no-op until dispatch path finalized)
- [ ] T007 Implement ADO Description PATCH step in `.github/workflows/spec-kit-specify.yml` after spec generation commit (uses `ADO_WORKITEM_RW_PAT`)
- [ ] T008 [P] Add minimal retry (x2 exponential) around PATCH step (inline shell or composite action) in `.github/workflows/spec-kit-specify.yml`
- [ ] T009 [P] Document PATCH contract reference link inside workflow as comment (maintainability)
- [ ] T010 Remove residual intermediary (Azure Function) language from `plan.md` (if any stray references remain)

**Checkpoint**: Workflow can be manually triggered with manual inputs (temporary) and successfully overwrites an ADO work item Description in a dry run (using test ID).

## Phase 3: User Story 1 - Automatic Spec Generation (Priority: P1) 🎯 MVP
**Goal**: Trigger generation & overwrite automatically when Feature enters `Specification – Doing` with assignee AI Teammate.
**Independent Test**: Move qualifying Feature → verify spec commit + Description overwrite without manual workflow dispatch.

### Implementation (US1)
- [ ] T011 [US1] Author pipeline YAML `azure-pipelines-spec-dispatch.yml` (reintroduced from design) with clearly marked STUB validation
- [ ] T012 [P] [US1] Add `GH_WORKFLOW_DISPATCH_PAT` as secret pipeline variable (document completion in `quickstart.md`)
- [ ] T013 [P] [US1] Add Service Hook (Work Item Updated) → pipeline run (external action; record pipeline ID in `quickstart.md`)
- [ ] T014 [P] [US1] Enhance pipeline to attempt payload capture (log raw environment for diagnosis)
- [ ] T015 [US1] Add fallback path in pipeline: if payload missing, require `WORK_ITEM_ID` variable (documented in quickstart)
- [ ] T016 [US1] Add branch hint slugification (sanitized: lowercase, alnum + hyphen) inside pipeline dispatch step
- [ ] T017 [US1] Update workflow to use `branch_hint` if supplied, else compute default (comment guarding existing logic)
- [ ] T018 [US1] Add commit message enhancement including ADO Feature ID placeholder
- [ ] T019 [P] [US1] Add minimal logging (echo lines) around spec generation to surface debugging context
- [ ] T020 [US1] Manual end-to-end test: move test Feature → confirm pipeline triggers, workflow runs, Description overwritten (record test evidence in `responses/` directory)

**Checkpoint**: US1 end-to-end functional with a real Feature.

## Phase 4: Polish & Cross-Cutting
Purpose: Non-functional improvements after MVP verified.

- [ ] T021 [P] Add security note & rotation cadence doc section in `specs/001-ado-github-spec/quickstart.md` (if not sufficiently explicit)
- [ ] T022 [P] Add comment in pipeline YAML enumerating future debounce insertion point
- [ ] T023 Create Backlog cross-link comment inside `.github/workflows/spec-kit-specify.yml` referencing FR-004..FR-011
- [ ] T024 [P] Remove neutralized placeholder content if still present in root (clean any empty pipeline stubs)
- [ ] T025 Consolidate assumptions table in `plan.md` (mark those validated vs pending)

## Dependencies & Execution Order
1. Phase 1 completes (secrets & documentation alignment) → unlock Phase 2.
2. Phase 2 completes (workflow ready) → unlock Phase 3.
3. Phase 3 completes → MVP achieved; Phase 4 optional polish.

## User Story Dependency Graph
Only US1 in scope (P1) → no inter-story dependencies.

## Parallel Opportunities
- Setup validation tasks (T004, T005) parallel.
- Foundational PATCH enhancements (T008, T009) parallel after T007 merges.
- In US1: credential addition (T012) can occur while payload exploration (T014) and Service Hook config (T013) proceed.

## Implementation Strategy
1. Land workflow input + PATCH (Phase 2).
2. Stand up pipeline + hook (Phase 3).
3. Run manual E2E test (T020) → declare MVP.
4. Apply polish tasks opportunistically.

## MVP Completion Criteria
- T007 (overwrite) + T020 (E2E) completed successfully.

## Notes
- No automated tests added (deferred per research). Manual evidence suffices for pilot.
- Debounce left intentionally for Backlog (no code stub beyond comment).

---
*Generated via /speckit.tasks workflow adaptation (manual execution).* 