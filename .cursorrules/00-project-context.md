# Project Context

## Overview

This is an **AI-Native SDLC** project that automates a lean, AI-augmented Specification → Planning → Validation workflow using GitHub Copilot & Spec Kit. It integrates Azure DevOps work item management with GitHub's AI processing capabilities.

## Architecture

### System Components

```
Azure DevOps (UI Layer)
├── Custom Process Template (AI-SDLC-Agile)
├── Work Item Types (Feature, User Story, Task)
├── Custom Fields (ArchitectNotes, Plan, PlanApproved, SpecKitBranch, TokensConsumed)
├── Edit Control Rules
└── Webhooks to GitHub

GitHub (AI Processing Layer)
├── Repository with Spec Kit
├── GitHub Actions Workflows
├── Feature Branches
└── AI Agent Integrations

Azure Functions (Integration Layer)
├── Service Hook Receiver
├── GitHub Workflow Dispatch
└── Validation & Logging
```

### Data Flow

1. Product Owner creates Feature in Azure DevOps
2. Feature assigned to "AI Teammate" and moved to "Specification – Doing" column
3. Azure DevOps Service Hook triggers Azure Function
4. Azure Function validates event and dispatches GitHub workflow
5. GitHub Actions runs Spec Kit to generate specification
6. Specification committed to feature branch and synced back to ADO

## Key Principles

- **Azure DevOps as Control Plane**: All human work happens in ADO
- **GitHub as AI Processing Engine**: Spec Kit runs in background via webhooks
- **Edit Protection**: ADO rules prevent inappropriate edits at each stage
- **Ownership via Board Columns**: Active owner (Human, AI, or Idle) is implied by Kanban column
- **Token Tracking**: Monitor AI usage costs per feature

## Project Structure

```
/
├── function_app/          # Azure Functions (Python)
│   ├── __init__.py        # HTTP trigger entry point
│   ├── validation.py      # Event validation logic
│   ├── dispatch.py        # GitHub workflow_dispatch client
│   ├── ado_client.py      # Azure DevOps REST client
│   └── models.py          # Data models
├── infra/                 # Terraform infrastructure
│   ├── main.tf            # Resource definitions
│   ├── variables.tf       # Input variables
│   └── outputs.tf         # Output values
├── .github/
│   ├── workflows/         # GitHub Actions workflows
│   └── prompts/           # Spec Kit prompts
├── specs/                 # Feature specifications
│   └── {feature-id}/      # Per-feature spec directories
└── docs/                  # Documentation
    └── diagrams/          # Mermaid diagrams
```

## Technology Stack

- **Python 3.11+**: Azure Functions runtime
- **Terraform**: Infrastructure as Code (azurerm provider ~> 3.0)
- **GitHub Actions**: CI/CD and Spec Kit automation
- **Azure Functions**: HTTP-triggered webhook receiver
- **Azure DevOps**: Work item management and Kanban boards

## Key Integrations

### Azure DevOps → GitHub
- Service Hook triggers on work item updates
- Feature branch creation and naming conventions
- Bidirectional sync of specifications

### Spec Kit Workflows
- Specification generation from feature descriptions
- Plan enrichment and validation
- Clarification question extraction

## Workflow States

### Feature States (Lean Model)
1. **New** → Initial state
2. **Specification** → Spec generation and clarification (Doing/Done columns)
3. **Planning** → Technical plan creation
4. **Validation** → Plan approval gate
5. **Ready** → Ready for decomposition into stories/tasks

### Board Columns
- **Specification – Doing**: AI actively generating spec
- **Specification – Done**: Spec complete, ready for planning
- **Planning – Doing**: Plan being created
- **Planning – Done**: Plan ready for validation
- **Validation**: Awaiting architect approval
- **Ready**: Approved and ready for implementation

## Related Rules

- See [ado-integration.md](ado-integration.md) for ADO integration patterns
- See [spec-kit.md](spec-kit.md) for Spec Kit workflow conventions
- See [azure-functions.md](azure-functions.md) for function deployment
- See [terraform.md](terraform.md) for infrastructure patterns

