# AI-Native SDLC Workflow Implementation Guide
## Azure DevOps + GitHub + Spec Kit Integration

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Team Structure](#team-structure)
4. [Azure DevOps Configuration](#azure-devops-configuration)
5. [GitHub Repository Setup](#github-repository-setup)
6. [Workflow Phases](#workflow-phases)
7. [Edit Control Rules](#edit-control-rules)
8. [Token Tracking](#token-tracking)
9. [Implementation Steps](#implementation-steps)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This document describes the complete implementation of an AI-augmented Software Development Lifecycle (SDLC) that integrates Azure DevOps work item management with GitHub Spec Kit's AI capabilities. Ownership visibility (Human vs AI vs Idle) is conveyed **exclusively through Kanban board columns** rather than tags or explicit ownership fields.

### Key Principles
- **Azure DevOps as Control Plane**: All human work happens in ADO
- **GitHub as AI Processing Engine**: Spec Kit runs in background via webhooks
- **Edit Protection**: ADO rules prevent inappropriate edits at each stage
- **Ownership via Board Columns**: The active owner (Human role, AI agent, or Idle) is implied by which dedicated column the work item sits in. No visual tags or AIOwner field are used.
- **Token Tracking**: Monitor AI usage costs per feature

---

## Architecture

### System Components

```
Azure DevOps (UI Layer)
├── Custom Process Template (AI-SDLC-Agile)
├── Work Item Types (Feature, User Story, Task)
├── Custom Fields (POInput, Specification, etc.)
├── Edit Control Rules
└── Webhooks to GitHub

GitHub (AI Processing Layer)
├── Repository with Spec Kit
├── GitHub Actions Workflows
├── Feature Branches
└── AI Agent Integrations

Azure Functions (Monitoring)
├── Token Consumption Tracking
├── Metrics Collection
└── Alert System
```

### Data Flow
1. Humans work in Azure DevOps
2. State changes trigger webhooks to GitHub
3. GitHub Actions run Spec Kit commands
4. Results update ADO work items
5. Azure Functions track token usage

---

## Team Structure

### Human Roles
- **Product Owner (1)**: Creates features, provides input, answers clarifications
- **Business Analyst (1)**: Assists with specifications and clarifications
- **Architect (1)**: Provides technical guidance, validates plans
- **Developers (3-5)**: Implementation, testing, code fixes
- **QA Tester (Optional)**: Final validation

### AI Agents
- **SpecAgent**: Generates specifications from PO input
- **PlanAgent**: Creates technical plans and architecture
- **TaskAgent**: Decomposes stories into tasks
- **ImplementAgent**: Generates code and tests

---

## Azure DevOps Configuration

### 1. Create Custom Process Template

1. Navigate to Organization Settings → Process
2. Clone "Agile" process as "AI-SDLC-Agile"
3. Apply to your project

### 2. Add Custom Fields

#### Feature Work Item Fields
```
POInput (Text, Multi-line, Required)
Specification (HTML)
Clarifications (Text, Multi-line)
Questions (Text, Multi-line)
QuestionsCount (Integer, Default: 0)
ArchitectInput (Text, Multi-line)
Plan (HTML)
Research (HTML)
Contracts (Text, Multi-line)
DataModel (Text, Multi-line)
ValidationFeedback (Text, Multi-line)
PlanApproved (Boolean, Default: false)
TokensConsumed (Integer, Default: 0)
SpecKitBranch (String, Formula: 'feature/[System.Id]')
```

#### User Story Fields
```
TaskCount (Integer, Default: 0)
TasksJSON (Text, Multi-line)
ImplementationComplete (Boolean, Default: false)
DeveloperTestPassed (Boolean, Default: false)
QATestPassed (Boolean, Default: false)
TestResults (HTML)
ImplementationPhase (String, Picklist)
```

### 3. Configure States

#### Feature States
- New → Spec Draft → Spec Clarify → Spec Ready → Planning → Plan Validation → Ready for Decomposition

#### User Story States  
- New → Decomposing → Tasks Created → Implementation → Testing → QA Ready → Done

### 3a. Kanban Board Ownership Model

Instead of tags or an `AIOwner` field, ownership is inferred from **which column a work item occupies**. Columns are intentionally granular where AI automation occurs so humans instantly understand who/what is acting.

#### Feature Board Columns
| Column | Ownership Meaning | Primary Actor(s) | Transition Trigger | Notes |
|--------|-------------------|------------------|--------------------|-------|
| Backlog | Not started | PO | Created | Input not yet provided |
| Spec Draft | PO authoring | PO / BA | PO moves item | Editable: POInput |
| AI Spec Generating | AI producing spec | SpecAgent (workflow) | State change to Spec Draft triggers webhook | Temporarily read-only core spec fields |
| Spec Clarify | Waiting on human answers | PO / BA | AI produced questions | Clarifications field unlocked |
| Spec Ready | Idle / awaiting architecture | None | All questions resolved & checklist pass | Hand-off point |
| Planning | Architect enriching | Architect | Architect pulls | ArchitectInput editable |
| AI Plan Generating | AI producing plan | PlanAgent | Architect moves to Planning | Plan/DataModel/Contracts generated |
| Plan Validation | Architect review | Architect | AI finishes plan | Approve or send back |
| Ready for Decomposition | Idle | None | Plan approved | Start story creation |

#### User Story Board Columns
| Column | Ownership | Actor(s) | Trigger | Notes |
|--------|-----------|----------|---------|-------|
| Backlog | Not started | PO / BA | Story created | Awaiting pull |
| Decomposing | Human initiating breakdown | Developer | Dev pulls | Prep for AI |
| AI Task Decomposition | AI expanding tasks | TaskAgent | Column move / webhook | tasks.json generated |
| Tasks Created | Idle / review | Developer | AI finished | Dev reviews/edit tasks |
| Implementation | Active build | Developer & ImplementAgent (per task) | Dev starts work | Code + tests cycles |
| Testing | Developer verification | Developer | Implementation complete | Local & integration tests |
| QA Ready | QA validation | QA | Dev marks ready | Optional phase |
| Done | Completed | Team | Tests + acceptance passed | Locked except fixes |

#### Task Board Columns (Optional Granularity)
| Column | Meaning |
|--------|---------|
| Ready | Task available |
| AI Generating | ImplementAgent working |
| Dev Refining | Human adjusting AI output |
| Verifying | Tests executing / being fixed |
| Done | Complete |

### Ownership Interpretation Rules
1. **Single Source**: Column placement is the *only* ownership signal.
2. **Automation Windows**: Any column beginning with `AI` implies temporary write-protection for protected fields.
3. **Human Columns**: Only explicitly human columns permit editing related narrative or acceptance data.
4. **Idle Columns**: Indicate safe hand-off moments; automation will not act until next move.
5. **Audit**: Historical ownership can be reconstructed from board column change history (no separate field needed).


### 4. Set Up Webhooks

Navigate to Project Settings → Service Hooks → Create Subscription

#### Webhook: Feature to Spec Draft
```json
{
  "Event": "Work item updated",
  "Filter": "State Changes TO 'Spec Draft'",
  "URL": "https://api.github.com/repos/{org}/{repo}/dispatches",
  "Headers": {
    "Authorization": "token {GITHUB_PAT}",
    "Accept": "application/vnd.github.v3+json"
  },
  "Payload": {
    "event_type": "spec-create",
    "client_payload": {
      "feature_id": "[System.Id]",
      "po_input": "[Custom.POInput]"
    }
  }
}
```

---

## GitHub Repository Setup

### 1. Repository Structure

```
project-repo/
├── .github/
│   ├── workflows/
│   │   ├── spec-kit-orchestrator.yml
│   │   ├── specification-workflow.yml
│   │   ├── planning-workflow.yml
│   │   ├── task-decomposition.yml
│   │   └── implementation-workflow.yml
│   └── spec-kit/
│       └── config.yml
├── constitution.md
├── specifications/
├── plans/
├── tasks/
└── implementations/
```

### 2. GitHub Actions Workflows

Create `.github/workflows/specification-workflow.yml`:

```yaml
name: Specification Workflow
on:
  repository_dispatch:
    types: [spec-create, spec-clarify]

env:
  ADO_ORG: ${{ secrets.ADO_ORGANIZATION }}
  ADO_PROJECT: ${{ secrets.ADO_PROJECT }}
  ADO_PAT: ${{ secrets.ADO_PAT }}

jobs:
  generate-specification:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install Spec Kit
        run: npm install -g @github/spec-kit
      
      - name: Create Feature Branch
        run: |
          BRANCH="feature/${{ github.event.client_payload.feature_id }}"
          git checkout -b $BRANCH || git checkout $BRANCH
      
      - name: Run Spec Kit Specify
        id: specify
        run: |
          FEATURE_ID="${{ github.event.client_payload.feature_id }}"
          
          spec-kit specify \
            --input "${{ github.event.client_payload.po_input }}" \
            --output ./specifications/$FEATURE_ID
          
          # Check for questions
          if [ -f "./specifications/$FEATURE_ID/questions.json" ]; then
            echo "has_questions=true" >> $GITHUB_OUTPUT
            QUESTIONS=$(cat ./specifications/$FEATURE_ID/questions.json)
            echo "questions=$QUESTIONS" >> $GITHUB_OUTPUT
          else
            echo "has_questions=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Update ADO Feature
        run: |
          FEATURE_ID="${{ github.event.client_payload.feature_id }}"
          NEW_STATE=${{ steps.specify.outputs.has_questions == 'true' && '"Spec Clarify"' || '"Spec Ready"' }}
          
          curl -X PATCH \
            -u :${{ env.ADO_PAT }} \
            -H "Content-Type: application/json-patch+json" \
            "https://dev.azure.com/${{ env.ADO_ORG }}/${{ env.ADO_PROJECT }}/_apis/wit/workitems/$FEATURE_ID?api-version=7.0" \
            -d '[
              {"op": "add", "path": "/fields/System.State", "value": '$NEW_STATE'},
              {"op": "add", "path": "/fields/Custom.TokensConsumed", "value": ${{ steps.specify.outputs.tokens_used || 0 }}}
            ]'
      
      - name: Commit Changes
        run: |
          git add specifications/
          git commit -m "Specification for feature #${{ github.event.client_payload.feature_id }}"
          git push origin feature/${{ github.event.client_payload.feature_id }}
```

### 3. GitHub Secrets Configuration

Add these secrets in Repository Settings → Secrets:
- `ADO_ORGANIZATION`: Your ADO org name
- `ADO_PROJECT`: Your ADO project name  
- `ADO_PAT`: Personal Access Token with Work Items read/write

---

## Workflow Phases

### Phase 1: Project Constitution
**Location**: GitHub repository  
**Participants**: Entire team  
**Output**: constitution.md defining project principles  

### Phase 2: Create Specification

1. **PO creates Feature in ADO**
   - Fills POInput field with requirements
   - Moves to "Spec Draft" state
   - ADO auto-assigns to AI:SpecAgent

2. **AI generates specification**
   - Webhook triggers GitHub Action
   - Spec Kit creates specification.md
   - Generates clarification questions if needed

3. **State transitions**
   - Has questions → "Spec Clarify" (Human:PO)
   - No questions → "Spec Ready" (None)

### Phase 3: Specification Clarification

1. **PO/BA answer questions**
   - Can only edit Clarifications field
   - Answer all question Task items
   - Move back to "Spec Draft" when ready

2. **AI processes clarifications**
   - Refines specification
   - May generate new questions
   - Maximum 5 rounds enforced

3. **Completion criteria**
   - All questions answered
   - Acceptance checklist passed
   - Specification marked complete

### Phase 4: Create Plan

1. **Architect provides input**
   - Pulls from "Spec Ready"
   - Adds architecture guidance
   - Specifies tech stack
   - Moves to "Planning"

2. **AI generates plan**
   - Creates contracts.yaml
   - Generates data model
   - Produces implementation plan
   - Conducts research

3. **Output stored in ADO**
   - Plan attached to Feature
   - State set to "Plan Validation"

### Phase 5: Validate Plan

1. **Architect reviews**
   - Validates tech stack compliance
   - Checks for over-engineering
   - Provides feedback if needed

2. **Iteration if needed**
   - Add ValidationFeedback
   - Move back to "Planning"
   - AI refines based on feedback

3. **Approval**
   - Set PlanApproved = true
   - Move to "Ready for Decomposition"
   - Auto-create User Stories

### Phase 6: Task Decomposition

1. **Developer initiates**
   - Pulls User Story
   - Moves to "Decomposing"
   - Auto-assigns to AI:TaskAgent

2. **AI decomposes**
   - Generates task list with phases
   - Estimates effort
   - Creates Task work items

3. **Review and proceed**
   - Developer reviews tasks
   - Moves to "Implementation"

### Phase 7: Implementation

1. **AI generates code**
   - Creates implementation
   - Generates unit tests
   - Runs automated tests

2. **Developer involvement**
   - Reviews generated code
   - Makes manual adjustments
   - Runs local tests

3. **State progression**
   - Tests pass → "Testing"
   - Tests fail → Fix and retry

### Phase 8: Testing & QA

1. **Developer testing**
   - Manual validation
   - Integration testing
   - Moves to "QA Ready" if passed

2. **QA validation** (optional)
   - Functional testing
   - Logs defects if found
   - Approves for Done

---

## Edit Control Rules

### Core Rules Implementation

#### Rule 1: Block Human Edits During AI Work
```json
{
  "name": "Block Human During AI Spec",
  "conditions": {
    "State": "Spec Draft",
    "ChangedBy": "NOT CONTAINS 'AI:'"
  },
  "actions": {
    "MakeReadOnly": ["Specification", "Questions"],
    "ShowMessage": "AI is generating specification. Please wait."
  }
}
```

#### Rule 2: Block AI During Human Work
```json
{
  "name": "Block AI During Clarification",
  "conditions": {
    "State": "Spec Clarify",
    "ChangedBy": "CONTAINS 'AI:'"
  },
  "actions": {
    "RejectChange": "ALL FIELDS",
    "ShowMessage": "Waiting for human clarification"
  }
}
```

#### Rule 3: Enforce Max Clarification Rounds
```json
{
  "name": "Max Clarification Rounds",
  "conditions": {
    "State": "Spec Clarify",
    "Custom.ClarificationRound": "> 5"
  },
  "actions": {
    "BlockTransition": "Spec Draft",
    "RequireApproval": "Architect",
    "ShowMessage": "Maximum clarification rounds reached. Architect review required."
  }
}
```

### State-Specific Permissions

| State | Can Edit | Cannot Edit |
|-------|----------|-------------|
| New | PO, BA | AI Agents |
| Spec Draft | AI:SpecAgent | All Humans |
| Spec Clarify | PO, BA | AI Agents |
| Spec Ready | Architect | PO, BA, AI |
| Planning | AI:PlanAgent | All Humans |
| Plan Validation | Architect | PO, BA, Devs |
| Implementation | AI:ImplementAgent, Developer | PO, BA, Arch |

---

## Token Tracking

### Azure Function Setup

1. **Create Function App** in Azure Portal
2. **Deploy token tracking function**:

```javascript
module.exports = async function (context, req) {
    const { work_item_id, tokens, ai_agent } = req.body;
    
    // Store in Azure Table Storage
    const entity = {
        partitionKey: 'Feature',
        rowKey: `${work_item_id}_${Date.now()}`,
        workItemId: work_item_id,
        aiAgent: ai_agent,
        tokensUsed: tokens,
        estimatedCost: (tokens / 1000) * 0.03,
        timestamp: new Date().toISOString()
    };
    
    await tableClient.createEntity(entity);
    
    // Update ADO work item
    await updateADOTokenCount(work_item_id, tokens);
    
    return { status: 200, body: "Tokens logged" };
};
```

3. **Configure webhook** in GitHub Actions to call function

### Token Budget Estimates

| Phase | Agent | Tokens | Cost |
|-------|-------|--------|------|
| Specification | SpecAgent | 10-20K | $0.30-0.60 |
| Planning | PlanAgent | 15-25K | $0.45-0.75 |
| Decomposition | TaskAgent | 5-10K | $0.15-0.30 |
| Implementation | ImplementAgent | 30-50K | $0.90-1.50 |
| **Total per Feature** | | **60-105K** | **$1.80-3.15** |

---

## Implementation Steps

### Week 1: ADO Setup
1. Create custom process template
2. Add all custom fields
3. Configure work item states
4. Set up edit control rules
5. Create service hooks for webhooks

### Week 2: GitHub Setup
1. Create repository structure
2. Deploy GitHub Actions workflows
3. Configure secrets
4. Test webhook connectivity
5. Install Spec Kit

### Week 3: Azure Infrastructure
1. Deploy Azure Function App
2. Create Table Storage
3. Configure Application Insights
4. Test token tracking
5. Set up alerts

### Week 4: Pilot Testing
1. Create test feature with simple requirements
2. Run through complete workflow
3. Verify edit controls work
4. Check token tracking accuracy
5. Document any issues

### Week 5: Team Training
1. Overview session for all team
2. Role-specific training sessions
3. Practice with test features
4. Create quick reference guides
5. Establish support channels

### Week 6: Go Live
1. Process first real feature
2. Daily standups to check progress
3. Monitor token consumption
4. Address issues immediately
5. Gather team feedback

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Work item stuck in AI state
**Symptoms**: Feature/Story in AI-ACTIVE state for >30 minutes  
**Solution**:
1. Check GitHub Actions logs: `https://github.com/{org}/{repo}/actions`
2. Look for failed workflows
3. Manually retrigger via webhook
4. If still stuck, Architect can override with special permission

#### Issue: Clarification loop exceeding 5 rounds
**Symptoms**: Multiple clarification cycles without resolution  
**Solution**:
1. Architect reviews and simplifies requirements
2. Consider splitting into smaller features
3. Provide more detailed initial POInput

#### Issue: Token consumption spike
**Symptoms**: Feature using >100K tokens  
**Solution**:
1. Review feature complexity
2. Check GitHub logs for retry loops
3. Split large features into smaller ones
4. Adjust AI model parameters (temperature)

#### Issue: Webhooks not triggering
**Symptoms**: State changes but GitHub Actions don't run  
**Solution**:
1. Verify webhook URL in ADO Service Hooks
2. Check GitHub PAT hasn't expired
3. Confirm repository dispatch events enabled
4. Test with manual trigger

#### Issue: Edit controls not working
**Symptoms**: Users can edit fields they shouldn't  
**Solution**:
1. Verify process template applied to project
2. Check rule conditions syntax
3. Confirm item is in the correct ownership column (e.g., NOT left in a human column while AI workflow is running)
4. Clear browser cache and refresh

### Emergency Procedures

#### Manual Override Process
1. Architect logs into ADO
2. Uses special "AI.Override" permission
3. Manually updates blocked fields
4. Documents reason for override
5. Notifies team of manual intervention

#### Rollback Procedure
1. Move work item to previous state
2. Clear AI-generated fields
3. Reset TokensConsumed counter
4. Delete feature branch if corrupted
5. Restart from last good state

---

## Monitoring and Metrics

### Daily Health Checks
- [ ] All work items progressing (none stuck >4 hours)
- [ ] Token consumption within budget
- [ ] No failed GitHub Actions
- [ ] Edit controls functioning
- [ ] Team not blocked

### Weekly Reports
```sql
-- ADO Query for Weekly Token Report
SELECT 
    [System.Id],
    [System.Title],
    [Custom.TokensConsumed],
    [System.State],
    [System.ChangedDate]
FROM workitems
WHERE [System.WorkItemType] = 'Feature'
    AND [Custom.TokensConsumed] > 0
    AND [System.ChangedDate] >= @Today - 7
ORDER BY [Custom.TokensConsumed] DESC
```

### Success Metrics
- Average cycle time per feature: Target < 3 days
- First-time specification acceptance: Target > 80%
- Token cost per feature: Target < $5
- Manual interventions required: Target < 10%

---

## Appendix

### ADO Picklist Values

#### (Removed) AIOwner Field
Ownership is now fully represented via board columns (see Kanban Board Ownership Model). No dedicated ownership field is required; remove any previously added `AIOwner` picklist.

#### ImplementationPhase Options
- Infrastructure
- Backend
- Frontend
- Integration
- Testing

### Useful Links
- ADO Process Customization: `https://dev.azure.com/{org}/_settings/process`
- GitHub Actions: `https://github.com/{org}/{repo}/actions`
- Token Dashboard Query: `https://dev.azure.com/{org}/{project}/_queries/shared`
- Spec Kit Documentation: `https://github.com/github/spec-kit`

### Support Contacts
- ADO Admin: [Your admin contact]
- GitHub Admin: [Your admin contact]
- Architect (Override Authority): [Architect contact]
- Emergency Escalation: [Escalation contact]

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | [Author] | Initial documentation |

---

*End of Documentation*