# Azure DevOps Integration

## Service Hook Integration

### Webhook Flow

1. Azure DevOps Service Hook triggers on work item update
2. Payload sent to Azure Function endpoint
3. Function validates event (work item type, assignee, column)
4. Function dispatches GitHub workflow via `workflow_dispatch`
5. GitHub Actions runs Spec Kit to generate specification

### Event Validation

The Azure Function validates:
- `eventType` must be `"workitem.updated"`
- `workItemType` must be `"Feature"`
- `assignee.displayName` must match `AI_USER_MATCH` (case-insensitive)
- `boardColumn` must match `SPEC_COLUMN_NAME` (default: "Specification – Doing")
- `boardColumnDone` must be `false` (Doing, not Done)

### Payload Structure

```json
{
  "eventType": "workitem.updated",
  "resource": {
    "workItemId": 123,
    "revision": {
      "fields": {
        "System.WorkItemType": "Feature",
        "System.AssignedTo": {
          "displayName": "AI Teammate"
        },
        "System.BoardColumn": "Specification – Doing",
        "System.BoardColumnDone": false,
        "System.Title": "Feature Title"
      }
    }
  }
}
```

## Work Item Fields

### Feature Work Item Fields

- **ArchitectNotes** (Text, Multi-line): Architect guidance + validation feedback
- **Plan** (HTML): Consolidated technical plan
- **PlanApproved** (Boolean, Default: false): Architect approval gate
- **SpecKitBranch** (String, Formula: 'feature/[System.Id]'): Feature branch name
- **TokensConsumed** (Integer, Default: 0): Aggregate token estimate (optional)

## Board Column Mapping

Board columns indicate ownership and state:

- **Specification – Doing**: AI actively generating spec
- **Specification – Done**: Spec complete, ready for planning
- **Planning – Doing**: Plan being created
- **Planning – Done**: Plan ready for validation
- **Validation**: Awaiting architect approval
- **Ready**: Approved and ready for implementation

## Work Item State Transitions

### Feature States (Lean Model)

1. **New** → Initial state
2. **Specification** → Spec generation and clarification (Doing/Done columns)
3. **Planning** → Technical plan creation
4. **Validation** → Plan approval gate
5. **Ready** → Ready for decomposition into stories/tasks

## ADO REST API Client

### Authentication

Use Personal Access Token (PAT) with Work Items (Read) scope:

```python
headers = {
    "Authorization": f"Basic {base64.b64encode(f':{pat}'.encode()).decode()}",
    "Content-Type": "application/json"
}
```

### Common Operations

#### Fetch Work Item

```python
url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.1"
response = requests.get(url, headers=headers, timeout=30)
```

#### Update Work Item Description

```python
url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.1"
payload = [
    {
        "op": "replace",
        "path": "/fields/System.Description",
        "value": new_description
    }
]
response = requests.patch(url, headers=headers, json=payload, timeout=30)
```

## Error Handling

- Always include `timeout` parameter in HTTP requests
- Handle 404 (work item not found) gracefully
- Log correlation IDs for tracing
- Return appropriate HTTP status codes from function

## Related Rules

- See [azure-functions.md](azure-functions.md) for function deployment
- See [python.md](python.md) for Python coding standards
- See [spec-kit.md](spec-kit.md) for Spec Kit workflow patterns

