#!/usr/bin/env python3
"""
Test the function logic directly (simulating what happens)
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set up environment
os.environ["AI_USER_MATCH"] = "AI Teammate"
os.environ["SPEC_COLUMN_NAME"] = "Specification"
os.environ["GITHUB_OWNER"] = "agzyamov"
os.environ["GITHUB_REPO"] = "ai-native-sdlc"
os.environ["GH_WORKFLOW_DISPATCH_PAT"] = "test-token"  # Won't actually call GitHub

# The exact payload
payload = {
    "subscriptionId": "20eeb007-3451-4aad-a749-4f069e36b67c",
    "notificationId": 79,
    "id": "efcf962e-c686-48d5-b6d7-2f6470ab275c",
    "eventType": "workitem.updated",
    "publisherId": "tfs",
    "resource": {
        "workItemId": 615,
        "revision": {
            "fields": {
                "System.WorkItemType": "Feature",
                "System.State": "Specification",
                "System.AssignedTo": "AI Teammate <Bot_AI_Teammate_ai-teammate@epam.com>",
                "System.Title": "hockey simulator game",
                "System.BoardColumn": "Specification",
                "System.BoardColumnDone": False,
                "System.Description": "create a hockey simulator game using unreal engine"
            }
        }
    }
}

print("=" * 70)
print("SIMULATING FUNCTION EXECUTION WITH WORK ITEM 615")
print("=" * 70)
print()

# Step 1: Parse payload
print("Step 1: Parse payload ✅")
body = payload
work_item_id = body["resource"]["workItemId"]
print(f"  Work Item ID: {work_item_id}")
print()

# Step 2: Validate config
print("Step 2: Validate configuration ✅")
import config
cfg = config.get_config()
config_valid, missing = cfg.validate()
print(f"  Config valid: {config_valid}")
if not config_valid:
    print(f"  Missing: {missing}")
    sys.exit(1)
print()

# Step 3: Validate event
print("Step 3: Validate event ✅")
import validation
is_valid, reason = validation.validate_event(body)
print(f"  Validation: {is_valid} - {reason}")
if not is_valid:
    print(f"  Would return 204 (filtered)")
    sys.exit(0)
print()

# Step 4: Try to fetch from ADO (THIS IS WHERE IT FAILS)
print("Step 4: Fetch work item from ADO API ❌")
print("  This is the problematic step!")
print()
print("  Code at line 105: work_item = ado_client.get_work_item(615)")
print("  ⚠️  If security blocks this HTTP call, it returns None")
print("  ⚠️  Line 108: if work_item is None: raise ValueError(...)")
print("  ⚠️  Lines 117-124: Exception caught → returns HTTP 500")
print()

# Check if we can use payload data instead
resource = body.get("resource", {})
revision = resource.get("revision", {})
fields = revision.get("fields", {})

if fields:
    description = fields.get("System.Description", "")
    title = fields.get("System.Title", f"Work Item #{work_item_id}")
    print("  ✅ PAYLOAD DATA AVAILABLE:")
    print(f"     Description: {description[:50]}...")
    print(f"     Title: {title}")
    print()
    print("  💡 SOLUTION: Use payload data instead of ADO API call!")
    print("     The ADO API call is unnecessary - all data is in the payload!")
else:
    print("  ❌ Payload missing revision.fields")
    print("  Would need ADO API call as fallback")

print()
print("=" * 70)
print("CONCLUSION:")
print("=" * 70)
print("The function fails at Step 4 because:")
print("  1. It tries to call ADO API (blocked by security)")
print("  2. ADO API returns None")
print("  3. Code raises ValueError")
print("  4. Returns HTTP 500")
print()
print("BUT the payload already has all the data needed!")
print("Fix: Use payload data first, only call ADO if payload is missing data.")
print("=" * 70)

