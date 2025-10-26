# Specification Clarification Loop

::: mermaid
flowchart TD
    Start[PO Creates Feature] --> Input[PO Fills POInput]
    Input --> SpecDraft[Move to Spec Draft]
    SpecDraft --> AISpec[AI Generates Specification]
    
    AISpec --> Questions{AI Has<br/>Questions?}
    
    Questions -->|No| Checklist[Run Acceptance Checklist]
    Checklist --> CheckPass{Checklist<br/>Pass?}
    CheckPass -->|Yes| SpecReady[State: Spec Ready]
    CheckPass -->|No| GenQuestions[Generate Questions from Checklist]
    GenQuestions --> ClarifyState
    
    Questions -->|Yes| ClarifyState[State: Spec Clarify]
    
    ClarifyState --> CountRound{Round<br/>Count}
    CountRound -->|< 5| POAnswer[PO/BA Answer Questions]
    CountRound -->|>= 5| MaxRounds[Max Rounds Reached]
    
    MaxRounds --> ArchReview[Architect Review Required]
    ArchReview --> Decision{Architect<br/>Decision}
    Decision -->|Simplify| Split[Split into smaller features]
    Decision -->|Override| ForceReady[Force Spec Ready]
    Decision -->|Retry| POAnswer
    
    POAnswer --> UpdateClar[Update Clarifications Field]
    UpdateClar --> BackToDraft[Move to Spec Draft]
    BackToDraft --> IncRound[Increment ClarificationRound]
    IncRound --> AIRefine[AI Refines Specification]
    AIRefine --> Questions
    
    SpecReady --> NextPhase[Proceed to Planning]
    Split --> End[Create New Features]
    ForceReady --> NextPhase
:::

This flowchart details the clarification loop process, including the 5-round limit and architect override mechanism.
