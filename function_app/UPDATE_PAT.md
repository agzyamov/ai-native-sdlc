# How to Update ADO_WORK_ITEM_PAT

## 1. Azure Function App (Deployed Function) - REQUIRED

### Option A: Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to: **Function App** → `func-dev-dispatch` (or your function app name)
3. Go to **Configuration** → **Application settings**
4. Find `ADO_WORK_ITEM_PAT`
5. Click **Edit** → Paste your new PAT → **OK** → **Save**

### Option B: Azure CLI
```bash
# Set the PAT
az functionapp config appsettings set \
  --name func-dev-dispatch \
  --resource-group <your-resource-group> \
  --settings ADO_WORK_ITEM_PAT="<your-new-pat-here>"
```

**Note:** After updating, the function app will automatically restart.

## 2. Local Development (Optional - for testing)

Update `function_app/local.settings.json`:

```json
{
  "Values": {
    "ADO_WORK_ITEM_PAT": "<your-new-pat-here>"
  }
}
```

**Important:** `local.settings.json` is gitignored - never commit secrets!

## Verify the PAT works

Test the PAT:
```bash
curl -u ":<your-new-pat>" \
  "https://dev.azure.com/RustemAgziamov/ai-native-sdlc-blueprint/_apis/wit/workitems/615?api-version=7.0"
```

Should return HTTP 200 with work item JSON, not 401.

