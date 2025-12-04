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

    json_str = ""  # Initialize to avoid unbound variable error
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
        required_fields = ['topic', 'question', 'context', 'answer_options']
        optional_fields = ['recommended_option', 'suggested_answer']
        for marker in markers:
            missing_required = [k for k in required_fields if k not in marker]
            if missing_required:
                print(f"⚠️  Warning: Marker missing required fields: {missing_required}", file=sys.stderr)
            # Note: recommended_option and suggested_answer are optional (spec kit format)
        
        return markers
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        if json_str:
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
    parser = argparse.ArgumentParser(description="Extract clarification markers from spec.md or spec_output.txt using LLM")
    parser.add_argument("--spec-file", help="Path to spec.md (legacy)")
    parser.add_argument("--spec-output-file", help="Path to spec_output.txt (Copilot output)")
    parser.add_argument("--output", required=True, help="Path to output JSON file with extracted questions")
    parser.add_argument("--feature-name", help="Feature name for header (optional, used only for clarifications.md generation)")
    
    args = parser.parse_args()
    
    # Determine input file
    if args.spec_output_file:
        input_path = Path(args.spec_output_file)
        output_json = True  # Output JSON for direct use in create-ado-issues.sh
    elif args.spec_file:
        input_path = Path(args.spec_file)
        output_json = False  # Output clarifications.md (legacy mode)
    else:
        print("❌ Error: Either --spec-file or --spec-output-file must be provided", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    spec_content = input_path.read_text()
    
    # Use LLM to clean the content (remove timestamps, fix formatting) instead of regex
    # Check if markers exist before calling LLM
    if '[NEEDS CLARIFICATION:' not in spec_content and '## Question' not in spec_content:
        print("ℹ️  No clarification markers found")
        sys.exit(0)
    
    print("📡 Calling Azure OpenAI API to extract questions...")
    # LLM will handle cleaning timestamps and extracting questions in one pass
    markers = extract_markers_with_llm(spec_content)
    
    if not markers:
        print("ℹ️  No clarification questions extracted")
        sys.exit(0)
    
    print(f"✅ Extracted {len(markers)} clarification markers")
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_json:
        # Output JSON for direct use in create-ado-issues.sh
        import json
        output_path.write_text(json.dumps(markers, indent=2))
        print(f"✅ Created JSON file with extracted questions: {output_path}")
    else:
        # Legacy: Generate clarifications.md
        if not args.feature_name:
            print("❌ Error: --feature-name required when using --spec-file", file=sys.stderr)
            sys.exit(1)
        clarifications_content = generate_clarifications_md(markers, args.feature_name)
        output_path.write_text(clarifications_content)
        print(f"✅ Created clarifications file: {output_path}")

if __name__ == "__main__":
    main()
