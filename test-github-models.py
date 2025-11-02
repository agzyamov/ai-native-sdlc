#!/usr/bin/env python3
"""Test GitHub Models API authentication and permissions"""

import os
import sys
from openai import OpenAI

def test_github_models():
    # Get token from environment
    token = os.getenv('GITHUB_TOKEN') or os.getenv('COPILOT_TOKEN')
    
    if not token:
        print("❌ Error: No token found")
        print("Please set COPILOT_TOKEN or GITHUB_TOKEN environment variable")
        print("\nExample:")
        print("  export COPILOT_TOKEN='github_pat_xxxxx'")
        sys.exit(1)
    
    print(f"✅ Token found (length: {len(token)})")
    print(f"   Prefix: {token[:10]}...")
    
    # Initialize client
    print("\n🔌 Connecting to GitHub Models API...")
    client = OpenAI(
        base_url='https://models.github.ai/inference',
        api_key=token
    )
    
    # Test API call
    print("📡 Testing API call with gpt-4o model...")
    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Say "Hello, GitHub Models API is working!"'}
            ],
            temperature=0.0,
            max_tokens=50
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"\n✅ SUCCESS! API Response:")
        print(f"   {answer}")
        print(f"\n✅ Your token has the required 'models' permission")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
        if '401' in str(e) or 'unauthorized' in str(e).lower():
            print("\n🔍 Token Permission Issue:")
            print("   Your token is missing the 'models' permission")
            print("\n📋 To fix:")
            print("   1. Go to: https://github.com/settings/tokens")
            print("   2. Find your token (or create new fine-grained PAT)")
            print("   3. Under 'Account permissions', set 'models' to 'Read-only'")
            print("   4. Save and regenerate if needed")
            print("   5. Update your COPILOT_TOKEN environment variable")
        
        sys.exit(1)

if __name__ == '__main__':
    test_github_models()
