# Deprecated Pipeline Removal Procedure

## Context

**Date Deprecated**: 2024-11-26  
**Removal Date**: 2025-11-26 (365-day retention per constitution)  
**Reason**: Pipeline approach replaced by Azure Function (constitution Principle 6: Direct Event Path)

## What Was Deprecated

- **File**: `.github/workflows/ado-spec-dispatch.yml` (annotated with deprecation notice)
- **Approach**: Azure Pipelines Run API for webhook handling
- **Issue**: Payload incompatibility between ADO Service Hook and GitHub Pipelines Run endpoint

## Replacement

- **New File**: `function_app/__init__.py` (Azure Function HTTP trigger)
- **Infrastructure**: `infra/` (Terraform for Azure Function + Storage + Service Plan)
- **Approach**: Direct Service Hook → Function → GitHub workflow_dispatch

## Removal Checklist (After 2025-11-26)

Execute these steps only after the grace period expires:

### 1. Verify No Active Usage

```bash
# Check for recent workflow runs in GitHub
gh run list --workflow ado-spec-dispatch.yml --limit 5

# Check Azure DevOps Service Hooks
# Verify no hooks point to pipeline endpoint
```

Expected: No runs in past 60 days.

### 2. Archive Pipeline File

```bash
# Move to archive directory
mkdir -p .github/workflows/archive
git mv .github/workflows/ado-spec-dispatch.yml .github/workflows/archive/

# Document in archive README
cat > .github/workflows/archive/README.md <<EOF
# Archived Workflows

## ado-spec-dispatch.yml
- **Archived**: $(date +%Y-%m-%d)
- **Replaced by**: Azure Function (function_app/)
- **Reason**: Constitution Principle 6 compliance (Direct Event Path)
- **History**: See specs/001-ado-github-spec/DEPRECATION.md
EOF

# Commit
git add .github/workflows/archive/
git commit -m "chore: archive deprecated pipeline after grace period

- Moved ado-spec-dispatch.yml to archive/
- Replaced by Azure Function approach (2024-11-26)
- Removal per constitution constraint (365-day retention)"
```

### 3. Update Documentation

Remove references in:

- `specs/001-ado-github-spec/quickstart.md` → Remove deprecated section entirely
- `specs/001-ado-github-spec/plan.md` → Update status from "DEPRECATED" to "REMOVED"
- `README.md` → Remove any pipeline setup instructions

```bash
# Remove deprecated section from quickstart
# (This section should already be collapsed; remove it entirely)
```

### 4. Verify Constitution Compliance

Check `specs/001-ado-github-spec/plan.md` constitution table:

| Principle | Gate | Status |
|-----------|------|--------|
| 6 (Direct Event Path) | Intermediary removed | ✅ OK (archived after grace period) |

### 5. Notify Team

Send notification to team:

```
Subject: Deprecated Pipeline Removed

The ado-spec-dispatch.yml pipeline has been archived after the 365-day grace period.

- **Deprecated**: 2024-11-26
- **Removed**: 2025-11-26
- **Replacement**: Azure Function (function_app/)

All Service Hooks should now point to the Function endpoint. If you encounter issues, see quickstart.md for current deployment instructions.
```

## Rollback Plan (Emergency Only)

If critical issues arise with the Function approach:

```bash
# Restore from archive
git mv .github/workflows/archive/ado-spec-dispatch.yml .github/workflows/

# Reconfigure Service Hook
# Point to GitHub pipeline endpoint (see archived quickstart)

# Document in incident report
# This should be exceptional; log in ops/incidents/
```

## Post-Removal Monitoring

After removal, monitor for 30 days:

- **Function error rates**: Should remain stable
- **Dispatch success rate**: >= 95%
- **Team feedback**: No reversion requests

If metrics degrade, investigate Function infrastructure, not pipeline.

## References

- Constitution deprecation constraint (365-day retention)
- Principle 6 (Direct Event Path)
- specs/001-ado-github-spec/plan.md (Architecture Decision)
