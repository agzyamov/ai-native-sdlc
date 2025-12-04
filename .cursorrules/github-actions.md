# GitHub Actions Workflow Standards

## Workflow Validation

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

3. **Check for common issues**:
   - Valid YAML syntax (proper indentation, no tabs)
   - Correct trigger syntax (`on:` section)
   - Valid action versions (e.g., `actions/checkout@v4`)
   - Required permissions specified
   - Proper environment variable syntax (`${{ }}` for expressions, `$VAR` for shell)
   - No deprecated actions or syntax

4. **Test workflow locally** (if possible):
   - Use `act` tool for local testing: https://github.com/nektos/act
   - Or trigger workflow manually via GitHub UI

**Before committing:**
- ✅ yamllint passes without errors (YAML syntax)
- ✅ actionlint passes without errors (GitHub Actions validation)
- ✅ All actions use pinned versions
- ✅ Workflow triggers are correctly configured

**Install tools:**
```bash
# macOS
brew install yamllint actionlint

# Linux
pip install yamllint
go install github.com/rhysd/actionlint/cmd/actionlint@latest
```

**Never commit broken GitHub Actions workflows!**

## Workflow Structure

### Basic Workflow Template

```yaml
name: Workflow Name

on:
  workflow_dispatch:
    inputs:
      input_name:
        description: 'Input description'
        required: true
        type: string

permissions:
  contents: read
  actions: write

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Step name
        run: echo "Step content"
```

## Permissions

Always specify explicit permissions:

```yaml
permissions:
  contents: read      # Read repository contents
  actions: write      # Trigger workflows
  pull-requests: write # Create/update PRs (if needed)
```

Use least-privilege principle - only grant permissions actually needed.

## Action Versions

- Always use pinned versions (e.g., `@v4`, not `@main`)
- Prefer major version pins for stability
- Check for updates periodically

## Environment Variables

- Use `${{ }}` for GitHub Actions expressions
- Use `$VAR` for shell environment variables
- Store secrets in repository secrets, never hardcode

```yaml
env:
  VAR_NAME: ${{ secrets.SECRET_NAME }}
  
steps:
  - name: Use variable
    run: echo "$VAR_NAME"
```

## Composite Actions

When creating composite actions:
- Use `runs.using: composite`
- Specify `shell: bash` or `shell: pwsh`
- Document inputs and outputs

## Error Handling

- Use `continue-on-error: true` only when appropriate
- Set `fail-fast: false` for matrix builds if needed
- Always check exit codes in scripts

## Related Rules

- See [spec-kit.md](spec-kit.md) for Spec Kit workflow patterns
- See [validation.md](validation.md) for validation requirements

