# Feature Specification Summary

## 📋 Feature: Preserve Clarification Questions in Workflow Mode

**Feature ID**: 002-preserve-clarification-questions  
**Created**: 2025-11-02  
**Status**: Draft - Ready for Planning

---

## 🎯 What This Feature Does

Currently, when the automated specification workflow runs (triggered by Azure DevOps), the AI assistant automatically resolves ambiguous requirements by making educated guesses, hiding the fact that clarification is needed. This feature changes that behavior to:

1. **Detect clarification markers** - check if spec generation produced `[NEEDS CLARIFICATION]` markers
2. **Conditionally preserve markers** - if present, keep them in spec instead of auto-resolving
3. **Extract questions** (only when markers exist) to a dedicated file for easy review
4. **Auto-create ADO Issues** (only when questions exist) for each clarification need, linked to parent Feature
5. **Update Feature Description** with actual spec content (with markers if present, clean spec if not)

When requirements are clear and no markers are generated, the workflow proceeds normally without creating clarification artifacts. This enables Product Owners to see exactly what needs human input only when ambiguities exist, and track resolution through standard ADO workflows.

---

## 🎨 Key User Journeys (All P1)

### Journey 1: Transparent Ambiguity (When Needed)
When a Feature triggers spec generation with unclear requirements that produce `[NEEDS CLARIFICATION]` markers, the system preserves those markers in the spec file and ADO Description, making gaps visible instead of hiding them with AI guesses. When requirements are clear (no markers generated), the workflow proceeds normally with a clean spec.

### Journey 2: Structured Question List (Conditional)
When clarification markers are detected, the system automatically extracts all questions to a dedicated `clarifications.md` file with context, making it easy for POs to review what needs answering. If no markers exist, no clarifications file is created.

### Journey 3: Trackable Resolution (When Questions Exist)
For each clarification question detected, the system creates an ADO Issue work item linked to the Feature, enabling POs to assign, discuss, and track resolution using existing workflows. Features with clear requirements don't generate Issues.

### Journey 4: Single Source of Truth (Always)
The ADO Feature Description is always updated with the actual spec content from spec.md - preserving clarification markers if present, or containing the clean spec if no clarifications are needed, ensuring consistency between Git and ADO views.

---

## 📦 Deliverables

### Specification Documents
- ✅ [spec.md](./spec.md) - Complete feature specification (11 FRs, 7 SCs, 4 user stories)
- ✅ [data-model.md](./data-model.md) - Entity relationships and state transitions
- ✅ [checklists/requirements.md](./checklists/requirements.md) - Quality validation (all items pass)

### Contract Definitions
- ✅ [contracts/clarifications-format.md](./contracts/clarifications-format.md) - Structure of clarifications.md file
- ✅ [contracts/ado-issue-creation.md](./contracts/ado-issue-creation.md) - ADO REST API payload format
- ✅ [contracts/README.md](./contracts/README.md) - Contract overview and integration flow

---

## 🔢 By The Numbers

- **User Stories**: 4 (all P1 - independently testable)
- **Functional Requirements**: 11 (FR-001 to FR-011)
- **Success Criteria**: 7 measurable outcomes
- **Edge Cases**: 6 documented scenarios
- **Assumptions**: 7 documented
- **Risks**: 5 identified with mitigations
- **New Entities**: 3 (Clarifications File, Clarification Marker, Issue Work Item)
- **Modified Entities**: 3 (Feature, Specification Artifact, Workflow Dispatch)

---

## 🔑 Key Requirements Highlights

### Functional Requirements (Selected)

- **FR-002**: In non-interactive mode, preserve `[NEEDS CLARIFICATION]` markers (no auto-resolution)
- **FR-003**: Extract markers using regex pattern `\[NEEDS CLARIFICATION:\s*([^\]]+)\]`
- **FR-004**: Create structured `clarifications.md` file with question context and answers
- **FR-005**: Auto-create ADO Issue work items with Parent-Child relationship to Feature
- **FR-006**: Implement idempotency (Feature ID + question hash) to prevent duplicate Issues
- **FR-007**: Overwrite ADO Description with clarification-preserved spec (not auto-resolved)
- **FR-008**: Enforce max 3 clarification markers per spec (existing Spec Kit limit)

### Success Criteria (Selected)

