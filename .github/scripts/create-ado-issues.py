#!/usr/bin/env python3
"""Create ADO Issue work items from LLM-extracted questions (JSON format)"""

import argparse
import sys
import os
import json
import hashlib
import re
from pathlib import Path

# Try to import html2text for HTML to markdown conversion
try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False

# Add function_app to path for ado_client import
GITHUB_WORKSPACE = os.getenv("GITHUB_WORKSPACE", ".")
sys.path.insert(0, os.path.join(GITHUB_WORKSPACE, "function_app"))

try:
    from ado_client import create_issue_workitem
except ImportError:
    print("❌ Error: Could not import ado_client. Make sure function_app is in the path.", file=sys.stderr)
    sys.exit(1)


def convert_html_to_markdown(html_text: str) -> str:
    """Convert HTML to markdown format
    
    If html2text is available, use it. Otherwise, do basic conversion.
    """
    if HTML2TEXT_AVAILABLE:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # Don't wrap lines
        markdown = h.handle(html_text)
        return markdown.strip()
    else:
        # Basic HTML to markdown conversion without library
        # Remove HTML tags but preserve structure
        text = html_text
        
        # Convert <br/> and <br> to newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        
        # Convert <p> tags to double newlines
        text = re.sub(r'<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
        
        # Convert <strong> and <b> to **
        text = re.sub(r'<(strong|b)[^>]*>', '**', text, flags=re.IGNORECASE)
        text = re.sub(r'</(strong|b)>', '**', text, flags=re.IGNORECASE)
        
        # Convert <em> and <i> to *
        text = re.sub(r'<(em|i)[^>]*>', '*', text, flags=re.IGNORECASE)
        text = re.sub(r'</(em|i)>', '*', text, flags=re.IGNORECASE)
        
        # Convert <h1> to #
        text = re.sub(r'<h1[^>]*>', '# ', text, flags=re.IGNORECASE)
        text = re.sub(r'</h1>', '\n', text, flags=re.IGNORECASE)
        
        # Convert <h2> to ##
        text = re.sub(r'<h2[^>]*>', '## ', text, flags=re.IGNORECASE)
        text = re.sub(r'</h2>', '\n', text, flags=re.IGNORECASE)
        
        # Convert <h3> to ###
        text = re.sub(r'<h3[^>]*>', '### ', text, flags=re.IGNORECASE)
        text = re.sub(r'</h3>', '\n', text, flags=re.IGNORECASE)
        
        # Convert <ul><li> to markdown list
        text = re.sub(r'<ul[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</ul>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<li[^>]*>', '- ', text, flags=re.IGNORECASE)
        text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()


def validate_and_fix_markdown(markdown_text: str) -> tuple[str, list[str]]:
    """Validate and fix markdown for Azure DevOps work items
    
    Returns:
        tuple: (fixed_markdown, list_of_warnings)
    """
    warnings = []
    fixed = markdown_text
    
    # Check 1: Ensure newlines are present (Azure DevOps may strip them)
    if '\n' not in fixed:
        warnings.append("No newlines found - markdown may not render correctly")
        # Add newlines after markdown elements
        fixed = fixed.replace('## ', '\n## ')
        fixed = fixed.replace('**', '\n**')
        fixed = fixed.replace('---', '\n---\n')
    
    # Check 2: Ensure proper spacing around headers
    # Add blank line before headers if missing
    fixed = re.sub(r'([^\n])(## )', r'\1\n\n\2', fixed)
    # Add blank line after headers if missing
    fixed = re.sub(r'(## [^\n]+)\n([^\n#])', r'\1\n\n\2', fixed)
    
    # Check 3: Ensure list items have proper spacing
    # Add blank line before lists if missing
    fixed = re.sub(r'([^\n])\n(- |\* |[0-9]+\. )', r'\1\n\n\2', fixed)
    
    # Check 4: Ensure horizontal rules have proper spacing
    fixed = re.sub(r'([^\n])\n---\n([^\n])', r'\1\n\n---\n\n\2', fixed)
    
    # Check 5: Fix multiple consecutive newlines (more than 2)
    fixed = re.sub(r'\n{3,}', '\n\n', fixed)
    
    # Check 6: Ensure markdown syntax is not broken
    # Check for unclosed bold/italic
    bold_count = fixed.count('**')
    if bold_count % 2 != 0:
        warnings.append(f"Unclosed bold markers detected ({bold_count} ** found)")
    
    italic_count = fixed.count('_')
    # Count italic markers, but ignore those in markdown links [text](url)
    italic_in_links = len(re.findall(r'\[[^\]]+\]\([^\)]+\)', fixed))
    if (italic_count - italic_in_links * 2) % 2 != 0:
        warnings.append(f"Possible unclosed italic markers detected")
    
    # Check 7: Ensure code blocks are properly closed
    code_block_count = fixed.count('```')
    if code_block_count % 2 != 0:
        warnings.append("Unclosed code blocks detected")
    
    # Check 8: Ensure headers have proper format
    # Check for headers without space after #
    fixed = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', fixed, flags=re.MULTILINE)
    
    # Check 9: Ensure lists have proper indentation
    # Fix lists that don't start with proper bullet
    lines = fixed.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # If line looks like a list item but doesn't start with bullet/number
        if stripped and not stripped.startswith(('#', '*', '-', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '**', '_', '---', '<')):
            # Check if previous line was a list
            if i > 0 and lines[i-1].strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                # This might be continuation text, keep as is
                pass
        fixed_lines.append(line)
    fixed = '\n'.join(fixed_lines)
    
    # Final check: Ensure we have newlines (critical for Azure DevOps)
    if '\n' not in fixed:
        warnings.append("CRITICAL: No newlines in final markdown - adding minimal formatting")
        # Add newlines in critical places
        fixed = fixed.replace('## ', '\n## ')
        fixed = fixed.replace('**', '\n**')
        fixed = fixed.replace('---', '\n---\n')
    
    return fixed, warnings


def convert_table_to_markdown(table_text: str) -> str:
    """Convert markdown table to clean markdown list format for Azure DevOps
    
    Azure DevOps supports markdown and will convert it properly.
    Example:
    | Option | Answer | Implications |
    |--------|--------|--------------|
    | A | Email/password | Simple implementation; user management |
    
    Becomes:
    ### Option A: Email/password
    
    **Implications:**
    - Simple implementation
    - user management
    
    ---
    """
    if not table_text or '|' not in table_text:
        return table_text
    
    lines = [line.rstrip() for line in table_text.split('\n')]
    options = []
    header_row = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped or '|' not in stripped:
            continue
        
        # Check if this is a header separator row (skip it)
        if all(c in '|-: ' for c in stripped) and '-' in stripped:
            continue
        
        # Parse table row
        parts = [p.strip() for p in stripped.split('|')]
        # Remove empty parts at start/end (from leading/trailing |)
        if parts and not parts[0]:
            parts = parts[1:]
        if parts and not parts[-1]:
            parts = parts[:-1]
        
        # Skip empty rows
        if not parts or all(not p for p in parts):
            continue
        
        # First row is usually header - store it
        if header_row is None:
            header_row = parts
            continue
        
        # Parse data row
        # Expected format: Option, Answer, Implications (or similar)
        if len(parts) >= 2:
            option = parts[0] if len(parts) > 0 else ""
            answer = parts[1] if len(parts) > 1 else ""
            implications = parts[2] if len(parts) > 2 else ""
            
            # Clean up option (remove any trailing dashes or extra spaces)
            option = option.strip().rstrip('-').strip()
            answer = answer.strip().rstrip('-').strip()
            implications = implications.strip().rstrip('-').strip()
            
            # Format as markdown with clear structure
            option_md = f"### Option {option}: {answer}\n"
            
            if implications:
                # Split implications by semicolons and format as markdown list
                implications_list = [imp.strip() for imp in implications.split(';') if imp.strip()]
                if len(implications_list) > 1:
                    # Multiple implications - format as markdown list
                    option_md += "\n**Implications:**\n"
                    for imp in implications_list:
                        option_md += f"- {imp}\n"
                else:
                    # Single implication - keep as is
                    option_md += f"\n**Implications:** {implications}\n"
            
            # Add separator between options
            option_md += "\n---\n"
            options.append(option_md)
    
    # Join options
    return '\n'.join(options) if options else table_text


def build_description(
    question_num: int,
    topic: str,
    question_text: str,
    context: str,
    answer_options: str,
    recommended_option: str = None,
    suggested_answer: str = None,
    branch_name: str = None,
    use_llm: bool = False,
    api_key: str = None,
    client=None
) -> str:
    """Build ADO Issue description with optional LLM formatting"""
    
    # Build raw description parts
    raw_description_parts = [
        f"## Question {question_num}: {topic}\n\n",
    ]
    
    if context:
        raw_description_parts.append(f"**Context**: {context}\n\n")
    
    # Add recommendation or suggestion if present (spec kit format)
    if recommended_option:
        # Extract reasoning if present in recommended_option (format: "Option X - reasoning")
        parts = recommended_option.split(" - ", 1)
        if len(parts) == 2:
            option_part, reasoning = parts
            raw_description_parts.append(f"**Recommended:** {option_part} - {reasoning}\n\n")
        else:
            raw_description_parts.append(f"**Recommended:** {recommended_option}\n\n")
    elif suggested_answer:
        # Extract reasoning if present in suggested_answer (format: "answer - reasoning")
        parts = suggested_answer.split(" - ", 1)
        if len(parts) == 2:
            answer_part, reasoning = parts
            raw_description_parts.append(f"**Suggested:** {answer_part} - {reasoning}\n\n")
        else:
            raw_description_parts.append(f"**Suggested:** {suggested_answer}\n\n")
    
    if question_text:
        raw_description_parts.append(f"**What we need to know**: {question_text}\n\n")
    
    if answer_options:
        # Convert table to clean markdown format (Azure DevOps supports markdown)
        # Parse table and convert to formatted markdown
        options_md = convert_table_to_markdown(answer_options)
        raw_description_parts.append(f"**Suggested Answers**:\n\n{options_md}\n")
    
    raw_description_parts.append(f"**Your choice**: _[Awaiting response]_\n\n")
    raw_description_parts.append(f"---\n\n")
    
    if branch_name:
        raw_description_parts.append(f"**Branch**: {branch_name}\n")
    
    raw_description = ''.join(raw_description_parts)
    
    # Use LLM to clean and fix markdown if available
    if use_llm and api_key and client:
        try:
            fix_prompt = f"""Clean and fix this ADO work item description markdown for Azure DevOps. Requirements:
1. Remove duplicate "Question N:" text from the heading (e.g., "Question 2: Question 2: Topic" should become "Question 2: Topic")
2. Ensure all markdown syntax is correct and will render properly in Azure DevOps
3. Convert any markdown tables to list format - Azure DevOps work items don't render tables well. Convert tables like this:
   - Instead of: | Option | Answer | Implications |
   - Use: - **Option A**: Answer text
           _Implications_: Implications text
4. Add proper spacing:
   - Two blank lines between major sections
   - One blank line between subsections
5. Improve readability:
   - Use proper markdown formatting (bold, italic where appropriate)
   - Break long lines if needed
6. Keep all content intact, just improve formatting and readability

Raw description:
{raw_description}

Return ONLY the cleaned and fixed markdown description, no code blocks, no explanation."""
            
            response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "You are a markdown formatter for Azure DevOps work items. Your job is to:\n1. Convert markdown tables to list format - Azure DevOps work items don't render tables well, so convert tables to bullet lists with bold option labels\n2. Improve readability with proper spacing and line breaks\n3. Remove duplicate text\n4. Ensure all markdown syntax is valid for Azure DevOps\nReturn only the fixed markdown text, no code blocks, no explanation."},
                    {"role": "user", "content": fix_prompt}
                ],
                max_completion_tokens=4000,
                extra_query={'api-version': '2025-01-01-preview'}
            )
            
            description = response.choices[0].message.content.strip()
            
            # Remove markdown code fences if LLM added them
            if description.startswith("```"):
                lines = description.split('\n')
                if lines and lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                description = '\n'.join(lines).strip()
            
            # Validate LLM response - if empty or whitespace-only, fallback to raw
            if not description or not description.strip():
                print(f"⚠️  LLM returned empty description, using raw description", file=sys.stderr)
                return raw_description
            
            # Check if LLM response has meaningful content (at least a header or some text)
            if len(description.strip()) < 10:
                print(f"⚠️  LLM returned very short description ({len(description)} chars), using raw description", file=sys.stderr)
                return raw_description
            
            # Check if LLM stripped all newlines (raw_description has them, but LLM response doesn't)
            # This indicates LLM broke the formatting
            if '\n' not in description and '\n' in raw_description:
                print(f"⚠️  LLM stripped all newlines (raw had {raw_description.count(chr(10))} newlines), using raw description", file=sys.stderr)
                return raw_description
            
            print(f"✅ Cleaned and fixed markdown using LLM")
            return description
            
        except Exception as e:
            print(f"⚠️  Could not fix markdown with LLM: {e}, using original", file=sys.stderr)
            # Fallback to raw description
            return raw_description
    else:
        # No LLM, return raw description
        return raw_description


