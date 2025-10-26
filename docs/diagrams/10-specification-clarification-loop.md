# Specification Clarification Loop

```mermaid
flowchart TD
    Start[PO Creates Feature] --> Input[PO Writes Description]
    Input --> SpecDraft[Move to Spec Draft]
    SpecDraft --> AISpec[AI Generates Specification]

    AISpec --> ClarifyNeed{Clarification<br/>Needed?}

    ClarifyNeed -->|No| Checklist[Run Acceptance Checklist]
    Checklist --> CheckPass{Checklist<br/>Pass?}
    CheckPass -->|Yes| SpecReady[State: Spec Ready]
    CheckPass -->|No| GenPrompts[Generate Clarification Prompts]
    GenPrompts --> ClarifyState

    ClarifyNeed -->|Yes| ClarifyState[State: Spec Clarify]

    ClarifyState --> POAnswer[PO/BA Resolve Clarification Issues]
    POAnswer --> BackToDraft[Move to Spec Draft]
    BackToDraft --> AIRefine[AI Refines Specification]
    AIRefine --> ClarifyNeed

    SpecReady --> NextPhase[Proceed to Planning]
```

This flowchart details the clarification loop process using child Clarification Issues (lean model: no Clarifications / Questions fields or artificial round limit; architect can still intervene manually if churn persists).
