# Implementation Cycle Details

::: mermaid
sequenceDiagram
    participant Dev as Developer
    participant ADO as Azure DevOps
    participant GHA as GitHub Actions
    participant AI as ImplementAgent
    participant Tests as Test Suite
    
    Dev->>ADO: Pull Task to Implementation
    ADO->>GHA: Trigger implementation workflow
    GHA->>AI: Generate code for task
    
    loop Implementation Iteration
        AI->>AI: Generate implementation
        AI->>AI: Generate unit tests
        AI->>Tests: Run tests
        
        alt Tests Pass
            Tests-->>AI: Success
            AI->>GHA: Return implementation
        else Tests Fail
            Tests-->>AI: Failure details
            AI->>AI: Analyze failures
            AI->>AI: Fix code
        end
    end
    
    GHA->>ADO: Commit code to feature branch
    GHA->>ADO: Update task status
    ADO->>Dev: Notify: Code ready for review
    
    Dev->>Dev: Review generated code
    
    alt Code Acceptable
        Dev->>Dev: Run local tests
        Dev->>Dev: Integration testing
        Dev->>ADO: Move to Testing state
    else Code Needs Changes
        Dev->>Dev: Manual adjustments
        Dev->>Dev: Commit changes
        Dev->>ADO: Update task
    end
    
    Dev->>Tests: Run full test suite
    
    alt All Tests Pass
        Dev->>ADO: Mark DeveloperTestPassed = true
        Dev->>ADO: Move to QA Ready
    else Tests Fail
        Dev->>Dev: Debug and fix
        Dev->>ADO: Stay in Implementation
    end
:::

::: mermaid
graph TB
    subgraph Phases["Task Implementation Phases"]
        P1[Infrastructure Setup]
        P2[Backend Implementation]
        P3[Frontend Implementation]
        P4[Integration]
        P5[Testing]
    end
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    
    subgraph EachPhase[For Each Phase]
        AI_Gen[AI Generates Code]
        AI_Test[AI Generates Tests]
        AI_Run[AI Runs Tests]
        Dev_Review[Developer Reviews]
        Dev_Adjust[Developer Adjusts]
        Commit[Commit to Branch]
    end
    
    P1 -.-> AI_Gen
    P2 -.-> AI_Gen
    P3 -.-> AI_Gen
    P4 -.-> AI_Gen
    
    AI_Gen --> AI_Test
    AI_Test --> AI_Run
    AI_Run --> Dev_Review
    Dev_Review --> Dev_Adjust
    Dev_Adjust --> Commit
    Commit --> P2
    Commit --> P3
    Commit --> P4
    Commit --> P5
:::

These diagrams show the detailed implementation cycle, including AI code generation, testing, and developer review processes.
