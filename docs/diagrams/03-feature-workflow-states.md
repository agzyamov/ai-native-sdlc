# Lean Feature State Model

```mermaid
stateDiagram-v2
    [*] --> New
    New --> Specification: Pulled for authoring
    Specification --> Planning: Exit criteria met
    Planning --> Validation: Plan ready for approval
    Validation --> Planning: Changes requested
    Validation --> Ready: PlanApproved == true
    Ready --> [*]

    state Specification {
        [*] --> Doing
        Doing --> Done: No open clarification issues & checklist pass
        Done --> Doing: New issue opened / major revision
    }

    note right of Specification
        Single workflow state
        Clarifications = child issues
        Loop stays internal (no extra states)
    end note

    note right of Planning
        Enrich technical plan
        Prepare for validation
    end note

    note right of Validation
        Confirm completeness & feasibility
        Approve via flag (PlanApproved)
    end note
```

Collapsed from legacy multi-step (SpecDraft / Clarify / Ready / PlanValidation / ReadyForDecomp) into a
minimal linear backbone plus an internal loop inside `Specification` using board columns (Doing/Done)
instead of separate workflow states.
