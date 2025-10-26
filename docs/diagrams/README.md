# AI-Native SDLC Workflow Diagrams

This directory contains visual diagrams to help understand the AI-Native SDLC workflow described in [workflow.md](../workflow.md).

## Diagram Index

### System Architecture
1. **[Architecture Overview](01-architecture-overview.md)** - High-level system components and their interactions
2. **[Data Flow](02-data-flow.md)** - Sequence diagram showing how data flows through the system

### Work Item Lifecycles
3. **[Feature Workflow States](03-feature-workflow-states.md)** - State transitions for Feature work items
4. **[User Story Workflow States](04-user-story-workflow-states.md)** - State transitions for User Story work items
5. **[Kanban Board Ownership](05-kanban-board-ownership.md)** - Visual representation of ownership via board columns

### Process Flows
6. **[Complete Workflow Phases](06-complete-workflow-phases.md)** - End-to-end workflow from start to finish
7. **[Edit Control Rules](07-edit-control-rules.md)** - How edit protection works at each stage
8. **[Specification Clarification Loop](10-specification-clarification-loop.md)** - Detailed clarification process
9. **[Implementation Cycle](11-implementation-cycle.md)** - Code generation and testing iterations

### Team & Monitoring
10. **[Team Structure](08-team-structure.md)** - Human roles and AI agents with responsibilities
11. **[Token Tracking Flow](09-token-tracking-flow.md)** - How AI usage costs are monitored
12. **[Troubleshooting Decision Tree](12-troubleshooting-decision-tree.md)** - Systematic problem resolution guide

## How to Use These Diagrams

### For New Team Members
Start with:
1. Architecture Overview (01)
2. Team Structure (08)
3. Complete Workflow Phases (06)

### For Product Owners / Business Analysts
Focus on:
- Feature Workflow States (03)
- Specification Clarification Loop (10)
- Kanban Board Ownership (05)

### For Architects
Review:
- Architecture Overview (01)
- Data Flow (02)
- Edit Control Rules (07)

### For Developers
Study:
- User Story Workflow States (04)
- Implementation Cycle (11)
- Troubleshooting Decision Tree (12)

### For Administrators
Reference:
- Architecture Overview (01)
- Token Tracking Flow (09)
- Troubleshooting Decision Tree (12)

## Viewing the Diagrams

All diagrams use [Mermaid](https://mermaid.js.org/) syntax with Azure DevOps wiki formatting (`::: mermaid` blocks) and can be viewed in:
- **Azure DevOps Wiki**: Copy/paste directly - diagrams will render automatically
- **GitHub**: May need conversion to ` ```mermaid` ` format (replace `::: mermaid` with ` ```mermaid` ` and `:::` with ` ``` `)
- **VS Code**: Install the "Markdown Preview Mermaid Support" extension
- **Mermaid Live Editor**: https://mermaid.live/ (copy/paste diagram code)

### Converting Between Formats

**For Azure DevOps Wiki:**
- Use `::: mermaid` to start and `:::` to close
- Already configured in these files

**For GitHub/Standard Markdown:**
- Replace `::: mermaid` with ` ```mermaid`
- Replace `:::` with ` ``` `

## Theme Compatibility

All diagrams have been designed to work in both **dark and light themes**:
- No hard-coded background colors
- Text labels instead of color-dependent styling
- Avoiding theme-specific color fills
- Using semantic labels and clear node descriptions

## Diagram Colors

These diagrams use minimal color coding to ensure compatibility with both dark and light themes. Instead of relying on background colors, we use:
- **Descriptive node labels** to indicate ownership and status
- **"AI" prefix** in column names to show AI-active states
- **Role names** in labels to show human ownership
- **"Idle"** markers to show hand-off points
- **Clear text descriptions** instead of color-dependent information

## Contributing

When adding new diagrams:
1. Use Mermaid syntax
2. Follow the naming convention: `##-descriptive-name.md`
3. Update this README with the new diagram
4. Validate syntax at https://mermaid.live/
5. Keep diagrams focused on a single concept
6. Use consistent color coding

## Questions or Issues?

Refer to the main [workflow.md](../workflow.md) documentation for detailed explanations of any concepts shown in these diagrams.
