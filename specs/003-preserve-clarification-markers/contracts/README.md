# Contracts: Clarification Questions Workflow

**Feature**: 002-preserve-clarification-questions  
**Purpose**: Define data formats and API contracts for clarification question handling

## Overview

This directory contains formal contracts for the clarification questions workflow extension. These contracts define:

1. **Data Formats**: Structure of files and payloads
2. **API Contracts**: Request/response formats for external services
3. **Validation Rules**: Constraints and business logic
4. **Integration Points**: How components communicate

## Contract Files

### 1. [clarifications-format.md](./clarifications-format.md)

**Purpose**: Defines the structure of the `clarifications.md` file that stores extracted questions.

**Key Sections**:
- File location and lifecycle
- Markdown template structure
- Field definitions (header, questions, resolution notes)
- Extraction algorithms (topic, context, spec section)
- Validation schema
- Real-world examples

**Used By**:
- Workflow extraction step (writes clarifications.md)
- Product Owners (reads for review)
- Future resolution automation (updates answers)

**Version**: 1.0

---

### 2. [ado-issue-creation.md](./ado-issue-creation.md)

**Purpose**: Defines the Azure DevOps REST API payload for creating clarification Issue work items.

**Key Sections**:
- API endpoint and authentication
- Request body (JSON Patch format)
- Field mapping (Title, Description, Tags, AreaPath, IterationPath, Parent link)
- Response handling (success and error cases)
- Retry strategy
- Idempotency mechanism
- Sample payloads

**Used By**:
- Workflow Issue creation step (sends POST requests)
- Azure DevOps REST API (receives and processes)
- Error handling and retry logic

**Version**: 1.0

---

## Contract Dependencies

```
Feature Description (Input)
  ↓
Spec Generation (Copilot)
  ↓
spec.md with [NEEDS CLARIFICATION] markers
  ↓
┌─────────────────────────┬─────────────────────────┐
│                         │                         │
Clarifications File       ADO Issue Work Items      ADO Description Update
(clarifications-format)   (ado-issue-creation)      (existing contract)
│                         │                         │
└─────────────────────────┴─────────────────────────┘
```

## Integration Flow

1. **Spec Generation**: Workflow generates spec.md with markers (existing contract modified)
2. **Marker Extraction**: Workflow parses spec.md using regex `\[NEEDS CLARIFICATION:\s*([^\]]+)\]`
3. **File Creation**: Workflow writes `clarifications.md` per [clarifications-format.md](./clarifications-format.md)
4. **Issue Creation**: For each question, workflow POSTs to ADO per [ado-issue-creation.md](./ado-issue-creation.md)
5. **Description Update**: Workflow PATCHes Feature Description with spec (including markers) per existing contract

## Validation Checklist

Before implementation, verify:

- [ ] **Clarifications File**:
  - [ ] Template renders valid markdown
  - [ ] File size < 10KB (3 questions max)
  - [ ] All placeholders populated
  - [ ] Links to spec.md and ADO Issues work

- [ ] **ADO Issue Creation**:
  - [ ] PAT token has correct scopes (Work Items: Write)
  - [ ] Project supports Issue work item type
  - [ ] Parent-Child relationship type allowed
  - [ ] HTML Description renders correctly in ADO UI
  - [ ] Idempotency query prevents duplicates
  - [ ] Retry logic handles transient errors

- [ ] **End-to-End**:
  - [ ] Marker extraction finds all instances
  - [ ] Topic extraction produces readable titles
  - [ ] Context extraction preserves meaning
  - [ ] Links between clarifications.md and Issues are bidirectional

## Error Scenarios

### Extraction Failures

- **Malformed Marker**: Log warning, skip extraction, proceed with other markers
- **No Context Available**: Use question text only, note missing context in clarifications.md
- **Spec Section Not Found**: Default to "Unknown Section", log warning

### Issue Creation Failures

- **401 Unauthorized**: Fail workflow, require PAT update
- **400 Bad Request (Invalid Type)**: Fallback to Task work item type, log warning
- **400 Bad Request (Invalid Parent)**: Create Issue without parent, log error for manual linking
- **429 Rate Limit**: Exponential backoff (2s, 6s, 14s), max 3 retries
- **Partial Success (2/3 created)**: Mark workflow as partial success, log which failed

## Testing Strategy

### Unit Tests

- Regex pattern matching for various marker formats
- Topic extraction from question text
- Context extraction from spec paragraphs
- Idempotency key generation (SHA256 hash)

### Integration Tests

- End-to-end workflow with sample spec containing 3 markers
- Verify clarifications.md structure matches template
- Verify ADO Issues created with correct fields
- Verify Parent-Child relationships established
- Verify idempotency (run twice, no duplicates)

### Manual Tests

- Review clarifications.md in GitHub UI (readability)
- Review Issue Description in ADO UI (HTML rendering)
- Click links in clarifications.md (navigation)
- Update spec.md, re-run workflow (deduplication)

## Migration Notes

**From 001-ado-github-spec**:
- No breaking changes to existing contracts
- New contracts add optional functionality (only triggered if markers present)
- Existing workflows without clarification markers unaffected

**Backward Compatibility**:
- Features without clarification needs: no clarifications.md created, no Issues generated
- Rollback: Remove extraction and Issue creation steps from workflow YAML

## Version History

| Version | Date       | Changes |
|---------|------------|---------|
| 1.0     | 2025-11-02 | Initial contracts for clarification workflow |

## References

- **Parent Feature**: [spec.md](../spec.md)
- **Data Model**: [data-model.md](../data-model.md)
- **Implementation**: `.github/workflows/spec-kit-specify.yml` (to be updated)
- **ADO API Docs**: [Work Items - Create](https://learn.microsoft.com/rest/api/azure/devops/wit/work-items/create)
- **GitHub Markdown**: [GFM Spec](https://github.github.com/gfm/)

---

**Maintained By**: Platform Engineering Team  
**Contact**: See repository CODEOWNERS  
**Last Updated**: 2025-11-02
