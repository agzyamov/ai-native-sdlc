# Architecture Overview

```mermaid
graph TB
    ADO_UI[Azure DevOps UI]
    ADO_WI[Work Items]
    ADO_RULES[Edit Control Rules]
    ADO_WEBHOOKS[Webhooks]
    
    GH_REPO[GitHub Repository]
    GH_ACTIONS[GitHub Actions]
    GH_SPECKIT[Spec Kit]
    GH_BRANCHES[Feature Branches]
    
    AZ_TOKENS[Token Tracking]
    AZ_METRICS[Metrics Collection]
    AZ_ALERTS[Alert System]
    
    PO[Product Owner]
    BA[Business Analyst]
    ARCH[Architect]
    DEV[Developers]
    QA[QA Tester]
    
    PO --> ADO_UI
    BA --> ADO_UI
    ARCH --> ADO_UI
    DEV --> ADO_UI
    QA --> ADO_UI
    
    ADO_UI --> ADO_WI
    ADO_WI --> ADO_RULES
    ADO_WI --> ADO_WEBHOOKS
    
    ADO_WEBHOOKS --> GH_REPO
    GH_REPO --> GH_ACTIONS
    GH_ACTIONS --> GH_SPECKIT
    GH_SPECKIT --> GH_BRANCHES
    
    GH_ACTIONS --> AZ_TOKENS
    AZ_TOKENS --> AZ_METRICS
    AZ_METRICS --> AZ_ALERTS
    
    GH_ACTIONS -.Update.-> ADO_WI
    AZ_TOKENS -.Update.-> ADO_WI
```

This diagram shows the three main system components and how they interact:
- **Azure DevOps**: Where humans work and manage work items
- **GitHub**: Where AI processing happens via Spec Kit
- **Azure Functions**: Where token usage is monitored
