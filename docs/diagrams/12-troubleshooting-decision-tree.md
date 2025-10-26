# Troubleshooting Decision Tree

::: mermaid
flowchart TD
    Issue[Issue Detected] --> Category{Issue<br/>Category}
    
    Category -->|Work Item Stuck| Stuck
    Category -->|Clarification Loop| Loop
    Category -->|Token Spike| Tokens
    Category -->|Webhook Failure| Webhook
    Category -->|Edit Control| EditCtrl
    
    subgraph WorkItemStuck[Work Item Stuck]
        Stuck[Item in AI state > 30min]
        Stuck --> CheckGH1[Check GitHub Actions logs]
        CheckGH1 --> GHStatus{Workflow<br/>Status?}
        GHStatus -->|Failed| Retrigger1[Manually retrigger webhook]
        GHStatus -->|Running| Wait1[Wait longer or check logs]
        GHStatus -->|No workflow| CheckWebhook1[Verify webhook configured]
        Retrigger1 --> StillStuck{Still<br/>Stuck?}
        StillStuck -->|Yes| ArchOverride1[Architect override]
        StillStuck -->|No| Resolved1[Resolved]
    end
    
    subgraph ClarificationLoop[Clarification Loop > 5]
        Loop[Exceeding max rounds]
        Loop --> ArchReview1[Architect reviews requirements]
        ArchReview1 --> Complexity{Feature<br/>Complexity?}
        Complexity -->|Too complex| SplitFeature[Split into smaller features]
        Complexity -->|Unclear input| SimplifyInput[Clarify Description]
        Complexity -->|AI confusion| DetailedInput[Provide more detailed input]
        SplitFeature --> Resolved2[Resolved]
        SimplifyInput --> Resolved2
        DetailedInput --> Resolved2
    end
    
    subgraph TokenSpike[Token Consumption Spike]
        Tokens[Feature using > 100K tokens]
        Tokens --> CheckLogs[Review GitHub Actions logs]
        CheckLogs --> CauseToken{Root<br/>Cause?}
        CauseToken -->|Retry loops| FixWorkflow[Fix workflow errors]
        CauseToken -->|Large feature| SplitFeature2[Split feature]
        CauseToken -->|AI inefficiency| AdjustParams[Adjust AI model parameters]
        FixWorkflow --> Resolved3[Resolved]
        SplitFeature2 --> Resolved3
        AdjustParams --> Resolved3
    end
    
    subgraph WebhookIssue[Webhook Not Triggering]
        Webhook[State change but no GH action]
        Webhook --> VerifyURL[Verify webhook URL in ADO]
        VerifyURL --> CheckPAT[Check GitHub PAT expiry]
        CheckPAT --> CheckDispatch[Confirm dispatch events enabled]
        CheckDispatch --> ManualTest[Test with manual trigger]
        ManualTest --> Working{Working<br/>Now?}
        Working -->|Yes| Resolved4[Resolved]
        Working -->|No| RecreateWebhook[Recreate webhook]
    end
    
    subgraph EditControl[Edit Controls Not Working]
        EditCtrl[Users can edit blocked fields]
        EditCtrl --> VerifyProcess[Verify process template applied]
        VerifyProcess --> CheckRules[Check rule conditions syntax]
        CheckRules --> VerifyColumn[Confirm correct board column]
        VerifyColumn --> ClearCache[Clear browser cache]
        ClearCache --> StillBroken{Still<br/>Broken?}
        StillBroken -->|Yes| ReapplyProcess[Reapply process template]
        StillBroken -->|No| Resolved5[Resolved]
    end
:::

This decision tree provides a systematic approach to troubleshooting common issues in the AI-Native SDLC workflow.
