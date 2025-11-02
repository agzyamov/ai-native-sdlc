# Contract: ADO Issue Work Item Creation

**Version**: 1.0  
**Feature**: 002-preserve-clarification-questions  
**Purpose**: Define payload structure for creating clarification Issue work items in Azure DevOps

## API Endpoint

**Method**: `POST`  
**URL**: `https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$Issue?api-version=7.0`  
**Content-Type**: `application/json-patch+json`  
**Authentication**: Basic (PAT token)

## Required Permissions

- **PAT Scope**: Work Items (Read & Write)
- **ADO Project Permissions**: Contributor or higher
- **Work Item Type**: Issue (must be enabled in project; fallback to Task if not available)

## Request Headers

```http
POST https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Issue?api-version=7.0 HTTP/1.1
Content-Type: application/json-patch+json
Authorization: Basic {base64_encoded_PAT}
```

## Request Body (JSON Patch Format)

```json
[
  {
    "op": "add",
    "path": "/fields/System.Title",
    "value": "Clarification Q1: [Topic - first 50 chars of question]"
  },
  {
    "op": "add",
    "path": "/fields/System.Description",
    "value": "<div><h3>Clarification Question</h3><p><strong>Context:</strong> [context from spec]</p><p><strong>Question:</strong> [full question text]</p><p><strong>Spec File:</strong> <code>specs/[feature-dir]/spec.md</code></p><p><strong>GitHub Branch:</strong> <a href='https://github.com/{owner}/{repo}/tree/{branch}'>{branch}</a></p><p><strong>Section:</strong> [spec section hierarchy]</p></div>"
  },
  {
    "op": "add",
    "path": "/fields/System.Tags",
    "value": "clarification; auto-generated"
  },
  {
    "op": "add",
    "path": "/fields/System.AreaPath",
    "value": "{project}\\{area}"
  },
  {
    "op": "add",
    "path": "/fields/System.IterationPath",
    "value": "{project}\\{iteration}"
  },
  {
    "op": "add",
    "path": "/relations/-",
    "value": {
      "rel": "System.LinkTypes.Hierarchy-Reverse",
      "url": "https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{parent_feature_id}",
      "attributes": {
        "comment": "Auto-generated clarification from spec generation workflow"
      }
    }
  }
]
```

## Field Mapping

### System.Title

**Format**: `"Clarification Q{N}: {Topic}"`

**Rules**:
- `{N}`: Question number (1-3)
- `{Topic}`: First 50 characters of question text, trimmed to last complete word
- Max length: 255 characters (ADO limit)
- If topic > 50 chars: truncate at word boundary + `"..."`

**Examples**:
- `"Clarification Q1: Auth Method Not Specified"`
- `"Clarification Q2: Data Retention Period"`
- `"Clarification Q3: Should We Validate Issue Work Item Type..."`

### System.Description

**Format**: HTML (ADO renders Description as HTML)

**Structure**:
```html
<div>
  <h3>Clarification Question</h3>
  
  <p><strong>Context:</strong> {context_from_spec}</p>
  
  <p><strong>Question:</strong> {full_question_text}</p>
  
  <p><strong>Spec File:</strong> <code>{spec_file_path}</code></p>
  
  <p><strong>GitHub Branch:</strong> <a href='{github_branch_url}'>{branch_name}</a></p>
  
  <p><strong>Section:</strong> {spec_section_hierarchy}</p>
  
  <hr/>
  
  <p><em>This Issue was auto-generated from the specification workflow. 
  To resolve: answer the question in the comments, update the spec file, 
  and mark this Issue as Done.</em></p>
  
  <p><strong>Idempotency Key:</strong> <code>{feature_id}-{question_hash}</code></p>
</div>
```

