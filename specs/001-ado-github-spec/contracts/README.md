# Contracts (Phase 1)

MVP exposes no public API; interactions are platform-native events and REST calls. This directory documents the single external call required: Azure DevOps Work Item PATCH for Description overwrite.

## Azure DevOps Work Item PATCH (Description Overwrite)

### Endpoint
```
PATCH https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{id}?api-version=7.0
Content-Type: application/json-patch+json
Authorization: Basic <base64("":ADO_PAT)>
```

### Request Body (JSON Patch)
```json
[
  {
    "op": "replace",
    "path": "/fields/System.Description",
    "value": "<FULL_RENDERED_SPEC_MARKDOWN_ESCAPED>"
  }
]
```

### Success Response
- 200 OK with updated work item JSON

### Failure Modes
| Code | Cause | Mitigation |
|------|-------|------------|
| 401  | Invalid/expired PAT | Rotate PAT; verify scope includes Work Items (Read, Write) |
| 403  | Insufficient permissions | Adjust PAT scope or use different identity |
| 409  | Work item revision conflict | (Deferred) Retry with latest rev fetch |
| 413  | Payload too large | (Deferred) Consider section trimming or attachment strategy |
| 429  | Throttled | (Deferred) Backoff + retry policy |

### Notes
- HTML vs Markdown: ADO Description stores as HTML; supply sanitized HTML or rely on markdown-to-HTML conversion if client lib used. MVP assumption: Spec content acceptable as-is (will verify visually). If raw markdown unsupported, add conversion step (Backlog candidate).
- Secret naming: use `ADO_WORKITEM_RW_PAT` (scoped Work Items Read/Write) for all work-item description overwrite operations.

## GitHub Workflow Dispatch (Triggered From Azure DevOps Pipeline)
```
POST https://api.github.com/repos/{owner}/{repo}/actions/workflows/spec-kit-specify.yml/dispatches
Authorization: Bearer $GH_WORKFLOW_DISPATCH_PAT
Accept: application/vnd.github+json
Content-Type: application/json

{"ref":"main","inputs":{"work_item_id":"<ID>","branch_hint":"feature/<slug>"}}
```

### Workflow Inputs (MVP)
| Name | Type | Required | Description |
|------|------|----------|-------------|
| work_item_id | string | yes | Numeric Azure DevOps Feature ID |
| branch_hint | string | no | Suggested branch name (slug of title) |

### Response
- 204 No Content accepted

### Errors
| Code | Cause | Mitigation |
|------|-------|------------|
| 401 | Invalid/expired `GH_WORKFLOW_DISPATCH_PAT` | Rotate PAT in ADO variable group |
| 404 | Workflow name mismatch | Verify filename/path |
| 422 | Missing required input | Ensure pipeline payload includes work_item_id |

## Azure DevOps Pipeline Dispatch (Service Hook → Pipeline) (Assumed)
Service Hook (Work Item Updated) performs:
```
POST https://dev.azure.com/{org}/{project}/_apis/pipelines/{pipelineId}/runs?api-version=7.0
Authorization: Basic <base64(":" ADO_PIPELINE_RUN_PAT)>
Content-Type: application/json

{"resources": {}}
```

Pipeline receives no guaranteed structured work item variables; script must (assumption) access payload if forwarded. If not available, fallback manual entry or alternate hook-to-pipeline relay required (documented in assumptions section of quickstart).

### Future (Deferred) Contracts
- Regen operation (FR-007) may introduce a distinct input (mode=regen)
- Failure notification channel (FR-005) may call ADO Discussion or create child Issue
- Debounce registry (hash endpoint) if introduced will add a pre-dispatch check
