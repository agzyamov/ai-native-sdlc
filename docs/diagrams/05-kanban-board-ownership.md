# Kanban Board Ownership Model (Simplified Doing / Done)

The previous many-column model is replaced by **stage groups** with optional `Doing` & `Done` subcolumns. This diagram shows the *board columns*, not underlying state machine (states remain for workflow automation).

### Feature Board
::: mermaid
graph LR
        FB0[Backlog]
        subgraph Specification
            FB1A[Spec - Doing]
            FB1B[Spec - Done]
        end
        subgraph Clarification
            FB2A[Clarify - Doing]
            FB2B[Clarify - Done]
        end
        subgraph Planning
            FB3A[Planning - Doing]
            FB3B[Planning - Done]
        end
        subgraph Validation
            FB4A[Validation - Doing]
            FB4B[Validation - Done]
        end
        FB5[Ready for Decomposition]

        FB0 --> FB1A
        FB1A --> FB1B
        FB1B --> FB2A
        FB2A --> FB2B
        FB2B --> FB1A
        FB1B --> FB3A
        FB3A --> FB3B
        FB3B --> FB4A
        FB4A --> FB4B
        FB4B --> FB3A
        FB4B --> FB5
:::

Legend (Feature):
- Spec/Planning *Doing*: AI + Human (PO/BA or Architect) may both act; AI runs do not move column.
- Clarify *Doing*: Human only; AI idle.
- *Done* subcolumns: Artifact stable; next pull triggers progression.
- Loop backs: Clarify Done → Spec Doing (regen); Validation Done → Planning Doing (rework).

### User Story Board
::: mermaid
graph LR
        SB0[Backlog]
        subgraph Decomposition
            SB1A[Decomp - Doing]
            SB1B[Decomp - Done]
        end
        subgraph Implementation
            SB2A[Impl - Doing]
            SB2B[Impl - Done]
        end
        subgraph Testing
            SB3A[Testing - Doing]
            SB3B[Testing - Done]
        end
        SB4[Done]

        SB0 --> SB1A
        SB1A --> SB1B
        SB1B --> SB2A
        SB2A --> SB2B
        SB2B --> SB3A
        SB3A --> SB3B
        SB3B --> SB2A
        SB3B --> SB4
:::

Legend (Story):
- Decomp Doing: Dev + AI TaskAgent.
- Impl Doing: Dev + AI ImplementAgent.
- Testing Doing: Dev (and QA if present).
- Testing Done replaces previous QA Ready.

> Ownership is inferred from Stage + Subcolumn; AI-specific “Generating” columns removed.
