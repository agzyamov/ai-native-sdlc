#!/usr/bin/env python3
"""Extract [NEEDS CLARIFICATION] markers from spec.md using LLM (GitHub Models)"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI

def extract_markers_with_llm(spec_content: str) -> list[dict]:
    """Extract all clarification questions using GitHub Models LLM"""
    
    # Initialize GitHub Models client
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=github_token
    )
    
    # Create prompt for LLM to extract questions
    system_prompt = """You are a precise question extractor. Extract clarification questions from markdown documents.

Output ONLY valid JSON array with this exact structure:
[
  {
    "topic": "Brief topic name from ## Question N: Topic heading",
    "question": "Full question text from **What we need to know**:",
    "context": "Text from **Context**: section",
    "answer_options": "Full markdown table from **Suggested Answers**: (if present, empty string if not)"
  }
]

Rules:
- Extract ALL questions that follow [NEEDS CLARIFICATION: ...] markers
- For topic: use text after "## Question N:" heading
- For question: use text after "**What we need to know**:"
- For context: use text after "**Context**:"
- For answer_options: include the full markdown table from "**Suggested Answers**:" including header and rows
- If answer options table doesn't exist, use empty string ""
- Return valid JSON only, no markdown code blocks, no explanation"""

    user_prompt = f"""Extract all clarification questions from this markdown document:

{spec_content}

Return JSON array as specified."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Deterministic output
            max_tokens=4000
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
        print(f"❌ Error calling GitHub Models API: {e}", file=sys.stderr)
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
    
    # Check if markers exist before calling LLM
    if '[NEEDS CLARIFICATION:' not in spec_content:
        print("ℹ️  No clarification markers found")
        sys.exit(0)
    
    print("📡 Calling GitHub Models API to extract questions...")
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
