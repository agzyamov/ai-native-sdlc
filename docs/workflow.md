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

We now simplify the boards by using a small set of STAGES, each (where it adds clarity) split into two **sub‑columns**:
`Doing` (active work happening) and `Done` (stage output ready; safe hand‑off). This reduces column sprawl (e.g. removing separate *AI* vs *Human* variants) while preserving ownership clarity. Ownership is still inferred **only from the current (Stage + Subcolumn)**. No tags or explicit owner field required.

#### Principles of the Simplified Model
| Principle | Description |
|-----------|-------------|
| Stage Minimalism | Only major value producing phases become board stages. |
| Doing / Done Pair | Doing = work in progress; Done = artifact stable & waiting for pull. |
| Implicit Actor | Actor is implied by the nature of work in that Stage (see tables). |
| Mixed Responsibility Windows | If both AI & Human act inside a Doing subcolumn, protected fields remain read-only while AI is executing; humans resume editing when AI run completes (without moving columns). |
| Idempotent AI Runs | Re-running AI inside the same Doing subcolumn never requires a column move (prevents “AI Generating” noise columns). |
| Auditability | History (Stage transitions + subcolumn changes) reconstructs ownership timeline. |

---
#### Feature Board (Simplified)

| Stage (Column Group) | Doing Subcolumn (Suggested Name) | Done Subcolumn (Suggested Name) | Primary Active Actor(s) in Doing | Artifact Produced / Criteria for Done | Transition to Next Stage |
|----------------------|----------------------------------|---------------------------------|----------------------------------|--------------------------------------|--------------------------|
| Backlog | (single column – no split) | — | PO | Raw idea, minimal POInput | PO pulls into Specification Doing |
| Specification | Spec – Doing | Spec – Done | AI SpecAgent (initial generation) then PO/BA refinement | Acceptable spec draft OR no open questions generated | If questions → Clarification Doing; else → Planning Doing |
| Clarification (conditional) | Clarify – Doing | Clarify – Done | PO / BA | All AI questions answered & clarification round closed | Move back to Specification Doing for regeneration OR (if no new questions) to Specification Done → Planning Doing |
| Planning | Planning – Doing | Planning – Done | Architect (inputs) + AI PlanAgent (plan generation) | Plan, Contracts, Data Model generated | Move to Plan Validation Doing |
| Plan Validation | Validation – Doing | Validation – Done | Architect | PlanApproved = true | Ready for Decomposition (single) |
| Ready for Decomposition | (single column) | — | — (Idle) | Feature ready to spawn stories | Story creation automation / manual trigger |

Notes:
- *Specification Done* replaces previous `Spec Ready`.
- AI execution happens **inside** Spec / Planning Doing rather than separate AI columns.
- Clarification Stage appears only if the spec generation produced questions.

##### Old → New Feature Column Mapping
| Old Column | New Stage/Subcolumn |
|------------|---------------------|
| Backlog | Backlog |
| Spec Draft | Specification – Doing |
| AI Spec Generating | Specification – Doing (AI run inside) |
| Spec Clarify | Clarification – Doing / Done (depending on progress) |
| Spec Ready | Specification – Done |
| Planning | Planning – Doing |
| AI Plan Generating | Planning – Doing (AI run inside) |
| Plan Validation | Plan Validation – Doing / Done |
| Ready for Decomposition | Ready for Decomposition |

---
#### User Story Board (Simplified)

| Stage (Column Group) | Doing Subcolumn | Done Subcolumn | Primary Actor(s) in Doing | Output / Done Criteria | Next Stage Trigger |
|----------------------|-----------------|----------------|---------------------------|-----------------------|--------------------|
| Backlog | (single) | — | PO / BA | Story defined | Developer pulls to Decomposition Doing |
| Decomposition | Decomposition – Doing | Decomposition – Done | Developer (setup) + AI TaskAgent (task expansion) | Tasks enumerated & reviewed | Implementation Doing |
| Implementation | Implementation – Doing | Implementation – Done | Developer + AI ImplementAgent | Code + unit tests passing locally | Testing Doing (or directly Done for trivial stories) |
| Testing | Testing – Doing | Testing – Done | Developer (dev tests) / QA (if present) | All required tests pass & acceptance verified | Done |
| Done | (single) | — | Team | Story meets Definition of Done | — |

Old QA Ready column merges into Testing (Done = “QA / acceptance complete”).

