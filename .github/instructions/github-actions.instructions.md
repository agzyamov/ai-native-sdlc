---
applyTo: '.github/workflows/**, docs/diagrams/**'
---

# GitHub Actions & Mermaid Diagrams

## Mermaid Diagram Validation

**Always validate Mermaid diagrams** before committing:

When creating or modifying Mermaid diagrams:

1. **Run validation script** after creation:
   ```bash
   node check_mermaid.js <filename>
   ```

2. **Check for common issues:**
   - Single diagram type per code block (graph TD, flowchart, mindmap, etc.)
   - No mixed diagram types in one block
   - Balanced quotes, brackets, parentheses
   - Valid node IDs (no special characters)
   - Proper arrow syntax (-->, -.->)

3. **Test rendering** in Mermaid Live Editor: https://mermaid.live/

**Before committing:**
- ✅ Script validation passes
- ✅ Diagram renders correctly in VS Code preview
- ✅ No parse errors in console

**Never commit broken Mermaid diagrams!**

### Additional Automated Validation (mermaid-cli)

Also run `@mermaid-js/mermaid-cli` (mmdc) against every changed diagram file in `docs/diagrams/`:

```bash
awk '/```mermaid/{flag=1;next}/```/{flag=0}flag' docs/diagrams/<file>.md \
  | npx mmdc -i /dev/stdin -o /dev/null
```

Existing repository helper:
```bash
scripts/validate_diagrams.sh            # validate all diagrams
scripts/validate_diagrams.sh changed    # only staged diagrams
```

---

## GitHub Actions Workflow Validation

**Always validate GitHub Actions workflows** before committing:

When creating or modifying `.github/workflows/*.yml` files:

1. **Run yamllint first** to catch YAML syntax errors:
   ```bash
   yamllint .github/workflows/<workflow-file>.yml
   ```

2. **Run actionlint** for GitHub Actions-specific validation:
   ```bash
   actionlint .github/workflows/<workflow-file>.yml
   ```

3. **Check for common issues:**
   - Valid YAML syntax (proper indentation, no tabs)
   - Correct trigger syntax (`on:` section)
   - Valid action versions (e.g., `actions/checkout@v4`)
   - Required permissions specified
   - Proper environment variable syntax (`${{ }}` for expressions, `$VAR` for shell)
   - No deprecated actions or syntax

**Before committing:**
- ✅ yamllint passes without errors (YAML syntax)
- ✅ actionlint passes without errors (GitHub Actions validation)
- ✅ All actions use pinned versions
- ✅ Workflow triggers are correctly configured

**Install tools:**
```bash
# macOS
brew install yamllint actionlint
```

**Never commit broken GitHub Actions workflows!**

---

## GitHub Actions Workflow Run Debugging

**Use `gh` CLI to diagnose why a workflow run used wrong inputs — do NOT guess from web UI alone.**

### Commands for run analysis
```bash
# List recent runs of a specific workflow
gh run list --repo <owner>/<repo> --workflow=<filename>.yml --limit=10

# View run summary and job structure
gh run view <run-id> --repo <owner>/<repo>

# Inspect actual input values used in a job (from runner log)
gh run view --job=<job-id> --log --repo <owner>/<repo> | grep "ENCODED_CONFIG:"

# Compare full run metadata (inputs field may be null for dispatch-via-API runs)
gh api "repos/<owner>/<repo>/actions/runs/<run-id>" --jq '{inputs: .inputs, head_sha: .head_sha}'

# Get all job IDs for a run
gh api "repos/<owner>/<repo>/actions/runs/<run-id>/jobs" --jq '.jobs[].id'
```

### Diagnosing `ai-teammate-ado.yml` (spec-dispatch) runs

| `ENCODED_CONFIG` value | Meaning |
|---|---|
| `dGVzdA==` (base64 "test") | Manual test dispatch from GitHub UI with placeholder — **not a real ADO event** |
| `{"params": {"inputJql": "...= 9999", "initiator": "test@example.com"}}` | Function dispatched with test ADO payload |
| `{"params": {"inputJql": "...= <real-id>", "initiator": "<real-email>"}}` | Real ADO service hook dispatch ✅ |

### If ADO hook fires (204 response) but no new GHA run appears
The Azure Function silently filtered the event. Check `validation.py` rules:

- **Work item type**: controlled by `ALLOWED_WORK_ITEM_TYPES` env var (default: `"Feature,User Story"`)
- **Assignee**: must match `AI_USER_MATCH` (default: `"AI Teammate"`)
- **Board column**: must match `SPEC_COLUMN_NAME` (default: `"Specification"`)
- **BoardColumnDone**: must be `false` (Doing state, not Done)

The function returns HTTP 204 for **both** successful dispatch and filtered events — use function logs, not the HTTP status, to distinguish them.

### Config file (`GITHUB_WORKFLOW_CONFIG_FILE`)
The Azure Function passes `config_file = agents/ado_story_description.json` to the workflow by default.
Override via the `GITHUB_WORKFLOW_CONFIG_FILE` env var on the Function App.