**Placeholders**:
- `{context_from_spec}`: 100-300 chars from spec.md surrounding the marker (HTML-escaped)
- `{full_question_text}`: Complete text from `[NEEDS CLARIFICATION: ...]` (HTML-escaped)
- `{spec_file_path}`: e.g., `specs/002-preserve-clarification-questions/spec.md`
- `{github_branch_url}`: e.g., `https://github.com/agzyamov/ai-native-sdlc/tree/002-preserve-clarification-questions`
- `{branch_name}`: e.g., `002-preserve-clarification-questions`
- `{spec_section_hierarchy}`: e.g., `Requirements > Functional Requirements`
- `{feature_id}`: ADO Feature work item ID
- `{question_hash}`: First 8 chars of SHA256 hash of question text (for idempotency)

### System.Tags

**Format**: Semicolon-separated string

**Required Tags**:
- `clarification` - identifies this as clarification Issue
- `auto-generated` - indicates workflow automation

**Optional Tags** (future):
- `priority:{P1|P2|P3}` - based on question position
- `feature:{feature-id}` - link to parent Feature ID

**Example**: `"clarification; auto-generated; priority:P1"`

### System.AreaPath

**Format**: `"{ProjectName}\\{AreaPath}"`

**Resolution Strategy**:
1. Use same AreaPath as parent Feature work item (query Feature first)
2. If Feature AreaPath query fails: use project root (e.g., `"MyProject"`)
3. Never hard-code; always derive from Feature

**Example**: `"AI-Native-SDLC\\Specifications"`

### System.IterationPath

**Format**: `"{ProjectName}\\{IterationPath}"`

**Resolution Strategy**:
1. Use same IterationPath as parent Feature work item
2. If Feature IterationPath query fails: use current sprint or project root
3. Never hard-code; always derive from Feature

**Example**: `"AI-Native-SDLC\\Sprint 42"`

### Parent-Child Relationship

**Relation Type**: `System.LinkTypes.Hierarchy-Reverse`

**Direction**: Issue (child) → Feature (parent)

**URL Format**: `https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{parent_feature_id}`

**Attributes**:
- `comment`: Descriptive text explaining the link (e.g., "Auto-generated clarification from spec generation workflow")

**Validation**:
- Parent Feature ID MUST exist before Issue creation
- If link creation fails: log error but continue (Issue still created, manual linking required)

## Response (Success)

**HTTP Status**: `200 OK`

**Body** (abbreviated):
```json
{
  "id": 12345,
  "rev": 1,
  "fields": {
    "System.Title": "Clarification Q1: Auth Method Not Specified",
    "System.WorkItemType": "Issue",
    "System.State": "New",
    "System.CreatedDate": "2025-11-02T15:45:00Z",
    "System.CreatedBy": {
      "displayName": "github-actions[bot]"
    },
    "System.Tags": "clarification; auto-generated"
  },
  "relations": [
    {
      "rel": "System.LinkTypes.Hierarchy-Reverse",
      "url": "https://dev.azure.com/{org}/{project}/_apis/wit/workitems/9876"
    }
  ],
  "url": "https://dev.azure.com/{org}/{project}/_apis/wit/workitems/12345"
}
```

## Response (Error)

### 401 Unauthorized
```json
{
  "message": "TF400813: The user '{guid}' is not authorized to access this resource."
}
```
**Mitigation**: Verify PAT token, check scopes (Work Items: Write)

### 400 Bad Request - Invalid Work Item Type
```json
{
  "message": "The work item type 'Issue' does not exist or you do not have permission to create it."
}
```
**Mitigation**: Fallback to `Task` work item type, log warning

### 400 Bad Request - Invalid Parent Link
```json
{
  "message": "The relation 'System.LinkTypes.Hierarchy-Reverse' is not valid."
}
```
**Mitigation**: Create Issue without parent link, log error for manual linking

## Retry Strategy

**Retryable Errors** (transient):
- 429 Too Many Requests (rate limit)
- 500 Internal Server Error
- 503 Service Unavailable
- Timeout errors

**Backoff**: Exponential (2s, 6s, 14s) - consistent with 001-ado-github-spec

