# GitHub App Setup for gh agent-task in Actions

Complete guide to set up GitHub App authentication for running `gh agent-task` in GitHub Actions workflows.

## Why GitHub App?

The `gh agent-task` command requires an **OAuth token** (prefix `gho_`), not a Personal Access Token. In GitHub Actions, we can't use interactive `gh auth login`, so we need a GitHub App to generate installation tokens.

**Benefits:**
- ✅ OAuth tokens that work with `gh agent-task`
- ✅ Better security (scoped permissions, short-lived tokens)
- ✅ No user account dependency
- ✅ Audit trail for all actions

## Step 1: Create GitHub App

1. Navigate to your GitHub account settings:
   - Go to https://github.com/settings/apps
   - Or: Click your profile → **Settings** → **Developer settings** → **GitHub Apps**

2. Click **New GitHub App**

3. Fill in the app details:

   | Field | Value |
   |-------|-------|
   | **GitHub App name** | `Copilot Agent Task Runner` (or your preferred name) |
   | **Homepage URL** | `https://github.com/YOUR-USERNAME/ai-native-sdlc` |
   | **Webhook** | ❌ **Disable** (uncheck "Active") |

4. Set **Repository permissions**:
   
   | Permission | Access Level | Why Needed |
   |------------|--------------|------------|
   | **Actions** | Read and write | To trigger and manage workflows |
   | **Contents** | Read and write | To create branches and commit code |
   | **Pull requests** | Read and write | To create and manage PRs |
   | **Metadata** | Read-only | Required (automatically set) |

5. Set **Where can this GitHub App be installed?**
   - Select **Only on this account** (recommended for personal use)

6. Click **Create GitHub App**

## Step 2: Generate Private Key

After creating the app:

1. On your app's page, scroll to **Private keys** section
2. Click **Generate a private key**
3. A `.pem` file will be downloaded - **save it securely!**
4. Note down the **App ID** (shown at the top of the page)

## Step 3: Install the App

1. On your app's page, click **Install App** in the left sidebar
2. Select your GitHub account
3. Choose **Only select repositories**
4. Select `ai-native-sdlc` repository (or your target repo)
5. Click **Install**
6. Note down the **Installation ID** from the URL:
   ```
   https://github.com/settings/installations/INSTALLATION_ID
   ```

## Step 4: Add Secrets to Repository

Navigate to your repository's secrets:
- Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add the following secrets:

### 1. `GH_APP_ID`
- **Value**: Your App ID from Step 2
- Example: `123456`

### 2. `GH_APP_INSTALLATION_ID`
- **Value**: Your Installation ID from Step 3
- Example: `12345678`

### 3. `GH_APP_PRIVATE_KEY`
- **Value**: Contents of the `.pem` file from Step 2
- Copy the entire file including the header and footer:
  ```
  -----BEGIN RSA PRIVATE KEY-----
  MIIEpAIBAAKCAQEA...
  ...
  -----END RSA PRIVATE KEY-----
  ```

## Step 5: Create Workflow with GitHub App Authentication

Create or update `.github/workflows/copilot-agent-task.yml`:

