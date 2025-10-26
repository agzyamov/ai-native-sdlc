# Data Flow (Lean Specification Loop)

```mermaid
sequenceDiagram
    autonumber
    participant User as User (PO/Analyst)
    participant Tracker as Tracker (ADO / Work Item)
    participant Hook as Webhook
    participant Actions as GitHub Actions
    participant SpecKit as Spec Kit
    participant Issues as Clarification Issues

    User->>Tracker: Create Feature (state = New, description seed)
    User->>Tracker: Move to Specification
    Tracker-->>Hook: State entered: Specification
    Hook-->>Actions: Dispatch (spec-generate)
    Actions->>SpecKit: Generate / update specification
    SpecKit-->>Actions: Spec markdown + prompts (if questions)
    Actions->>Tracker: Update Description (spec content)
    alt Clarification prompts present
        Actions->>Issues: Create / update clarification issues
        User->>Issues: Answer & close
        Issues-->>Actions: All closed
        Actions->>Actions: (Optional) re-trigger spec regeneration
    end
    Actions->>Tracker: Re-run acceptance checklist
    alt Checklist passes & no open issues
        User->>Tracker: Mark column = Specification Done
        User->>Tracker: Transition to Planning when pulled
    else Still open clarifications / fail
        Actions->>Tracker: Remain in Specification (Doing)
    end
```

This lean sequence removes transitional micro-states: clarifications live purely as child issues while
the work item remains in `Specification` until exit criteria (no open issues + checklist pass) are met.