**Non-Retryable Errors** (client):
- 401 Unauthorized
- 400 Bad Request (invalid data)
- 404 Not Found (project/work item type)

## Idempotency Mechanism

**Problem**: Workflow re-runs may attempt to create duplicate Issues

**Solution**: Query existing Issues before creation

**Query Pattern**:
```http
GET https://dev.azure.com/{org}/{project}/_apis/wit/wiql?api-version=7.0
Content-Type: application/json

{
  "query": "SELECT [System.Id] FROM WorkItems WHERE [System.WorkItemType] = 'Issue' AND [System.Tags] CONTAINS 'clarification' AND [System.Parent] = {parent_feature_id} AND [System.Description] CONTAINS '{idempotency_key}'"
}
```

**Idempotency Key Format**: `{feature_id}-{question_hash}`
- `{feature_id}`: ADO Feature work item ID
- `{question_hash}`: First 8 chars of SHA256(question_text)

**Example**: `9876-a3f5e1b2`

**Workflow Logic**:
1. For each question, generate idempotency key
2. Query ADO for existing Issues with key in Description
3. If found: skip creation, log "Issue already exists"
4. If not found: proceed with POST request

## Sample Real Payload

```json
[
  {
    "op": "add",
    "path": "/fields/System.Title",
    "value": "Clarification Q1: Auth Method Not Specified"
  },
  {
    "op": "add",
    "path": "/fields/System.Description",
    "value": "<div><h3>Clarification Question</h3><p><strong>Context:</strong> 'Copilot's <code>--allow-all-tools</code> mode can be configured to preserve markers instead of auto-resolving them (may require prompt engineering or environment variable).'</p><p><strong>Question:</strong> How can we configure Copilot to preserve [NEEDS CLARIFICATION] markers instead of auto-resolving them - is there an environment flag or does this require prompt modification?</p><p><strong>Spec File:</strong> <code>specs/002-preserve-clarification-questions/spec.md</code></p><p><strong>GitHub Branch:</strong> <a href='https://github.com/agzyamov/ai-native-sdlc/tree/002-preserve-clarification-questions'>002-preserve-clarification-questions</a></p><p><strong>Section:</strong> Assumptions</p><hr/><p><em>This Issue was auto-generated from the specification workflow. To resolve: answer the question in the comments, update the spec file, and mark this Issue as Done.</em></p><p><strong>Idempotency Key:</strong> <code>9876-a3f5e1b2</code></p></div>"
  },
  {
    "op": "add",
    "path": "/fields/System.Tags",
    "value": "clarification; auto-generated"
  },
  {
    "op": "add",
    "path": "/fields/System.AreaPath",
    "value": "AI-Native-SDLC\\Specifications"
  },
  {
    "op": "add",
    "path": "/fields/System.IterationPath",
    "value": "AI-Native-SDLC\\Sprint 42"
  },
  {
    "op": "add",
    "path": "/relations/-",
    "value": {
      "rel": "System.LinkTypes.Hierarchy-Reverse",
      "url": "https://dev.azure.com/myorg/AI-Native-SDLC/_apis/wit/workitems/9876",
      "attributes": {
        "comment": "Auto-generated clarification from spec generation workflow"
      }
    }
  }
]
```

## Testing Checklist

- [ ] PAT token has Work Items (Write) scope
- [ ] Project supports Issue work item type (or fallback to Task)
- [ ] Parent Feature ID exists and is accessible
- [ ] AreaPath and IterationPath are valid for project
- [ ] Description HTML renders correctly in ADO UI
- [ ] Tags are searchable in ADO queries
- [ ] Parent-Child relationship appears in Feature's Related Work section
- [ ] Idempotency: Running twice doesn't create duplicates

---

**Contract Version**: 1.0  
**API Version**: Azure DevOps REST API 7.0  
**Last Updated**: 2025-11-02  
**References**: [Azure DevOps REST API - Work Items](https://learn.microsoft.com/rest/api/azure/devops/wit/work-items/create)
