# Data Flow Sequence

::: mermaid
sequenceDiagram
    participant PO as Product Owner
    participant ADO as Azure DevOps
    participant WH as Webhook
    participant GHA as GitHub Actions
    participant SK as Spec Kit
    participant AF as Azure Functions
    
    PO->>ADO: Create Feature (Description = initial context)
    PO->>ADO: Move to "Spec Draft"
    ADO->>WH: State change trigger
    WH->>GHA: Repository dispatch event
    GHA->>SK: Run spec-kit specify
    SK->>SK: Generate specification
    SK->>GHA: Return spec (+ clarification prompts if any)
    GHA->>AF: Log token usage
    AF->>ADO: Update TokensConsumed
    GHA->>ADO: Update Description (spec markdown)
    alt Clarifications Needed
        GHA->>ADO: Set state "Spec Clarify"
        ADO->>PO: Notification
    else No Clarifications Needed
        GHA->>ADO: Set state "Spec Ready"
    end
:::

This sequence diagram illustrates the step-by-step data flow when a Product Owner creates a feature and the AI generates a specification.