```yaml
name: Copilot Agent Task with GitHub App

on:
  workflow_dispatch:
    inputs:
      task_description:
        description: 'Task description for Copilot'
        required: true
        type: string
      base_branch:
        description: 'Base branch for the PR'
        required: false
        type: string
        default: 'main'

jobs:
  copilot-agent:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate GitHub App Token
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.GH_APP_ID }}
          private-key: ${{ secrets.GH_APP_PRIVATE_KEY }}
          
      - name: Verify GitHub CLI
        run: |
          gh --version
          if ! gh agent-task --help &>/dev/null; then
            echo "❌ gh agent-task not available"
            exit 1
          fi
          echo "✅ GitHub CLI ready"
      
      - name: Run Copilot Agent Task
        env:
          GH_TOKEN: ${{ steps.app-token.outputs.token }}
        run: |
          echo "🤖 Starting Copilot Agent Task..."
          echo "Task: ${{ inputs.task_description }}"
          echo "Base: ${{ inputs.base_branch }}"
          
          gh agent-task create \
            "${{ inputs.task_description }}" \
            --base "${{ inputs.base_branch }}" \
            --repo "${{ github.repository }}" \
            --follow | tee agent_output.log
          
          # Extract PR URL
          PR_URL=$(grep -oP 'https://github\.com/[^/]+/[^/]+/pull/\d+' agent_output.log | head -1 || echo "")
          
          if [ -n "$PR_URL" ]; then
            echo "PR_URL=$PR_URL" >> $GITHUB_ENV
            echo "✅ PR created: $PR_URL"
          else
            echo "⚠️ No PR URL found"
          fi
      
      - name: Upload Logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: agent-logs
          path: agent_output.log
          retention-days: 30
      
      - name: Summary
        if: always()
        run: |
          echo "## 🤖 Copilot Agent Task" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Task:** ${{ inputs.task_description }}" >> $GITHUB_STEP_SUMMARY
          echo "**Base Branch:** \`${{ inputs.base_branch }}\`" >> $GITHUB_STEP_SUMMARY
          
          if [ -n "$PR_URL" ]; then
            echo "**Pull Request:** $PR_URL" >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "✅ Copilot agent is working on your task." >> $GITHUB_STEP_SUMMARY
          fi
```

## Step 6: Test the Workflow

Run the workflow manually:

```bash
gh workflow run copilot-agent-task.yml \
  -f task_description="Create a Python function to calculate prime numbers" \
  -f base_branch="main"
```

Monitor the workflow:

```bash
gh run list --workflow="copilot-agent-task.yml" --limit 1
gh run watch
```

## Validation Checklist

Before running, verify:

- [ ] GitHub App created with correct permissions
- [ ] Private key generated and downloaded
- [ ] App installed on your repository
- [ ] All 3 secrets added to repository:
  - [ ] `GH_APP_ID`
  - [ ] `GH_APP_INSTALLATION_ID`
  - [ ] `GH_APP_PRIVATE_KEY`
- [ ] Workflow file created in `.github/workflows/`
- [ ] Repository has Actions enabled

## Troubleshooting

### Error: "Failed to create GitHub App token"
- **Check:** All secrets are correctly set
- **Check:** Private key includes header and footer
- **Check:** App is installed on the repository

### Error: "gh agent-task requires an OAuth token"
- **Check:** Using `actions/create-github-app-token@v1` action
- **Check:** Token is passed as `GH_TOKEN` environment variable

### Error: "Resource not accessible by integration"
- **Check:** GitHub App has required permissions
- **Check:** App is installed on correct repository

### Workflow doesn't create PR
- **Check:** Task description is clear and actionable
- **Check:** Base branch exists
- **Check:** Copilot subscription is active

## Security Best Practices

1. **Private Key Storage**
   - ✅ Store in GitHub Secrets only
   - ❌ Never commit to repository
   - ❌ Never share or expose publicly

2. **Minimum Permissions**
   - Only grant necessary permissions to GitHub App
   - Review permissions periodically

3. **Token Lifetime**
   - GitHub App tokens expire after 1 hour (automatic)
   - No manual rotation needed

4. **Audit Logs**
   - Review GitHub App activity regularly
   - Monitor Actions workflow runs

## Advanced: Using GitHub App in Multiple Repositories

To use the same GitHub App across multiple repositories:

1. When installing the app (Step 3), select **All repositories** or select multiple specific repositories

2. Each repository needs the same secrets (`GH_APP_ID`, `GH_APP_INSTALLATION_ID`, `GH_APP_PRIVATE_KEY`)

3. Optional: Use [organization secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-organization) to share across repos

## References

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Creating GitHub App tokens in workflows](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow)
- [actions/create-github-app-token](https://github.com/actions/create-github-app-token)
- [GitHub CLI agent-task](https://cli.github.com/manual/gh_agent-task_create)

---

**Next Steps:** After successful setup, explore the [main README](../README.md) for more examples and use cases.
