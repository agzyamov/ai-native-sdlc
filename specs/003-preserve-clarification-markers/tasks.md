---

description: "Task list for preserve clarification markers feature implementation"
---

# Tasks: Preserve Clarification Questions in Workflow Mode

**Input**: Design documents from `/specs/003-preserve-clarification-markers/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - tasks will focus on implementation with manual testing via quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Project uses CI/CD workflow extension pattern:
- `.github/workflows/` for workflow modifications
- `.github/scripts/` for new automation scripts
- `function_app/` for ADO client extensions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure for new scripts

- [x] T001 Create `.github/scripts/` directory if it doesn't exist
- [x] T002 Verify Python 3.11 is available in GitHub Actions environment (ubuntu-latest)
- [x] T003 Verify existing workflow `.github/workflows/spec-kit-specify.yml` structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core marker detection logic that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add marker detection step to `.github/workflows/spec-kit-specify.yml` after spec generation step
- [x] T005 Implement detection logic using `grep -q '\[NEEDS CLARIFICATION:'` pattern from research.md
- [x] T006 Set GitHub Actions output variables: `markers_found` (true/false) and `marker_count` (0-3)

**Checkpoint**: Foundation ready - conditional workflow paths now work, user story implementation can proceed

---

## Phase 3: User Story 1 - Preserve Initial Spec with Clarification Markers (Priority: P1) 🎯 MVP

**Goal**: Ensure spec.md retains [NEEDS CLARIFICATION] markers and ADO Description is updated with marked version (not auto-resolved)

**Independent Test**: Trigger workflow with ambiguous Feature → verify spec.md contains markers → verify ADO Description has markers

### Implementation for User Story 1

- [x] T007 [US1] Add environment variable `PRESERVE_CLARIFICATION_MARKERS=true` to workflow YAML in spec generation step
- [x] T008 [US1] Update workflow step "Update ADO Feature Description" to use spec.md with markers (verify it reads from correct file path)
- [x] T009 [US1] Add conditional check: only update ADO Description if workflow completed successfully (existing behavior validation)
- [x] T010 [US1] Add workflow logging to output whether markers were preserved or not (echo statement in workflow)

**Checkpoint**: User Story 1 complete - spec.md preserves markers, ADO Description updated with marked version

---

## Phase 4: User Story 2 - Extract Clarification Questions to Dedicated File (Priority: P1)

**Goal**: Auto-generate clarifications.md file with structured questions when markers exist

**Independent Test**: Generate spec with markers → verify clarifications.md exists → verify format matches contracts/clarifications-format.md

### Implementation for User Story 2

- [x] T011 [P] [US2] Create Python script `.github/scripts/extract-clarifications.py` using code from quickstart.md Step 2
- [x] T012 [P] [US2] Implement `extract_markers()` function with regex pattern `\[NEEDS CLARIFICATION:\s*([^\]]+)\]` from research.md
- [x] T013 [US2] Implement `generate_clarifications_md()` function to create structured output per contracts/clarifications-format.md
- [x] T014 [US2] Add context extraction logic (200 char window before/after marker, sentence boundary heuristic from research.md)
- [x] T015 [US2] Add section header detection (search backwards for `##` pattern) to populate "Spec Section" field
- [x] T016 [US2] Add command-line argument parsing: `--spec-file`, `--output`, `--feature-name`
- [x] T017 [US2] Make script executable with `chmod +x .github/scripts/extract-clarifications.py`
- [x] T018 [US2] Add workflow step "Extract Clarifications" conditional on `markers_found == 'true'` in `.github/workflows/spec-kit-specify.yml`
- [x] T019 [US2] Configure workflow step to call Python script with correct file paths from `steps.create_feature.outputs`

**Checkpoint**: User Story 2 complete - clarifications.md auto-generated when markers present

---

## Phase 5: User Story 3 - Auto-Create ADO Issue Work Items (Priority: P1)

**Goal**: Create ADO Issue work items with Parent-Child links to Feature for each clarification question

**Independent Test**: Generate spec with markers → verify Issues created in ADO → verify Parent-Child links → verify idempotency on re-run

### Implementation for User Story 3

- [x] T020 [P] [US3] Extend `function_app/ado_client.py` with `create_issue_workitem()` function using code from quickstart.md Step 4
- [x] T021 [US3] Implement idempotency check using WIQL query searching for existing Issues with matching idempotency key
- [x] T022 [US3] Implement Issue creation using ADO REST API 7.0 with JSON Patch format per contracts/ado-issue-creation.md
- [x] T023 [US3] Add Parent-Child relationship creation using `System.LinkTypes.Hierarchy-Reverse` relation type
- [x] T024 [US3] Add error handling and logging for Issue creation failures (partial success scenario from edge cases)
- [x] T025 [P] [US3] Create Bash orchestrator script `.github/scripts/create-ado-issues.sh` using code from quickstart.md Step 3
- [x] T026 [US3] Implement argument parsing in Bash script: `--clarifications-file`, `--feature-id`, `--branch`, `--org`, `--project`
- [x] T027 [US3] Add markdown parsing logic to extract questions from clarifications.md (use grep/awk or embedded Python)
- [x] T028 [US3] Implement loop to create one Issue per question, calling `create_issue_workitem()` for each
- [x] T029 [US3] Add idempotency key generation: `${FEATURE_ID}-${sha256_hash[:8]}` pattern from research.md
- [x] T030 [US3] Make Bash script executable with `chmod +x .github/scripts/create-ado-issues.sh`
- [x] T031 [US3] Add workflow step "Create ADO Issues for Clarifications" conditional on `markers_found == 'true'` in `.github/workflows/spec-kit-specify.yml`
- [x] T032 [US3] Configure workflow environment variables: `ADO_WORKITEM_RW_PAT`, `ADO_ORG`, `ADO_PROJECT`, `FEATURE_ID`

