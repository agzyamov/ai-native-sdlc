#!/usr/bin/env python3
"""Extract [NEEDS CLARIFICATION] markers from spec.md and create clarifications.md"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

MARKER_PATTERN = r'\[NEEDS CLARIFICATION:\s*([^\]]+)\]'

def extract_markers(spec_content: str) -> list[dict]:
    """Extract all clarification markers with context and answer options"""
    markers = []
    
    for match in re.finditer(MARKER_PATTERN, spec_content):
        question = match.group(1).strip()
        pos = match.start()
        
        # Extract context (200 chars before marker)
        start = max(0, pos - 200)
        context_before = spec_content[start:pos].strip()
        
        # Extract extended context AFTER marker to capture answer options
        # Look for content until next section header (##) or end of paragraph
        after_marker = spec_content[pos:]
        
        # Find end of question block (next ## header, ---, or blank line + ##)
        end_patterns = [
            r'\n\s*#{1,6}\s+',  # Next section header
            r'\n\s*---\s*\n',   # Horizontal rule
            r'\n\s*\n\s*#{1,6}\s+',  # Blank line then header
        ]
        
        end_pos = len(after_marker)
        for pattern in end_patterns:
            end_match = re.search(pattern, after_marker)
            if end_match:
                end_pos = min(end_pos, end_match.start())
        
        # Extract full question block (marker + everything after until boundary)
        full_question_block = after_marker[:end_pos].strip()
        
        # Extract just the answer options table if present
        answer_options = ""
        table_match = re.search(
            r'\*\*Suggested Answers\*\*:?\s*\n\n(.+?)(?=\n\n\*\*Your choice\*\*|\n\n---|\Z)',
            full_question_block,
            re.DOTALL
        )
        if table_match:
            answer_options = table_match.group(1).strip()
        
        # Find section header (search backwards for ##)
        before_marker = spec_content[:pos]
        section_match = re.findall(r'^#{1,6}\s+(.+)$', before_marker, re.MULTILINE)
        section = section_match[-1] if section_match else "Unknown Section"
        
        # Extract clean topic from full_question_block if Copilot generated heading
        # Pattern: ## Question N: Topic Name
        topic_match = re.search(r'^##\s+Question\s+\d+:\s+(.+)$', full_question_block, re.MULTILINE)
        if topic_match:
            topic = topic_match.group(1).strip()
        else:
            # Fallback: first 50 chars of question (remove question markers)
            clean_question = question.replace('?', '').strip()
            topic = clean_question[:50] + ("..." if len(clean_question) > 50 else "")
        
        # Extract actual question text from "What we need to know:" section
        question_text_match = re.search(
            r'\*\*What we need to know\*\*:?\s+(.+?)(?=\n\n\*\*Suggested Answers\*\*|\n\n---|\Z)',
            full_question_block,
            re.DOTALL
        )
        if question_text_match:
            question_text = question_text_match.group(1).strip()
        else:
            # Fallback: use marker content
            question_text = question
        
        markers.append({
            'question': question_text,
            'answer_options': answer_options,
            'context': context_before,
            'section': section,
            'topic': topic,
            'full_block': full_question_block
        })
    
    return markers

def generate_clarifications_md(markers: list[dict], feature_name: str, spec_link: str = "./spec.md") -> str:
    """Generate clarifications.md content with answer options"""
    created_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    content = f"""# Clarification Questions: {feature_name}

**Feature**: [{spec_link}]({spec_link})  
**Created**: {created_date}  
**Status**: Open  
**Total Questions**: {len(markers)}

---

"""
    
    for i, marker in enumerate(markers, 1):
        content += f"""## Question {i}: {marker['topic']}

**Spec Section**: {marker['section']}

**Context**: {marker['context']}

**Question**: {marker['question']}

"""
        # Include answer options if present
        if marker.get('answer_options'):
            content += f"""**Answer Options**:

{marker['answer_options']}

"""
        
        content += f"""**Answer**: _Pending_

**ADO Issue**: _To be created_

---

"""
    
    content += """## Resolution Notes

_This section will be populated when questions are answered (manual or automated)._

"""
    
    return content

def main():
    parser = argparse.ArgumentParser(description="Extract clarification markers from spec.md")
    parser.add_argument("--spec-file", required=True, help="Path to spec.md")
    parser.add_argument("--output", required=True, help="Path to output clarifications.md")
    parser.add_argument("--feature-name", required=True, help="Feature name for header")
    
    args = parser.parse_args()
    
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        print(f"❌ Error: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    spec_content = spec_path.read_text()
    markers = extract_markers(spec_content)
    
    if not markers:
        print("ℹ️  No clarification markers found")
        sys.exit(0)
    
    print(f"✅ Extracted {len(markers)} clarification markers")
    
    clarifications_content = generate_clarifications_md(markers, args.feature_name)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clarifications_content)
    
    print(f"✅ Created clarifications file: {output_path}")

if __name__ == "__main__":
    main()
