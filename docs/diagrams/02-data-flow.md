# Data Flow Sequence

::: mermaid
sequenceDiagram
    participant PO as Product Owner
    participant ADO as Azure DevOps
    participant WH as Webhook
    participant GHA as GitHub Actions
    participant SK as Spec Kit
    participant AF as Azure Functions
    
    PO->>ADO: Create Feature with POInput
    PO->>ADO: Move to "Spec Draft"
    ADO->>WH: State change trigger
    WH->>GHA: Repository dispatch event
    GHA->>SK: Run spec-kit specify
    SK->>SK: Generate specification
    SK->>GHA: Return spec + questions
    GHA->>AF: Log token usage
    AF->>ADO: Update TokensConsumed
    GHA->>ADO: Update Specification field
    alt Has Questions
        GHA->>ADO: Set state "Spec Clarify"
        ADO->>PO: Notification
    else No Questions
        GHA->>ADO: Set state "Spec Ready"
    end
:::

This sequence diagram illustrates the step-by-step data flow when a Product Owner creates a feature and the AI generates a specification.
