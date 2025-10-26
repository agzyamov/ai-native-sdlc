# Token Tracking and Cost Monitoring

::: mermaid
sequenceDiagram
    participant AI as AI Agent
    participant GHA as GitHub Actions
    participant AF as Azure Function
    participant TS as Table Storage
    participant ADO as Azure DevOps
    participant Alert as Alert System
    
    AI->>GHA: Complete AI task
    GHA->>GHA: Calculate tokens used
    GHA->>AF: POST token metrics
    
    AF->>TS: Store usage record
    Note over TS: Partition: Feature<br/>Row: WorkItem_Timestamp<br/>Data: Agent, Tokens, Cost
    
    AF->>AF: Calculate estimated cost
    AF->>ADO: Update TokensConsumed field
    
    AF->>Alert: Check budget threshold
    
    alt Over Budget
        Alert->>Alert: Trigger alert
        Alert-->>ADO: Notify Architect
    end
    
    Note over AF,TS: Daily aggregation
    AF->>TS: Query daily totals
    TS-->>AF: Return metrics
    AF->>ADO: Update dashboard query
:::

::: mermaid
graph TB
    subgraph TokenBudget["Token Budget per Feature"]
        T1["Specification: 10-20K tokens / $0.30-0.60"]
        T2["Planning: 15-25K tokens / $0.45-0.75"]
        T3["Decomposition: 5-10K tokens / $0.15-0.30"]
        T4["Implementation: 30-50K tokens / $0.90-1.50"]
        Total["Total: 60-105K tokens / $1.80-3.15 per feature"]
    end
    
    T1 --> Total
    T2 --> Total
    T3 --> Total
    T4 --> Total
    
    Total --> Monitor{Budget<br/>Exceeded?}
    Monitor -->|No| Continue[Continue]
    Monitor -->|Yes| Actions[Alert + Review]
    
    Actions --> Split[Consider splitting feature]
    Actions --> Review[Review complexity]
    Actions --> Adjust[Adjust AI parameters]
:::

These diagrams show how token usage is tracked and monitored throughout the workflow, with budget estimates and alerting mechanisms.
