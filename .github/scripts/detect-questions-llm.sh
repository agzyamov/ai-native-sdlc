#!/bin/bash
# Detect if Copilot output contains clarification questions using GPT-4o
# Output: JSON with {has_questions: bool, reason: string}
# Prompts loaded from: .github/prompts/custom/detect-clarification-questions.*.md

set -euo pipefail

# Check if spec_output.txt exists
if [ ! -f "spec_output.txt" ]; then
    echo '{"has_questions": false, "reason": "ERROR: spec_output.txt not found"}' >&2
    exit 1
fi

# Run Python script with LLM detection logic
python3 << 'EOF'
import sys
import os
import json
from pathlib import Path
from openai import OpenAI

# Get Azure OpenAI API key from environment
api_key = os.getenv('AZURE_OPENAI_API_KEY')
if not api_key:
    sys.stderr.write('Error: AZURE_OPENAI_API_KEY environment variable not set\n')
    sys.exit(1)

# Initialize Azure OpenAI client
client = OpenAI(
    base_url='https://ruste-mhinjxi0-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-5-nano',
    api_key=api_key,
    default_headers={'api-key': api_key}
)

# Read Copilot output
try:
    with open('spec_output.txt', 'r') as f:
        copilot_output = f.read()
except FileNotFoundError:
    result = {'has_questions': False, 'reason': 'ERROR: spec_output.txt not found'}
    print(json.dumps(result))
    sys.exit(1)

# Clean GitHub Actions timestamps (format: "specify-feature\tStep 3-6 - ...\t2025-11-03T03:41:52.3630529Z ")
import re
copilot_output = re.sub(r'^[^\t]+\t[^\t]+\t\d{4}-\d{2}-\d{2}T[\d:.]+Z\s+', '', copilot_output, flags=re.MULTILINE)

# Load prompts from dedicated files
prompts_dir = Path('.github/prompts/custom')
system_prompt = (prompts_dir / 'detect-clarification-questions.system.md').read_text().strip()
user_template = (prompts_dir / 'detect-clarification-questions.user.md').read_text().strip()

# Replace placeholder in user prompt
user_prompt = user_template.replace('{copilot_output}', copilot_output)

# Call LLM to detect questions
try:
    response = client.chat.completions.create(
        model='gpt-5-nano',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.0,
        max_tokens=100,
        extra_query={'api-version': '2025-01-01-preview'}
    )
    
    answer = response.choices[0].message.content.strip()
    has_questions = answer.upper().startswith('YES')
    result = {'has_questions': has_questions, 'reason': answer}
    print(json.dumps(result))
    
except Exception as e:
    import traceback
    sys.stderr.write(f'Error calling Azure OpenAI API: {type(e).__name__}: {e}\n')
    sys.stderr.write(f'Full traceback:\n{traceback.format_exc()}\n')
    result = {'has_questions': False, 'reason': f'ERROR: API call failed - {str(e)}'}
    print(json.dumps(result))
    sys.exit(1)
EOF
