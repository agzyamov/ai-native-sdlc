# Tasks: ADO Process Change Alert

**Input**: Design documents from `/specs/005-ado-process-change-alert/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Tests ARE included - the plan.md specifies pytest and moto for testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md project structure:
- **Lambda Functions**: `aws_functions/`
- **Terraform Infrastructure**: `infra/terraform/`
- **Azure Bridge**: `infra/azure_bridge/`
- **Tests**: `tests/`
- **Fixtures**: `tests/fixtures/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and initialize dependencies

- [ ] T001 Create project structure per implementation plan (aws_functions/, tests/, infra/)
- [ ] T002 Initialize Python 3.11 project with pyproject.toml (boto3, python-dateutil dependencies)
- [ ] T003 [P] Create aws_functions/shared/__init__.py with package setup
- [ ] T004 [P] Create aws_functions/process_change_monitor/__init__.py with package setup
- [ ] T005 [P] Create aws_functions/alert_history_api/__init__.py with package setup
- [ ] T006 [P] Create tests/__init__.py and tests/unit/__init__.py, tests/integration/__init__.py
- [ ] T007 [P] Configure pytest.ini with pytest-cov settings
- [ ] T008 Create tests/fixtures/sample_audit_events.json with sample ADO process change events

**Checkpoint**: Project structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Terraform Infrastructure

- [ ] T009 Create infra/terraform/main.tf with AWS provider configuration
- [ ] T010 [P] Create infra/terraform/variables.tf with all configurable variables
- [ ] T011 [P] Create infra/terraform/outputs.tf with resource outputs
- [ ] T012 Create infra/terraform/iam.tf with Lambda execution roles and policies
- [ ] T013 Create infra/terraform/eventbridge.tf with custom event bus and rules
- [ ] T014 [P] Create infra/terraform/dynamodb.tf with ProcessChangeAlerts table and GSI
- [ ] T015 [P] Create infra/terraform/ses.tf with SES configuration
- [ ] T016 [P] Create infra/terraform/sqs.tf with Dead Letter Queue
- [ ] T017 Create infra/terraform/lambda.tf with Lambda function resources
- [ ] T018 Create infra/terraform/api_gateway.tf with HTTP API for alert history

### Shared Infrastructure Code

- [ ] T019 Create aws_functions/shared/config.py with Parameter Store configuration loading
- [ ] T020 [P] Create aws_functions/shared/utils.py with common utilities (logging, date formatting)
- [ ] T021 Create aws_functions/process_change_monitor/models.py with ProcessChangeEvent dataclass

### Azure Bridge

- [ ] T022 Create infra/azure_bridge/event_grid_webhook.py (Azure Function to forward events to AWS)
- [ ] T023 Create infra/azure_bridge/requirements.txt with Azure Function dependencies

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Receive Alert on Manual Process Change (Priority: P1) 🎯 MVP

**Goal**: Operations team receives email alert within 5 minutes whenever someone manually modifies ADO process template

**Independent Test**: Make a manual process change in ADO and verify alert email received

### Tests for User Story 1

- [ ] T024 [P] [US1] Create unit test for event filtering in tests/unit/test_event_filter.py
- [ ] T025 [P] [US1] Create unit test for email service in tests/unit/test_email_service.py
- [ ] T026 [P] [US1] Create unit test for history service in tests/unit/test_history_service.py
- [ ] T027 [US1] Create integration test for end-to-end flow in tests/integration/test_end_to_end.py

### Implementation for User Story 1

- [ ] T028 [US1] Implement event_filter.py with is_process_change_event() in aws_functions/process_change_monitor/event_filter.py
- [ ] T029 [US1] Implement history_service.py with store_event() in aws_functions/process_change_monitor/history_service.py
- [ ] T030 [US1] Implement email_service.py with send_alert() in aws_functions/process_change_monitor/email_service.py
- [ ] T031 [US1] Implement handler.py Lambda entry point in aws_functions/process_change_monitor/handler.py
- [ ] T032 [US1] Add error handling for SES failures with SQS DLQ fallback in aws_functions/process_change_monitor/handler.py
- [ ] T033 [US1] Add CloudWatch logging for event processing in aws_functions/process_change_monitor/handler.py

**Checkpoint**: User Story 1 complete - alerts are sent for ALL process changes (CI/CD filtering in US2)

---

## Phase 4: User Story 2 - Distinguish Manual vs CI/CD Changes (Priority: P2)

**Goal**: System excludes changes made by authorized CI/CD service accounts from alerting

