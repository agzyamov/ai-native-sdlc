# User Story Work Item State Transitions

::: mermaid
stateDiagram-v2
    [*] --> New
    New --> Decomposing: Developer pulls story
    Decomposing --> TasksCreated: AI generates tasks
    TasksCreated --> Implementation: Developer reviews & starts
    Implementation --> Testing: Code complete
    Testing --> Implementation: Tests fail
    Testing --> QAReady: Tests pass
    QAReady --> Testing: QA finds issues
    QAReady --> Done: QA approves
    Done --> [*]
    
    note right of Decomposing
        AI:TaskAgent active
        Creates Task work items
    end note
    
    note right of Implementation
        AI:ImplementAgent + Developer
        Iterative code generation
    end note
    
    note right of Testing
        Human:Developer
        Manual validation
    end note
    
    note right of QAReady
        Human:QA
        Final acceptance
    end note
:::

This state diagram illustrates the lifecycle of a User Story from creation through completion.
