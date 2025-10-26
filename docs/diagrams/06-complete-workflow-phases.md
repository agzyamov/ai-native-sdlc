# Complete Workflow Phases

::: mermaid
flowchart TD
    Start([Start]) --> Phase1[Phase 1: Project Constitution]
    Phase1 --> Phase2[Phase 2: Create Specification]
    Phase2 --> Decision1{Has Questions?}
    Decision1 -->|Yes| Phase3[Phase 3: Clarification]
    Decision1 -->|No| Phase4[Phase 4: Create Plan]
    Phase3 --> Decision2{Round < 5?}
    Decision2 -->|Yes| Phase2
    Decision2 -->|No| Override[Architect Override]
    Override --> Phase4
    Phase4 --> Phase5[Phase 5: Validate Plan]
    Phase5 --> Decision3{Plan Approved?}
    Decision3 -->|No| Feedback[Add Feedback]
    Feedback --> Phase4
    Decision3 -->|Yes| Phase6[Phase 6: Task Decomposition]
    Phase6 --> Phase7[Phase 7: Implementation]
    Phase7 --> Decision4{Tests Pass?}
    Decision4 -->|No| Fix[Fix Issues]
    Fix --> Phase7
    Decision4 -->|Yes| Phase8[Phase 8: Testing & QA]
    Phase8 --> Decision5{QA Approved?}
    Decision5 -->|No| Defect[Log Defects]
    Defect --> Phase7
    Decision5 -->|Yes| Done([Done])
:::

**Phase Types:**
- Phases 2, 4, 6: AI-driven phases
- Phases 3, 5, 8: Human-driven phases
- Phase 7: Collaborative phase

This flowchart shows the complete workflow from start to finish with all decision points.
