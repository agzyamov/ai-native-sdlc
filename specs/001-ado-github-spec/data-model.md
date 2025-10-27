# Data Model: Azure DevOps → GitHub Spec Generation (Phase 1)

MVP is primarily workflow/automation; minimal persistent model. Still, conceptual entities and relationships clarify contracts.

## Entities

### Feature (ADO Work Item)
- Fields Used:
  - ID (int)
  - Title (string)
  - Description (HTML/Markdown) – overwritten
  - Assigned To (identity)
  - Board Column (string – "Specification – Doing" / "Specification – Done")
  - State (string)
- Invariants:
  - Description becomes authoritative structured spec after generation.
  - Assignee must equal AI Teammate at trigger moment.

### Specification Artifact (spec.md)
- Location: `specs/<feature-branch>/spec.md` in Git
- Relationship: 1:1 with Feature (branch naming scheme creates implicit linkage)
- Content Sections: Summary, User Scenarios, Functional Requirements, Backlog, etc.

### Branch (Git)
- Name: `001-ado-github-spec` (pattern `<seq>-<short-name>` future generalized)
- State: Reused on regeneration (future Backlog item)

### Workflow Dispatch Request
- Payload Inputs:
  - feature_description (string – original or current user-provided text)
  - create_branch (bool)
- Origin: Intermediary trigger (Service Hook) or manual dispatch (pilot)

### Generation Run (Ephemeral)
- Attributes:
  - Start Time
  - Completion Status (success/failure)
  - Commit SHA (resulting spec commit)
- Persistence: Only via GitHub Actions log + commit history

### Credential (Secret)
- GitHub PAT (Spec generation) – already present implicitly
- ADO PAT (Description PATCH) – to be added
- Constraints: Least privilege, rotated per policy

## Relationships
| From | To | Type | Notes |
|------|----|------|-------|
| Feature | Branch | 1:1 | Branch reused for subsequent spec operations |
| Feature | Specification Artifact | 1:1 | Description mirrors artifact content |
| Workflow Dispatch | Generation Run | 1:N | Multiple runs possible (future regen) |
| Generation Run | Commit | 1:1 | Each successful run produces >=1 commit |

## State Transitions (Conceptual)
```
(Feature Assigned To AI + Column Change) --> Trigger Candidate
Trigger Candidate + Column=Specification – Doing + Assignee=AI --> Generation Dispatched
Generation Dispatched --> (Workflow Success) --> Description Overwritten
Workflow Success + Human Review --> Column moves to Specification – Done
```

## Validation Rules
- Trigger only valid if both column AND assignee conditions hold simultaneously.
- Reject overwrite attempt if generated spec empty (guard clause recommended – Backlog for robust error path).

## Open Modeling Considerations (Deferred)
- Explicit Regen Counter (FR-007 future)
- Generation audit entity (failure metrics)
- Hash of last generated spec for idempotency

## Summary
Model suffices for MVP: no new storage, entities are either existing platform records or ephemeral execution artifacts.