- **SC-001**: 100% preservation of markers in non-interactive mode
- **SC-003**: ≥95% Issue creation success rate
- **SC-004**: 0% duplicate Issues (idempotency validation)
- **SC-005**: ADO Description identical to spec.md (including markers)
- **SC-007**: Workflow completes within 5 minutes (including Issue creation)

---

## 🏗️ Architecture Overview

```
Azure DevOps Service Hook
  ↓
GitHub Actions Workflow (spec-kit-specify.yml)
  ↓
┌────────────────────────────────────────────────────┐
│ 1. Copilot generates spec.md                      │
│ 2. Detect if [NEEDS CLARIFICATION] markers exist  │
│    ├─ IF markers found:                           │
│    │   ├─ Extract markers                         │
│    │   ├─ Create clarifications.md                │
│    │   └─ For each question: Create ADO Issue     │
│    └─ IF no markers:                              │
│        └─ Skip extraction/Issue creation          │
│ 3. Update ADO Feature Description (with spec.md)  │
└────────────────────────────────────────────────────┘
  ↓
Outputs (conditional):
  - spec.md (always - with or without markers)
  - clarifications.md (only if markers exist)
  - ADO Issues (only if markers exist, 0-3)
  - Updated Feature Description (always)
```

---

## 📊 Impact Assessment

### Extending 001-ado-github-spec

This feature **extends** the existing implementation without breaking changes:

- ✅ Adds new workflow steps (backward compatible)
- ✅ Introduces new files only when clarifications present
- ✅ Uses existing ADO PAT (may need scope expansion)
- ✅ No schema changes to existing entities

### Rollback Strategy

If needed, rollback is simple:
1. Remove marker extraction steps from workflow
2. Re-enable auto-resolution (remove `PRESERVE_MARKERS` flag)
3. Existing Features without clarifications unaffected

---

## ⚠️ Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Copilot auto-resolves despite instructions | High | Add explicit environment flag, validate output |
| ADO API rate limiting blocks Issue creation | Medium | Exponential backoff, log partial successes |
| Malformed markers not extracted | Low | Log warnings, continue with valid markers |
| Partial Issue creation (2/3 success) | Medium | Idempotency ensures safe re-run |

---

## 🚀 Next Steps

### Immediate (After Spec Approval)
1. **Planning Phase** (`/speckit.plan`)
   - Technical design for marker extraction
   - ADO API integration approach
   - Workflow YAML modifications
   - Testing strategy

2. **Task Breakdown** (`/speckit.tasks`)
   - Granular implementation tasks
   - Acceptance criteria per task
   - Effort estimation

3. **Implementation** (`/speckit.implement`)
   - Modify spec-kit-specify.yml workflow
   - Add extraction and Issue creation steps
   - Update prompt with preservation flag
   - Add tests for new functionality

### Validation Criteria

Before moving to planning, verify:
- ✅ All checklist items pass (completed)
- ✅ No unresolved clarification markers in spec (completed)
- ✅ Stakeholder approval on approach (pending)
- ✅ Security review for new ADO API usage (pending)

---

## 📚 Related Documentation

- **Parent Spec**: [001-ado-github-spec](../001-ado-github-spec/spec.md) - Baseline implementation
- **Workflow File**: `.github/workflows/spec-kit-specify.yml` - To be modified
- **Prompt File**: `.github/prompts/speckit.specify.prompt.md` - Clarification behavior defined here
- **ADO API Docs**: [Work Items REST API](https://learn.microsoft.com/rest/api/azure/devops/wit/work-items)

---

## 📝 Notes

- **Happy Path**: Most Features with clear requirements will generate specs without clarification markers, proceeding normally without creating clarifications artifacts
- **Conditional Behavior**: Clarifications file and ADO Issues are only created when `[NEEDS CLARIFICATION]` markers are detected in spec.md
- **Spec Kit Constraint**: Max 3 clarification questions enforced by CLI design (not a new limit)
- **ADO Project Assumption**: Must support Issue work item type (fallback to Task if needed)
- **Idempotency Strategy**: Feature ID + question hash prevents duplicate Issues on re-runs
- **Resolution Workflow**: Deferred to future enhancement (manual update via ADO for MVP)

---

**Specification Approved**: _Pending stakeholder review_  
**Ready for Planning**: ✅ Yes (all quality checks pass)  
**Last Updated**: 2025-11-02
