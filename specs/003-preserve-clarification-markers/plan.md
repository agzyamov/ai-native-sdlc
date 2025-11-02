# Implementation Plan: Preserve Clarification Questions in Workflow Mode

**Branch**: `003-preserve-clarification-markers` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-preserve-clarification-markers/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the existing GitHub Actions workflow (`spec-kit-specify.yml`) to conditionally detect and preserve `[NEEDS CLARIFICATION]` markers in generated specifications. When markers are present, extract questions to a structured `clarifications.md` file and auto-create Azure DevOps Issue work items linked to the parent Feature. When markers are absent (clear requirements), skip extraction and proceed normally. This enables asynchronous clarification resolution through existing ADO workflows while maintaining spec-ADO consistency.

## Technical Context

**Language/Version**: Bash (shell scripts), Python 3.11 (for marker extraction script), YAML (GitHub Actions workflow)
**Primary Dependencies**: 
- Existing: GitHub Actions workflow (`spec-kit-specify.yml`), GitHub Copilot CLI, Spec Kit CLI
- New: Python regex library (built-in), jq (JSON processing), Azure DevOps REST API 7.0
- ADO Client: Existing `ado_client.py` from 001-ado-github-spec (will be extended)

**Storage**: 
- Git repository (feature branch) for spec.md, clarifications.md
- Azure DevOps (work items database) for Feature and Issue entities
- No new persistent storage required

**Testing**: 
- Bash script testing (manual + unit tests via bats if needed)
- Python script testing (pytest for extraction logic)
- Integration testing (trigger workflow with sample Feature, verify artifacts)
- Contract validation (JSON schema validation for ADO payloads)

**Target Platform**: 
- GitHub Actions runners (ubuntu-latest)
- Compatible with existing workflow environment (Node 22, Python 3.11)

**Project Type**: CI/CD workflow extension (modifies existing GitHub Actions YAML)

**Performance Goals**: 
- Workflow completion within 5 minutes (including Issue creation for 3 clarifications) - SC-007
- Marker extraction < 5 seconds for typical spec file
- Issue creation < 10 seconds per question (ADO API latency)

**Constraints**: 
- Must not break existing workflow behavior when no clarifications exist
- Maximum 3 clarification markers enforced (existing Spec Kit constraint)
- Idempotent Issue creation (no duplicates on re-runs)
- Backward compatible with 001-ado-github-spec implementation

**Scale/Scope**: 
- Expected: 1-3 clarification questions per 20% of Features (80% have clear requirements)
- ADO API rate limits: ~200 requests/minute (well above needed capacity)
- Spec file size: typically 5-20KB, clarifications.md < 10KB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The plan MUST explicitly confirm each gate below (FAIL any → plan not approvable):

| Gate | Pass Criteria | Status | Notes |
|------|---------------|--------|-------|
| Spec Exit Integrity | No open clarification issues; acceptance checklist passed | ✅ OK | Checklist validation complete (checklists/requirements.md all items pass) |
| Story Independence | All listed user stories independently testable & prioritized (P1..N) | ✅ OK | 4 user stories, all P1/P2, each independently testable per spec |
| Minimal State Model | No added workflow states; only New→Specification→Planning→Validation→Ready referenced | ✅ OK | No state changes; feature modifies behavior within existing Specification state |
| Quality Automation | Diagram + workflow validation steps documented (mermaid-cli, actionlint) | ✅ OK | Will use actionlint for workflow YAML validation (already in CI), no new diagrams |
| Complexity Justification | Any structural deviations justified in Complexity Tracking section | ✅ OK | No violations; extends existing workflow in-place |

**Principle 6 (Direct Event Path)**: Feature preserves direct Azure Function → GitHub Actions path from 001-ado-github-spec. No intermediaries added.

**Principle 7 (Infrastructure as Code)**: No new cloud resources required; extends existing GitHub Actions workflow and reuses ADO client code.

**Gate Status**: ✅ ALL PASS - Proceed to Phase 0 research

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
.github/
├── workflows/
│   └── spec-kit-specify.yml          # MODIFY: Add marker detection, extraction, Issue creation steps
└── scripts/                           # NEW DIRECTORY
    ├── extract-clarifications.py      # NEW: Extracts [NEEDS CLARIFICATION] markers from spec.md
    └── create-ado-issues.sh           # NEW: Creates ADO Issues via REST API (calls ado_client.py)

function_app/                          # EXISTING from 001-ado-github-spec
└── ado_client.py                      # EXTEND: Add create_issue_workitem() function

specs/003-preserve-clarification-markers/
├── spec.md                            # EXISTING
├── plan.md                            # THIS FILE
├── research.md                        # PHASE 0 OUTPUT
├── data-model.md                      # EXISTING
├── quickstart.md                      # PHASE 1 OUTPUT
├── contracts/                         # EXISTING
│   ├── clarifications-format.md       # EXISTING
│   ├── ado-issue-creation.md          # EXISTING
│   └── README.md                      # EXISTING
└── tests/                             # NEW DIRECTORY
    ├── test_extract_clarifications.py # NEW: Unit tests for extraction logic
    └── test_ado_issue_creation.sh     # NEW: Integration test for Issue creation
```

**Structure Decision**: 
- Modify existing workflow YAML in-place (no new workflow files)
- Add Python extraction script to `.github/scripts/` (co-located with workflow)
- Extend existing `function_app/ado_client.py` with Issue creation capability
- Place feature-specific tests in specs directory (not root tests/ - keeps feature encapsulated)
- Reuse existing contract documentation structure from spec phase

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. Feature extends existing workflow without introducing new states, intermediaries, or architectural complexity.