def clean_topic_with_llm(topic: str, api_key: str, client) -> str:
    """Extract clean topic using LLM"""
    try:
        title_prompt = f"""Extract a clean, concise topic from this text. Remove any "Question N:" prefix. Return only the topic text, nothing else.

Text: {topic}

Topic:"""
        title_response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "Extract clean topic text. Remove 'Question N:' prefixes. Return only the topic."},
                {"role": "user", "content": title_prompt}
            ],
            max_completion_tokens=100,
            extra_query={'api-version': '2025-01-01-preview'}
        )
        clean_topic = title_response.choices[0].message.content.strip()
        return clean_topic if clean_topic else topic
    except Exception as e:
        print(f"⚠️  Could not clean topic with LLM: {e}, using original", file=sys.stderr)
        return topic


def main():
    parser = argparse.ArgumentParser(description="Create ADO Issues from extracted questions JSON")
    parser.add_argument("--questions-json", required=True, help="Path to questions JSON file")
    parser.add_argument("--feature-id", required=True, help="Parent Feature work item ID")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--org-url", required=True, help="ADO organization URL")
    parser.add_argument("--project", required=True, help="ADO project name")
    
    args = parser.parse_args()
    
    # Set environment variables for ado_client
    os.environ['ADO_ORG_URL'] = args.org_url
    os.environ['ADO_PROJECT'] = args.project
    ado_pat = os.getenv('ADO_WORK_ITEM_PAT')
    if not ado_pat:
        print("❌ Error: ADO_WORK_ITEM_PAT environment variable not set", file=sys.stderr)
        sys.exit(1)
    os.environ['ADO_WORK_ITEM_PAT'] = ado_pat
    
    # Load questions from JSON
    questions_path = Path(args.questions_json)
    if not questions_path.exists():
        print(f"❌ Error: Questions JSON file not found: {questions_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(questions_path, 'r') as f:
        questions = json.load(f)
    
    print(f"📋 Loaded {len(questions)} questions from JSON")
    
    # Initialize LLM client if API key is available
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    client = None
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://ruste-mhinjxi0-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-5-nano",
                api_key=api_key,
                default_headers={'api-key': api_key}
            )
        except ImportError:
            print("⚠️  openai package not available, skipping LLM features", file=sys.stderr)
            api_key = None
    
    # Process each question
    for i, q in enumerate(questions, 1):
        try:
            topic = q.get('topic', f'Question {i}').strip()
            question_text = q.get('question', '').strip()
            context = q.get('context', '').strip()
            answer_options = q.get('answer_options', '').strip()
            recommended_option = q.get('recommended_option', '').strip() if q.get('recommended_option') else None
            suggested_answer = q.get('suggested_answer', '').strip() if q.get('suggested_answer') else None
            
            print(f"\n📝 Processing Question {i}: {topic}")
            
            # Generate idempotency key
            question_hash = hashlib.sha256(question_text.encode()).hexdigest()[:8]
            idempotency_key = f"{args.feature_id}-{question_hash}"
            
            # Build description
            description = build_description(
                question_num=i,
                topic=topic,
                question_text=question_text,
                context=context,
                answer_options=answer_options,
                recommended_option=recommended_option,
                suggested_answer=suggested_answer,
                branch_name=args.branch,
                use_llm=bool(api_key and client),
                api_key=api_key,
                client=client
            )
            
            # Extract clean topic for title (use LLM if available)
            if api_key and client:
                clean_topic = clean_topic_with_llm(topic, api_key, client)
            else:
                clean_topic = topic
            
            # Check if description contains HTML (from previous conversions)
            # If it does, convert to markdown first
            if '<' in description and '>' in description and not description.strip().startswith('#'):
                # Looks like HTML, convert to markdown
                print(f"🔄 Converting HTML to markdown...")
                description = convert_html_to_markdown(description)
            
            # Validate and fix markdown before sending to Azure DevOps
            validated_description, warnings = validate_and_fix_markdown(description)
            
            if warnings:
                print(f"⚠️  Markdown validation warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
            
            # Azure DevOps now supports markdown (2025) via /multilineFieldsFormat API
            # Send pure markdown - ado_client.py will set the format to Markdown
            final_description = validated_description
            
            # Final validation: ensure description is not empty
            if not final_description or not final_description.strip():
                print(f"❌ Error: Final description is empty for Question {i}, skipping issue creation", file=sys.stderr)
                print(f"   Raw description length: {len(description) if 'description' in locals() else 'N/A'}", file=sys.stderr)
                continue
            
            # Create Issue
            result = create_issue_workitem(
                parent_feature_id=int(args.feature_id),
                title=f"Q{i}: {clean_topic}",
                description=final_description,
                tags="clarification; auto-generated",
                idempotency_key=idempotency_key
            )
            
            if result:
                print(f"✅ Created Issue {result['id']}")
            else:
                print(f"⚠️ Issue creation failed for Question {i} (may be duplicate or API error)", file=sys.stderr)
                # Continue with next question
            
        except Exception as e:
            print(f"❌ Exception creating Issue for Question {i}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Continue with next question instead of failing entire script
    
    print(f"\n✅ Issue creation complete - processed {len(questions)} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

