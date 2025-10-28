# Azure Function: Spec Dispatch

## Purpose

HTTP-triggered Azure Function that receives Azure DevOps Service Hook events and dispatches the GitHub spec generation workflow.

## Flow

1. **Receive** work item update event from ADO Service Hook
2. **Validate** event type, work item type, assignee, and column
3. **Dispatch** GitHub workflow_dispatch to trigger spec generation
4. **Log** structured JSON output with correlation ID

## Environment Variables

### Required
- `GITHUB_OWNER` - GitHub repository owner
- `GITHUB_REPO` - GitHub repository name
- `GITHUB_WORKFLOW_FILENAME` - Workflow file (default: `spec-kit-specify.yml`)
- `GH_WORKFLOW_DISPATCH_PAT` - GitHub PAT (Actions: RW, Contents: R)
- `ADO_WORK_ITEM_PAT` - Azure DevOps PAT (Work Items: Read) - used for fallback fetch
- `SPEC_COLUMN_NAME` - Board column trigger (default: `Specification – Doing`)
- `AI_USER_MATCH` - AI teammate display name (case-insensitive)

### Optional
- `LOG_LEVEL` - Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) - default: `INFO`
- `FUNCTION_TIMEOUT_SECONDS` - Max execution time - default: `30`

## Local Development

### Prerequisites
- Python 3.11+
- Azure Functions Core Tools v4

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run locally
```bash
func start
```

### Test with sample payload
```bash
# Using sample ADO hook JSON
curl -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d @../specs/001-ado-github-spec/contracts/sample-ado-hook.json

# Or use the test script
cd tests
./test-local.sh
```

### Test with real work item
```bash
# Test with real Azure DevOps work item
cd tests
./test-real-workitem.sh 448  # Replace 448 with your work item ID
```

See `tests/LOCAL_TESTING.md` for detailed testing documentation.

## Deployment

### Via Azure CLI
```bash
cd function_app
func azure functionapp publish <function-app-name>
```

### Via Terraform
See `infra/README.md` for infrastructure provisioning.

## Modules

- `__init__.py` - HTTP trigger entry point
- `validation.py` - Event validation logic
- `dispatch.py` - GitHub workflow_dispatch client
- `models.py` - Data models (WorkItemEvent)
- `ado_client.py` - (T027) Azure DevOps REST client
- `config.py` - (T035) Environment configuration loader

## Testing

Unit tests are located in `/tests` directory (workspace root).

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=function_app tests/
```

Local integration testing scripts are in `function_app/tests/`:
- `test-local.sh` - Test with sample ADO hook JSON
- `test-real-workitem.sh` - Test with real work item from Azure DevOps
- `debug-test.sh` - Debug mode test with verbose output
- `LOCAL_TESTING.md` - Comprehensive local testing guide

## Logging

Structured JSON logs include:
- `correlation_id` - Unique request identifier
- `work_item_id` - ADO work item ID
- `event` - Event type or step
- `status` - Outcome (success, validation_failed, etc.)
- `latency_ms` - Execution time

## Error Responses

| Code | Reason | Action |
|------|--------|--------|
| 200 | Accepted but not processed | Event doesn't match filter criteria (graceful no-op) |
| 204 | Successfully dispatched | Workflow triggered |
| 400 | Malformed payload | Check Service Hook JSON structure |
| 403 | Validation failed | Wrong work item type, assignee, or column |
| 500 | Internal error | Check function logs |

## Security

- All outbound HTTP calls include explicit `timeout` parameter
- PATs stored in Azure App Settings (encrypted at rest)
- Function key required for endpoint access
- Consider HMAC signature validation for production (future enhancement)

## Manual Testing

Test the deployed function with a sample payload:

```bash
# Get function URL and key from Azure Portal or Terraform output
FUNCTION_URL="https://<your-function-app>.azurewebsites.net"
FUNCTION_KEY="<your-function-key>"

curl -X POST "$FUNCTION_URL/api/spec-dispatch?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d @../specs/001-ado-github-spec/contracts/sample-ado-hook.json

# Expected responses:
# 204 - Successfully dispatched (check GitHub Actions for workflow run)
# 403 - Validation failed (check assignee, column, work item type)
# 400 - Malformed payload
# 500 - Internal error (check function logs)
```

**Validate specific scenarios**:

```bash
# Test wrong event type (should return 403)
jq '.eventType = "workitem.created"' ../specs/001-ado-github-spec/contracts/sample-ado-hook.json | \
  curl -X POST "$FUNCTION_URL/api/spec-dispatch?code=$FUNCTION_KEY" -H "Content-Type: application/json" -d @-

# Test wrong work item type (should return 403)
jq '.resource.fields."System.WorkItemType" = "Bug"' ../specs/001-ado-github-spec/contracts/sample-ado-hook.json | \
  curl -X POST "$FUNCTION_URL/api/spec-dispatch?code=$FUNCTION_KEY" -H "Content-Type: application/json" -d @-

# Test missing work item ID (should return 400)
jq 'del(.resource.workItemId)' ../specs/001-ado-github-spec/contracts/sample-ado-hook.json | \
  curl -X POST "$FUNCTION_URL/api/spec-dispatch?code=$FUNCTION_KEY" -H "Content-Type: application/json" -d @-
```

