<!--
Sync Impact Report
Version: (new) 1.0.0 (initial adoption)
Previous Version: none
Modified Principles: (initial set created)
Added Sections: Core Principles, Constraints & Standards, Operational Workflow, Governance
Removed Sections: none
Templates Reviewed:
	- .specify/templates/plan-template.md ✅ updated (Constitution Check expanded)
	- .specify/templates/spec-template.md ✅ aligned (independent user stories already present)
	- .specify/templates/tasks-template.md ✅ aligned (story-based task grouping already present)
	- .specify/templates/commands/* ⚠ none present (directory absent) - no action
Follow-up TODOs: none
-->

# AI-Native SDLC Constitution

## Core Principles

### 1. Single-State Specification Loop
All specification and clarification occurs within the single workflow state `Specification`.
Clarification questions MUST be represented exclusively as child Issues. The work item
MUST NOT change state until exit criteria are satisfied (no open clarification issues,
acceptance checklist passes, description stabilized). No additional micro-states may be
introduced without a MAJOR governance amendment.

### 2. Description-as-Spec & Traceability
The canonical specification MUST live in the work item description. Regenerations MUST
replace (not append) outdated sections while preserving resolved clarifications. All AI‑
assisted changes SHOULD be reviewable via normal diff/PR mechanisms. No shadow spec
files unless explicitly justified (security/compliance).

### 3. Independently Deliverable User Stories
Each user story MUST be:
- Independently implementable
- Independently testable (can form a temporary MVP)
- Prioritized (P1, P2, P3...) with rationale
- Mapped to tasks and tests without cross‑story hard dependencies
Stories failing independence MUST be decomposed before planning sign‑off.

### 4. Minimal State & Explicit Gates
State model is fixed: New → Specification → Planning → Validation → Ready. Progression
MUST depend on clear, testable gates (Specification Done criteria, PlanApproved flag,
Validation completion). Adding new workflow states, hidden queues, or implicit review
stages is PROHIBITED without amendment.

### 5. Automated Quality & Structural Integrity
The following MUST be enforced:
- Mermaid diagrams: validated via `check_mermaid.js` + mermaid-cli
- GitHub workflows: linted with `actionlint`
- Specification exit: zero open clarification issues + acceptance checklist pass
- Plan: explicit structure + Constitution Check section completed
- Tasks: grouped strictly by user story; test tasks precede implementation when requested

## Constraints & Standards

- Line length guidance: target ≤100 characters for authored Markdown and code (non-binding
	for embedded examples exceeding clarity).
- Version control hygiene: small, logical commits referencing story or task scope.
- No introduction of optional “enhancement” states; use labels or metadata instead.
- Tooling pinning: Critical validation tooling (mermaid-cli version) SHOULD be pinned in
	scripts to reduce drift.
- Clarification churn: If >3 regeneration cycles without convergence, escalate manually
	(human review) rather than adding automation complexity.

## Operational Workflow

1. Specification Phase: Iterate description + clarifications until exit criteria.
2. Planning Phase: Produce plan.md using template; complete Constitution Check gates.
3. Validation Phase: Architect/reviewer confirms completeness; set `PlanApproved=true`.
4. Ready: Downstream decomposition / implementation proceeds (outside constitution scope).
5. Continuous Quality: Diagrams + workflows validated pre-commit or in CI.

## Governance

- Scope: This constitution supersedes ad-hoc process documents for specification, planning,
	and validation activities.
- Amendments: Propose via PR modifying this file + impact rationale. Version bump per
	semantic rules (see below). Approval requires at least one maintainer + one architect
	(if roles diverge) OR documented consensus in PR discussion.
- Versioning Policy:
	- MAJOR: Breaking workflow/state changes; removal/redefinition of a principle.
	- MINOR: Addition of a new principle or new normative constraint.
	- PATCH: Wording clarity, non-normative edits, formatting.
- Review Cadence: Minimum quarterly review or triggered earlier by any principle violation
	encountered during a PR.
- Compliance: Each plan MUST include a Constitution Check outcome; reviewers MUST block
	if unmet. Automated scripts MAY surface violations but human approval is final.

**Version**: 1.0.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-10-26
