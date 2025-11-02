# Contract: Clarifications File Format

**Version**: 1.0  
**Feature**: 002-preserve-clarification-questions  
**Purpose**: Define structured format for extracted clarification questions

## File Location

- **Path Pattern**: `specs/<feature-dir>/clarifications.md`
- **Example**: `specs/002-preserve-clarification-questions/clarifications.md`
- **Lifecycle**: Created when spec.md contains [NEEDS CLARIFICATION] markers
- **Deletion**: Remove when all questions resolved (future automation) or manually when no longer needed

## File Format Template

```markdown
# Clarification Questions: [FEATURE NAME]

**Feature**: [Link to spec.md]  
**Created**: [ISO 8601 Date]  
**Status**: Open | Partially Answered | Complete  
**Total Questions**: [N]

---

## Question 1: [Topic - extracted from first 5-7 words]

**Spec Section**: [Section header where marker appeared]

**Context**: [Quote 1-3 sentences surrounding the marker from spec.md]

**Question**: [Full text extracted from [NEEDS CLARIFICATION: ...] marker]

**Answer**: _Pending_

**ADO Issue**: [Link to associated Issue work item - auto-generated]

---

## Question 2: [Topic]

**Spec Section**: [Section header]

**Context**: [Quote from spec]

**Question**: [Question text]

**Answer**: _Pending_

**ADO Issue**: [Issue work item link]

---

[Repeat for questions 3+, max 3 total per MVP]

---

## Resolution Notes

_This section is populated when questions are answered (manual or automated)._

- **Q1 Resolved**: [Date] - [Brief answer summary]
- **Q2 Resolved**: [Date] - [Brief answer summary]

```

## Field Definitions

### Header Fields

- **Feature Name**: Extracted from spec.md `# Feature Specification: [NAME]` header
- **Feature Link**: Relative path to spec.md (e.g., `[spec.md](./spec.md)`)
- **Created**: ISO 8601 timestamp when file was generated (e.g., `2025-11-02T14:30:00Z`)
- **Status**:
  - `Open`: All questions unanswered
  - `Partially Answered`: At least one question has answer, at least one pending
  - `Complete`: All questions answered
- **Total Questions**: Integer 1-3 (enforced by workflow)

### Question Fields

- **Topic**: Auto-extracted from first 5-7 words of question text, converted to Title Case
- **Spec Section**: Full header hierarchy (e.g., `## Requirements > ### Functional Requirements`)
- **Context**: 1-3 sentences from spec.md surrounding the marker (before and/or after)
- **Question**: Exact text extracted from `[NEEDS CLARIFICATION: <this text>]`
- **Answer**: Initially `_Pending_`; replaced with answer text when resolved
- **ADO Issue**: Markdown link in format `[#<WorkItemID>](https://dev.azure.com/...)`

## Extraction Rules

### LLM-Based Extraction (Primary Method)

**Implementation**: GitHub Models API (GPT-4o) via OpenAI client
- **Endpoint**: `https://models.inference.ai.azure.com`
- **Authentication**: `GITHUB_TOKEN` environment variable
- **Model**: `gpt-4o` (free tier in GitHub Actions)
- **Temperature**: 0.0 (deterministic extraction)
- **Max Tokens**: 4000

**Extraction Process**:
1. Detect `[NEEDS CLARIFICATION:` markers in spec.md (simple string match)
2. Send full spec content to LLM with structured prompt
3. LLM extracts JSON array with fields: `topic`, `question`, `context`, `answer_options`
4. Validate JSON structure and required fields
5. Generate clarifications.md from structured data

**Benefits Over Regex**:
- Robust to format variations in Copilot output
- Understands semantic structure even with spacing/formatting differences
- Can handle missing or reordered sections
- No regex maintenance needed when Copilot changes output format

### Topic Extraction (LLM)

LLM extracts topic from `## Question N: Topic Name` heading structure:
- Locates heading after `[NEEDS CLARIFICATION:]` marker
- Extracts text after colon
- Handles variations: missing colon, different heading levels, extra whitespace
- Fallback: Uses first few words of question if no heading found
- Example: `## Question 1: Authentication Method` → `Authentication Method`

### Context Extraction (LLM)

LLM extracts context from `**Context**:` section:
- Locates section between marker and question
- Extracts full paragraph (not truncated)
- Preserves markdown formatting (bold, inline code, links)
- Handles multi-paragraph context
- Example: `**Context**: Creating a snake game for 4-year-old...` → full text extracted