**Checkpoint**: User Story 3 complete - ADO Issues auto-created with proper links and idempotency

---

## Phase 6: User Story 4 - Overwrite ADO Description with Marked Spec (Priority: P2)

**Goal**: Ensure ADO Feature Description field contains exact spec content with markers (consistency check)

**Independent Test**: Generate spec with markers → verify ADO PATCH uses marked version → verify ADO UI shows markers

### Implementation for User Story 4

- [x] T033 [US4] Verify existing workflow step "Update ADO Feature Description" reads from correct spec.md path (not cached version)
- [x] T034 [US4] Add validation that PATCH request payload contains raw spec content with markers intact
- [x] T035 [US4] Add retry logic with exponential backoff for transient ADO API failures per research.md decisions
- [x] T036 [US4] Add logging to confirm Description field was updated successfully with marker preservation

**Checkpoint**: User Story 4 complete - ADO Description always reflects spec.md content including markers

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and workflow improvements

- [x] T037 [P] Run `actionlint .github/workflows/spec-kit-specify.yml` to validate workflow YAML syntax
- [x] T038 [P] Add workflow execution summary comment showing: markers found (Y/N), clarifications created (Y/N), Issues created count
- [x] T039 [P] Update quickstart.md testing instructions if any implementation details differ from design
- [ ] T040 Test end-to-end workflow per quickstart.md Step 5.1 (ambiguous Feature - markers expected)
- [ ] T041 Test happy path workflow per quickstart.md Step 5.3 (clear Feature - no markers expected)
- [ ] T042 Verify idempotency by re-running workflow on same Feature (no duplicate Issues created)
- [ ] T043 [P] Commit all changes with message format: "feat: preserve clarification markers in workflow mode (US1-4)"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P1 → P1 → P2)
  - Or in parallel if team has capacity (US1/US2/US3 can partially overlap)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent from US1 (different files)
- **User Story 3 (P1)**: Depends on US2 completion (needs clarifications.md to exist) - But can develop ado_client extension in parallel
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent from all other stories (validates existing behavior)

### Within Each User Story

**US1**: Sequential (environment variable → description update → validation → logging)

**US2**: 
- T011-T017 can be done in parallel (Python script development)
- T018-T019 must follow T017 (workflow integration after script ready)

**US3**:
- T020-T024 and T025-T030 can be done in parallel (ADO client extension vs Bash orchestrator)
- T031-T032 must follow both groups (workflow integration after both scripts ready)

**US4**: Sequential (verification → validation → retry → logging)

### Parallel Opportunities

- **Setup phase**: T001-T003 can run in parallel
- **Foundational phase**: T004-T006 must be sequential (modify same file)
- **US2 implementation**: T011-T012 in parallel (Python script files)
- **US3 implementation**: T020-T024 in parallel with T025-T030 (two separate scripts)
- **Polish phase**: T037-T039 and T043 can run in parallel

---

## Parallel Example: User Story 3

```bash
# Launch ADO client extension and Bash orchestrator in parallel:
Task: "Extend function_app/ado_client.py with create_issue_workitem()"
Task: "Create Bash orchestrator .github/scripts/create-ado-issues.sh"

# After both complete, integrate into workflow:
Task: "Add workflow step with environment variables"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - enables conditional workflow)
3. Complete Phase 3: User Story 1 (marker preservation)
4. Complete Phase 4: User Story 2 (clarifications.md extraction)
5. Complete Phase 5: User Story 3 (ADO Issues creation)
6. **STOP and VALIDATE**: Test with ambiguous Feature (markers path) and clear Feature (no markers path)
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Conditional workflow ready
2. Add User Story 1 → Test marker preservation independently
3. Add User Story 2 → Test clarifications file generation independently
4. Add User Story 3 → Test Issue creation independently
5. Add User Story 4 → Test ADO Description consistency (validation only)
6. Each story adds value without breaking previous stories

### Sequential Team Strategy (Recommended)

With one developer:

1. Complete Setup + Foundational together
2. Implement US1 → Test → Commit
3. Implement US2 → Test → Commit
4. Implement US3 → Test → Commit
5. Implement US4 → Test → Commit
6. Polish and end-to-end validation

### Parallel Team Strategy (Optional)

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 4 (both touch ADO Description logic)
   - Developer B: User Story 2 (Python extraction script)
   - Developer C: User Story 3 (ADO Issues creation - depends on US2 output format)
3. Stories integrate at Phase 7 polish

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable per acceptance scenarios
- Stop at any checkpoint to validate story independently
- Testing strategy: Manual testing per quickstart.md (no automated tests requested in spec)
- Workflow modifications should be done incrementally with commits after each user story
- Always validate with `actionlint` before committing workflow changes
