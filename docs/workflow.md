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
├── Custom Fields (ArchitectNotes, Plan, PlanApproved, SpecKitBranch, TokensConsumed*)
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

#### Feature Work Item Fields (Ultra-Lean Model)
```
ArchitectNotes (Text, Multi-line)               # Architect guidance + validation feedback
Plan (HTML)                                     # Consolidated technical plan (incl. contracts, data model summary, key research)
PlanApproved (Boolean, Default: false)          # Architect approval gate
SpecKitBranch (String, Formula: 'feature/[System.Id]')
TokensConsumed (Integer, Default: 0)            # (Optional/Post-MVP) aggregate token estimate
```

System field used for BOTH initial PO intent and evolving specification: **Description**.
The PO writes the initial problem/context in Description; AI overwrites/appends structured spec sections while keeping the original PO intent embedded (Spec Kit already preserves source input in generated artifacts, avoiding data loss).

##### Removed / Not Created & Rationale
| Removed / Omitted | Reason |
|-------------------|--------|
| POInput | Use built-in Description; eliminates duplication and field sprawl |
| Specification | Description holds living spec; version history via work item revisions + Git commits |
| Clarifications | Replaced by child Clarification Issues (see below) |
| Questions | Transient AI output; persisted in artifacts / issues, not a field |
| QuestionsCount | Derivable by counting open Clarification Issues |
| ArchitectInput / ValidationFeedback | Consolidated into `ArchitectNotes` |
| Research | Folded into `Plan` field (links + summary) |
| Contracts / DataModel | Embedded or linked inside `Plan` (markdown / attached repo files) |

##### Clarification Handling (No Custom Fields)
Clarification needs are tracked as **child Issue work items** instead of concatenated text fields:
1. When the AI detects ambiguity it emits a list of clarification prompts.
2. Automation (or a manual quick action) creates one child Issue per prompt with:
  - Title: concise question
  - Description: (a) AI prompt text (b) PO/BA answer section
  - Tag: `Clarification`
3. PO/BA answer by editing the Issue Description (or a dedicated Answer field if desired later).
4. Closed child Issues = resolved clarifications; open Issues = outstanding.
5. Regeneration is triggered only when all child Clarification Issues are closed.

Advantages:
- Natural audit trail & discussion thread per question
- Eliminates brittle parsing of multi-line fields
- Enables analytics (time-to-answer, churn) without extra counters

##### Specification / Plan Storage
- Living specification resides in the system **Description** field (single source inside ADO) and in versioned markdown in Git/GitHub.
- `Plan` HTML field mirrors key technical planning output (contracts summary, data model overview, links to repo artifacts).
- Large structured assets (e.g., `contracts.yaml`, `data_model.md`) are committed to the feature branch and linked from Plan / Description rather than stored as individual custom fields.

##### Description Template (Optional Starter)
Teams may enable a markdown template inside the `Specification` field (or use a Git commit template) instead of extra fields:
```
# Context
<business context>

# User / Stakeholders
<primary users>

# Functional Requirements
- 

# Non-Functional / Constraints
- 

# Open Clarifications
- (link to child clarification Issues)

# Acceptance Criteria
- 
```

> Note: Token consumption tracking (`TokensConsumed`) remains Post-MVP; you may omit creating it initially.

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

#### Feature States (Lean)
New → Specification → Planning → Validation → Ready

Notes:
- Legacy micro-states (Spec Draft, Spec Clarify, Spec Ready, Plan Validation, Ready for Decomposition) were intentionally removed. Board columns and child clarification Issues express intermediate progress.
- System states (Active, Resolved, Closed, Removed) from the Agile process template remain available but are not part of the core Feature lifecycle unless you explicitly map Ready → Closed later.

#### User Story States  
- New → Decomposing → Tasks Created → Implementation → Testing → QA Ready → Done

### 3a. Kanban Board Model (Lean Columns, No AI/Human Split)

Each stage has at most a Doing / Done pair. Clarifications occur inside Specification Doing via child Issue work items (Work Item Type: Issue). No dedicated Clarify state or column is required for MVP.

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
#### Feature Board Columns

| Stage | Doing Column | Done Column | Done Criteria |
|-------|--------------|-------------|--------------|
| Backlog | Backlog (single) | — | Initial context captured in Description |
| Specification | Spec – Doing | Spec – Done | Spec stable; zero open Clarification Issues |
| Planning | Planning – Doing | Planning – Done | Plan artifacts generated & summarized in Plan field |
| Validation | Validation – Doing | Validation – Done | PlanApproved = true |
| Ready | Ready (single) | — | Feature ready for story decomposition |

Clarifications: While any child Issue (Clarification) is open the Feature stays in Spec – Doing. (Optional later: add a `Spec – Clarify` column if visual separation is desired.)

##### Removed Legacy Columns
If previously used, retire: Spec Draft, Spec Clarify, Spec Ready, AI Spec Generating, AI Plan Generating, Plan Validation, Ready for Decomposition.

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
### Ownership Interpretation Rules
1. Doing = active work (human or brief AI). Done = artifact stable & pullable.
2. AI runs happen inside existing Doing columns; they do not trigger column moves.
3. Clarifications = presence of open child Clarification Issues (no extra state/column mandatory).
4. Rework = explicit move from Done back to Doing.
5. Progression = only pull from a Done column into the next stage's Doing.
6. Ready is terminal in the Feature lifecycle (further execution tracked on Stories/Tasks).