**Independent Test**: Make change via CI/CD service account → no alert; make manual change → alert received

### Tests for User Story 2

- [ ] T034 [P] [US2] Create unit test for CI/CD filter in tests/unit/test_cicd_filter.py
- [ ] T035 [US2] Create integration test for CI/CD exclusion in tests/integration/test_cicd_exclusion.py

### Implementation for User Story 2

- [ ] T036 [US2] Implement cicd_filter.py with is_authorized_cicd_account() in aws_functions/process_change_monitor/cicd_filter.py
- [ ] T037 [US2] Update config.py to load authorized accounts from Parameter Store in aws_functions/shared/config.py
- [ ] T038 [US2] Integrate CI/CD filter into handler.py in aws_functions/process_change_monitor/handler.py
- [ ] T039 [US2] Add logging for skipped CI/CD changes in aws_functions/process_change_monitor/handler.py

**Checkpoint**: User Story 2 complete - CI/CD changes are excluded, only manual changes generate alerts

---

## Phase 5: User Story 3 - Review Alert History (Priority: P3)

**Goal**: Operations team lead can query and export alert history for auditing

**Independent Test**: Query API with date range and verify history returned; export as CSV/JSON

### Tests for User Story 3

- [ ] T040 [P] [US3] Create unit test for query service in tests/unit/test_query_service.py
- [ ] T041 [P] [US3] Create unit test for export service in tests/unit/test_export_service.py
- [ ] T042 [US3] Create integration test for API endpoints in tests/integration/test_api_endpoints.py

### Implementation for User Story 3

- [ ] T043 [P] [US3] Create query_service.py with query_alerts() in aws_functions/alert_history_api/query_service.py
- [ ] T044 [P] [US3] Create export_service.py with export_csv(), export_json() in aws_functions/alert_history_api/export_service.py
- [ ] T045 [US3] Implement handler.py for GET /alerts in aws_functions/alert_history_api/handler.py
- [ ] T046 [US3] Implement GET /alerts/export endpoint in aws_functions/alert_history_api/handler.py
- [ ] T047 [US3] Add pagination support with nextToken in aws_functions/alert_history_api/query_service.py
- [ ] T048 [US3] Add request validation and error responses per contracts/alert-history-api.yaml in aws_functions/alert_history_api/handler.py

**Checkpoint**: User Story 3 complete - operations team can query and export alert history

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T049 [P] Create deployment script for Lambda packaging in scripts/deploy_lambdas.sh
- [ ] T050 [P] Add CloudWatch alarms for Lambda errors in infra/terraform/cloudwatch.tf
- [ ] T051 [P] Add CloudWatch alarms for SQS DLQ message count in infra/terraform/cloudwatch.tf
- [ ] T052 Create retry Lambda for DLQ processing in aws_functions/process_change_monitor/retry_handler.py
- [ ] T053 [P] Add comprehensive error handling and input validation across all Lambda handlers
- [ ] T054 Run quickstart.md validation - test full deployment flow
- [ ] T055 Add API Gateway API key configuration for operations team in infra/terraform/api_gateway.tf

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 handler but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses DynamoDB from US1 but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before handlers
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: Phase 2 Foundational

```bash
# After T009 (main.tf), these can run in parallel:
T010: infra/terraform/variables.tf
T011: infra/terraform/outputs.tf
T014: infra/terraform/dynamodb.tf
T015: infra/terraform/ses.tf
T016: infra/terraform/sqs.tf

# After T012 (iam.tf), these can run:
T013: infra/terraform/eventbridge.tf
T017: infra/terraform/lambda.tf
T018: infra/terraform/api_gateway.tf
```

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
T024: tests/unit/test_event_filter.py
T025: tests/unit/test_email_service.py  
T026: tests/unit/test_history_service.py

# After tests, implement services in parallel:
T028: aws_functions/process_change_monitor/event_filter.py
T029: aws_functions/process_change_monitor/history_service.py
T030: aws_functions/process_change_monitor/email_service.py

# Then handler (depends on services):
T031: aws_functions/process_change_monitor/handler.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - alerts work for ALL changes

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP: basic alerting)
3. Add User Story 2 → Test independently → Deploy (CI/CD filtering)
4. Add User Story 3 → Test independently → Deploy (History API)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core alerting)
   - Developer B: User Story 2 (CI/CD filtering - can start early, integrate later)
   - Developer C: User Story 3 (History API - independent)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach with moto)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use moto library to mock AWS services in unit tests
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

