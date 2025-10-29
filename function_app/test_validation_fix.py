#!/usr/bin/env python3
"""
Test validation.py with the actual ADO webhook payload
"""
import json
import os
import sys

# Set environment variables for testing
os.environ["AI_USER_MATCH"] = "AI Teammate"
os.environ["SPEC_COLUMN_NAME"] = "Specification"

import validation

# The actual payload from ADO webhook
payload = {
    "subscriptionId": "20eeb007-3451-4aad-a749-4f069e36b67c",
    "notificationId": 1,
    "id": "12cbb67f-55b6-419a-b6bc-4ba2f1b4ba10",
    "eventType": "workitem.updated",
    "publisherId": "tfs",
    "resource": {
        "id": 4,
        "workItemId": 451,
        "rev": 4,
        "fields": {
            "System.Rev": {"oldValue": 3, "newValue": 4},
            "System.BoardColumn": {"oldValue": "New", "newValue": "Specification"}
        },
        "revision": {
            "id": 451,
            "rev": 4,
            "fields": {
                "System.WorkItemType": "Feature",
                "System.State": "Specification",
                "System.AssignedTo": "AI Teammate <Bot_AI_Teammate_ai-teammate@epam.com>",
                "System.Title": "test - motivation quotes",
                "System.BoardColumn": "Specification",
                "System.BoardColumnDone": False,
                "System.Description": "create motivation quote generator\n"
            }
        }
    }
}

print("Testing validation with actual ADO payload...")
print(f"Environment: AI_USER_MATCH={os.getenv('AI_USER_MATCH')}, SPEC_COLUMN_NAME={os.getenv('SPEC_COLUMN_NAME')}")
print()

is_valid, reason = validation.validate_event(payload)

print(f"Validation result: {is_valid}")
print(f"Reason: {reason}")
print()

if is_valid:
    print("✅ SUCCESS: Validation passed!")
    sys.exit(0)
else:
    print(f"❌ FAILURE: Validation failed - {reason}")
    sys.exit(1)
