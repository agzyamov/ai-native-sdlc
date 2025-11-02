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

# Get GitHub token from environment
token = os.getenv('GITHUB_TOKEN') or os.getenv('COPILOT_TOKEN')
if not token:
    sys.stderr.write('Error: No GitHub token available (GITHUB_TOKEN or COPILOT_TOKEN)\n')
    sys.exit(1)

# Initialize GitHub Models client
client = OpenAI(
    base_url='https://models.inference.ai.azure.com',
    api_key=token
)

# Read Copilot output
try:
    with open('spec_output.txt', 'r') as f:
        copilot_output = f.read()
except FileNotFoundError:
    result = {'has_questions': False, 'reason': 'ERROR: spec_output.txt not found'}
    print(json.dumps(result))
    sys.exit(1)

# Load prompts from dedicated files
prompts_dir = Path('.github/prompts/custom')
system_prompt = (prompts_dir / 'detect-clarification-questions.system.md').read_text().strip()
user_template = (prompts_dir / 'detect-clarification-questions.user.md').read_text().strip()

# Replace placeholder in user prompt
user_prompt = user_template.replace('{copilot_output}', copilot_output)

# Call LLM to detect questions
try:
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.0,
        max_tokens=100
    )
    
    answer = response.choices[0].message.content.strip()
    has_questions = answer.upper().startswith('YES')
    result = {'has_questions': has_questions, 'reason': answer}
    print(json.dumps(result))
    
except Exception as e:
    sys.stderr.write(f'Error calling GitHub Models API: {e}\n')
    result = {'has_questions': False, 'reason': f'ERROR: API call failed - {str(e)}'}
    print(json.dumps(result))
    sys.exit(1)
EOF
