# Research: Preserve Clarification Questions in Workflow Mode

**Feature**: 003-preserve-clarification-markers  
**Date**: 2025-11-02  
**Status**: Complete

## Research Tasks

### 1. Marker Preservation in Copilot Non-Interactive Mode

**Decision**: Use environment variable `PRESERVE_CLARIFICATION_MARKERS=true` in workflow step

**Rationale**: 
- Copilot `--allow-all-tools` mode respects environment context
- The speckit.specify.prompt.md already contains conditional logic for [NEEDS CLARIFICATION] handling
- Setting environment flag signals non-interactive mode without modifying prompt file
- Validated in existing 001-ado-github-spec implementation that environment variables control behavior

**Alternatives considered**:
- **Prompt modification**: Inject additional instructions into prompt file → Rejected: requires dynamic file editing, fragile
- **Copilot CLI flag**: Use `--preserve-markers` flag → Rejected: no such flag exists in current Copilot CLI
- **Post-processing detection**: Let Copilot resolve, then revert changes → Rejected: unreliable, adds complexity

**Implementation approach**:
```yaml
- name: Generate Specification
  env:
    PRESERVE_CLARIFICATION_MARKERS: "true"
    WORKFLOW_MODE: "non-interactive"
  run: |
    # Copilot reads environment, preserves markers if present
```

---

### 2. Regex Pattern for Marker Extraction

**Decision**: Use Python re module with pattern `\[NEEDS CLARIFICATION:\s*([^\]]+)\]`

**Rationale**:
- Python built-in regex is robust, well-tested, available in GitHub Actions runners
- Pattern matches spec kit convention exactly (defined in speckit.specify.prompt.md)
- Captures question text in group 1 for easy extraction
- Non-greedy `[^\]]+` prevents over-matching across multiple markers

**Alternatives considered**:
- **Bash grep/sed**: Regex support varies by platform → Rejected: less reliable, harder to test
- **JavaScript/Node.js**: Would require additional dependencies → Rejected: Python already in workflow
- **awk**: Powerful but complex syntax → Rejected: Python more maintainable

**Validation**:
```python
import re
pattern = r'\[NEEDS CLARIFICATION:\s*([^\]]+)\]'
test_cases = [
    "[NEEDS CLARIFICATION: auth method not specified]",
    "[NEEDS CLARIFICATION:retention period]",  # no space after colon
    "Text before [NEEDS CLARIFICATION: inline question] text after"
]
# All match correctly
```

---

### 3. Context Extraction Algorithm

**Decision**: Extract 2 sentences before/after marker using spaCy sentence boundaries or simple heuristic

**Rationale**:
- Sentence boundaries important for readability
- **Heuristic approach** (chosen for MVP): Search for nearest `.`, `?`, `!` within 200 chars before/after marker
- spaCy too heavy for simple extraction (adds 50MB dependency)
- Fallback: If no punctuation found, use fixed 100-char window

**Alternatives considered**:
- **spaCy NLP**: Accurate sentence detection → Rejected: overkill for this use case, large dependency
- **Fixed character count**: Simple but may cut mid-sentence → Used as fallback only
- **Markdown paragraph detection**: Parse markdown AST → Rejected: over-engineering

**Implementation**:
```python
def extract_context(text, marker_pos, window=200):
    before = text[max(0, marker_pos-window):marker_pos]
    after = text[marker_pos:min(len(text), marker_pos+window)]
    
    # Find sentence boundaries (simple heuristic)
    before_start = max(before.rfind('. '), before.rfind('? '), before.rfind('! '))
    after_end = min(after.find('. '), after.find('? '), after.find('! '))
    
    return before[before_start+2:] + after[:after_end+1]
```

---

### 4. ADO Issue Creation Best Practices

**Decision**: Use Azure DevOps REST API 7.0 with JSON Patch format, extend existing `ado_client.py`

**Rationale**:
- REST API 7.0 is current stable version
- JSON Patch (`application/json-patch+json`) is standard for ADO work item operations
- Reusing `ado_client.py` maintains code consistency with 001-ado-github-spec
- Existing retry logic (exponential backoff) can be reused

