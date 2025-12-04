# User Prompt: Extract Clarification Questions

Extract all clarification questions from this markdown document.

IMPORTANT: Clean the content first:
- Remove any GitHub Actions timestamps (format: TAB TAB YYYY-MM-DDTHH:MM:SSZ)
- Remove any log prefixes or formatting artifacts
- Focus on the actual question content

Then extract questions. Support BOTH formats:

1. **Spec Kit Format** (preferred):
   - Questions may have "**Recommended:** Option [X] - <reasoning>" (for multiple-choice)
   - OR "**Suggested:** <answer> - <reasoning>" (for short-answer)
   - Table format: `Option | Description` (2 columns)
   - Question text may be directly after heading, not always labeled with "**What we need to know**:"

2. **Legacy Format**:
   - Questions have "**What we need to know**:" label
   - Table format: `Option | Answer | Implications` (3 columns)

Extract all questions:

---

{spec_content}

---

Return JSON array as specified. Include recommended_option or suggested_answer fields if present in the source.
