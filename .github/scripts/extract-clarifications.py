#!/usr/bin/env python3
"""Extract [NEEDS CLARIFICATION] markers from spec.md and create clarifications.md"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

MARKER_PATTERN = r'\[NEEDS CLARIFICATION:\s*([^\]]+)\]'

def extract_markers(spec_content: str) -> list[dict]:
    """Extract all clarification markers with context"""
    markers = []
    
    for match in re.finditer(MARKER_PATTERN, spec_content):
        question = match.group(1).strip()
        pos = match.start()
        
        # Extract context (200 chars before/after)
        start = max(0, pos - 200)
        end = min(len(spec_content), pos + 200)
        context = spec_content[start:end].strip()
        
        # Find section header (search backwards for ##)
        before_marker = spec_content[:pos]
        section_match = re.findall(r'^#{1,6}\s+(.+)$', before_marker, re.MULTILINE)
        section = section_match[-1] if section_match else "Unknown Section"
        
        # Generate topic (first 50 chars of question)
        topic = question[:50] + ("..." if len(question) > 50 else "")
        
        markers.append({
            'question': question,
            'context': context,
            'section': section,
            'topic': topic
        })
    
    return markers

def generate_clarifications_md(markers: list[dict], feature_name: str, spec_link: str = "./spec.md") -> str:
    """Generate clarifications.md content"""
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

**Answer**: _Pending_

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
