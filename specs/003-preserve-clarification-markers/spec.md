# Feature Specification: Preserve Clarification Questions in Workflow Mode

**Feature Branch**: `002-preserve-clarification-questions`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "I want to change the behavior of BA agent: AS IS - described in #file:001-ado-github-spec and already implemented. the problem with this approach is that during the CLI session github spec kit asks clarifying questions and expects input from user. in workflow mode that is not possible so these questions are not addressed but the output spec is somehow adjusted by spec kit so it never contains those clarifying questions. TO BE: I want the workflow to preserve: 1 the spec version of the workflow containing CLARIFICATION NEEDED marks 2 clarifying questions in separate folder next to the spec file once these are done, the workflow should overwrite the feature description with the spec - that's already done but the version with spec kit's best guesses is used, not the initial one with clarification questions AND for each clarification question a dedicated Issue WI should be created and connected to Feature with Parent-Child relationship."

## Summary

When the automated specification generation workflow runs in non-interactive mode (triggered by Azure DevOps Service Hook), the system must detect whether the generated specification contains [NEEDS CLARIFICATION] markers. If markers are present, the system must preserve them instead of auto-resolving with AI-generated guesses, extract each clarification question to a dedicated questions file, and automatically create Azure DevOps Issue work items linked to the parent Feature. If no clarification markers exist (when requirements are clear), the workflow proceeds normally without creating clarifications artifacts. This enables asynchronous human review and resolution of ambiguities only when needed, while maintaining full traceability between specification gaps and their resolution tasks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Initial Spec with Clarification Markers (Priority: P1)

As a Product Owner, when the automated workflow generates a specification from my Feature description, I want the system to preserve the initial version containing [NEEDS CLARIFICATION] markers in the spec file and in the ADO Feature Description, so that I can review what information is missing before proceeding to planning.

**Why this priority**: Core value proposition - ensures visibility of specification gaps and prevents AI from making critical assumptions without human oversight.

**Independent Test**: Trigger workflow with ambiguous Feature description → verify spec.md contains [NEEDS CLARIFICATION] markers → verify ADO Description is overwritten with spec containing markers (not resolved version).

**Acceptance Scenarios**:

1. **Given** a Feature assigned to "AI Teammate" with ambiguous description "Add user authentication", **When** workflow generates specification in non-interactive mode and produces markers, **Then** spec.md contains at least one [NEEDS CLARIFICATION: auth method not specified] marker and ADO Description field is updated with this version (not an auto-resolved version).

2. **Given** a Feature with clear, unambiguous description "Add OAuth2 authentication using industry-standard flows", **When** workflow generates specification in non-interactive mode, **Then** spec.md contains no [NEEDS CLARIFICATION] markers, no clarifications.md is created, no ADO Issues are generated, and workflow proceeds normally to ADO Description update.

3. **Given** a specification generation that produces more than 3 clarification markers, **When** the limit enforcement runs, **Then** only the 3 most critical markers (by scope/security/UX impact) are preserved and remaining items are resolved with documented assumptions.

---

### User Story 2 - Extract Clarification Questions to Dedicated File (Priority: P1)

As a Product Owner, when the workflow generates a specification with clarification needs, I want each question automatically extracted to a structured questions file (`clarifications.md`) in the feature directory, so that I have a clear checklist of what needs human input.

**Why this priority**: Essential for workflow usability - provides actionable artifact for PO review without parsing the full spec.

**Independent Test**: Generate spec with 2 clarification markers → verify `clarifications.md` exists with numbered questions and context → verify file structure matches template.

**Acceptance Scenarios**:

1. **Given** a spec.md with 2 [NEEDS CLARIFICATION] markers, **When** workflow completes extraction step, **Then** a file `specs/<feature-dir>/clarifications.md` is created containing 2 numbered questions with context, spec section reference, and placeholder for answers.

2. **Given** a spec.md with no clarification markers (clear requirements), **When** workflow detects absence of markers, **Then** extraction step is skipped, no `clarifications.md` file is created, and workflow proceeds directly to ADO Description update (FR-007).

3. **Given** clarification markers scattered across multiple spec sections, **When** extraction runs, **Then** each question in `clarifications.md` includes the spec section header where it originated for traceability.

---

### User Story 3 - Auto-Create ADO Issue Work Items for Each Clarification (Priority: P1)