#### Workflow Examples
| Scenario | Action | Board Movement |
|----------|--------|----------------|
| AI generates specification | Run inside Spec – Doing | Spec – Doing → Spec – Done when stable & no open clarifications |
| Clarifications discovered | Spec – Doing (remains) | Stays until all Clarification Issues closed |
| Pull into Planning | Spec – Done → Planning – Doing | Manual pull |
| Architect requests plan changes | Validation – Doing → Planning – Doing | Rework |
| Plan approved | Validation – Doing → Validation – Done → Ready | PlanApproved true |
| Minor spec tweak | Spec – Done → Spec – Doing → Spec – Done | Small cycle |

> Implementation detail: In Azure DevOps, create board columns for each Stage/ Subcolumn pair (e.g. `Specification – Doing`, `Specification – Done`). Limit WIP on Doing columns; use policies on Done columns (Definition of Done checklist).

#### Migration Notes (If Coming From Legacy Model)
Remove any of the following legacy columns if they exist: Spec Draft, Spec Clarify, Spec Ready, AI Spec Generating, AI Plan Generating, Plan Validation, Ready for Decomposition. Map in‑flight items as:

| Legacy Pattern | New Placement |
|----------------|---------------|
| Spec Draft / Spec Ready | Specification – Doing / Specification – Done (depending on stability) |
| Spec Clarify (and its Done) | Specification – Doing (use Clarification Issues) |
| AI Spec Generating / AI Plan Generating | Corresponding Stage – Doing (AI runs inline) |
| Plan Validation (Doing/Done) | Validation – Doing / Validation – Done |
| Ready for Decomposition | Ready |
| Decomposing / AI Task Decomposition | Decomposition – Doing |
| Tasks Created | Decomposition – Done |
| QA Ready | Testing – Done |

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

#### Webhook: Feature enters Specification
```json
{
  "Event": "Work item updated",
  "Filter": "State Changes TO 'Specification'",
  "URL": "https://api.github.com/repos/{org}/{repo}/dispatches",
  "Headers": {
    "Authorization": "token {GITHUB_PAT}",
    "Accept": "application/vnd.github.v3+json"
  },
  "Payload": {
    "event_type": "spec-create",
    "client_payload": {
      "feature_id": "[System.Id]",
      "po_input": "[System.Description]"
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
          # Lean model: stay in Specification state; clarifications handled via child Issues
          NEW_STATE="Specification"
          
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

### Phase 2: Specification (Authoring & Clarification Loop)

1. PO creates Feature, adds initial context in Description, sets state to Specification (Board: Specification – Doing).
2. Webhook triggers AI spec generation (specification.md produced / updated). If the AI has questions it creates child Clarification Issues (NOT a state change).
3. PO/BA answers Clarification Issues; AI may regenerate spec. Card remains in Specification – Doing throughout the loop.
4. Completion: no open Clarification Issues, Description/spec stable, acceptance checklist satisfied → move card to Specification – Done (state still Specification).

### Phase 3: Planning

1. Architect (or designated planner) pulls Feature from Specification – Done into Planning – Doing (state: Planning) and enriches Description / Plan field with architectural notes.
2. AI (optional) augments plan (contracts/data model/outline) inline; no extra state.
3. When plan content complete, move card to Planning – Done.

### Phase 4: Validation

1. Architect / Tech Lead reviews plan while in Validation – Doing (state: Validation). Uses PlanApproved flag for gating.
2. If changes needed: move back to Planning – Doing, update, then return.
3. Approval: Set PlanApproved=true and move to Validation – Done; then transition state to Ready.

### Phase 5: Ready & Decomposition

1. Feature now in Ready state (Ready column). Team creates User Stories (manually or via light templates). No AI state transitions required.
2. (Optional) Lightweight decomposition can still be assisted by AI scripts, but remains outside core documented flow.

### Phase 6: Implementation

1. Stories pulled into team sprint; Tasks created as needed.
2. AI assistance (code suggestions/tests) occurs within normal dev workflow; no special states.
3. Definition of Done: tests pass, code reviewed, acceptance criteria met.

### Phase 7: Testing & QA (Inline)

Testing occurs continuously; no dedicated QA Ready state. Teams may add a Testing column locally if desired, but it's outside the lean baseline.

---

## Edit Control Rules

### Core Rules Implementation

#### Lean Guidance (Optional Soft Locks)
Keep rules minimal; prefer social contracts over complex automation. Example optional rules:

1. Soft lock during generation (optional)
```json
{
  "name": "Lock Description During Spec Generation",
  "conditions": { "State": "Specification", "BoardColumn": "Specification – Doing", "ChangedBy": "NOT CONTAINS 'AI:'" },
  "actions": { "MakeReadOnly": ["System.Description"], "ShowMessage": "Spec generation in progress" }
}
```
2. Prevent AI edits if clarifications open (enforce manual resolution first)
```json
{
  "name": "Block AI When Clarifications Open",
  "conditions": { "State": "Specification", "OpenClarificationIssues": "> 0", "ChangedBy": "CONTAINS 'AI:'" },
  "actions": { "RejectChange": "System.Description", "ShowMessage": "Answer remaining Clarification Issues first" }
}
```

No separate clarification state or max-round enforcement required. If governance needed, implement a lightweight dashboard showing open Clarification Issues per Feature.

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
3. Provide more detailed initial Description context

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