### Question Extraction (LLM)

LLM extracts question from `**What we need to know**:` section:
- Locates section after context
- Extracts full question text
- Handles multi-line questions
- Preserves formatting

### Answer Options Extraction (LLM)

LLM extracts answer options table from `**Suggested Answers**:` section:
- Locates markdown table after question
- Extracts full table including header and all rows
- Preserves markdown table format for clarifications.md
- Returns empty string if no table present
- Handles variations in table structure

## Validation Schema (Conceptual)

```typescript
interface ClarificationsFile {
  header: {
    featureName: string;          // From spec.md H1
    featureLink: string;           // Relative path to spec.md
    created: string;               // ISO 8601 datetime
    status: 'Open' | 'Partially Answered' | 'Complete';
    totalQuestions: number;        // 1-3
  };
  questions: Question[];           // Array length 1-3
  resolutionNotes?: ResolutionNote[];
}

interface Question {
  number: number;                  // 1-3
  topic: string;                   // Auto-extracted, Title Case
  specSection: string;             // Header hierarchy
  context: string;                 // 100-300 chars from spec
  question: string;                // Exact text from marker
  answer: string;                  // "_Pending_" or answer text
  adoIssueLink?: string;          // Markdown link to Issue WI
}

interface ResolutionNote {
  questionNumber: number;
  resolvedDate: string;            // ISO 8601
  answerSummary: string;           // Brief text
}
```

## Example (Real Data)

```markdown
# Clarification Questions: Preserve Clarification Questions in Workflow Mode

**Feature**: [spec.md](./spec.md)  
**Created**: 2025-11-02T15:45:00Z  
**Status**: Open  
**Total Questions**: 2

---

## Question 1: Copilot Marker Preservation Method

**Spec Section**: Assumptions

**Context**: "Copilot's `--allow-all-tools` mode can be configured to preserve markers instead of auto-resolving them (may require prompt engineering or environment variable)."

**Question**: How can we configure Copilot to preserve [NEEDS CLARIFICATION] markers instead of auto-resolving them - is there an environment flag or does this require prompt modification?

**Answer**: _Pending_

**ADO Issue**: [#12345](https://dev.azure.com/org/project/_workitems/edit/12345)

---

## Question 2: ADO Issue Type Support

**Spec Section**: Assumptions

**Context**: "ADO project supports Issue work item type and Parent-Child link relationship (validate during deployment; fallback to Task type if needed)."

**Question**: Should we validate Issue work item type availability before deployment, or auto-detect and fallback to Task type if Issue is not supported?

**Answer**: _Pending_

**ADO Issue**: [#12346](https://dev.azure.com/org/project/_workitems/edit/12346)

---

## Resolution Notes

_Questions will be tracked and resolved through ADO Issues. Answers will be updated here once Issues are marked Done._
```

## Usage Pattern

### Workflow Generation (Automated)

1. After spec.md is generated by Copilot
2. Parse spec.md for `[NEEDS CLARIFICATION: ...]` markers
3. For each marker (max 3):
   - Extract question text, context, spec section
   - Generate topic from question text
   - Create Question object
4. Render clarifications.md using template
5. Commit to feature branch alongside spec.md

### Human Review (Manual)

1. Product Owner opens clarifications.md in GitHub
2. Reviews each question with context
3. Optionally adds notes or answers directly in file
4. More commonly: resolves via ADO Issue work items

### Resolution Workflow (Future Automation)

1. When ADO Issue marked Done:
   - Extract resolution comment from Issue
   - Update corresponding Question.answer in clarifications.md
   - Update Status if all questions answered
2. When Status = Complete:
   - Trigger spec.md update with resolved answers
   - Archive or remove clarifications.md

## Compatibility Notes

- **Markdown Standard**: GitHub Flavored Markdown (GFM)
- **Line Endings**: LF (Unix style)
- **Encoding**: UTF-8
- **Max File Size**: Recommended < 10KB (3 questions × ~3KB max)
- **Validation**: No strict schema enforcement in MVP; manual inspection acceptable

---

**Contract Owner**: Workflow automation (spec-kit-specify.yml)  
**Consumers**: Product Owners (manual review), Future automation (resolution workflow)  
**Version History**: 1.0 (initial) - 2025-11-02
