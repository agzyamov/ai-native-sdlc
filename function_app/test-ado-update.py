#!/usr/bin/env python3
"""
Test ADO work item description update locally.
"""
import os
import sys
import json
import requests
import base64

# Set environment variables
os.environ["ADO_ORG_URL"] = "https://dev.azure.com/RustemAgziamov"
os.environ["ADO_PROJECT"] = "ai-native-sdlc-blueprint"
os.environ["ADO_WORK_ITEM_PAT"] = "CT3dNvWwrwR6r1V8OaDNBLzHoGJMfVsWK5HoUP9Fykf8uBAbeEKNJQQJ99BJACAAAAAc0or1AAASAZDOaUC8"

WORK_ITEM_ID = 444
TEST_DESCRIPTION = """
<h2>Test Specification Update</h2>
<p>This is a test update from the Azure Function local testing.</p>
<p><strong>Updated at:</strong> 2025-10-28T02:35:00Z</p>
<p><strong>Feature:</strong> Test - Pacman game</p>
<h3>Requirements</h3>
<ul>
<li>Classic Pacman gameplay</li>
<li>Ghost AI</li>
<li>Score tracking</li>
</ul>
"""

def get_work_item(work_item_id: int) -> dict:
    """Fetch work item details."""
    org_url = os.environ["ADO_ORG_URL"]
    project = os.environ["ADO_PROJECT"]
    pat = os.environ["ADO_WORK_ITEM_PAT"]
    
    url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.1"
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


def update_work_item_description(work_item_id: int, description: str) -> bool:
    """Update work item description using PATCH operation."""
    org_url = os.environ["ADO_ORG_URL"]
    project = os.environ["ADO_PROJECT"]
    pat = os.environ["ADO_WORK_ITEM_PAT"]
    
    url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.1"
    auth_header = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json-patch+json"
    }
    
    # JSON Patch format for ADO API
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": description
        }
    ]
    
    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            print(f"✅ Successfully updated work item {work_item_id}")
            return True
        else:
            print(f"❌ Failed to update work item: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating work item: {str(e)}")
        return False


def main():
    print("=== ADO Work Item Description Update Test ===\n")
    
    # Step 1: Fetch current work item
    print(f"1️⃣ Fetching work item {WORK_ITEM_ID}...")
    try:
        work_item = get_work_item(WORK_ITEM_ID)
        print(f"   ✅ Found: {work_item['fields']['System.Title']}")
        print(f"   Type: {work_item['fields']['System.WorkItemType']}")
        print(f"   State: {work_item['fields']['System.State']}")
        
        current_desc = work_item['fields'].get('System.Description', '(empty)')
        print(f"\n   Current Description ({len(current_desc)} chars):")
        print(f"   {current_desc[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)
    
    # Step 2: Update description
    print(f"\n2️⃣ Updating description...")
    success = update_work_item_description(WORK_ITEM_ID, TEST_DESCRIPTION)
    
    if not success:
        sys.exit(1)
    
    # Step 3: Verify update
    print(f"\n3️⃣ Verifying update...")
    try:
        work_item = get_work_item(WORK_ITEM_ID)
        new_desc = work_item['fields'].get('System.Description', '(empty)')
        print(f"   ✅ New Description ({len(new_desc)} chars):")
        print(f"   {new_desc[:200]}...")
        
        if TEST_DESCRIPTION.strip() in new_desc:
            print("\n✅ SUCCESS - Description was updated correctly!")
        else:
            print("\n⚠️ WARNING - Description was updated but content doesn't match exactly")
    except Exception as e:
        print(f"   ❌ Error verifying: {e}")
        sys.exit(1)
    
    print("\n🎉 Test complete!")
    print(f"\nView work item: https://dev.azure.com/RustemAgziamov/ai-native-sdlc-blueprint/_workitems/edit/{WORK_ITEM_ID}")


if __name__ == "__main__":
    main()