##### Old → New User Story Column Mapping
| Old Column | New Stage/Subcolumn |
|------------|---------------------|
| Backlog | Backlog |
| Decomposing | Decomposition – Doing |
| AI Task Decomposition | Decomposition – Doing (AI run) |
| Tasks Created | Decomposition – Done |
| Implementation | Implementation – Doing |
| Testing | Testing – Doing |
| QA Ready | Testing – Done |
| Done | Done |

---
#### Task (Optional) Board (Lean Version)

If you still visualize Tasks, apply the same pattern:

| Stage | Doing | Done Meaning |
|-------|-------|--------------|
| Ready | (single) | Task not yet pulled |
| Implementation | Impl – Doing | Impl – Done = code + unit test passing |
| Verification | Verify – Doing | Verify – Done = merged / integrated |
| Done | (single) | Task closed |

---
### Ownership Interpretation Rules (Revised)
1. **Single Source**: (Stage, Subcolumn) pair encodes ownership & readiness.
2. **AI Inside Doing**: AI executions do not cause column moves; UI cues (e.g. decoration, automation log) mark active AI window.
3. **Human Editing Windows**: Humans may edit permitted fields in Doing unless an AI run is active (then protected fields are locked temporarily by rule).
4. **Done Subcolumns Are Read-Only for Core Artifacts**: Except for explicit “Return to Doing” action (e.g. architect feedback or new clarification discovered).
5. **Clarification Rounds**: Round counter increments only when moving Clarify Done → Specification Doing for regeneration.
6. **Audit**: Transition history of Doing/Done boundaries captures cadence and waits (latency hotspots).

#### Workflow Examples
| Scenario | Action | Board Movement |
|----------|--------|----------------|
| AI generates initial spec | Run inside Spec – Doing | Stay in Spec – Doing (spinner) → Spec – Done |
| Questions produced | Spec – Done → Clarify – Doing | Manual move or automation |
| Architect requests plan changes | Validation – Doing → Planning – Doing | (Re-open) |
| Minor spec tweak (no AI) | Spec – Done → Spec – Doing → Spec – Done | Fast cycle |
| Clarification loop ends | Clarify – Done → Spec – Doing (regen) | Then back to Spec – Done |

> Implementation detail: In Azure DevOps, create board columns for each Stage/ Subcolumn pair (e.g. `Specification – Doing`, `Specification – Done`). Limit WIP on Doing columns; use policies on Done columns (Definition of Done checklist).

#### Migration Notes (Legacy → Simplified Board)
| Legacy Column | New Home | Migration Action |
|---------------|----------|------------------|
| AI Spec Generating | Specification – Doing | Remove legacy column; AI runs inline. |
| Spec Draft | Specification – Doing | Rename. |
| Spec Ready | Specification – Done | Rename. |
| Spec Clarify | Clarification – Doing / Done | Split by whether answers complete. |
| Planning | Planning – Doing | Rename. |
| AI Plan Generating | Planning – Doing | Remove; AI runs inline. |
| Plan Validation | Validation – Doing / Done | Split by approval state. |
| Ready for Decomposition | Ready for Decomposition | Keep. |
| Decomposing / AI Task Decomposition | Decomposition – Doing | Merge; AI inline. |
| Tasks Created | Decomposition – Done | Rename. |
| QA Ready | Testing – Done | Merge. |

Steps:
1. Freeze board moves briefly (communicate to team).
2. Create new columns (Doing then Done for each stage) in desired order.
3. Bulk move items based on rules above (filter by current column & state).
4. Delete obsolete AI-prefixed columns.
5. Update any automation referencing old column names.
6. Announce new WIP limits & Done policies.
7. Monitor first week: capture friction & adjust naming if needed.



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

> Post-MVP Notice: Full automated token consumption tracking (Azure Function, storage, dashboards,
> alerting) is **deferred to the Post-MVP phase**. For the MVP the team will:
> - Capture approximate token usage manually from GitHub Action logs (aggregate per Feature weekly)
> - Track a simple cumulative estimate in a temporary custom field (optional) or a shared spreadsheet
> - Skip Azure Function + Table Storage deployment until stability of core spec/plan/implementation loop is validated
>
> Sections below describe the intended Post-MVP target architecture; implement only after core workflow adoption metrics (feature cycle time, clarification loop stability) are satisfactory.

### Azure Function Setup (Post-MVP Target)

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

### Token Budget Estimates (Planning Reference)

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