As a Product Owner, when clarification questions are identified, I want the system to automatically create an Azure DevOps Issue work item for each question and link it to the parent Feature with Parent-Child relationship, so that I can track resolution of each ambiguity in my backlog.

**Why this priority**: Critical for ADO workflow integration - enables existing processes (assignment, tracking, discussion) to handle clarification resolution.

**Independent Test**: Generate spec with 1 clarification marker → verify Issue WI is created in ADO with title prefix "Clarification:" → verify Parent-Child link to Feature → verify Issue Description contains question context.

**Acceptance Scenarios**:

1. **Given** a spec with 1 [NEEDS CLARIFICATION: auth method] marker, **When** workflow completes, **Then** an Issue work item is created in ADO with Title "Clarification: Auth method not specified", Description containing question context and spec file reference, and Parent link to original Feature.

2. **Given** a spec with 3 clarification markers, **When** workflow completes, **Then** exactly 3 Issue work items are created, each with unique numbered titles (Q1, Q2, Q3) and distinct Parent-Child relationships to the Feature.

3. **Given** an Issue work item is created for a clarification, **When** it is resolved and marked Done, **Then** the resolution can be traced back to the spec file and Feature (through work item links and comments).

4. **Given** a workflow run fails during Issue creation, **When** retry or manual intervention occurs, **Then** duplicate Issues are not created (idempotency based on Feature ID + question hash or marker position).

---

### User Story 4 - Overwrite ADO Description with Clarification-Preserved Spec (Priority: P2)

As a Product Owner, when the workflow completes, I want the ADO Feature Description to be updated with the specification containing clarification markers (not the auto-resolved version), so that anyone reviewing the Feature in ADO sees the same content as in the spec file.

**Why this priority**: Important for consistency between Git and ADO, but lower priority than P1 items since spec file is source of truth.

**Independent Test**: Generate spec with clarification markers → verify ADO PATCH request sends spec content with markers intact → verify ADO UI displays markers in Description field.

**Acceptance Scenarios**:

1. **Given** a spec.md with [NEEDS CLARIFICATION] markers, **When** ADO Description overwrite step runs, **Then** the Description field in ADO contains the exact same markdown including all [NEEDS CLARIFICATION: ...] markers.

2. **Given** the overwrite step encounters a transient error (timeout), **When** retry logic executes, **Then** the eventual successful PATCH contains the correct clarification-preserved spec (not accidentally using a cached resolved version).

---

### Edge Cases

- What happens when spec is generated with no [NEEDS CLARIFICATION] markers (clear requirements)?
- What happens when Copilot generates spec without creating files directly (falls back to output extraction) and clarification markers are embedded in command output?
- How does system handle malformed [NEEDS CLARIFICATION] markers (missing colon, unclosed bracket)?
- What if ADO Issue creation succeeds for first 2 questions but fails on 3rd (partial success)?
- How does system detect duplicate clarifications across workflow re-runs (same Feature, same questions)?
- What if spec generation produces 5 markers but limit is 3 - which ones are kept and how are others documented?
- What happens if ADO project doesn't allow Issue work item type or Parent-Child links are disabled?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Workflow MUST detect when running in non-interactive mode (GitHub Actions workflow_dispatch) versus interactive CLI mode (explicit flag or environment variable). In non-interactive mode, workflow MUST also detect whether generated spec contains [NEEDS CLARIFICATION] markers before proceeding with extraction steps.

- **FR-002**: When in non-interactive mode, IF the Copilot spec generation produces [NEEDS CLARIFICATION: ...] markers, the workflow MUST preserve the initial specification containing those markers and MUST NOT auto-resolve them with AI guesses. If no markers are produced, the workflow proceeds with normal spec (no preservation needed).

- **FR-003**: IF spec.md contains [NEEDS CLARIFICATION: specific question] markers, workflow MUST extract all markers using regex pattern `\[NEEDS CLARIFICATION:\s*([^\]]+)\]` and parse the surrounding context (section header, paragraph). If no markers are found, skip extraction steps (FR-004, FR-005) and proceed to FR-007.

