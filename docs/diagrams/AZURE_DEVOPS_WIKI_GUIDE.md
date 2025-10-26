# Azure DevOps Wiki Integration Guide

This guide explains how to use these Mermaid diagrams in Azure DevOps Wiki.

## Quick Start

All diagrams in this directory are already formatted for Azure DevOps Wiki:
- Use `::: mermaid` syntax (not ` ```mermaid` `)
- Designed for both dark and light themes
- No color dependencies

## How to Add Diagrams to ADO Wiki

1. **Navigate to your Azure DevOps Wiki**
2. **Create or edit a wiki page**
3. **Copy the entire diagram** from any `.md` file in this directory
4. **Paste directly** into the wiki editor
5. **Save** - the diagram will render automatically

## Example

From `01-architecture-overview.md`:

```
::: mermaid
graph TB
    subgraph AzureDevOps["Azure DevOps - Control Plane"]
        ADO_UI["Azure DevOps UI"]
        ADO_WI["Work Items"]
    end
:::
```

Simply copy everything from `::: mermaid` to `:::` and paste it into your wiki page.

## Theme Compatibility

✅ **Works in Dark Theme**  
✅ **Works in Light Theme**  

All diagrams avoid hard-coded colors and use descriptive text labels instead.

## Diagram Format Differences

| Format | Start Block | End Block | Where Used |
|--------|-------------|-----------|------------|
| Azure DevOps Wiki | `::: mermaid` | `:::` | ADO Wiki (these files) |
| GitHub/Standard | ` ```mermaid` | ` ``` ` | GitHub, most markdown |

## Converting to GitHub Format (if needed)

If you need to use these diagrams in GitHub instead:

```bash
# Replace Azure DevOps syntax with GitHub syntax
sed 's/::: mermaid/```mermaid/g' diagram.md | sed 's/^:::$/```/g'
```

Or manually:
1. Replace `::: mermaid` with ` ```mermaid`
2. Replace `:::` with ` ``` `

## Troubleshooting

### Diagram Not Rendering in ADO Wiki

**Problem**: Diagram shows as plain text

**Solutions**:
1. Ensure you're using `::: mermaid` (not ` ```mermaid` `)
2. Check that the closing `:::` is on its own line
3. Verify no extra spaces before/after the delimiters
4. Make sure Mermaid support is enabled in your ADO organization

### Diagram Looks Bad in Dark/Light Theme

**Problem**: Colors are hard to see in one theme

**Solution**: These diagrams are designed to work in both themes. If you've modified them and added custom colors, remove the `style` statements.

**Before (theme-dependent):**
```
style Node1 fill:#ffcccc
```

**After (theme-independent):**
```
Node1["Description with context"]
```

## Recommended Wiki Structure

Organize diagrams in your ADO Wiki like this:

```
📁 Project Wiki
├── 📄 Home
├── 📁 Architecture
│   ├── 📄 Overview (use 01-architecture-overview.md)
│   └── 📄 Data Flow (use 02-data-flow.md)
├── 📁 Workflow
│   ├── 📄 Feature States (use 03-feature-workflow-states.md)
│   ├── 📄 User Story States (use 04-user-story-workflow-states.md)
│   ├── 📄 Kanban Board (use 05-kanban-board-ownership.md)
│   └── 📄 Complete Workflow (use 06-complete-workflow-phases.md)
├── 📁 Team
│   └── 📄 Team Structure (use 08-team-structure.md)
└── 📁 Operations
    ├── 📄 Token Tracking (use 09-token-tracking-flow.md)
    └── 📄 Troubleshooting (use 12-troubleshooting-decision-tree.md)
```

## Validation

All diagrams have been validated with the Mermaid syntax checker. To validate yourself:

```bash
node check_mermaid.js docs/diagrams/<filename>.md
```

The output will show diagnostic information (not errors).

## Support

For Mermaid syntax questions: https://mermaid.js.org/  
For ADO Wiki questions: https://learn.microsoft.com/azure/devops/project/wiki/

---

**Last Updated**: October 26, 2025  
**Format Version**: Azure DevOps Wiki (Mermaid)  
**Theme Support**: Dark & Light
