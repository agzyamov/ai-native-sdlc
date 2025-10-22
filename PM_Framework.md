# PROJECT MANAGEMENT FRAMEWORK
## AI Native SDLC - Azure DevOps + GitHub

::: mermaid
graph TD
    CORE["PROJECT MANAGEMENT FRAMEWORK<br/>AI Native SDLC - Azure DevOps + GitHub<br/>• 4-Level Hierarchy: Epic → Feature → Story → Task<br/>• Story as Requirements: 8-13 SP max<br/>• Research-Driven Development at Feature level<br/>• Role-based Sign-offs: BMAD and GitHub Spec Kit framework"]
    
    EPIC["EPIC - Portfolio Container - OPTIONAL<br/>• Owner: Product Manager<br/>• Purpose: Business Process, Capability, or Theme grouping<br/>• States: New → In Progress → Done<br/>• Examples: User Auth Capability, Payment Processing System<br/>• Standard Fields: Title, Description, State, Area Path, Iteration Path"]
    
    FEATURE["FEATURE - Business Requirement + Technical Contracts<br/>• Owner: Product Manager (business) + Architect (contracts)<br/>• States: New → In Analysis → Research → Ready for Decomposition → AI Processing → Decomposed → In Development → Done<br/>• Custom Fields: Data Contract (HTML), API Contract (HTML), Implementation Plan (HTML), Technical Diagrams (HTML with mermaid)<br/>• Standard Fields: Title, Description, Acceptance Criteria (success metrics), Priority, Business Value<br/>• Research Outputs: Data/API contracts, Implementation plan, Technical diagrams<br/>• Typical Diagrams: System Architecture, Sequence, Data Flow, State Machines, ERD, Components"]
    
    STORY["USER STORY - Decomposed Requirement<br/>• Owner: Business Analyst - Sign-off: Story decomposition<br/>• 8-13 SP max - User story format in Title: As a... I want... So that...<br/>• References Feature's contracts in Description<br/>• Links to GitHub PR (standard integration)<br/>• States: New → AI Proposed → BA Review → Approved → Ready for Dev → In Development → Code Review → Testing → Done<br/>• Standard Fields: Title, Description, Acceptance Criteria (checklist), Story Points (max 13)<br/>• Tags: Backend, API, UI, Security, Performance"]
    
    TASK["TASK - Technical Implementation & Questions<br/>• Owner: Varies by prefix<br/>• Title Format: [PREFIX] Description<br/>• Prefixes: [Q] Questions/Decisions, [SD API] API Design, [SD UI] UI Design, [CORE] Backend Logic, [API] REST/GraphQL, [UI] UI Implementation, [UI-COMP] Design System Component<br/>• States: Standard tasks (To Do → In Progress → Done), [Q] tasks (Open → In Progress → Answered → Closed OR Open → Rejected → Closed)<br/>• Standard Fields: Title, Description, Assigned To, Original Estimate, Completed Work, Remaining Work<br/>• Tags: Auto-applied based on prefix"]
    
    QTASK["[Q] TASK - Questions & Decisions<br/>• Created by: Anyone (Human or AI)<br/>• Human questions: Open → In Progress → Answered → Closed (cannot be rejected)<br/>• AI questions: Open → In Progress → Answered → Closed OR Open → Rejected → Closed<br/>• Rejection reasons: Out of context, Already answered, Not relevant<br/>• Resolution: Document in comments before closing<br/>• Purpose: Requirement clarifications, Domain expertise, Technical decisions, Design decisions, Implementation clarifications, Test strategy"]
    
    SDTASK["[SD *] TASK - Solution Design<br/>• [SD API]: Story-specific API details with Swagger spec<br/>• [SD UI]: Story-specific UI designs and mockups<br/>• Reference: Feature-level contracts and diagrams<br/>• Created during: Story development<br/>• Owner: Architect ([SD API]) or UI Designer ([SD UI])"]
    
    DEVTASK["DEVELOPMENT TASKS<br/>• [CORE]: Backend business logic implementation<br/>• [API]: API endpoint implementation (REST/GraphQL)<br/>• [UI]: UI implementation (Web/Mobile/Desktop platform-agnostic)<br/>• [UI-COMP]: Reusable design system component<br/>• Owner: Developer<br/>• All reference Feature contracts"]
    
    TESTCASE["TEST CASE<br/>• Owner: Tester<br/>• Test scenarios and execution<br/>• Links to User Stories<br/>• States: Design → Review → Ready → Passed/Failed<br/>• Standard Fields: Title, Steps, Expected Results, Associated Work Items"]
    
    BUG["BUG - Defect Tracking<br/>• Owner: Reporter (Anyone)<br/>• States: New → Triaged → Assigned → In Progress → Fixed → Closed<br/>• Standard Fields: Title, Repro Steps, System Info, Found In Build, Severity, Priority, Activity"]
    
    PM["PRODUCT MANAGER<br/>• Azure DevOps only<br/>• Creates: Epics (optional) and Features<br/>• Owns: Feature requirements, priorities, business context<br/>• Uses [Q] tasks for: Requirement clarifications<br/>• Deliverables: Feature requirements, business justification, success criteria"]
    
    BA["BUSINESS ANALYST<br/>• Azure DevOps only<br/>• Sign-off: User Story decomposition quality<br/>• Reviews: AI-generated stories, domain coverage, story points ≤13<br/>• Uses [Q] tasks for: Domain expertise requests<br/>• Quality Gates: All domains covered, clear acceptance criteria, business rules defined"]
    
    ARCH["ARCHITECT<br/>• ADO + GitHub<br/>• Sign-off: Feature-level technical design and contracts<br/>• Creates: Data/API contracts and diagrams at Feature level<br/>• Reviews: Technical approach, system design, task dependencies<br/>• Uses [Q] tasks for: Technical decisions<br/>• Owns: [SD API] tasks<br/>• Deliverables: Solution design, data models, API contracts, architecture decisions"]
    
    UIDESIGNER["UI DESIGNER - OPTIONAL ROLE<br/>• Azure DevOps only<br/>• Required when: Feature or Story includes UI components<br/>• Sign-off: UI/UX designs<br/>• Creates/Reviews: [SD UI] tasks for screen-specific mockups<br/>• Maintains: [UI-COMP] tasks for design system components<br/>• Uses [Q] tasks for: Design decisions<br/>• Deliverables: Approved mockups, design system components, interaction patterns"]
    
    DEV["DEVELOPER<br/>• ADO + GitHub<br/>• Sign-off: Code quality (via PR)<br/>• Implements: [CORE], [API], [UI] tasks<br/>• Reviews: AI-generated code via PR comments (GitHub Copilot interaction)<br/>• Uses [Q] tasks for: Implementation clarifications<br/>• GitHub Activities: PR reviews, code improvements, bug fixes, merge approvals"]
    
    TESTER["TESTER<br/>• Azure DevOps only<br/>• Sign-off: Test coverage<br/>• Creates: Test Cases linked to User Stories<br/>• Uses [Q] tasks for: Test strategy questions<br/>• Deliverables: Approved test cases, test execution results, coverage reports, bug reports"]
    
    RESEARCH["FEATURE RESEARCH PHASE<br/>• Trigger: Feature enters Research state<br/>• Owner: Architect + AI (+ UI Designer if UI involved)<br/>• Duration: 2-5 days typically<br/>• Outputs stored in Feature custom fields:<br/>  - Data Contract: Input/Output schemas, DB models, event schemas, validation rules<br/>  - API Contract: Full API spec, Swagger/OpenAPI, GraphQL schema, webhooks<br/>  - Implementation Plan: Technical approach, risk assessment, dependencies, performance<br/>  - Technical Diagrams: System architecture, sequence diagrams, data flow, state machines (mermaid)<br/>• Review: Architect (technical), UI Designer (design if applicable), BA (business), Developer (clarity)<br/>• Outcome: Go/No-Go decision"]
    
    AIDECOMP["AI: REQUIREMENTS DECOMPOSITION<br/>• Trigger: Feature research complete and approved<br/>• Input: Feature with contracts and diagrams<br/>• Actions: Analyzes Feature requirements and contracts<br/>  - Generates 3-8 User Stories (each ≤13 SP)<br/>  - Covers all required domains<br/>  - Creates acceptance criteria<br/>  - Identifies stories requiring UI<br/>• Output: Draft User Stories<br/>• Human Review: BA validates and adjusts<br/>• Iteration: Via [Q] task if domains missing"]
    
    AITASKGEN["AI: TASK GENERATION<br/>• Trigger: Story approved by BA<br/>• Input: User Story + Feature contracts<br/>• Actions: Creates story-level tasks with appropriate prefixes<br/>  - Generates [SD UI] tasks if UI needed<br/>  - Generates [SD API] tasks for endpoint details<br/>  - Creates [CORE], [API], [UI] implementation tasks<br/>  - Suggests [UI-COMP] if reusable component needed<br/>• Output: Task breakdown with prefixes<br/>• Human Review: Architect validates technical plan"]
    
    AICODE["AI: CODE GENERATION<br/>• Trigger: Development task assigned to AI<br/>• Input: Task + Feature contracts + [SD *] task designs<br/>• Actions: Writes code following contracts<br/>  - Implements UI based on [SD UI] designs<br/>  - Creates unit tests, follows coding standards<br/>  - Opens draft PR in GitHub linked to User Story (not Task)<br/>• Output: Draft PR with code<br/>• Human Review: Developer reviews via PR comments<br/>• Iteration: AI responds to PR comments (GitHub Copilot)"]
    
    AITEST["AI: TEST CASE GENERATION<br/>• Trigger: Story ready for testing<br/>• Input: User Story + acceptance criteria + Feature contracts<br/>• Actions: Generates test scenarios and detailed test steps<br/>  - Includes UI test cases (if applicable)<br/>  - Identifies test data needs<br/>  - Proposes automation approach<br/>  - Estimates execution time<br/>• Output: Executable test cases<br/>• Human Review: Tester validates and executes<br/>• Execution: Mix of automated and manual"]
    
    GITHUB["GITHUB INTEGRATION<br/>• main branch protected<br/>• feature/* and bugfix/* branches<br/>• Branch Protection: Required reviews, all tests must pass, no direct commits<br/>• PR Workflow: AI creates draft PR linked to User Story (not Task)<br/>  - AI adds reviewers, sets labels and milestones<br/>  - Review: Developer reviews code, AI responds to PR comments via GitHub Copilot<br/>• Merge Criteria: All tests passing (coverage >80%), approvals, no unresolved comments<br/>• Quality Controls: Unit tests, integration tests, security scanning, code style validation"]
    
    FLOW["END-TO-END PROCESS FLOW<br/>1. PM creates Feature (optionally under Epic)<br/>2. Architect conducts Feature research<br/>3. Architect defines Data/API contracts and diagrams in Feature<br/>4. AI decomposes Feature to 3-8 User Stories<br/>5. BA reviews and approves stories<br/>6. AI creates story-level tasks with prefixes<br/>7. UI Designer completes [SD UI] tasks (if UI needed)<br/>8. Developers implement [CORE], [API], [UI] tasks<br/>9. AI creates PR linked to User Story<br/>10. Developer reviews via PR comments<br/>11. Tester executes Test Cases<br/>12. Team marks Story as Done"]
    
    QFLOW["QUESTION FLOW ([Q] TASKS)<br/>• Human questions: Always get answered (cannot be rejected)<br/>• AI questions: Can be rejected if irrelevant<br/>• Rejection: Goes to Rejected state with reason in comments<br/>• Valid questions: Get answered and moved to Closed<br/>• Rejection reasons: Out of context, Already answered, Not relevant<br/>• All questions: Must link to parent work item<br/>• SLA tracking: Response time metrics"]
    
    GATES["SIGN-OFF GATES<br/>• BA → Story decomposition quality<br/>• Architect → Feature-level contracts and technical design<br/>• UI Designer → UI/UX designs in [SD UI] tasks (if applicable)<br/>• Developer → Code quality via PR approval<br/>• Tester → Test coverage and test case validation<br/>• PM → Feature acceptance"]
    
    METRICS["KEY METRICS & KPIs<br/>• Velocity: Stories/sprint, Story points delivered, Task completion by prefix type, [Q] task response time<br/>• Quality: Defect density, Test coverage %, PR review turnaround, Contract compliance rate, [Q] task rejection rate (AI questions)<br/>• Process: Feature research duration, Feature → Production time, Question resolution time, AI question relevance rate, Parallel task efficiency"]
    
    CUSTOMFIELDS["CUSTOM FIELDS REQUIRED<br/>• Feature Level (Custom Fields):<br/>  - Data Contract: HTML (schemas, models, validation rules)<br/>  - API Contract: HTML (Swagger/OpenAPI spec)<br/>  - Implementation Plan: HTML (approach, risks, dependencies)<br/>  - Technical Diagrams: HTML (mermaid diagrams)<br/>• User Story Level: Standard fields only, reference Feature contracts in Description<br/>• Task Level: Standard fields only, Title format [PREFIX] Description"]
    
    CORE --> EPIC
    CORE --> FEATURE
    CORE --> STORY
    CORE --> TASK
    CORE --> TESTCASE
    
    EPIC --> FEATURE
    FEATURE --> STORY
    STORY --> TASK
    TASK --> QTASK
    TASK --> SDTASK
    TASK --> DEVTASK
    STORY --> TESTCASE
    STORY --> BUG
    STORY --> GITHUB
    
    FEATURE --> PM
    FEATURE --> RESEARCH
    STORY --> BA
    TASK --> ARCH
    TASK --> UIDESIGNER
    TASK --> DEV
    TESTCASE --> TESTER
    
    RESEARCH --> ARCH
    RESEARCH --> UIDESIGNER
    
    FEATURE --> AIDECOMP
    AIDECOMP --> STORY
    STORY --> AITASKGEN
    AITASKGEN --> TASK
    TASK --> AICODE
    AICODE --> GITHUB
    STORY --> AITEST
    AITEST --> TESTCASE
    
    PM -.-> QTASK
    BA -.-> QTASK
    ARCH -.-> QTASK
    UIDESIGNER -.-> QTASK
    DEV -.-> QTASK
    TESTER -.-> QTASK
    
    GITHUB --> DEV
    GITHUB --> ARCH
    
    EPIC --> FLOW
    FEATURE --> FLOW
    STORY --> FLOW
    TASK --> FLOW
    
    FLOW --> QFLOW
    QFLOW --> GATES
    GATES --> METRICS
    METRICS --> CUSTOMFIELDS
    
    style CORE fill:#2c3e50,stroke:#34495e,stroke-width:4px,color:#ecf0f1
    style EPIC fill:#9b59b6,stroke:#8e44ad,stroke-width:3px,color:#ecf0f1
    style FEATURE fill:#8e44ad,stroke:#9b59b6,stroke-width:3px,color:#ecf0f1
    style STORY fill:#8e44ad,stroke:#9b59b6,stroke-width:3px,color:#ecf0f1
    style TASK fill:#16a085,stroke:#1abc9c,stroke-width:3px,color:#ecf0f1
    style QTASK fill:#d35400,stroke:#e67e22,stroke-width:3px,color:#ecf0f1
    style SDTASK fill:#f39c12,stroke:#f1c40f,stroke-width:3px,color:#2c3e50
    style DEVTASK fill:#16a085,stroke:#1abc9c,stroke-width:3px,color:#ecf0f1
    style TESTCASE fill:#16a085,stroke:#1abc9c,stroke-width:3px,color:#ecf0f1
    style BUG fill:#c0392b,stroke:#e74c3c,stroke-width:3px,color:#ecf0f1
    style PM fill:#3498db,stroke:#5dade2,stroke-width:3px,color:#ecf0f1
    style BA fill:#3498db,stroke:#5dade2,stroke-width:3px,color:#ecf0f1
    style ARCH fill:#3498db,stroke:#5dade2,stroke-width:3px,color:#ecf0f1
    style UIDESIGNER fill:#3498db,stroke:#5dade2,stroke-width:3px,color:#ecf0f1
    style DEV fill:#3498db,stroke:#5dade2,stroke-width:3px,color:#ecf0f1
    style TESTER fill:#3498db,stroke:#5dade2,stroke-width:3px,color:#ecf0f1
    style RESEARCH fill:#f39c12,stroke:#f1c40f,stroke-width:3px,color:#2c3e50
    style AIDECOMP fill:#27ae60,stroke:#2ecc71,stroke-width:3px,color:#ecf0f1
    style AITASKGEN fill:#27ae60,stroke:#2ecc71,stroke-width:3px,color:#ecf0f1
    style AICODE fill:#27ae60,stroke:#2ecc71,stroke-width:3px,color:#ecf0f1
    style AITEST fill:#27ae60,stroke:#2ecc71,stroke-width:3px,color:#ecf0f1
    style GITHUB fill:#34495e,stroke:#95a5a6,stroke-width:3px,color:#ecf0f1
    style FLOW fill:#f39c12,stroke:#f1c40f,stroke-width:3px,color:#2c3e50
    style QFLOW fill:#d35400,stroke:#e67e22,stroke-width:3px,color:#ecf0f1
    style GATES fill:#e67e22,stroke:#f39c12,stroke-width:3px,color:#ecf0f1
    style METRICS fill:#16a085,stroke:#1abc9c,stroke-width:3px,color:#ecf0f1
    style CUSTOMFIELDS fill:#34495e,stroke:#95a5a6,stroke-width:3px,color:#ecf0f1
:::