- **FR-004**: IF markers were extracted in FR-003, workflow MUST create a structured `clarifications.md` file in the feature directory (`specs/<feature-dir>/clarifications.md`) with this format. If no markers exist, do NOT create this file:
  ```markdown
  # Clarification Questions: [FEATURE NAME]
  
  **Feature**: [Link to spec.md]
  **Created**: [ISO Date]
  **Status**: Open
  
  ## Question 1: [Topic extracted from marker]
  
  **Context**: [Quote from spec section where marker appeared]
  
  **Question**: [Full text from NEEDS CLARIFICATION marker]
  
  **Answer**: _Pending_
  
  ---
  
  [Repeat for each question]
  ```

- **FR-005**: For each clarification question extracted (if any), workflow MUST create an Azure DevOps Issue work item with:
  - **Title**: "Clarification Q[N]: [Topic - first 50 chars of question]"
  - **Description**: Question context, spec file path, link to GitHub branch
  - **Assigned To**: Same as parent Feature's "Created By" or leave unassigned
  - **Tags**: "clarification", "auto-generated"
  - **Parent Link**: Parent-Child relationship to originating Feature work item

- **FR-006**: Issue creation MUST be idempotent based on Feature ID + question position/hash to prevent duplicate Issues on workflow re-runs (implement marker hash or position-based deduplication).

- **FR-007**: The ADO Description overwrite step MUST use the spec.md content as-is from the feature branch. If markers are present, they will be preserved in the Description field. If no markers exist, the clean spec is used. Never use an auto-resolved version that removes markers.

- **FR-008**: Workflow MUST enforce maximum 3 clarification markers per spec (existing limit in prompt) and document handling when more are generated (keep 3 most critical by scope/security/UX, convert others to Assumptions section with note "Auto-resolved due to limit").

- **FR-009**: Workflow MUST commit both spec.md (with markers) and clarifications.md to the feature branch in a single commit with message referencing Feature ID and clarification count.

- **FR-010**: If Issue creation fails for any question after 3 retry attempts, workflow MUST log error, continue processing remaining questions, and set workflow status to partial success with warning in summary.

- **FR-011**: System MUST validate PAT scope requirements for ADO Issue creation (Work Items: Write) and document required permissions in security review checklist.

### Key Entities

- **Specification File (spec.md)**: Generated markdown containing structured requirements; may include [NEEDS CLARIFICATION] markers indicating gaps.

- **Clarifications File (clarifications.md)**: Extracted list of questions requiring human input; 1:1 relationship with spec.md per feature.

- **Clarification Marker**: Inline text pattern `[NEEDS CLARIFICATION: question text]` embedded in spec sections; extracted and converted to Issue work items.

- **Issue Work Item (ADO)**: Child work item type in Azure DevOps; tracks single clarification question; linked to parent Feature via Parent-Child relationship.

- **Feature Work Item (ADO)**: Parent work item that triggered spec generation; Description field overwritten with spec containing markers.

- **Workflow Run Context**: Environment metadata (interactive vs non-interactive mode, Feature ID, branch name) controlling behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of non-interactive workflow runs preserve initial spec markers when present (no auto-resolution occurs). When spec has no markers, workflow proceeds normally without creating clarification artifacts.

- **SC-002**: When clarification markers exist in spec.md, 100% are extracted to clarifications.md with complete context (section, question, answer placeholder). When no markers exist, no clarifications.md file is created.

- **SC-003**: Issue work item creation success rate ≥ 95% across all workflow runs (allowing for transient ADO API failures).

- **SC-004**: 0% duplicate Issue work items created for same Feature + question combination across multiple workflow runs (idempotency validation).

- **SC-005**: ADO Feature Description contains identical content to spec.md - preserving markers if present, or containing clean spec if no markers exist (verified via checksum or text comparison).

- **SC-006**: Product Owner can locate and resolve all clarification questions using only ADO work item UI (no need to access Git directly) - qualitative validation through pilot testing.

- **SC-007**: Workflow completes within 5 minutes including Issue creation for up to 3 clarifications (performance target consistent with FR-010 from 001-ado-github-spec).

## Assumptions

- **Assumption 1**: Copilot's `--allow-all-tools` mode can be configured to preserve markers instead of auto-resolving them (may require prompt engineering or environment variable).

- **Assumption 2**: ADO project supports Issue work item type and Parent-Child link relationship (validate during deployment; fallback to Task type if needed).

- **Assumption 3**: The pattern `[NEEDS CLARIFICATION: ...]` is stable and won't change in Spec Kit CLI (low risk as defined in prompt instructions).

