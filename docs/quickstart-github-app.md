# Quick Start: GitHub App for Copilot Agent Task

## TL;DR

1. **Create GitHub App** → https://github.com/settings/apps/new
2. **Set Permissions**: Actions (RW), Contents (RW), PRs (RW)
3. **Generate Private Key** → Download `.pem` file
4. **Install App** → Select your repository
5. **Add 3 Secrets** → `GH_APP_ID`, `GH_APP_INSTALLATION_ID`, `GH_APP_PRIVATE_KEY`
6. **Run Workflow**:
   ```bash
   gh workflow run copilot-agent-github-app.yml \
     -f task_description="Your task here"
   ```

## Copy-Paste Commands

### Create Secrets (after getting values)

```bash
# Replace with your values
APP_ID="123456"
INSTALLATION_ID="12345678"
PRIVATE_KEY_FILE="path/to/your-app.2025-01-01.private-key.pem"

# Add secrets using gh CLI
gh secret set GH_APP_ID --body "$APP_ID"
gh secret set GH_APP_INSTALLATION_ID --body "$INSTALLATION_ID"
gh secret set GH_APP_PRIVATE_KEY < "$PRIVATE_KEY_FILE"
```

### Run Workflow

```bash
# Basic usage
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Create a Python function to calculate factorial"

# With custom base branch
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Add error handling to user authentication" \
  -f base_branch="develop"

# Monitor workflow
gh run list --workflow="copilot-agent-github-app.yml" --limit 1
gh run watch
```

## Minimal GitHub App Permissions

| Permission | Level | Required |
|------------|-------|----------|
| Actions | Read and write | ✅ |
| Contents | Read and write | ✅ |
| Pull requests | Read and write | ✅ |
| Metadata | Read-only | ✅ (auto) |

## Get Installation ID

**Option 1:** From URL after installing app
```
https://github.com/settings/installations/INSTALLATION_ID
```

**Option 2:** Using GitHub API
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.github.com/app/installations
```

## Troubleshooting One-Liners

```bash
# Verify secrets are set
gh secret list

# Check workflow runs
gh run list --workflow="copilot-agent-github-app.yml"

# View latest run logs
gh run view --log

# Download artifacts
gh run download
```

## Example Tasks

```bash
# Feature development
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Implement user registration with email validation"

# Bug fixes
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Fix memory leak in image processing module"

# Testing
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Add integration tests for payment gateway"

# Refactoring
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Refactor database queries to use async/await"

# Documentation
gh workflow run copilot-agent-github-app.yml \
  -f task_description="Add API documentation with OpenAPI spec"
```

## What NOT to Do ❌

- ❌ Don't commit private key to repository
- ❌ Don't use PAT instead of GitHub App
- ❌ Don't grant more permissions than needed
- ❌ Don't share private key or expose in logs
- ❌ Don't skip webhook disabling (unnecessary overhead)

## Success Checklist

- [ ] GitHub App created with name
- [ ] Webhook is **disabled**
- [ ] Permissions set: Actions (RW), Contents (RW), PRs (RW)
- [ ] Private key generated and downloaded
- [ ] App installed on repository
- [ ] `GH_APP_ID` secret added
- [ ] `GH_APP_INSTALLATION_ID` secret added
- [ ] `GH_APP_PRIVATE_KEY` secret added (full PEM content)
- [ ] Workflow file exists: `.github/workflows/copilot-agent-github-app.yml`
- [ ] Test run successful

---

📚 **Full Documentation:** [GitHub App Setup Guide](github-app-setup.md)

🔧 **Workflow File:** [copilot-agent-github-app.yml](../.github/workflows/copilot-agent-github-app.yml)

📖 **Main README:** [README.md](../README.md)
