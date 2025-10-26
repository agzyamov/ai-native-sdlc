# Feature Work Item State Transitions

::: mermaid
stateDiagram-v2
    [*] --> New
    New --> SpecDraft: PO adds POInput
    SpecDraft --> SpecClarify: AI has questions
    SpecDraft --> SpecReady: No questions
    SpecClarify --> SpecDraft: PO answers questions
    SpecClarify --> SpecReady: Max rounds (5) reached
    SpecReady --> Planning: Architect adds input
    Planning --> PlanValidation: AI generates plan
    PlanValidation --> Planning: Architect requests changes
    PlanValidation --> ReadyForDecomp: Architect approves
    ReadyForDecomp --> [*]: Stories created
    
    note right of SpecDraft
        AI:SpecAgent active
        Humans read-only
    end note
    
    note right of SpecClarify
        Human:PO active
        AI read-only
    end note
    
    note right of Planning
        AI:PlanAgent active
        Humans read-only
    end note
    
    note right of PlanValidation
        Human:Architect active
        AI read-only
    end note
:::

This state diagram shows all possible states for a Feature work item and the transitions between them, with ownership notes.
