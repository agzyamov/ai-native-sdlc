# Local Testing Guide for Azure Function

## Prerequisites

1. **Install Azure Functions Core Tools v4**:
   ```bash
   # macOS
   brew tap azure/functions
   brew install azure-functions-core-tools@4
   
   # Or npm (all platforms)
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Install Python 3.11**:
   ```bash
   python3 --version  # Should be 3.11.x
   ```

3. **Install dependencies**:
   ```bash
   cd function_app
   pip install -r requirements.txt
   ```

## Configuration

1. **Set environment variables** in `local.settings.json`:
   ```json
   {
     "Values": {
       "GH_WORKFLOW_DISPATCH_PAT": "your-real-github-pat",
       "ADO_WORK_ITEM_PAT": "your-real-ado-pat"
     }
   }
   ```

   **Important**: `local.settings.json` is gitignored - never commit secrets!

## Running Locally

### Start the function:
```bash
cd function_app
func start
```

Expected output:
```
Azure Functions Core Tools
Core Tools Version:       4.x.x
Function Runtime Version: 4.x.x

Functions:

        spec-dispatch: [POST,GET] http://localhost:7071/api/spec-dispatch
```

### Test with curl:

```bash
# Test with sample payload
curl -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d @../specs/001-ado-github-spec/contracts/sample-ado-hook.json

# Expected: 204 No Content (success)
# Or: 403 Forbidden (validation failed)
```

### Test validation failures:

```bash
# Wrong event type (should return 403)
curl -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "workitem.created",
    "resource": {"workItemId": 123}
  }'

# Missing work item ID (should return 400)
curl -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "workitem.updated",
    "resource": {}
  }'
```

## VS Code Integration

### Using Azure Functions Extension:

1. **Install extension**:
   - Open Extensions (Cmd+Shift+X)
   - Search "Azure Functions"
   - Install by Microsoft

2. **Debug locally**:
   - Open `function_app/function_app.py`
   - Press F5 (or Run → Start Debugging)
   - Set breakpoints
   - Send test request with curl

3. **View logs**:
   - Terminal shows real-time logs
   - Debug Console shows structured output

### VS Code Launch Configuration:

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Python Functions",
      "type": "python",
      "request": "attach",
      "port": 9091,
      "preLaunchTask": "func: host start"
    }
  ]
}
```

## Debugging Tips

### Check function is running:
```bash
curl http://localhost:7071/api/spec-dispatch
# Should return 400 or 403 (not 404)
```

### View detailed logs:
```bash
# In function_app directory
func start --verbose
```

### Common Issues:

**Port already in use**:
```bash
# Kill existing function process
lsof -ti:7071 | xargs kill -9

# Or use different port
func start --port 7072
```

**Module import errors**:
```bash
# Ensure you're in function_app directory
cd function_app
pip install -r requirements.txt
```

**Storage emulator issues**:
```bash
# Use Azurite (local Azure Storage emulator)
npm install -g azurite
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log

# Or disable storage requirement in local.settings.json
"AzureWebJobsStorage": ""
```

## Testing Workflow

1. **Start function locally**: `func start`
2. **Modify code** in `__init__.py`, `validation.py`, etc.
3. **Function auto-reloads** (no restart needed)
4. **Test with curl** or Postman
5. **Check logs** in terminal
6. **Iterate** until working

## Production Deployment

Once local testing passes:

```bash
# Build and deploy (from infra directory)
cd ../infra
terraform apply

# Deploy function code
cd ../function_app
func azure functionapp publish <function-app-name>
```

## Monitoring Local Execution

### Structured logs example:
```json
{
  "correlation_id": "abc-123",
  "work_item_id": 456,
  "event": "dispatch_success",
  "latency_ms": 1250
}
```

### Enable verbose logging:
```bash
# In local.settings.json
"LOG_LEVEL": "DEBUG"
```

## Quick Test Script

```bash
#!/bin/bash
# test-local.sh

echo "Starting function..."
cd function_app
func start &
FUNC_PID=$!

sleep 5  # Wait for function to start

echo "Testing validation..."
curl -s -X POST http://localhost:7071/api/spec-dispatch \
  -H "Content-Type: application/json" \
  -d @../specs/001-ado-github-spec/contracts/sample-ado-hook.json

echo ""
echo "Stopping function..."
kill $FUNC_PID
```

Make executable: `chmod +x test-local.sh`

## Next Steps

- Set real PAT values in `local.settings.json`
- Run `func start` in `function_app/` directory
- Test with sample payloads
- Debug with VS Code F5
- Deploy to Azure when ready
