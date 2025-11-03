#!/usr/bin/env python3
"""Extract [NEEDS CLARIFICATION] markers from spec.md using LLM (Azure OpenAI)"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI

def extract_markers_with_llm(spec_content: str) -> list[dict]:
    """Extract all clarification questions using Azure OpenAI LLM"""
    
    # Initialize Azure OpenAI client
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: AZURE_OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    client = OpenAI(
        base_url="https://ruste-mhinjxi0-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-5-nano",
        api_key=api_key,
        default_headers={'api-key': api_key}
    )    # Load prompts from dedicated files
    script_dir = Path(__file__).parent
    prompts_dir = script_dir.parent / "prompts" / "custom"
    
    system_prompt = (prompts_dir / "extract-questions.system.md").read_text().strip()
    user_template = (prompts_dir / "extract-questions.user.md").read_text().strip()
    
    # Replace placeholder in user prompt
    user_prompt = user_template.replace("{spec_content}", spec_content)

    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=16000,  # Allow up to 16K tokens for large JSON responses
            extra_query={'api-version': '2025-01-01-preview'}
        )
        
        # Parse JSON response
        json_str = response.choices[0].message.content.strip()
        
        # Remove markdown code fences if LLM added them despite instructions
        if json_str.startswith("```json"):
            json_str = json_str.replace("```json", "").replace("```", "").strip()
        elif json_str.startswith("```"):
            json_str = json_str.replace("```", "").strip()
        
        markers = json.loads(json_str)
        
        # Validate structure
        for marker in markers:
            if not all(k in marker for k in ['topic', 'question', 'context', 'answer_options']):
                print(f"⚠️  Warning: Marker missing required fields: {marker}", file=sys.stderr)
        
        return markers
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        print(f"Raw response: {json_str[:500]}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error calling Azure OpenAI API: {e}", file=sys.stderr)
        sys.exit(1)

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

**Context**: {marker['context']}

**Question**: {marker['question']}

"""
        # Include answer options if present
        if marker.get('answer_options') and marker['answer_options'].strip():
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
    parser = argparse.ArgumentParser(description="Extract clarification markers from spec.md using LLM")
    parser.add_argument("--spec-file", required=True, help="Path to spec.md")
    parser.add_argument("--output", required=True, help="Path to output clarifications.md")
    parser.add_argument("--feature-name", required=True, help="Feature name for header")
    
    args = parser.parse_args()
    
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        print(f"❌ Error: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    spec_content = spec_path.read_text()
    
    # Clean GitHub Actions timestamps if present
    import re
    spec_content = re.sub(r'^[^\t]+\t[^\t]+\t\d{4}-\d{2}-\d{2}T[\d:.]+Z\s+', '', spec_content, flags=re.MULTILINE)
    
    # Check if markers exist before calling LLM
    if '[NEEDS CLARIFICATION:' not in spec_content:
        print("ℹ️  No clarification markers found")
        sys.exit(0)
    
    print("📡 Calling Azure OpenAI API to extract questions...")
    markers = extract_markers_with_llm(spec_content)
    
    if not markers:
        print("ℹ️  No clarification questions extracted")
        sys.exit(0)
    
    print(f"✅ Extracted {len(markers)} clarification markers")
    
    clarifications_content = generate_clarifications_md(markers, args.feature_name)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clarifications_content)
    
    print(f"✅ Created clarifications file: {output_path}")

if __name__ == "__main__":
    main()