- **Assumption 4**: Three clarification questions per spec is sufficient for MVP (aligns with existing Spec Kit constraint; can be increased in future if needed).

- **Assumption 5**: PAT credentials for ADO Issue creation can reuse existing `ADO_WORKITEM_RW_PAT` secret (or new secret `ADO_ISSUE_CREATE_PAT` with narrower scope).

- **Assumption 6**: Clarifications are expected to be resolved asynchronously (no synchronous blocking of spec-to-plan progression required in MVP).

- **Assumption 7**: Markdown format for clarifications.md is acceptable for human review (no need for custom UI or ADO wiki page in MVP).

## Out of Scope

- Automatic resolution workflow when Issues are marked Done (update spec.md with answers) - deferred to future enhancement.
- Bidirectional sync between clarifications.md and Issue work items (manual update required if Issue is modified in ADO).
- Integration with `/speckit.clarify` CLI command for interactive resolution (workflow focuses on non-interactive automation).
- Notification mechanism for Product Owner when clarifications are needed (ADO query or email alerts) - rely on existing ADO notifications.
- Support for more than 3 clarification questions (enforce existing limit per Spec Kit design).
- Custom ADO work item templates or fields for clarifications (use standard Issue type).

## Risks

- **Risk 1**: Copilot may still auto-resolve markers despite prompt instructions (mitigation: add explicit environment flag, validate output contains markers).
- **Risk 2**: Regex extraction may fail on malformed markers (mitigation: log warnings, create Issue for manual review).
- **Risk 3**: ADO API rate limiting may block Issue creation (mitigation: implement exponential backoff, fail gracefully with manual fallback).
- **Risk 4**: Partial Issue creation failure may leave inconsistent state (mitigation: idempotency ensures safe re-run, log partial successes).
- **Risk 5**: Feature Description overwrite may occur before Issue creation, leaving no trace if Issue step fails (mitigation: reorder steps or make overwrite conditional on Issue success).

## Open Clarifications

None (all clarification markers resolved during initial spec generation).

## Backlog

### Deferred User Stories

- **US-DEFERRED-1**: Auto-resolution workflow (when Issue marked Done, update spec.md and re-run validation).
- **US-DEFERRED-2**: Clarification dashboard (ADO query widget showing all pending clarifications across Features).
- **US-DEFERRED-3**: Slack/Teams notification when clarifications are identified.

### Deferred Functional Requirements

- **FR-DEFERRED-1**: Bidirectional sync between clarifications.md and Issue Description (update clarifications.md when Issue Description is edited in ADO).
- **FR-DEFERRED-2**: Support for nested clarifications (sub-questions based on initial answers).
- **FR-DEFERRED-3**: Automatic link from Issue back to specific line in spec.md (GitHub line anchors).
- **FR-DEFERRED-4**: Rich text formatting for ADO Description (currently plain markdown).
- **FR-DEFERRED-5**: Custom ADO work item type "Clarification" with specialized fields.

### Deferred Success Criteria

- **SC-DEFERRED-1**: Mean time to clarification resolution < 24 hours (requires tracking and notification).
- **SC-DEFERRED-2**: 90% of clarifications resolved before planning phase begins (requires workflow enforcement).
- **SC-DEFERRED-3**: Zero manual re-sync required between clarifications.md and ADO Issues (requires bidirectional sync).

## Traceability

- **FR-001 ↔ Implementation**: Environment detection logic in workflow YAML (check for `CI=true` or `WORKFLOW_MODE=non-interactive`).
- **FR-002 ↔ SC-001**: Validation test - parse committed spec.md for markers, assert count > 0 when expected.
- **FR-003 ↔ FR-004**: Extraction script output feeds into clarifications.md generation template.
- **FR-005 ↔ SC-003**: ADO REST API call success rate monitoring.
- **FR-006 ↔ SC-004**: Deduplication test - run workflow twice, count Issues, assert no duplicates.
- **FR-007 ↔ SC-005**: ADO PATCH request body validation - assert contains `[NEEDS CLARIFICATION` substring.
- **FR-009**: Git commit SHA links workflow run to spec.md + clarifications.md state.
- **FR-010 ↔ Implementation**: Workflow failure handling logic with partial success exit codes.

---

*End of Draft Specification*