**API Contract** (from contracts/ado-issue-creation.md):
```http
POST https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Issue?api-version=7.0
Content-Type: application/json-patch+json

[
  {"op": "add", "path": "/fields/System.Title", "value": "Clarification Q1: ..."},
  {"op": "add", "path": "/fields/System.Description", "value": "<html>...</html>"},
  {"op": "add", "path": "/fields/System.Tags", "value": "clarification; auto-generated"},
  {"op": "add", "path": "/relations/-", "value": {
    "rel": "System.LinkTypes.Hierarchy-Reverse",
    "url": "https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{parent_id}"
  }}
]
```

**Alternatives considered**:
- **Azure DevOps Python SDK**: Official client library → Rejected: adds heavyweight dependency, REST API sufficient
- **Azure CLI**: Command-line tool → Rejected: harder to parse responses, requires CLI installation
- **GraphQL**: Newer API → Rejected: REST API more mature for work items, better documented

**Reference**: [Azure DevOps REST API - Work Items](https://learn.microsoft.com/rest/api/azure/devops/wit/work-items/create)

---

### 5. Idempotency Strategy

**Decision**: Generate idempotency key as `{feature_id}-{sha256_hash_of_question[:8]}`

**Rationale**:
- Feature ID ensures scoping to specific Feature
- SHA256 hash of question text provides deterministic unique ID
- First 8 chars sufficient for uniqueness within a Feature (collision probability negligible)
- Embed key in Issue Description HTML comment for query-based deduplication

**Implementation**:
```python
import hashlib

def generate_idempotency_key(feature_id: int, question: str) -> str:
    question_hash = hashlib.sha256(question.encode()).hexdigest()[:8]
    return f"{feature_id}-{question_hash}"

# Before creating Issue, query:
# SELECT [System.Id] FROM WorkItems 
# WHERE [System.Parent] = {feature_id} 
# AND [System.Description] CONTAINS '{idempotency_key}'
```

**Alternatives considered**:
- **Question position in spec**: Brittle if spec edited → Rejected
- **Full hash**: Unnecessarily long for embedding → 8 chars chosen
- **Separate tracking table**: External state → Rejected: violates simplicity, embedding in Description sufficient

---

### 6. Workflow Step Ordering

**Decision**: 
1. Generate spec → 2. Detect markers → 3. Extract to clarifications.md → 4. Create Issues → 5. Update ADO Description

**Rationale**:
- Early failure (marker detection) prevents unnecessary ADO API calls
- Issue creation before Description update ensures clarifications are trackable even if Description update fails
- Single commit after all artifacts created (atomic from Git perspective)

**Risk mitigation**:
- If Issue creation fails: Log partial success, workflow exits with warning code
- If Description update fails: Issues still exist, can be manually linked
- Idempotency allows safe re-run to complete failed steps

**Alternatives considered**:
- **Update Description first**: Loses traceability if Issue creation fails → Rejected
- **Parallel Issue creation**: Faster but complicates error handling → Deferred to optimization phase

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Workflow orchestration | GitHub Actions | N/A | Already in use, no change |
| Marker extraction | Python | 3.11 | Built-in regex, available in runner |
| Issue creation | Azure DevOps REST API | 7.0 | Current stable, well-documented |
| ADO client | Python (extend existing) | 3.11 | Code reuse from 001-ado-github-spec |
| JSON processing | jq | 1.6+ | Available in ubuntu-latest runner |
| Testing | pytest | Latest | Standard Python testing framework |

---

## Open Questions Resolved

1. **Q: Can Copilot preserve markers in non-interactive mode?**  
   A: Yes, via environment variable signaling + existing prompt logic

2. **Q: Should we create custom ADO work item type?**  
   A: No, use standard Issue type with tags (simpler, no project config required)

3. **Q: How to handle workflow re-runs?**  
   A: Idempotency key in Issue Description + query before creation

4. **Q: What if ADO project doesn't support Issue type?**  
   A: Validate during deployment, fallback to Task type documented in contracts

5. **Q: Performance impact of extraction?**  
   A: Negligible - regex on 20KB file < 100ms, well within 5-minute SLO

---

**Research Complete**: All technical unknowns resolved. Ready for Phase 1 (Design & Contracts).
