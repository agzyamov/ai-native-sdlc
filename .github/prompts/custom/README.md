# Custom LLM Prompts

This directory contains custom LLM prompts used by automation scripts in this repository.

**IMPORTANT**: These prompts are separate from GitHub Spec Kit prompts (in parent directory) to avoid conflicts during Spec Kit updates.

## Prompt Naming Convention

Prompts are stored as separate files following this pattern:

- `{task-name}.system.md` - System prompt (role definition, instructions)
- `{task-name}.user.md` - User prompt template (with placeholders like `{variable_name}`)

## Current Prompts

### Question Detection

**Purpose**: Detect if Copilot output contains clarification questions

**Files**:
- `detect-clarification-questions.system.md` - System role and behavior
- `detect-clarification-questions.user.md` - User input template

**Used by**: `.github/scripts/detect-questions-llm.sh`

**Model**: gpt-4o (GitHub Models)

**Parameters**: temperature=0.0, max_tokens=100

---

### Question Extraction

**Purpose**: Extract structured clarification questions from spec markdown

**Files**:
- `extract-questions.system.md` - System role, output format, extraction rules
- `extract-questions.user.md` - User input template

**Used by**: `.github/scripts/extract-clarifications-llm.py`

**Model**: gpt-4o (GitHub Models)

**Parameters**: temperature=0.0, max_tokens=4000

---

## Usage Pattern

Scripts should:
1. Read prompt files from this directory
2. Replace placeholders in user prompt (e.g., `{copilot_output}`)
3. Send to LLM API
4. Parse response

Example:
```python
from pathlib import Path

prompts_dir = Path(__file__).parent.parent / "prompts" / "custom"
system_prompt = (prompts_dir / "task-name.system.md").read_text()
user_template = (prompts_dir / "task-name.user.md").read_text()
user_prompt = user_template.replace("{variable}", value)
```

## Governance

- **Never** embed LLM prompts directly in workflow YAML files
- **Never** embed LLM prompts directly in shell scripts (.sh files)
- **Never** embed LLM prompts directly in Python scripts (.py files)
- **Always** store prompts in dedicated markdown files
- **Always** keep custom prompts separate from Spec Kit prompts (parent directory)
- **Version control**: All prompt changes go through PR review
- **Testing**: Update affected scripts when prompts change
