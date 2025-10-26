# Edit Control Rules Flow

::: mermaid
flowchart TD
    Edit[User Attempts Edit] --> CheckState{Check<br/>Current State}
    
    CheckState -->|Spec Draft| CheckUser1{Is User<br/>AI:SpecAgent?}
    CheckUser1 -->|Yes| Allow1[Allow Edit]
    CheckUser1 -->|No| Block1[Block: AI is working]
    
    CheckState -->|Spec Clarify| CheckUser2{Is User<br/>Human PO/BA?}
    CheckUser2 -->|Yes| Allow2[Allow Clarifications Only]
    CheckUser2 -->|No| Block2[Block: Awaiting clarification]
    
    CheckState -->|Planning| CheckUser3{Is User<br/>AI:PlanAgent?}
    CheckUser3 -->|Yes| Allow3[Allow Edit]
    CheckUser3 -->|No| Block3[Block: AI is planning]
    
    CheckState -->|Plan Validation| CheckUser4{Is User<br/>Architect?}
    CheckUser4 -->|Yes| Allow4[Allow ValidationFeedback]
    CheckUser4 -->|No| Block4[Block: Architect review only]
    
    CheckState -->|Implementation| CheckUser5{Is User<br/>Dev or AI:Implement?}
    CheckUser5 -->|Yes| Allow5[Allow Edit]
    CheckUser5 -->|No| Block5[Block: Implementation in progress]
    
    CheckState -->|Other States| CheckColumn{Check<br/>Board Column}
    CheckColumn -->|AI Column| BlockAI[Block: AI Active]
    CheckColumn -->|Human Column| CheckRole{User Has<br/>Required Role?}
    CheckRole -->|Yes| AllowRole[Allow Edit]
    CheckRole -->|No| BlockRole[Block: Wrong role]
    
    Block1 --> Log[Log Violation]
    Block2 --> Log
    Block3 --> Log
    Block4 --> Log
    Block5 --> Log
    BlockAI --> Log
    BlockRole --> Log
    
    Log --> Notify[Notify User]
    
    Allow1 --> Success[Edit Successful]
    Allow2 --> Success
    Allow3 --> Success
    Allow4 --> Success
    Allow5 --> Success
    AllowRole --> Success
```

This diagram shows how edit control rules enforce ownership and prevent inappropriate edits at each stage.
