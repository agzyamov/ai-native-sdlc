<!--
Constitution Validation Report - 2025-11-02
Version: 1.1.1 (patch) – Validation review, documentation alignment check
Previous Version: 1.1.0
Change Type: PATCH (no semantic changes; validation and alignment verification)
Modified Principles: None (validation only)
Added Sections: None
Removed Sections: None
Templates Reviewed:
  - .specify/templates/plan-template.md ✅ updated (added Principles 6 & 7 to Constitution Check gates)
  - .specify/templates/spec-template.md ✅ aligned (user story independence, priority requirements match)
  - .specify/templates/tasks-template.md ✅ aligned (story grouping, test-first approach matches principles)
  - .specify/templates/agent-file-template.md ✅ aligned (no conflicts)
  - .specify/templates/checklist-template.md ✅ aligned (validation requirements match)
  - .github/prompts/speckit.constitution.prompt.md ✅ aligned (this validation follows its instructions)
Repository Documentation:
  - README.md ✅ aligned (references lean state model, clarification via Issues)
  - docs/workflow.md ✅ expected to align (not validated in this review)
Active Features:
  - specs/001-ado-github-spec/ ✅ Constitution compliance verified in implementation
  - specs/003-preserve-clarification-markers/ ✅ Constitution Check complete (plan.md all gates PASS)
Compliance Status: ✅ ALL ALIGNED
Follow-up Actions: None required
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

### 6. Direct Event Path (Eliminate Unnecessary Intermediaries)
Event-driven automation MUST avoid superfluous workflow hops. Transformations, validation,
and dispatch orchestration SHOULD occur in the minimal viable component (e.g., direct Azure
Function) rather than chaining CI pipelines purely as relays. Intermediary removal is
encouraged when it reduces latency, secret proliferation, or failure surfaces—provided
observability is preserved. Re‑introducing an intermediary requires justification tied to
debounce, batching, or compliance.

### 7. Infrastructure as Code Mandate
Durable cloud resources (Function Apps, storage, plans, schedulers, Key Vault, queues) MUST
be declared via Infrastructure as Code (Terraform baseline) before production usage. Manual
portal or ad-hoc creation is permissible only for exploratory spikes and MUST NOT persist
past the spike branch lifecycle. All IaC changes SHOULD remain reviewable with plan output
attached or summarized.

## Constraints & Standards

- Line length guidance: target ≤100 characters for authored Markdown and code (non-binding
	for embedded examples exceeding clarity).
- Version control hygiene: small, logical commits referencing story or task scope.
- No introduction of optional “enhancement” states; use labels or metadata instead.
- Tooling pinning: Critical validation tooling (mermaid-cli version) SHOULD be pinned in
	scripts to reduce drift.
- Clarification churn: If >3 regeneration cycles without convergence, escalate manually
	(human review) rather than adding automation complexity.

### Deprecation Retention & Sunset
Deprecated automation components (e.g., superseded pipeline definitions) MAY remain for a
grace period spanning one MINOR version or 30 days (whichever is shorter) unless they
introduce security, reliability, or cost risk. Each deprecated artifact MUST include a
comment header: `DEPRECATED: <reason> (remove by <date>)`.

### Idempotency & External Observability
Automation entry points (functions, dispatch handlers) MUST be:
- Idempotent with respect to duplicate upstream events (safe no-op or merged effect)
- Externally observable through structured logs (include correlation/work item id)
- Bounded by explicit timeouts on outbound network calls
Retries MUST use exponential backoff with bounded attempts; validation failures MUST NOT be
retried.

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

**Version**: 1.1.1 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-11-02 (Validation review and template alignment verification; no semantic changes)
